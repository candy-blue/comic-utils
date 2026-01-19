import os
import zipfile
from pathlib import Path
from src.core.utils import is_image_file, natural_sort_key

def create_cbz(source_dir, output_dir=None):
    """Compress the directory into a .cbz file."""
    source_path = Path(source_dir)
    cbz_name = source_path.name + '.cbz'
    
    if output_dir:
        output_path = Path(output_dir) / cbz_name
    else:
        # Create in the parent directory of the source folder
        output_path = source_path.parent / cbz_name
        
    # Get all image files
    images = [f for f in os.listdir(source_path) if is_image_file(f)]
    # Use natural sort
    images.sort(key=natural_sort_key)
    
    if not images:
        return False, "No images found"

    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for img in images:
                file_path = source_path / img
                # Archive name is just the filename to keep it flat inside the cbz
                zf.write(file_path, arcname=img)
        return True, f"Created {output_path}"
    except Exception as e:
        return False, str(e)

def process_directory(root_dir, output_dir=None, progress_callback=None, log_callback=None):
    """Recursively find and process folders containing images."""
    if log_callback is None:
        log_callback = print

    root_path = Path(root_dir)
    comic_folders = []
    
    # First pass: find all folders containing images
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_images = [f for f in filenames if is_image_file(f)]
        if current_images:
            comic_folders.append(Path(dirpath))
            
    if not comic_folders:
        log_callback(f"No folders with images found in {root_dir}")
        return

    log_callback(f"Found {len(comic_folders)} folders containing images.")
    
    # Create output directory if it doesn't exist and is specified
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Process each folder
    total = len(comic_folders)
    for i, folder in enumerate(comic_folders):
        if progress_callback:
            progress_callback(i, total, f"Converting {folder.name}")
            
        success, message = create_cbz(folder, output_dir)
        
        if not success:
             log_callback(f"Error processing {folder}: {message}")
        else:
             log_callback(f"Success: {folder.name} -> {message}")
        
    if progress_callback:
        progress_callback(total, total, "Done")
