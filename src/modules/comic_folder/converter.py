import os
from pathlib import Path
from src.core.utils import is_image_file
from src.core.archive_manager import ArchiveManager

import shutil
import tempfile

def process_directory(root_dir, output_dir=None, formats=None, process_archives=False, progress_callback=None, log_callback=None):
    """Recursively find and process folders (and optionally archives) containing images."""
    if formats is None:
        formats = ['cbz']
    # If formats is passed as string (legacy), wrap it
    if isinstance(formats, str):
        formats = [formats]
        
    if log_callback is None:
        log_callback = print

    root_path = Path(root_dir)
    tasks = [] # (source_path, is_archive)
    
    # First pass: find all folders containing images
    for dirpath, dirnames, filenames in os.walk(root_path):
        current_images = [f for f in filenames if is_image_file(f)]
        if current_images:
            tasks.append((Path(dirpath), False))
            
        # If process_archives is enabled, look for archives too
        if process_archives:
            # Archives to process as "Source Folders"
            # We treat .zip, .rar, .cbz, etc. as sources
            archive_exts = {'.zip', '.cbz', '.rar', '.cbr', '.7z', '.cb7', '.epub', '.mobi'}
            for f in filenames:
                if Path(f).suffix.lower() in archive_exts:
                    tasks.append((Path(dirpath) / f, True))
            
    if not tasks:
        log_callback(f"No folders or archives found in {root_dir}")
        return

    log_callback(f"Found {len(tasks)} items to process.")
    
    # Create output directory if it doesn't exist and is specified
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Process each task
    total = len(tasks) * len(formats)
    current_progress = 0
    
    for source_path, is_archive in tasks:
        # Determine source name
        source_name = source_path.stem if is_archive else source_path.name
        
        # If it's an archive, we need to extract it first to a temp dir
        temp_source_dir = None
        working_source = source_path
        
        try:
            if is_archive:
                # Extract to temp
                temp_source_dir = tempfile.TemporaryDirectory()
                log_callback(f"Extracting {source_path.name}...")
                ArchiveManager.extract_archive(source_path, Path(temp_source_dir.name))
                working_source = Path(temp_source_dir.name)
            
            # Now convert to all target formats
            for fmt in formats:
                current_progress += 1
                if progress_callback:
                    progress_callback(current_progress, total, f"Processing {source_name} -> {fmt}")
                
                try:
                    archive_name = source_name + '.' + fmt
                    if output_dir:
                        output_path = Path(output_dir) / archive_name
                    else:
                        output_path = source_path.parent / archive_name
                        
                    # Avoid overwriting source if source is same as output (e.g. zip -> zip in same folder)
                    if output_path.resolve() == source_path.resolve():
                        output_path = source_path.parent / (source_name + "_converted." + fmt)

                    ArchiveManager.create_archive(working_source, output_path, fmt)
                    log_callback(f"Success: {source_name} -> {output_path.name}")
                    
                except Exception as e:
                    log_callback(f"Error converting {source_name} to {fmt}: {e}")
                    
        except Exception as e:
             log_callback(f"Error preparing {source_name}: {e}")
        finally:
            if temp_source_dir:
                temp_source_dir.cleanup()
        
    if progress_callback:
        progress_callback(total, total, "Done")
