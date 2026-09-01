import io
import os
from PIL import Image, ImageOps
from typing import Tuple
from src.core.optimizer.models import OptimizerProfile
from src.core.optimizer.color_detector import ColorDetector

class ImagePipeline:
    """ High-performance image processing and compression pipeline """

    @staticmethod
    def process_image(img_bytes: bytes, filename: str, is_cover: bool, 
                      profile: OptimizerProfile) -> Tuple[bytes, str, bool]:
        """
        Processes single image buffer:
        1. Decodes and checks orientation.
        2. Downsamples via Lanczos3 if exceeding max_dimension.
        3. Converts to 8-bit single channel grayscale if monochrome manga page.
        4. Compresses to target format (WebP / JPEG / PNG) with differential cover quality.

        Returns: (optimized_bytes, new_extension, was_converted_to_grayscale)
        """
        img = Image.open(io.BytesIO(img_bytes))
        
        # Auto-orient based on EXIF tag if present
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        orig_w, orig_h = img.size
        target_quality = profile.cover_quality if is_cover else profile.quality

        # 1. Dimension downsampling (Lanczos3)
        if profile.max_dimension > 0:
            max_side = max(orig_w, orig_h)
            if max_side > profile.max_dimension:
                scale = float(profile.max_dimension) / float(max_side)
                new_w = max(1, int(orig_w * scale))
                new_h = max(1, int(orig_h * scale))
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 2. Grayscale detection & conversion
        converted_grayscale = False
        if profile.auto_grayscale and not (is_cover and img.mode in ('RGB', 'RGBA')):
            # Don't force grayscale on color covers
            if ColorDetector.is_grayscale(img):
                img = img.convert('L')
                converted_grayscale = True
        elif img.mode in ('RGBA', 'LA') and profile.target_format in ('jpeg', 'jpg'):
            # JPEG doesn't support alpha channel, convert on white background
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                bg.paste(img, mask=img.split()[3])
            else:
                bg.paste(img, mask=img.split()[1])
            img = bg

        # 3. Determine target format
        fmt = profile.target_format.lower()
        if fmt == "original":
            ext = os.path.splitext(filename)[1].lower().lstrip('.')
            if ext in ('jpg', 'jpeg'):
                target_fmt = "JPEG"
                out_ext = ".jpg"
            elif ext == 'png':
                target_fmt = "PNG"
                out_ext = ".png"
            elif ext == 'webp':
                target_fmt = "WEBP"
                out_ext = ".webp"
            else:
                target_fmt = "JPEG"
                out_ext = ".jpg"
        elif fmt in ("jpeg", "jpg"):
            target_fmt = "JPEG"
            out_ext = ".jpg"
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
        elif fmt == "webp":
            target_fmt = "WEBP"
            out_ext = ".webp"
        elif fmt == "png":
            target_fmt = "PNG"
            out_ext = ".png"
        else:
            target_fmt = "WEBP"
            out_ext = ".webp"

        # 4. Save and encode
        out_buf = io.BytesIO()
        if target_fmt == "WEBP":
            img.save(
                out_buf,
                format="WEBP",
                quality=target_quality,
                method=4
            )
        elif target_fmt == "JPEG":
            img.save(
                out_buf,
                format="JPEG",
                quality=target_quality,
                optimize=True,
                progressive=True
            )
        elif target_fmt == "PNG":
            img.save(
                out_buf,
                format="PNG",
                optimize=True,
                compress_level=9
            )
        else:
            img.save(out_buf, format=target_fmt, quality=target_quality)

        opt_bytes = out_buf.getvalue()

        # If original was already smaller (e.g. tiny thumbnail/icon), and formats match, preserve original
        if len(opt_bytes) > len(img_bytes) and out_ext == os.path.splitext(filename)[1].lower():
            return img_bytes, os.path.splitext(filename)[1].lower(), False

        return opt_bytes, out_ext, converted_grayscale
