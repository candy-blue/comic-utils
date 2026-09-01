from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class OptimizerProfile:
    """ Profile configuration for comic archive & image optimization """
    id: str = "custom"
    name: str = "自定义优化"
    target_format: str = "webp"  # 'webp', 'jpeg', 'png', 'original'
    quality: int = 80            # 1 - 100
    cover_quality: int = 90      # Cover page (1st page) quality
    max_dimension: int = 2160    # Max width or height (e.g. 2160 for 2K, 0 for no limit)
    auto_grayscale: bool = True  # Auto detect and convert black & white manga to 8-bit 1-channel grayscale
    output_mode: str = "suffix"  # 'suffix', 'overwrite', 'new_folder'
    output_folder: Optional[str] = None
    output_suffix: str = "_optimized"
    keep_backup: bool = True

    @classmethod
    def preset_extreme_webp(cls) -> 'OptimizerProfile':
        return cls(
            id="extreme_webp",
            name="极致压缩 (WebP + 黑白灰度 + 2K限制)",
            target_format="webp",
            quality=75,
            cover_quality=88,
            max_dimension=2160,
            auto_grayscale=True,
            output_mode="suffix",
            output_suffix="_optimized"
        )

    @classmethod
    def preset_balanced_jpeg(cls) -> 'OptimizerProfile':
        return cls(
            id="balanced_jpeg",
            name="高清平衡 (JPEG + Q80)",
            target_format="jpeg",
            quality=80,
            cover_quality=92,
            max_dimension=2560,
            auto_grayscale=True,
            output_mode="suffix",
            output_suffix="_optimized"
        )

    @classmethod
    def preset_lossless_lineart(cls) -> 'OptimizerProfile':
        return cls(
            id="lossless_lineart",
            name="线稿优化 (PNG 降维灰度)",
            target_format="png",
            quality=100,
            cover_quality=100,
            max_dimension=0,
            auto_grayscale=True,
            output_mode="suffix",
            output_suffix="_optimized"
        )

@dataclass
class OptimizationStats:
    """ Statistics report for an archive optimization run """
    total_images: int = 0
    grayscale_images: int = 0
    original_size_bytes: int = 0
    optimized_size_bytes: int = 0
    saved_bytes: int = 0
    saved_ratio: float = 0.0     # Percentage e.g. 45.2%
    duration_ms: int = 0
    output_path: str = ""
    success: bool = True
    error_message: Optional[str] = None
