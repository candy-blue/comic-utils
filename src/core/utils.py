import re
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
