import os
import zipfile
from typing import Dict, Any
from src.core.utils import is_image_file
from src.core.optimizer.models import OptimizerProfile
from src.core.optimizer.image_pipeline import ImagePipeline

class FastSamplingEstimator:
    """ Rapidly estimates archive optimization ratio by sampling 4 keyframes in <300ms """

    @classmethod
    def estimate_archive(cls, archive_path: str, profile: OptimizerProfile) -> Dict[str, Any]:
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"File not found: {archive_path}")

        orig_size = os.path.getsize(archive_path)
        if orig_size == 0:
            return {"original_size": 0, "estimated_size": 0, "saved_ratio": 0.0, "total_images": 0}

        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                all_entries = zf.infolist()
                image_entries = [
                    e for e in all_entries 
                    if not e.is_dir() and is_image_file(e.filename) and not e.filename.startswith("__MACOSX/")
                ]
                non_image_bytes = sum(
                    e.file_size for e in all_entries 
                    if not e.is_dir() and not is_image_file(e.filename) and not e.filename.startswith("__MACOSX/")
                )

                total_images = len(image_entries)
                if total_images == 0:
                    return {
                        "original_size": orig_size,
                        "estimated_size": orig_size,
                        "saved_ratio": 0.0,
                        "total_images": 0,
                        "grayscale_rate": 0.0
                    }

                # Sort naturally
                image_entries.sort(key=lambda x: x.filename)

                # Pick 4 sample indices: 0 (cover), 25%, 50%, 75%
                indices = [0]
                if total_images > 1:
                    indices.append(int(total_images * 0.25))
                if total_images > 2:
                    indices.append(int(total_images * 0.50))
                if total_images > 3:
                    indices.append(int(total_images * 0.75))
                
                indices = sorted(list(set(indices)))

                cover_opt_size = 0
                inner_opt_sizes = []
                grayscale_count = 0

                for idx in indices:
                    entry = image_entries[idx]
                    raw_bytes = zf.read(entry.filename)
                    is_cover = (idx == 0)

                    opt_bytes, _, was_gray = ImagePipeline.process_image(
                        raw_bytes, entry.filename, is_cover, profile
                    )
                    
                    if was_gray:
                        grayscale_count += 1

                    if is_cover:
                        cover_opt_size = len(opt_bytes)
                    else:
                        inner_opt_sizes.append(len(opt_bytes))

                if inner_opt_sizes:
                    avg_inner = sum(inner_opt_sizes) / float(len(inner_opt_sizes))
                else:
                    avg_inner = cover_opt_size

                # Estimated total raw uncompressed image size
                estimated_img_bytes = cover_opt_size + (total_images - 1) * avg_inner

                # WebP / JPEG in Zip container overhead factor (typically ~0.99 - 1.01)
                estimated_zip_size = int(estimated_img_bytes + non_image_bytes + (total_images * 64))

                saved_bytes = max(0, orig_size - estimated_zip_size)
                saved_ratio = round((saved_bytes / float(orig_size)) * 100.0, 1) if orig_size > 0 else 0.0
                gray_rate = round((grayscale_count / float(len(indices))) * 100.0, 1)

                return {
                    "original_size": orig_size,
                    "estimated_size": estimated_zip_size,
                    "saved_bytes": saved_bytes,
                    "saved_ratio": saved_ratio,
                    "total_images": total_images,
                    "grayscale_rate": gray_rate
                }

        except Exception as e:
            return {
                "original_size": orig_size,
                "estimated_size": orig_size,
                "saved_ratio": 0.0,
                "total_images": 0,
                "error": str(e)
            }
