# macOS Universal Binary Build Guide

## Recommended Approach for GitHub Actions

For building universal macOS applications in GitHub Actions, we recommend using **native architecture runners** when possible:

1. Use `macos-13` (Intel) for x86_64 builds
2. Use `macos-14` (Apple Silicon) for arm64 builds 
3. Combine them with `create_universal.py`

This approach produces the most reliable binaries because each architecture is built on its native hardware.

## Alternative Approach: Cross-Compilation

If Apple Silicon runners aren't available, or you need to build locally on an Intel Mac:

1. Install Universal2 Python from python.org
2. Use `build_arm64_universal2.sh` to cross-compile for arm64
3. Combine with an Intel build using `create_universal.py`

## Choosing the Right Approach

- **For GitHub Actions**: The workflow uses both approaches, preferring native builds
- **For local development**: 
  - On Apple Silicon Mac: Just use normal builds
  - On Intel Mac: Use cross-compilation with Universal2 Python

## Build Script Reference

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `build.py` | Standard build for current architecture | Always |
| `build_arm64_universal2.sh` | Cross-compile for arm64 on Intel | When Apple Silicon isn't available |
| `create_universal.py` | Combine x86_64 and arm64 builds | Always for universal binaries |
| `test_macos_build.sh` | Test all build approaches | When validating build scripts |
