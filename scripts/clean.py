#!/usr/bin/env python3
"""
Project Cleanup Tool
Interactive script to clean cache, build artifacts, and temporary files.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import List, NoReturn

# Directories to exclude from cleanup (virtual environments, IDE configs, etc.)
EXCLUDED_DIRS = {".venv", "venv", "env", "node_modules", ".git", ".idea", ".vscode"}

# Define cleanup targets by category
PATTERNS = {
    "1": [
        "**/__pycache__",
        "**/*.py[cod]",
        "**/*.so",
    ],
    "2": [
        ".pytest_cache",
        ".coverage",
        ".coverage.*",
        "htmlcov",
        ".tox",
        ".nox",
        ".benchmarks",
        "coverage.xml",
        "nosetests.xml",
    ],
    "3": [
        ".mypy_cache",
        ".ruff_cache",
        ".dmypy.json",
    ],
    "4": [
        "build",
        "dist",
        "**/*.egg-info",
        "wheels",
        "*.egg",
    ],
    "5": [
        "**/*.scip",
        "**/*.scip.gz",
    ],
    "6": [
        "**/*.log",
        "temp",
        ".tmp",
    ],
}

ROOT_DIR = Path(__file__).resolve().parent.parent


def is_excluded(path: Path) -> bool:
    """Check if a path or any of its parents are in the excluded directories list."""
    try:
        rel_path = path.relative_to(ROOT_DIR)
        return any(part in EXCLUDED_DIRS for part in rel_path.parts)
    except ValueError:
        # Path is not relative to ROOT_DIR, shouldn't happen but be safe
        return False


def find_targets(categories: List[str]) -> List[Path]:
    """Find all files and directories matching the selected categories."""
    targets: set[Path] = set()
    for cat in categories:
        if cat == "0":
            # recursive call for all categories 1-6
            return find_targets([str(i) for i in range(1, 7)])

        if cat not in PATTERNS:
            continue

        for pattern in PATTERNS[cat]:
            # Use rglob for recursive patterns (starting with **/)
            # and glob for root-level patterns
            if pattern.startswith("**/"):
                # Remove prefix for rglob
                clean_pattern = pattern[3:]
                found = ROOT_DIR.rglob(clean_pattern)
            else:
                found = ROOT_DIR.glob(pattern)

            # Filter out excluded paths (e.g., .venv, node_modules)
            targets.update(p for p in found if not is_excluded(p))

    return sorted(list(targets))


def format_size(size: float) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def get_total_size(paths: List[Path]) -> int:
    total = 0
    for p in paths:
        if p.is_file():
            total += p.stat().st_size
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    total += f.stat().st_size
    return total


def print_menu() -> None:
    """Displays the interactive cleanup menu options to stdout."""
    print("\nProject Cleanup Tool")
    print("====================")
    print("[1] Python Cache (__pycache__, *.pyc, *.pyo, *.pyd, *.so)")
    print("[2] Test & Coverage (.pytest_cache, .coverage, htmlcov, .tox, .nox, .benchmarks)")
    print("[3] Type & Lint (.mypy_cache, .ruff_cache, .dmypy.json)")
    print("[4] Build Artifacts (build/, dist/, *.egg-info/, wheels/)")
    print("[5] SCIP Files (*.scip, *.scip.gz)")
    print("[6] Logs & Temp (*.log, temp/, .tmp/)")
    print("[0] All of the above")
    print("[q] Quit")


def remove_path(path: Path) -> None:
    try:
        if path.is_file() or path.is_symlink():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
    except Exception as e:
        print(f"Error removing {path}: {e}")


def process_selection(choice: str) -> None:
    targets = find_targets([choice])

    if not targets:
        print("No matching files found.")
        return

    total_size = get_total_size(targets)
    print(f"\nFound {len(targets)} targets ({format_size(total_size)}):")

    # Show first 10 items
    for p in targets[:10]:
        print(f" - {p.relative_to(ROOT_DIR)}")

    has_more = len(targets) > 10
    if has_more:
        print(f" ... and {len(targets) - 10} more")

    while True:
        if has_more:
            confirm = input("\nProceed? [y]es / [n]o / [a]ll (show full list): ").strip().lower()
        else:
            confirm = input("\nProceed with deletion? [y/N] ").strip().lower()

        if confirm == "a" and has_more:
            print(f"\nFull list ({len(targets)} items):")
            for p in targets:
                print(f" - {p.relative_to(ROOT_DIR)}")
            # After showing full list, ask again (no longer has_more context)
            has_more = False
            continue
        elif confirm == "y":
            print("\nDeleting...")
            for p in targets:
                remove_path(p)
            print("Done.")
            break
        elif confirm in ("n", ""):
            print("Operation cancelled.")
            break
        else:
            print("Invalid input. Please enter y, n, or a.")


def main() -> NoReturn:
    """
    Main entry point for the cleanup script.

    Runs the interactive loop, processing user input until 'q' is selected.
    """
    while True:
        print_menu()
        choice = input("\nEnter choice: ").strip().lower()

        if choice == "q":
            print("Exiting.")
            sys.exit(0)
        elif choice in ("0", "1", "2", "3", "4", "5", "6"):
            process_selection(choice)
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
