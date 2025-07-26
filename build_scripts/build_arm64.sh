#!/bin/bash
# Cross-compile Qrew for arm64 on Intel Mac using Universal2 Python

# Make sure we fail on any error
set -e

# Check if we're running on Intel Mac
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
  echo "✅ Running on $ARCH architecture - no need for cross-compilation"
  echo "Use normal build process instead of this script"
  exit 0
fi

# Set environment variables for the build
export MACOS_BUILD_ARCH=arm64

# Use Universal2 Python approach
echo "🔍 Checking for Universal2 Python installation..."

# Look for Python.org's Universal2 Python
UNIVERSAL_PYTHON_PATHS=(
  "/Library/Frameworks/Python.framework/Versions/3.9/bin/python3"
  "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3"
  "/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
)

UNIVERSAL_PYTHON=""
for python_path in "${UNIVERSAL_PYTHON_PATHS[@]}"; do
  if [ -f "$python_path" ]; then
    # Check if it's a Universal2 binary
    if file "$python_path" | grep -q "arm64"; then
      UNIVERSAL_PYTHON="$python_path"
      break
    fi
  fi
done

if [ -z "$UNIVERSAL_PYTHON" ]; then
  echo "❌ No Universal2 Python found from Python.org"
  echo ""
  echo "To cross-compile for arm64 on Intel Mac, you need a Universal2 Python installation"
  echo "containing both x86_64 and arm64 binaries."
  echo ""
  echo "Please download and install Python from Python.org (NOT Homebrew):"
  echo "https://www.python.org/downloads/macos/"
  echo ""
  echo "After installing, run this script again."
  exit 1
fi

echo "✅ Found Universal2 Python: $($UNIVERSAL_PYTHON --version)"
echo "📦 Binary includes architectures: $(file "$UNIVERSAL_PYTHON" | grep -o "x86_64\|arm64")"

# Set up virtual environment with Universal2 Python
VENV_NAME="venv_universal2"
echo "🏗️ Setting up virtual environment with Universal2 Python..."

if [ -d "$VENV_NAME" ]; then
  echo "🧹 Removing existing virtual environment..."
  rm -rf "$VENV_NAME"
fi

$UNIVERSAL_PYTHON -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

# Verify the Python in the virtual environment is Universal2
VENV_PYTHON_PATH=$(which python3)
echo "🔍 Using Python from venv: $VENV_PYTHON_PATH"
echo "📦 Python architectures: $(file "$VENV_PYTHON_PATH" | grep -o "x86_64\|arm64")"

# Install required packages in the virtual environment
echo "📦 Installing build requirements..."
pip install --upgrade pip wheel
pip install -e .[dev]
pip install pyinstaller>=5.9

# Clean any old build artifacts
echo "🧹 Cleaning previous builds..."
rm -rf build/Qrew dist/*.app dist/*.dmg Qrew.spec

# Generate the spec file with proper architecture
echo "📝 Generating PyInstaller spec file for arm64..."
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

# Run PyInstaller directly with the spec file
echo "🏗️ Building arm64 package with PyInstaller..."
# Set environment variable for architecture tracking
export _PYTHON_HOST_PLATFORM=macosx-11.0-arm64
# Run PyInstaller in verbose mode for debugging
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
    if [ -d "dist/Qrew-arm64.app" ]; then
      python build_scripts/build_macos.py --create-dmg-only dist/Qrew-arm64.app
    else
      echo "⚠️ No app bundle found for DMG creation"
    fi
  fi
  
  # Deactivate virtual environment
  deactivate
  echo "🧹 Cleaning up virtual environment..."
  rm -rf "$VENV_NAME"
else
  echo "❌ Build failed"
  # Deactivate virtual environment before exiting
  deactivate
  exit 1
fi

echo "✨ Done!"
