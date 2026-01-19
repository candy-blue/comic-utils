import zipfile
import shutil
from pathlib import Path
from src.core.utils import natural_sort_key, IMAGE_EXTENSIONS

class ConvertError(RuntimeError):
  pass

def convert_to_cbz(input_path: Path, output_dir: Path | None = None) -> Path:
  if not input_path.exists():
    raise ConvertError(f"File not found: {input_path}")

  suffix = input_path.suffix.lower()
  if suffix in {".epub", ".equb"}:
    return _convert_zip_book_to_cbz(input_path, output_dir=output_dir)
  if suffix == ".mobi":
    return _convert_mobi_to_cbz(input_path, output_dir=output_dir)

  raise ConvertError(f"Unsupported file type: {suffix}")


def _convert_zip_book_to_cbz(input_path: Path, output_dir: Path | None) -> Path:
  if not zipfile.is_zipfile(input_path):
    raise ConvertError("EPUB is not a ZIP container (possibly encrypted)")

  output_dir = (output_dir or input_path.parent).resolve()
  output_dir.mkdir(parents=True, exist_ok=True)
  output_path = output_dir / f"{input_path.stem}.cbz"

  with zipfile.ZipFile(input_path, "r") as zin:
    candidates = []
    for name in zin.namelist():
      p = Path(name)
      if p.suffix.lower() in IMAGE_EXTENSIONS and not p.name.startswith("."):
        candidates.append(name)

    if not candidates:
      raise ConvertError("No images found in book.")

    candidates.sort(key=lambda x: natural_sort_key(Path(x).name))

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
      for idx, name in enumerate(candidates, start=1):
        ext = Path(name).suffix.lower()
        if ext == ".jpeg":
          ext = ".jpg"
        arcname = f"{idx:04d}{ext}"
        data = zin.read(name)
        zout.writestr(arcname, data)

  return output_path


def _convert_mobi_to_cbz(input_path: Path, output_dir: Path | None) -> Path:
  output_dir = (output_dir or input_path.parent).resolve()
  output_dir.mkdir(parents=True, exist_ok=True)
  output_path = output_dir / f"{input_path.stem}.cbz"

  try:
    import mobi
  except Exception as e:
    raise ConvertError("Missing dependency: mobi (pip install mobi)") from e

  try:
    tempdir, _ = mobi.extract(str(input_path))
  except Exception as e:
    raise ConvertError(str(e)) from e

  try:
    extract_dir = Path(tempdir)
    images = []
    for p in extract_dir.rglob("*"):
      if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
        images.append(p)

    if not images:
      raise ConvertError("No images extracted from MOBI.")

    images.sort(key=lambda x: natural_sort_key(x.name))

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zout:
      for idx, p in enumerate(images, start=1):
        ext = p.suffix.lower()
        if ext == ".jpeg":
          ext = ".jpg"
        arcname = f"{idx:04d}{ext}"
        zout.write(p, arcname)
  finally:
    try:
      shutil.rmtree(tempdir, ignore_errors=True)
    except Exception:
      pass

  return output_path
