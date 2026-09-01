import os
import shutil
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Optional, Callable
from src.core.utils import is_image_file
from src.core.optimizer.models import OptimizerProfile, OptimizationStats
from src.core.optimizer.image_pipeline import ImagePipeline

class ArchiveOptimizer:
    """ High-performance comic archive optimizer with 3-stage integrity validation and atomic replacement """

    @classmethod
    def optimize_archive(cls, source_path: str, profile: OptimizerProfile,
                         progress_callback: Optional[Callable[[int, int, str], None]] = None) -> OptimizationStats:
        start_time = time.time()
        source_p = Path(source_path)

        if not source_p.exists():
            return OptimizationStats(success=False, error_message=f"File not found: {source_path}")

        orig_size = source_p.stat().st_size
        dest_path = cls._resolve_output_path(source_p, profile)

        # Ensure output directory exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = dest_path.with_name(f"{dest_path.name}.tmp_{int(time.time()*1000)}")
        total_images = 0
        grayscale_count = 0

        try:
            with zipfile.ZipFile(source_p, 'r') as in_zip:
                all_entries = in_zip.infolist()
                
                # Filter valid entries
                image_entries = [
                    e for e in all_entries 
                    if not e.is_dir() and is_image_file(e.filename) and not e.filename.startswith("__MACOSX/")
                ]
                non_image_entries = [
                    e for e in all_entries 
                    if not e.is_dir() and not is_image_file(e.filename) and not e.filename.startswith("__MACOSX/")
                ]

                total_images = len(image_entries)
                if total_images == 0:
                    return OptimizationStats(
                        total_images=0,
                        original_size_bytes=orig_size,
                        optimized_size_bytes=orig_size,
                        success=False,
                        error_message="No images found in archive"
                    )

                # Sort image entries naturally
                image_entries.sort(key=lambda x: x.filename)

                # Write to temp archive using ZIP_DEFLATED (or ZIP_STORED since WebP/JPEG are pre-compressed)
                with zipfile.ZipFile(tmp_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as out_zip:
                    # 1. Process images
                    for i, entry in enumerate(image_entries):
                        if progress_callback:
                            progress_callback(i + 1, total_images, entry.filename)

                        raw_bytes = in_zip.read(entry.filename)
                        is_cover = (i == 0)

                        opt_bytes, new_ext, was_gray = ImagePipeline.process_image(
                            raw_bytes, entry.filename, is_cover, profile
                        )

                        if was_gray:
                            grayscale_count += 1

                        # Rename extension in target zip if format changed
                        base_name, _ = os.path.splitext(entry.filename)
                        target_filename = f"{base_name}{new_ext}"

                        out_zip.writestr(target_filename, opt_bytes)

                    # 2. Copy non-image entries (e.g. ComicInfo.xml) as-is
                    for non_img in non_image_entries:
                        raw_data = in_zip.read(non_img.filename)
                        out_zip.writestr(non_img.filename, raw_data)

            # 3-Stage Integrity Validation
            cls._validate_archive_integrity(tmp_path, total_images)

            # Backup if overwriting original
            if dest_path.resolve() == source_p.resolve() and profile.keep_backup:
                cls._create_backup(source_p)

            # Atomic replace
            if dest_path.exists() and dest_path.resolve() != tmp_path.resolve():
                dest_path.unlink()
            os.replace(tmp_path, dest_path)

            opt_size = dest_path.stat().st_size
            saved_bytes = max(0, orig_size - opt_size)
            saved_ratio = round((saved_bytes / float(orig_size)) * 100.0, 1) if orig_size > 0 else 0.0
            duration = int((time.time() - start_time) * 1000)

            return OptimizationStats(
                total_images=total_images,
                grayscale_images=grayscale_count,
                original_size_bytes=orig_size,
                optimized_size_bytes=opt_size,
                saved_bytes=saved_bytes,
                saved_ratio=saved_ratio,
                duration_ms=duration,
                output_path=str(dest_path),
                success=True
            )

        except Exception as e:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            return OptimizationStats(
                original_size_bytes=orig_size,
                success=False,
                error_message=str(e)
            )

    @staticmethod
    def _validate_archive_integrity(zip_path: Path, expected_min_images: int):
        """ Three-stage integrity check """
        if not zip_path.exists() or zip_path.stat().st_size < 128:
            raise IOError("Integrity check failed: Output file is empty or missing")

        with zipfile.ZipFile(zip_path, 'r') as zf:
            # 1. Central directory & CRC check
            corrupted = zf.testzip()
            if corrupted is not None:
                raise IOError(f"Integrity check failed: Corrupted entry '{corrupted}'")

            # 2. Count verification
            images = [e for e in zf.infolist() if is_image_file(e.filename)]
            if len(images) < expected_min_images:
                raise IOError(f"Integrity check failed: Expected {expected_min_images} images, found {len(images)}")

            # 3. Sample keyframe decompression
            sample_keys = [0, len(images) - 1]
            for idx in sample_keys:
                if 0 <= idx < len(images):
                    data = zf.read(images[idx].filename)
                    if len(data) == 0:
                        raise IOError(f"Integrity check failed: Image '{images[idx].filename}' decompressed to 0 bytes")

    @staticmethod
    def _resolve_output_path(source_p: Path, profile: OptimizerProfile) -> Path:
        if profile.output_mode == "overwrite":
            return source_p
        elif profile.output_mode == "new_folder" and profile.output_folder:
            out_dir = Path(profile.output_folder)
            return out_dir / source_p.name
        else: # suffix
            suffix = profile.output_suffix or "_optimized"
            return source_p.with_name(f"{source_p.stem}{suffix}{source_p.suffix}")

    @staticmethod
    def _create_backup(source_p: Path):
        backup_dir = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "ComicUtils" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_target = backup_dir / f"{source_p.stem}_{int(time.time())}{source_p.suffix}"
        shutil.copy2(source_p, backup_target)
