from PIL import Image
import io
from typing import Union

class ColorDetector:
    """ Fast discrete pixel sampling algorithm to detect black & white / grayscale manga pages """

    @staticmethod
    def is_grayscale(image_input: Union[Image.Image, bytes], sample_size: int = 50) -> bool:
        """
        Detects if an image is essentially grayscale/monochrome even if stored in RGB/RGBA format.
        Downsamples to a small grid (e.g. 50x50 = 2500 samples) and computes saturation S.
        """
        img = None
        if isinstance(image_input, bytes):
            try:
                img = Image.open(io.BytesIO(image_input))
            except Exception:
                return False
        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            return False

        if img.mode in ('L', '1'):
            return True

        if img.mode in ('RGBA', 'LA', 'P'):
            # Convert to RGB for checking
            try:
                img = img.convert('RGB')
            except Exception:
                return False

        if img.mode != 'RGB':
            return False

        # Fast downsample to sample_size x sample_size for holistic saturation analysis
        thumb = img.resize((sample_size, sample_size), Image.Resampling.BILINEAR)
        pixels = list(thumb.getdata())

        total_sat = 0.0
        max_sat = 0.0
        count = 0

        for r, g, b in pixels:
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            
            # Avoid division by zero on pure black pixels
            if max_c < 5:
                continue

            sat = (max_c - min_c) / float(max_c)
            total_sat += sat
            if sat > max_sat:
                max_sat = sat
            count += 1

        if count == 0:
            return True

        avg_sat = total_sat / float(count)

        # Standard Japanese black & white manga criteria:
        # Average color saturation < 0.025 and maximum saturation spike < 0.06
        return (avg_sat < 0.025) and (max_sat < 0.06)
