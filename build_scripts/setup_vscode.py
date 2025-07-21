"""
Setup VSCode integration for Qrew
"""

import json
import os
from pathlib import Path


def setup_vscode():
    """Setup complete VSCode integration"""
    print("Setting up VSCode integration for Qrew...")

    # Create .vscode directory
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    # Configuration files to create
    configs = {
        "settings.json": get_settings(),
        "tasks.json": get_tasks(),
        "launch.json": get_launch(),
        "extensions.json": get_extensions(),
    }

    # Write each configuration file
    for filename, config in configs.items():
        config_file = vscode_dir / filename
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
        print(f"✓ Created {config_file}")

    # Create workspace file
    workspace_file = Path("qrew.code-workspace")
    with open(workspace_file, "w") as f:
        json.dump(get_workspace(), f, indent=4)
    print(f"✓ Created {workspace_file}")

    # Create additional files
    create_additional_files()

    print("\n🎉 VSCode integration setup complete!")
    print("📁 Open the workspace with: code qrew.code-workspace")
    print("🔧 Available keyboard shortcuts:")
    print("   • Ctrl+Shift+B (Cmd+Shift+B): Full Build")
    print("   • Ctrl+F5 (Cmd+F5): Run Qrew")
    print("   • F5: Start Debugging")


def get_settings():
    """VSCode workspace settings"""
    return {
        "python.defaultInterpreterPath": "./venv/bin/python",
        "python.terminal.activateEnvironment": True,
        "python.linting.enabled": True,
        "python.linting.pylintEnabled": True,
        "python.linting.flake8Enabled": True,
        "python.formatting.provider": "black",
        "python.formatting.blackArgs": ["--line-length", "88"],
        "python.testing.pytestEnabled": True,
        "python.testing.unittestEnabled": False,
        "python.testing.pytestArgs": ["tests"],
        "files.associations": {
            "*.spec": "python",
            "*.nsi": "nsis",
            "*.desktop": "properties",
        },
        "files.exclude": {
            "**/__pycache__": True,
            "**/build": True,
            "**/dist": True,
            "**/*.pyc": True,
            "**/.pytest_cache": True,
            "**/venv": True,
            "**/.tox": True,
        },
        "editor.formatOnSave": True,
        "editor.codeActionsOnSave": {"source.organizeImports": True},
        "terminal.integrated.env.osx": {"PYTHONPATH": "${workspaceFolder}"},
        "terminal.integrated.env.linux": {"PYTHONPATH": "${workspaceFolder}"},
        "terminal.integrated.env.windows": {"PYTHONPATH": "${workspaceFolder}"},
        "python.analysis.extraPaths": ["./qrew"],
    }


def get_tasks():
    return {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Setup Development Environment",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["-m", "pip", "install", "-e", ".[dev]"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Install Build Dependencies",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["build_scripts/build.py", "--deps"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Clean Build",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["build_scripts/build.py", "--clean"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Build PyInstaller Only",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["build_scripts/build.py"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Build Platform Installer",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["build_scripts/build.py", "--platform"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Full Build (Clean + Platform)",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["build_scripts/build.py", "--clean", "--platform"],
                "group": {"kind": "build", "isDefault": True},
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Run Qrew (Development)",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["-m", "qrew"],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Run Qrew Direct",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["run_dev.py"],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["-m", "pytest", "tests/", "-v"],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Format Code",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["-m", "black", "qrew/", "tests/"],
                "group": "build",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
            {
                "label": "Lint Code",
                "type": "shell",
                "command": "${command:python.interpreterPath}",
                "args": ["-m", "flake8", "qrew/"],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared",
                },
                "problemMatcher": [],
            },
        ],
    }


def get_launch():
    """VSCode launch configurations for debugging"""
    return {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Debug Qrew Main",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/qrew/main.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}"},
                "args": [],
                "justMyCode": False,
            },
            {
                "name": "Debug Qrew Module",
                "type": "python",
                "request": "launch",
                "module": "qrew",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}"},
                "args": [],
                "justMyCode": False,
            },
            {
                "name": "Debug Build Script",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/build_scripts/build.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "args": ["--clean"],
                "justMyCode": False,
            },
            {
                "name": "Debug Tests",
                "type": "python",
                "request": "launch",
                "module": "pytest",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "args": ["tests/", "-v", "--tb=short"],
                "justMyCode": False,
            },
            {
                "name": "Debug Current File",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}"},
                "justMyCode": False,
            },
        ],
    }


def get_extensions():
    """Recommended VSCode extensions"""
    return {
        "recommendations": [
            "ms-python.python",
            "ms-python.flake8",
            "ms-python.black-formatter",
            "ms-python.pylint",
            "ms-vscode.vscode-json",
            "redhat.vscode-yaml",
            "ms-python.debugpy",
            "ms-python.isort",
            "njpwerner.autodocstring",
            "ms-python.mypy-type-checker",
            "ms-vscode.test-adapter-converter",
            "littlefoxteam.vscode-python-test-adapter",
            "idleberg.nsis",
        ]
    }


def get_workspace():
    """VSCode workspace configuration"""
    return {
        "folders": [{"path": "."}],
        "settings": {
            "python.defaultInterpreterPath": "./venv/bin/python",
            "python.terminal.activateEnvironment": True,
            "files.exclude": {
                "**/__pycache__": True,
                "**/build": True,
                "**/dist": True,
                "**/*.pyc": True,
                "**/venv": True,
            },
        },
        "tasks": {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Quick Build",
                    "type": "shell",
                    "command": "python build_scripts/build.py --clean --platform",
                    "group": {"kind": "build", "isDefault": True},
                }
            ],
        },
        "launch": {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Debug Qrew",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/qrew/main.py",
                    "console": "integratedTerminal",
                }
            ],
        },
        "extensions": {
            "recommendations": [
                "ms-python.python",
                "ms-python.flake8",
                "ms-python.black-formatter",
            ]
        },
    }


def create_additional_files():
    """Create additional configuration files"""

    # Create .flake8 config
    flake8_config = """[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    build,
    dist,
    venv,
    .venv,
    .tox
"""

    with open(".flake8", "w") as f:
        f.write(flake8_config)
    print("✓ Created .flake8")

    # Create pyproject.toml if it doesn't exist
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        pyproject_config = """[tool.black]
line-length = 88
target-version = ['py38']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
  | \\.git
  | \\.hg
  | \\.mypy_cache
  | \\.tox
  | \\.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = [
    "tests",
]
python_files = [
    "test_*.py",
    "*_test.py"
]
"""

        with open(pyproject_file, "w") as f:
            f.write(pyproject_config)
        print("✓ Created pyproject.toml")

    # Create .gitignore if it doesn't exist
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/settings.json.user
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Build artifacts
*.spec
*.dmg
*.exe
*.deb
*.rpm
*.msi

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Temporary files
*.tmp
*.temp
*.log
"""

        with open(gitignore_file, "w") as f:
            f.write(gitignore_content)
        print("✓ Created .gitignore")


if __name__ == "__main__":
    setup_vscode()
