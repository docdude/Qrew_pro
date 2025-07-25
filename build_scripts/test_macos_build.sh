#!/bin/bash
# Script to test macOS build scripts functionality

# Stop on first error
set -e

# Get current architecture
ARCH=$(uname -m)
echo "🔍 Current architecture: $ARCH"

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function test_build_script {
  name=$1
  script=$2
  args=$3
  
  echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}Testing: ${name}${NC}"
  echo -e "${BLUE}Command: ${script} ${args}${NC}"
  echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
  
  # Clean any old build artifacts
  rm -rf build/Qrew dist/*.app dist/*.dmg Qrew.spec
  
  # Run the build script with specified args
  if $script $args; then
    echo -e "${GREEN}✅ Test passed: ${name}${NC}"
    return 0
  else
    echo -e "${RED}❌ Test failed: ${name}${NC}"
    return 1
  fi
}

function test_file_architecture {
  file_path=$1
  expected_arch=$2
  
  echo -e "${BLUE}Testing architecture of: ${file_path}${NC}"
  
  if [ ! -e "$file_path" ]; then
    echo -e "${RED}❌ File not found: ${file_path}${NC}"
    return 1
  fi
  
  archs=$(file "$file_path" | grep -o "x86_64\|arm64")
  
  if [[ "$archs" == *"$expected_arch"* ]]; then
    echo -e "${GREEN}✅ File contains expected architecture: ${expected_arch}${NC}"
    return 0
  else
    echo -e "${RED}❌ Architecture mismatch. Expected: ${expected_arch}, Found: ${archs}${NC}"
    return 1
  fi
}

# Print header
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Testing macOS Build Scripts for Qrew${NC}"
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo
echo -e "${YELLOW}This test script verifies both build approaches:${NC}"
echo -e "1. Native builds for current architecture (preferred for CI)"
echo -e "2. Cross-compilation using Universal2 Python (alternative/fallback)"
echo

# Test 1: Native build (minimal)
test_build_script "Native Build (Minimal)" "python build_scripts/build.py" "--clean"

# Check architecture of native build
if [ -d "dist/Qrew.app" ]; then
  test_file_architecture "dist/Qrew.app/Contents/MacOS/Qrew" "$ARCH"
elif [ -f "dist/Qrew" ]; then
  test_file_architecture "dist/Qrew" "$ARCH"
else
  echo -e "${RED}❌ Native build output not found${NC}"
fi

# Test 2: If we're on Intel, test arm64 cross-compilation
if [ "$ARCH" == "x86_64" ]; then
  if [ -f "/Library/Frameworks/Python.framework/Versions/3.10/bin/python3" ]; then
    test_build_script "ARM64 Cross-Compilation" "bash build_scripts/build_arm64_universal2.sh" "--clean"
    
    # Check architecture of arm64 build
    if [ -d "dist/Qrew-arm64.app" ]; then
      test_file_architecture "dist/Qrew-arm64.app/Contents/MacOS/Qrew" "arm64"
    elif [ -f "dist/Qrew-arm64" ]; then
      test_file_architecture "dist/Qrew-arm64" "arm64"
    else
      echo -e "${RED}❌ ARM64 build output not found${NC}"
    fi
    
    # Test 3: Universal binary creation
    if [ -d "dist/Qrew.app" ] && [ -d "dist/Qrew-arm64.app" ]; then
      echo -e "${BLUE}Testing Universal App Bundle Creation${NC}"
      mkdir -p dist/universal
      
      # Run create_universal.py
      if python build_scripts/create_universal.py dist/Qrew.app dist/Qrew-arm64.app dist/universal/Qrew.app; then
        echo -e "${GREEN}✅ Universal app bundle created${NC}"
        
        # Check architecture of universal build
        test_file_architecture "dist/universal/Qrew.app/Contents/MacOS/Qrew" "x86_64"
        test_file_architecture "dist/universal/Qrew.app/Contents/MacOS/Qrew" "arm64"
      else
        echo -e "${RED}❌ Failed to create universal app bundle${NC}"
      fi
    elif [ -f "dist/Qrew" ] && [ -f "dist/Qrew-arm64" ]; then
      echo -e "${BLUE}Testing Universal Executable Creation${NC}"
      mkdir -p dist/universal
      
      # Run create_universal.py
      if python build_scripts/create_universal.py dist/Qrew dist/Qrew-arm64 dist/universal/Qrew; then
        echo -e "${GREEN}✅ Universal executable created${NC}"
        
        # Check architecture of universal build
        test_file_architecture "dist/universal/Qrew" "x86_64"
        test_file_architecture "dist/universal/Qrew" "arm64"
      else
        echo -e "${RED}❌ Failed to create universal executable${NC}"
      fi
    else
      echo -e "${YELLOW}⚠️ Cannot test universal binary creation, missing required builds${NC}"
    fi
  else
    echo -e "${YELLOW}⚠️ Skipping ARM64 cross-compilation test - Universal2 Python not found${NC}"
    echo "Please install Python from python.org to test cross-compilation"
  fi
else
  echo -e "${YELLOW}⚠️ Skipping ARM64 cross-compilation test - running on ${ARCH}${NC}"
fi

echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}All tests completed!${NC}"
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
