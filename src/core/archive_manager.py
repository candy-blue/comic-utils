import os
import shutil
import zipfile
import tempfile
from pathlib import Path
from PIL import Image
import img2pdf
import py7zr

# Common
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}

def is_image_file(filename):
    return Path(filename).suffix.lower() in IMAGE_EXTENSIONS

def natural_sort_key(value: str):
    import re
    if isinstance(value, Path):
        value = value.name
    parts = re.split(r'(\d+)', value)
    return [int(p) if p.isdigit() else p.lower() for p in parts]

class ArchiveManager:
    """Handles creation and extraction of various archive formats."""
    
    @staticmethod
    def create_archive(source_dir: Path, output_path: Path, fmt: str):
        """
        Create an archive from a directory of images.
        fmt: 'cbz', 'zip', 'pdf', 'epub', '7z'
        """
        if not source_dir.exists():
            raise FileNotFoundError(f"{source_dir} not found")

        # Gather images
        images = [f for f in os.listdir(source_dir) if is_image_file(f)]
        images.sort(key=natural_sort_key)
        
        if not images:
            raise ValueError("No images found in folder")

        fmt = fmt.lower()
        if fmt in ['cbz', 'zip']:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for img in images:
                    zf.write(source_dir / img, arcname=img)
                    
        elif fmt == '7z':
            with py7zr.SevenZipFile(output_path, 'w') as zf:
                for img in images:
                    zf.write(source_dir / img, arcname=img)
                    
        elif fmt == 'pdf':
            # Convert images to PDF bytes
            img_paths = [str(source_dir / img) for img in images]
            with open(output_path, "wb") as f:
                f.write(img2pdf.convert(img_paths))
                
        elif fmt == 'epub':
            # Simple EPUB creation (container + manifest)
            ArchiveManager._create_simple_epub(source_dir, images, output_path)
            
        elif fmt == 'mobi':
             # Placeholder: MOBI creation is complex. 
             # For now we might create an EPUB and rename it or warn user.
             # Or just create a ZIP structure with .mobi extension (invalid but requested)
             # Better: raise NotImplemented or fallback
             raise NotImplementedError("Direct MOBI creation not fully supported. Try converting to EPUB first.")
             
        else:
            raise ValueError(f"Unsupported write format: {fmt}")

    @staticmethod
    def _create_simple_epub(source_dir, images, output_path):
        """Create a valid (but simple) EPUB 2.0/3.0 structure."""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # mimetype (must be uncompressed and first)
            zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            
            # Container
            container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
            zf.writestr("META-INF/container.xml", container_xml)
            
            # Images & Manifest
            manifest_items = []
            spine_refs = []
            
            for i, img in enumerate(images):
                img_path = source_dir / img
                ext = img_path.suffix.lower()
                mime = "image/jpeg"
                if ext == '.png': mime = "image/png"
                elif ext == '.gif': mime = "image/gif"
                
                # Copy image
                zf.write(img_path, arcname=f"OEBPS/images/{img}")
                
                # Create XHTML page for image
                page_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>{img}</title></head>
<body><div style="text-align:center"><img src="images/{img}" style="max-width:100%;" /></div></body>
</html>"""
                page_name = f"page_{i:04d}.xhtml"
                zf.writestr(f"OEBPS/{page_name}", page_content)
                
                manifest_items.append(f'<item id="img_{i}" href="images/{img}" media-type="{mime}"/>')
                manifest_items.append(f'<item id="page_{i}" href="{page_name}" media-type="application/xhtml+xml"/>')
                spine_refs.append(f'<itemref idref="page_{i}"/>')
                
            # Content.opf
            opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{source_dir.name}</dc:title>
    <dc:language>en</dc:language>
  </metadata>
  <manifest>
    {''.join(manifest_items)}
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx">
    {''.join(spine_refs)}
  </spine>
</package>"""
            zf.writestr("OEBPS/content.opf", opf)
            
            # Simple TOC (required for EPUB 2)
            ncx = """<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head><meta name="dtb:uid" content=""/></head>
  <docTitle><text>Comic</text></docTitle>
  <navMap/>
</ncx>"""
            zf.writestr("OEBPS/toc.ncx", ncx)

    @staticmethod
    def extract_archive(input_path: Path, output_dir: Path):
        """
        Extract images from an archive to a folder.
        Supports: zip, cbz, epub, mobi, 7z, rar (read-only if tool available)
        """
        ext = input_path.suffix.lower()
        
        # Temp dir to hold extraction before filtering images
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            if ext in ['.zip', '.cbz', '.epub']:
                with zipfile.ZipFile(input_path, 'r') as zf:
                    zf.extractall(temp_path)
            
            elif ext in ['.7z', '.cb7']:
                with py7zr.SevenZipFile(input_path, mode='r') as zf:
                    zf.extractall(temp_path)
                    
            elif ext == '.mobi':
                # Use mobi lib to extract
                import mobi
                extracted_temp, _ = mobi.extract(str(input_path))
                # Move content to our temp_path
                shutil.copytree(extracted_temp, temp_path, dirs_exist_ok=True)
                # Cleanup mobi temp
                shutil.rmtree(extracted_temp, ignore_errors=True)

            elif ext in ['.rar', '.cbr']:
                # Requires unrar
                try:
                    import rarfile
                    with rarfile.RarFile(input_path) as rf:
                        rf.extractall(temp_path)
                except Exception as e:
                    raise RuntimeError(f"RAR extraction failed (ensure unrar/UnRAR.dll is installed): {e}")
                    
            elif ext == '.pdf':
                # Extract images from PDF?
                # This is complex with just img2pdf (which is write-only).
                # We might need pdf2image or similar.
                # For now, let's say "PDF extraction requires poppler" or skip
                # Or use pikepdf/pypdf to extract raw images.
                # Let's try basic pypdf or just skip PDF extraction for now if libraries missing.
                # User asked for PDF -> Folder. 
                # Let's assume we can't easily do it without heavy deps like poppler.
                # We will mark it as "Not supported without heavy libs" or try a simple extraction.
                raise NotImplementedError("PDF extraction not yet supported (requires heavy dependencies)")
                
            else:
                raise ValueError(f"Unsupported format: {ext}")
                
            # Now move images from temp_path to output_dir
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
                
            image_count = 0
            for root, dirs, files in os.walk(temp_path):
                for f in files:
                    if is_image_file(f):
                        # Move
                        src = Path(root) / f
                        dst = output_dir / f
                        # Handle duplicate names?
                        if dst.exists():
                            dst = output_dir / f"{Path(root).name}_{f}"
                        shutil.copy2(src, dst)
                        image_count += 1
                        
            return image_count
