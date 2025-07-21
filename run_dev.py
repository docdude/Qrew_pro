#!/usr/bin/env python3
"""
Development launcher for Qrew - handles import paths
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    from qrew.main import main
    main()
