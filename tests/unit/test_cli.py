"""
Test CLI functionality
"""

import subprocess
import sys
from pathlib import Path


def test_main_help():
    """Test that main.py --help works"""
    result = subprocess.run([sys.executable, "main.py", "--help"], 
                          capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    assert result.returncode == 0
    assert "Alpine Trading Bot" in result.stdout
    assert "--help" in result.stdout
    assert "--test" in result.stdout
    assert "--version" in result.stdout


def test_main_version():
    """Test that main.py --version works"""
    result = subprocess.run([sys.executable, "main.py", "--version"], 
                          capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    assert result.returncode == 0
    assert "2.0.0" in result.stdout


def test_main_test_mode():
    """Test that main.py --test works"""
    result = subprocess.run([sys.executable, "main.py", "--test"], 
                          capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    assert result.returncode == 0
    assert "Alpine Trading Bot" in result.stdout or "Alpine Trading Bot" in result.stderr


def test_main_status():
    """Test that main.py --status works"""
    result = subprocess.run([sys.executable, "main.py", "--status"], 
                          capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    assert result.returncode == 0


if __name__ == "__main__":
    test_main_help()
    test_main_version()
    test_main_test_mode()
    test_main_status()
    print("All CLI tests passed!")