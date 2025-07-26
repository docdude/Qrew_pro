# GitHub Workflows and macOS Universal Builds for Qrew

This document explains how the GitHub Actions workflow has been configured to build macOS universal binaries for Qrew, combining both x86_64 and arm64 architectures.

## Workflow Structure

The GitHub Actions workflow (`.github/workflows/build.yml`) has been updated to:

1. Build on native architectures (Intel x86_64, Apple Silicon arm64)
2. Support cross-compilation from Intel to arm64 using build_arm64_universal2.sh
3. Create universal binaries by combining architecture-specific builds

## Build Matrix Strategy

The macOS build job now includes three configurations:

```yaml
strategy:
  matrix:
    include:
      - arch: x86_64
        runner: macos-13  # Intel runner
      - arch: arm64
        runner: macos-14  # Native Apple Silicon runner
      - arch: arm64-crosscompile
        runner: macos-13  # Intel runner with cross-compilation
```

## Building arm64 on Intel Macs (Cross-Compilation)

When building on GitHub Actions, the workflow:

1. Installs Python.org's Universal2 Python distribution
2. Uses the `build_arm64_universal2.sh` script to create an arm64 build 
3. Configures the environment properly for PyInstaller cross-compilation

## Universal Binary Creation

After building both architectures, the workflow:

1. Downloads the architecture-specific artifacts
2. Extracts the app bundles from DMGs or zip files
3. Uses `create_universal.py` to combine them
4. Creates a universal DMG package

## Script Integration

The scripts interact in the following way:

1. `build.py`: Standard build script for native architecture
2. `build_arm64_universal2.sh`: Cross-compile for arm64 on Intel Macs
3. `create_universal.py`: Combine x86_64 and arm64 builds
4. `build_macos.py`: Create DMGs and handle notarization

## Cross-Compilation Requirements

For cross-compilation to work on Intel Macs:

1. A Universal2 Python installation is required
2. Dependencies need Universal2 wheels when possible
3. PyInstaller target_arch needs to be set correctly

## Troubleshooting

If cross-compilation fails:

1. Check if Python contains both architectures:
   ```bash
   file $(which python3) | grep -o "x86_64\|arm64"
   ```

2. Verify PyInstaller spec file has correct target architecture:
   ```bash
   grep -q "target_arch='arm64'" Qrew.spec
   ```

3. Check binary outputs for the right architecture:
   ```bash
   file dist/Qrew-arm64.app/Contents/MacOS/Qrew
   ```

## Setting up Locally vs GitHub Actions

When running on GitHub Actions, Universal2 Python is downloaded and installed during the workflow.
For local development, you should install Python.org's Universal2 Python manually.

## Important Environment Variables

- `MACOS_BUILD_ARCH`: Set to "arm64" for cross-compilation
- `_PYTHON_HOST_PLATFORM`: Set to "macosx-11.0-arm64" for PyInstaller
- `UNIVERSAL_PYTHON_PATH`: Optional path to Universal2 Python installation
