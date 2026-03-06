import os
import tempfile
from pathlib import Path

from src.core.archive_manager import ArchiveManager
from src.core.utils import is_image_file


def process_directory(
    root_dir,
    output_dir=None,
    formats=None,
    process_archives=False,
    progress_callback=None,
    log_callback=None,
    stop_event=None,
):
    """Recursively find and process folders (and optionally archives) containing images."""
    if formats is None:
        formats = ["cbz"]
    if isinstance(formats, str):
        formats = [formats]

    if log_callback is None:
        log_callback = print

    summary = {
        "total": 0,
        "success": 0,
        "failed": 0,
        "cancelled": False,
    }

    root_path = Path(root_dir)
    tasks = []  # (source_path, is_archive)

    # First pass: find all folders containing images.
    for dirpath, _, filenames in os.walk(root_path):
        current_images = [f for f in filenames if is_image_file(f)]
        if current_images:
            tasks.append((Path(dirpath), False))

        if process_archives:
            archive_exts = {".zip", ".cbz", ".rar", ".cbr", ".7z", ".cb7", ".epub", ".mobi"}
            for filename in filenames:
                if Path(filename).suffix.lower() in archive_exts:
                    tasks.append((Path(dirpath) / filename, True))

    if not tasks:
        log_callback(f"No folders or archives found in {root_dir}")
        return summary

    log_callback(f"Found {len(tasks)} items to process.")

    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    total = len(tasks) * len(formats)
    summary["total"] = total
    current_progress = 0

    for source_path, is_archive in tasks:
        if stop_event is not None and stop_event.is_set():
            summary["cancelled"] = True
            break

        source_name = source_path.stem if is_archive else source_path.name
        temp_source_dir = None
        working_source = source_path
        prep_error = None

        try:
            if is_archive:
                temp_source_dir = tempfile.TemporaryDirectory()
                log_callback(f"Extracting {source_path.name}...")
                ArchiveManager.extract_archive(source_path, Path(temp_source_dir.name))
                working_source = Path(temp_source_dir.name)
        except Exception as error:
            prep_error = error

        if prep_error is not None:
            for fmt in formats:
                if stop_event is not None and stop_event.is_set():
                    summary["cancelled"] = True
                    break

                current_progress += 1
                summary["failed"] += 1
                if progress_callback:
                    progress_callback(current_progress, total, f"Processing {source_name} -> {fmt}")
                log_callback(f"Error converting {source_name} to {fmt}: {prep_error}")

            if temp_source_dir:
                temp_source_dir.cleanup()
            if summary["cancelled"]:
                break
            continue

        for fmt in formats:
            if stop_event is not None and stop_event.is_set():
                summary["cancelled"] = True
                break

            current_progress += 1
            if progress_callback:
                progress_callback(current_progress, total, f"Processing {source_name} -> {fmt}")

            try:
                archive_name = f"{source_name}.{fmt}"
                if output_dir:
                    output_path = Path(output_dir) / archive_name
                else:
                    output_path = source_path.parent / archive_name

                # Avoid overwriting source if source and output are identical.
                if output_path.resolve() == source_path.resolve():
                    output_path = source_path.parent / f"{source_name}_converted.{fmt}"

                ArchiveManager.create_archive(working_source, output_path, fmt)
                summary["success"] += 1
                log_callback(f"Success: {source_name} -> {output_path.name}")
            except Exception as error:
                summary["failed"] += 1
                log_callback(f"Error converting {source_name} to {fmt}: {error}")

        if temp_source_dir:
            temp_source_dir.cleanup()
        if summary["cancelled"]:
            break

    if progress_callback:
        done_msg = "Cancelled" if summary["cancelled"] else "Done"
        progress_callback(current_progress, total, done_msg)

    return summary
