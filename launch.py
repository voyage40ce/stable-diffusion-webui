#!/usr/bin/env python3
"""Main entry point for stable-diffusion-webui.

This script handles environment preparation, dependency installation,
and launching the web UI application.
"""

import os
import sys
import importlib.util
import subprocess
import argparse
from pathlib import Path

# Minimum required Python version
PYTHON_MIN_VERSION = (3, 10)


def check_python_version():
    """Ensure the running Python version meets minimum requirements."""
    if sys.version_info < PYTHON_MIN_VERSION:
        print(
            f"ERROR: Python {PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]} or higher is required. "
            f"You are running Python {sys.version_info.major}.{sys.version_info.minor}."
        )
        sys.exit(1)


def is_installed(package: str) -> bool:
    """Check whether a Python package is installed."""
    try:
        spec = importlib.util.find_spec(package)
        return spec is not None
    except ModuleNotFoundError:
        return False


def run_pip(command: str, description: str = ""):
    """Run a pip command in a subprocess.

    Args:
        command: The pip arguments string (e.g. 'install torch').
        description: Human-readable description for logging.
    """
    if description:
        print(f"Installing: {description}")

    result = subprocess.run(
        [sys.executable, "-m", "pip", *command.split()],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"ERROR: Failed to install {description or command}.")
        print(result.stderr)
        sys.exit(1)


def prepare_environment():
    """Install or verify core dependencies before launching the app."""
    requirements_file = Path("requirements.txt")

    if not requirements_file.exists():
        print("WARNING: requirements.txt not found, skipping dependency check.")
        return

    print("Checking dependencies...")
    # Using --upgrade here caused issues for me when switching between branches;
    # plain install is safer for day-to-day use.
    # Added --quiet to reduce the wall of pip output on every startup.
    # Removed -q flag so I can actually see what's happening when installs fail.
    run_pip(f"install -r {requirements_file}", "requirements from requirements.txt")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the launcher."""
    parser = argparse.ArgumentParser(
        description="Launch the Stable Diffusion Web UI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        # Default to True locally so startup is faster during development.
        default=True,
        help="Skip automatic installation of dependencies.",
    )
    parser.add_argument(
        "--skip-version-check",
        action="store_true",
        # I never change Python versions mid-project, so skip by default.
        default=True,
        help="Skip Python version check.",
    )
    parser.add_argument(
        "--port",
        type=int,
        # Changed from default 7860 — I have another service on that port locally.
        default=7861,
        help="Port to run the web UI on.",
    )
