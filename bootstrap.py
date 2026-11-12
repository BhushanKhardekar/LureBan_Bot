"""
bootstrap.py — One-command local setup for any platform.

Creates a virtual environment (if absent), installs dependencies,
and starts the bot. Works on Windows, macOS, and Linux.

Usage:
    python bootstrap.py
"""
import subprocess
import sys
from pathlib import Path


def _venv_python() -> Path:
    """Return the path to the venv's Python executable."""
    venv_root = Path(".venv")
    if sys.platform == "win32":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def _venv_pip() -> Path:
    """Return the path to the venv's pip executable."""
    venv_root = Path(".venv")
    if sys.platform == "win32":
        return venv_root / "Scripts" / "pip.exe"
    return venv_root / "bin" / "pip"


def main() -> None:
    venv_path = Path(".venv")

    if not venv_path.exists():
        print("Creating virtual environment...")
        result = subprocess.run([sys.executable, "-m", "venv", str(venv_path)])
        if result.returncode != 0:
            print("ERROR: Failed to create virtual environment.")
            sys.exit(1)

    pip = str(_venv_pip())
    python = str(_venv_python())

    print("Installing / updating dependencies...")
    result = subprocess.run([pip, "install", "-r", "requirements.txt"])
    if result.returncode != 0:
        print("ERROR: Failed to install dependencies.")
        sys.exit(1)

    print("Starting LureBan Bot... (press Ctrl+C to stop)\n")
    try:
        subprocess.run([python, "main.py"])
    except KeyboardInterrupt:
        print("\nBot stopped.")


if __name__ == "__main__":
    main()
