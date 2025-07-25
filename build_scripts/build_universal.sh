#!/bin/bash
# Full universal build script for macOS
# Builds both x86_64 and arm64 versions and combines them

# Make sure we fail on any error
set -e

# Parse command line arguments
ONEFILE_ARG=""
PLATFORM_ARG=""
CLEAN_ARG=""

for arg in "$@"
do
    if [[ "$arg" == "--onefile" ]]; then
        ONEFILE_ARG="--onefile"
    elif [[ "$arg" == "--platform" ]]; then
        PLATFORM_ARG="--platform"
    elif [[ "$arg" == "--clean" ]]; then
        CLEAN_ARG="--clean"
    fi
done

# Determine architecture
CURRENT_ARCH=$(uname -m)
echo "🔍 Current architecture: $CURRENT_ARCH"

# Clean artifacts if requested
if [[ -n "$CLEAN_ARG" ]]; then
    echo "🧹 Cleaning build artifacts..."
    rm -rf build/Qrew dist/* Qrew.spec
fi

# Step 1: Build native architecture version
echo "🏗️ Building for native architecture ($CURRENT_ARCH)..."
python build_scripts/build.py $ONEFILE_ARG $PLATFORM_ARG

# Check what was built
if [[ "$ONEFILE_ARG" == "--onefile" ]]; then
    if [ -f "dist/Qrew" ]; then
        echo "✅ Native executable built: dist/Qrew"
        NATIVE_BINARY="dist/Qrew"
        # Make a copy with architecture suffix
        if [[ "$CURRENT_ARCH" == "x86_64" ]]; then
            cp "dist/Qrew" "dist/Qrew-x86_64"
            echo "📋 Copied to dist/Qrew-x86_64"
        else
            cp "dist/Qrew" "dist/Qrew-arm64"
            echo "📋 Copied to dist/Qrew-arm64"
        fi
    else
        echo "❌ Native executable build failed"
        exit 1
    fi
else
    if [ -d "dist/Qrew.app" ]; then
        echo "✅ Native app bundle built: dist/Qrew.app"
        NATIVE_APP="dist/Qrew.app"
        # Make a copy with architecture suffix
        if [[ "$CURRENT_ARCH" == "x86_64" ]]; then
            cp -r "dist/Qrew.app" "dist/Qrew-x86_64.app"
            echo "📋 Copied to dist/Qrew-x86_64.app"
        else
            cp -r "dist/Qrew.app" "dist/Qrew-arm64.app"
            echo "📋 Copied to dist/Qrew-arm64.app"
        fi
    else
        echo "❌ Native app bundle build failed"
        exit 1
    fi
fi

# Step 2: Build non-native architecture version
if [[ "$CURRENT_ARCH" == "x86_64" ]]; then
    echo "🏗️ Building for arm64 architecture..."
    bash build_scripts/build_arm64.sh $ONEFILE_ARG $PLATFORM_ARG
    
    # Check what was built
    if [[ "$ONEFILE_ARG" == "--onefile" ]]; then
        if [ -f "dist/Qrew-arm64" ]; then
            echo "✅ arm64 executable built: dist/Qrew-arm64"
            CROSS_BINARY="dist/Qrew-arm64"
        else
            echo "❌ arm64 executable build failed"
            exit 1
        fi
    else
        if [ -d "dist/Qrew-arm64.app" ]; then
            echo "✅ arm64 app bundle built: dist/Qrew-arm64.app"
            CROSS_APP="dist/Qrew-arm64.app"
        else
            echo "❌ arm64 app bundle build failed"
            exit 1
        fi
    fi
else
    echo "🏗️ Building for x86_64 architecture..."
    echo "❌ Cross-compilation from arm64 to x86_64 not implemented yet"
    echo "Please build the x86_64 version on an Intel Mac"
    exit 1
fi

# Step 3: Create universal binary
echo "🔄 Creating universal binary..."

if [[ "$ONEFILE_ARG" == "--onefile" ]]; then
    python build_scripts/create_universal.py "dist/Qrew-x86_64" "dist/Qrew-arm64" "dist/Qrew-universal"
    
    if [ -f "dist/Qrew-universal" ]; then
        echo "✅ Universal executable created: dist/Qrew-universal"
        file "dist/Qrew-universal"
        
        # Replace the original binary with the universal version
        mv "dist/Qrew-universal" "dist/Qrew"
        echo "📋 Moved to dist/Qrew"
    else
        echo "❌ Universal executable creation failed"
        exit 1
    fi
else
    python build_scripts/create_universal.py "dist/Qrew-x86_64.app" "dist/Qrew-arm64.app" "dist/Qrew-universal.app"
    
    if [ -d "dist/Qrew-universal.app" ]; then
        echo "✅ Universal app bundle created: dist/Qrew-universal.app"
        file "dist/Qrew-universal.app/Contents/MacOS/Qrew"
        
        # Replace the original app with the universal version
        rm -rf "dist/Qrew.app"
        mv "dist/Qrew-universal.app" "dist/Qrew.app"
        echo "📋 Moved to dist/Qrew.app"
        
        # Create DMG if needed
        if [[ -n "$PLATFORM_ARG" ]]; then
            echo "📀 Creating DMG package..."
            python build_scripts/build_macos.py --create-dmg-only "dist/Qrew.app"
        fi
    else
        echo "❌ Universal app bundle creation failed"
        exit 1
    fi
fi

echo "✨ Universal build complete!"
