import shutil
import tempfile
from pathlib import Path
from src.core.utils import natural_sort_key, IMAGE_EXTENSIONS
from src.core.archive_manager import ArchiveManager

class ConvertError(RuntimeError):
  pass

def convert_ebook(input_path: Path, output_dir: Path | None = None, fmt: str = 'cbz') -> Path:
  if not input_path.exists():
    raise ConvertError(f"File not found: {input_path}")

  # Temporary extraction
  with tempfile.TemporaryDirectory() as temp_dir:
      temp_path = Path(temp_dir)
      
      # Extract images from input (reuse extract logic or custom ebook logic)
      # For now, we reuse the specialized logic for epub/mobi image extraction 
      # but we need to put them in a clean folder for ArchiveManager to consume
      
      images_dir = temp_path / "images"
      images_dir.mkdir()
      
      count = ArchiveManager.extract_archive(input_path, images_dir)
      
      if count == 0:
          raise ConvertError("No images found in ebook.")
          
      # Now create output archive
      output_dir = (output_dir or input_path.parent).resolve()
      output_dir.mkdir(parents=True, exist_ok=True)
      output_path = output_dir / f"{input_path.stem}.{fmt}"
      
      ArchiveManager.create_archive(images_dir, output_path, fmt)
      
      return output_path
