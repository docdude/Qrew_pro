# macOS Universal Build Guide for Qrew

This guide explains how to build universal macOS binaries for Qrew that run natively on both Intel (x86_64) and Apple Silicon (arm64) Macs.

## Prerequisites

- macOS 10.15 or newer
- Python from Python.org (Universal2 binary)
- PyInstaller 5.9 or newer
- Xcode Command Line Tools

## Installation Steps

1. **Install Python from Python.org**

   Download and install Python from [Python.org](https://www.python.org/downloads/macos/). This version contains Universal2 binaries with both x86_64 and arm64 code.

   **Important**: Do not use Homebrew Python for cross-compilation, as it only contains the native architecture.

2. **Install Xcode Command Line Tools**

   ```bash
   xcode-select --install
   ```

3. **Clone Qrew Repository**

   ```bash
   git clone https://github.com/yourusername/qrew.git
   cd qrew
   ```

4. **Install Development Dependencies**

   ```bash
   pip install -e .[dev]
   ```

## Building Universal Binaries

You can create universal binaries through two methods:

### Method 1: Build Separately and Combine

1. **Build Intel (x86_64) Version**

   ```bash
   # Using your regular Python installation
   python build_scripts/build.py [options]
   # This creates dist/Qrew.app or dist/Qrew
   ```

2. **Build Apple Silicon (arm64) Version**

   ```bash
   # Using the cross-compilation script
   bash build_scripts/build_arm64.sh [options]
   # This creates dist/Qrew-arm64.app or dist/Qrew-arm64
   ```

3. **Create Universal Binary**

   ```bash
   # For app bundles
   python build_scripts/create_universal.py dist/Qrew.app dist/Qrew-arm64.app dist/Qrew-universal.app
   
   # For standalone executables
   python build_scripts/create_universal.py dist/Qrew dist/Qrew-arm64 dist/Qrew-universal
   ```

### Method 2: Full Universal Build

```bash
# This script automates all the steps above
bash build_scripts/build_universal.sh [options]
```

## Troubleshooting

### Binary Architecture Problems

If you get errors about incompatible architectures:

1. Verify your Python installation has Universal2 support:

   ```bash
   file /Library/Frameworks/Python.framework/Versions/3.x/bin/python3
   # Should show both x86_64 and arm64
   ```

2. Check your PyInstaller version:

   ```bash
   pip show pyinstaller
   # Should be 5.9 or newer
   ```

3. Check if libraries are universal:

   ```bash
   # For important libraries
   file venv_universal2/lib/python3.x/site-packages/PyQt6/QtCore.abi3.so
   # Should contain both architectures
   ```

### Cross-Compilation Limitations

- Some Python extensions don't have arm64 binaries available
- PyInstaller cannot convert architecture-specific binaries
- Dynamic libraries need to include the target architecture

For best results, use a full universal Python installation from Python.org.

## Notes

- The Universal2 Python approach allows building arm64 binaries on Intel Macs
- For production builds, testing on both architectures is recommended
- Careful handling of architecture-specific dependencies is important
