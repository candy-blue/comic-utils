import os
from pathlib import Path
from src.core.utils import is_image_file
from src.core.archive_manager import ArchiveManager

def process_directory(root_dir, output_dir=None, fmt='cbz', progress_callback=None, log_callback=None):
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
            progress_callback(i, total, f"Processing {folder.name}")
            
        try:
            # Determine output path
            archive_name = folder.name + '.' + fmt
            if output_dir:
                output_path = Path(output_dir) / archive_name
            else:
                output_path = folder.parent / archive_name
                
            ArchiveManager.create_archive(folder, output_path, fmt)
            log_callback(f"Success: {folder.name} -> {output_path}")
            
        except Exception as e:
            log_callback(f"Error processing {folder}: {e}")
        
    if progress_callback:
        progress_callback(total, total, "Done")
