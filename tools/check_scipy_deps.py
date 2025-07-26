#!/usr/bin/env python3
"""
Check what packages are importing scipy
"""

import sys
import importlib.util
from pathlib import Path

def find_scipy_importers():
    """Find which packages in your environment import scipy"""
    print("Checking for packages that import scipy...")
    
    # Common packages that might import scipy
    suspects = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'sklearn', 
        'statsmodels', 'plotly', 'bokeh', 'altair', 'colour', 'colorspacious'
    ]
    
    scipy_importers = []
    
    for package in suspects:
        try:
            # Try to import the package
            spec = importlib.util.find_spec(package)
            if spec is not None:
                print(f"✓ Found {package}")
                
                # Try to import and see if it brings in scipy
                try:
                    module = importlib.import_module(package)
                    
                    # Check if scipy is now in sys.modules
                    scipy_modules = [m for m in sys.modules.keys() if m.startswith('scipy')]
                    if scipy_modules:
                        scipy_importers.append(package)
                        print(f"  → {package} imports scipy modules: {scipy_modules[:3]}...")
                    else:
                        print(f"  → {package} does not import scipy")
                        
                except ImportError as e:
                    print(f"  → {package} failed to import: {e}")
                    
        except ImportError:
            print(f"✗ {package} not installed")
            
    return scipy_importers

def check_your_imports():
    """Check your actual project imports"""
    print("\nChecking your project's direct imports...")
    
    # Look for imports in your main files
    qrew_dir = Path("qrew")
    if qrew_dir.exists():
        for py_file in qrew_dir.glob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    if 'scipy' in content.lower():
                        print(f"Found scipy reference in {py_file}")
                        # Find the specific lines
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if 'scipy' in line.lower():
                                print(f"  Line {i}: {line.strip()}")
            except Exception as e:
                print(f"Could not read {py_file}: {e}")

if __name__ == "__main__":
    print("=== SCIPY DEPENDENCY CHECKER ===")
    
    # Check initial state
    initial_scipy = [m for m in sys.modules.keys() if m.startswith('scipy')]
    print(f"Initial scipy modules loaded: {len(initial_scipy)}")
    
    # Find importers
    importers = find_scipy_importers()
    
    print(f"\nPackages that import scipy: {importers}")
    
    # Check your code
    check_your_imports()
    
    print("\n=== RECOMMENDATIONS ===")
    if importers:
        print("To fix the scipy warnings:")
        print("1. The updated build_config.py already excludes scipy aggressively")
        print("2. Consider if you really need these packages:", importers)
        print("3. Some alternatives:")
        for pkg in importers:
            if pkg == 'pandas':
                print("   - pandas: You might only need basic DataFrame operations")
            elif pkg == 'colour':
                print("   - colour: Consider using a simpler color library")
        print("4. The warnings won't affect functionality, just build size")
    else:
        print("No obvious scipy importers found. The warnings might be from:")
        print("- Transitive dependencies")
        print("- PyQt5 optional features")
        print("- Build environment packages")