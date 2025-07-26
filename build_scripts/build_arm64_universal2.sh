#!/bin/bash
# Cross-compile Qrew for ARM64 architecture on Intel Macs using Python.org's Universal2 Python
#
# NOTE: This is an alternative to native builds. When possible, prefer building on Apple Silicon directly.
# This script is primarily useful for development on Intel Macs or when Apple Silicon runners aren't available.

# Make sure we fail on any error
set -e

# Check for custom Python path from environment variable or use default
PYTHON_PATH=${UNIVERSAL_PYTHON_PATH:-"/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"}
VENV_DIR="venv_universal2"

# Try multiple potential locations for Universal2 Python
if [ ! -f "$PYTHON_PATH" ]; then
  echo "🔍 Universal2 Python not found at $PYTHON_PATH, trying alternative locations..."
  
  # Look in other common locations
  POTENTIAL_PATHS=(
    "/Library/Frameworks/Python.framework/Versions/3.9/bin/python3"
    "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
    "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
  )
  
  for path in "${POTENTIAL_PATHS[@]}"; do
    if [ -f "$path" ]; then
      echo "✅ Found Python at $path"
      PYTHON_PATH=$path
      break
    fi
  done
fi

# Final check if we found a usable Python
if [ ! -f "$PYTHON_PATH" ]; then
  echo "❌ Universal2 Python from Python.org not found"
  echo "Please download and install Python from python.org, which includes Universal2 binaries"
  echo "Visit: https://www.python.org/downloads/macos/"
  exit 1
fi

echo "🔍 Found Python.org's Universal2 Python: $($PYTHON_PATH --version)"

# Setup Python environment with Universal2 Python
echo "🏗️ Setting up virtual environment with Universal2 Python..."
$PYTHON_PATH -m venv "$VENV_DIR" --clear
source "$VENV_DIR/bin/activate"

# Verify the Python is Universal2
ARCHS=$(file $(which python3) | grep -o "x86_64\|arm64")
if [[ "$ARCHS" == *"arm64"* ]]; then
  echo "✅ Universal2 Python properly set up, contains ARM64 architecture"
else
  echo "❌ Python doesn't contain ARM64 architecture: $ARCHS"
  exit 1
fi

# Install requirements
echo "📦 Installing requirements..."
pip install -U pip wheel
pip install -e .[dev]
pip install pyinstaller>=5.9

# Clean previous build artifacts
echo "🧹 Cleaning previous builds..."
rm -rf build/Qrew dist/*.app dist/*.dmg Qrew.spec

# Generate spec file with ARM64 target architecture
echo "📝 Generating PyInstaller spec file for arm64..."
export MACOS_BUILD_ARCH=arm64
python build_scripts/build_spec.py $([[ "$*" == *"--onefile"* ]] && echo "--onefile")

# Verify the spec file has correct architecture
if grep -q "target_arch='arm64'" Qrew.spec; then
  echo "✅ Spec file correctly configured for arm64"
else
  echo "❌ Spec file doesn't contain target_arch='arm64'"
  echo "Generated spec file content:"
  cat Qrew.spec
  exit 1
fi

# Run PyInstaller for ARM64
echo "🏗️ Building arm64 package with PyInstaller..."
# Key environment variable for cross-compilation
export _PYTHON_HOST_PLATFORM=macosx-11.0-arm64
python -m PyInstaller --log-level=INFO Qrew.spec

# Check if build succeeded
if [ $? -eq 0 ]; then
  echo "✅ Build completed successfully"
  
  # Check what was built
  if [ -d "dist/Qrew.app" ]; then
    echo "📦 Built app bundle: dist/Qrew.app"
    file dist/Qrew.app/Contents/MacOS/Qrew
    # Rename for clarity
    mv dist/Qrew.app dist/Qrew-arm64.app
    echo "📦 Renamed to: dist/Qrew-arm64.app"
  elif [ -f "dist/Qrew" ]; then
    echo "📦 Built executable: dist/Qrew"
    file dist/Qrew
    # Rename for clarity
    mv dist/Qrew dist/Qrew-arm64
    echo "📦 Renamed to: dist/Qrew-arm64"
  else
    echo "⚠️ Built files not found in expected location"
    ls -la dist/
  fi
  
  # Create DMG if needed
  if [[ "$*" == *"--platform"* ]]; then
    echo "📀 Creating DMG package..."
    python build_scripts/build_macos.py --create-dmg-only dist/Qrew-arm64.app
  fi
else
  echo "❌ Build failed"
  exit 1
fi

echo "✨ Done!"

# Deactivate virtual environment
deactivate
echo "🧹 You can remove the temporary virtual environment with: rm -rf $VENV_DIR"
