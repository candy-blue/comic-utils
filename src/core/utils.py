import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Shared constants
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

def is_image_file(filename):
    """Check if the file has a valid image extension."""
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS

_number_re = re.compile(r"(\d+)")

def natural_sort_key(value: str):
    """
    Sort key for natural sorting (e.g., 1, 2, 10 instead of 1, 10, 2).
    """
    # If input is a Path object, use its name
    if isinstance(value, Path):
        value = value.name
        
    parts = _number_re.split(value)
    key = []
    for part in parts:
        if part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())
    return key


def collect_supported_files(paths, supported_exts):
    """Collect supported files from files or directories, preserving input order."""
    supported = {ext.lower() for ext in supported_exts}
    collected = []
    seen = set()

    for raw_path in paths:
        if not raw_path:
            continue

        path = Path(raw_path).expanduser()
        if not path.exists():
            continue

        if path.is_dir():
            files = sorted(
                (
                    item for item in path.rglob("*")
                    if item.is_file() and item.suffix.lower() in supported
                ),
                key=lambda item: natural_sort_key(str(item.relative_to(path))),
            )
        elif path.is_file() and path.suffix.lower() in supported:
            files = [path]
        else:
            files = []

        for file_path in files:
            resolved = str(file_path.resolve())
            if resolved in seen:
                continue
            seen.add(resolved)
            collected.append(Path(resolved))

    return collected


def suggested_output_dir(paths):
    """Suggest a friendly output directory based on the first valid path."""
    for raw_path in paths:
        if not raw_path:
            continue

        path = Path(raw_path).expanduser()
        if not path.exists():
            continue

        base_path = path if path.is_dir() else path.parent
        return str(base_path.resolve())

    return ""


def open_in_file_manager(path: Path):
    """Open a directory in the system file manager."""
    target = Path(path).expanduser().resolve()

    if os.name == "nt":
        os.startfile(str(target))
    elif sys.platform == "darwin":
        subprocess.run(["open", str(target)], check=False)
    else:
        subprocess.run(["xdg-open", str(target)], check=False)


def is_relative_to(path: Path, base: Path):
    """Compatibility helper for Path.is_relative_to."""
    try:
        path.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def delete_path(path: Path):
    """Delete a file or directory."""
    target = Path(path).expanduser().resolve()
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
