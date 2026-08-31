import os
import tempfile
from pathlib import Path

from src.core.i18n import i18n
from src.core.archive_manager import ArchiveManager
from src.core.utils import delete_path, is_image_file, is_relative_to

ARCHIVE_EXTENSIONS = {".zip", ".cbz", ".rar", ".cbr", ".7z", ".cb7", ".epub", ".mobi"}


def folder_contains_images(folder_path):
    """Return True when a directory contains image files directly inside it."""
    target = Path(folder_path)
    if not target.exists() or not target.is_dir():
        return False

    return any(item.is_file() and is_image_file(item.name) for item in target.iterdir())


def suggest_output_base(root_dir):
    """
    Suggest the most useful folder to open/show for auto output mode.

    - If the selected folder itself is an image folder, output is placed beside it.
    - Otherwise, nested image folders create archives inside the selected root.
    """
    root_path = Path(root_dir).expanduser().resolve()
    if not root_path.exists():
        return root_path

    if root_path.is_file():
        return root_path.parent

    return root_path.parent if folder_contains_images(root_path) else root_path


def build_output_path(source_path, root_path, output_dir, fmt, is_archive):
    """Build the destination archive path while preserving useful folder structure."""
    source = Path(source_path).expanduser().resolve()
    root = Path(root_path).expanduser().resolve()
    output_name = f"{source.stem if is_archive else source.name}.{fmt}"

    if output_dir:
        output_root = Path(output_dir).expanduser().resolve()

        try:
            relative_parent = source.parent.relative_to(root)
        except ValueError:
            relative_parent = Path()

        return output_root / relative_parent / output_name

    return source.with_suffix(f".{fmt}")


def process_directory(
    root_dir,
    output_dir=None,
    formats=None,
    process_archives=False,
    delete_source=False,
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
            for filename in filenames:
                if Path(filename).suffix.lower() in ARCHIVE_EXTENSIONS:
                    tasks.append((Path(dirpath) / filename, True))

    if not tasks:
        log_callback(i18n.get("msg_no_items_found", root_dir))
        return summary

    log_callback(i18n.get("msg_found_tasks", len(tasks)))

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
        created_outputs = []
        task_success = True

        try:
            if is_archive:
                temp_source_dir = tempfile.TemporaryDirectory()
                log_callback(i18n.get("msg_extracting_archive", source_path.name))
                ArchiveManager.extract_archive(source_path, Path(temp_source_dir.name))
                working_source = Path(temp_source_dir.name)
        except Exception as error:
            prep_error = error

        if prep_error is not None:
            for fmt in formats:
                if stop_event is not None and stop_event.is_set():
                    summary["cancelled"] = True
                    break

                summary["failed"] += 1
                task_success = False
                log_callback(i18n.get("msg_convert_error", source_name, fmt, prep_error))
                current_progress += 1
                if progress_callback:
                    progress_callback(
                        current_progress,
                        total,
                        summary["success"],
                        summary["failed"],
                        i18n.get("msg_processing_item", source_name, fmt),
                    )

            if temp_source_dir:
                temp_source_dir.cleanup()
            if summary["cancelled"]:
                break
            continue

        for fmt in formats:
            if stop_event is not None and stop_event.is_set():
                summary["cancelled"] = True
                break

            try:
                output_path = build_output_path(source_path, root_path, output_dir, fmt, is_archive)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Avoid overwriting source if source and output are identical.
                if output_path.resolve() == source_path.resolve():
                    output_path = source_path.parent / f"{source_name}_converted.{fmt}"

                ArchiveManager.create_archive(working_source, output_path, fmt)
                summary["success"] += 1
                created_outputs.append(output_path)
                log_callback(i18n.get("msg_convert_success", source_name, output_path.name))
            except Exception as error:
                summary["failed"] += 1
                task_success = False
                log_callback(i18n.get("msg_convert_error", source_name, fmt, error))

            current_progress += 1
            if progress_callback:
                progress_callback(
                    current_progress,
                    total,
                    summary["success"],
                    summary["failed"],
                    i18n.get("msg_processing_item", source_name, fmt),
                )

        if delete_source and not summary["cancelled"] and task_success:
            output_inside_source = source_path.is_dir() and any(
                is_relative_to(created_output, source_path) for created_output in created_outputs
            )
            if output_inside_source:
                log_callback(i18n.get("msg_delete_source_blocked", source_path.name))
            else:
                try:
                    delete_path(source_path)
                    log_callback(i18n.get("msg_delete_source_success", source_path.name))
                except Exception as error:
                    log_callback(i18n.get("msg_delete_source_fail", source_path.name, error))

        if temp_source_dir:
            temp_source_dir.cleanup()
        if summary["cancelled"]:
            break

    if progress_callback:
        done_msg = i18n.get("cancelled") if summary["cancelled"] else i18n.get("done")
        progress_callback(current_progress, total, summary["success"], summary["failed"], done_msg)

    return summary
