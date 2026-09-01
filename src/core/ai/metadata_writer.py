import os
import io
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Optional, Any
from src.core.ai.models import MangaStructuredMetadata
from src.core.ai.comicinfo import ComicInfoGenerator

class UniversalMetadataWriter:
    """ Unified metadata injector supporting CBZ, ZIP, EPUB, PDF, Folders and Calibre metadata.opf """

    @classmethod
    def generate_calibre_opf_bytes(cls, metadata: MangaStructuredMetadata) -> bytes:
        """ Generates standard Calibre metadata.opf bytes """
        root = ET.Element("package")
        root.set("xmlns", "http://www.idpf.org/2007/opf")
        root.set("unique-identifier", "uuid_id")
        root.set("version", "2.0")

        meta_elem = ET.SubElement(root, "metadata")
        meta_elem.set("xmlns:dc", "http://purl.org/dc/elements/1.1/")
        meta_elem.set("xmlns:opf", "http://www.idpf.org/2007/opf")

        # dc:title
        title_tag = ET.SubElement(meta_elem, "dc:title")
        title_tag.text = metadata.title or metadata.series or "Untitled"

        # dc:creator
        creator_tag = ET.SubElement(meta_elem, "dc:creator")
        creator_tag.set("opf:role", "aut")
        creator_tag.set("opf:file-as", metadata.author or "Unknown")
        creator_tag.text = metadata.author or "Unknown"

        # dc:description
        if metadata.summary:
            desc_tag = ET.SubElement(meta_elem, "dc:description")
            desc_tag.text = metadata.summary

        # dc:language
        lang_tag = ET.SubElement(meta_elem, "dc:language")
        lang_tag.text = metadata.language or "zh-CN"

        # calibre:series & calibre:series_index
        series_name = metadata.series or metadata.title
        if series_name:
            series_meta = ET.SubElement(meta_elem, "meta")
            series_meta.set("name", "calibre:series")
            series_meta.set("content", series_name)

            series_idx = metadata.volume if metadata.volume is not None else 1
            idx_meta = ET.SubElement(meta_elem, "meta")
            idx_meta.set("name", "calibre:series_index")
            idx_meta.set("content", str(series_idx))

        # dc:subject (tags)
        if metadata.tags:
            for tag in metadata.tags:
                subj_tag = ET.SubElement(meta_elem, "dc:subject")
                subj_tag.text = str(tag)

        # publish year
        if metadata.publish_year:
            date_tag = ET.SubElement(meta_elem, "dc:date")
            date_tag.text = f"{metadata.publish_year}-01-01T00:00:00+00:00"

        raw_str = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(raw_str)
        return parsed.toprettyxml(indent="  ", encoding="utf-8")

    @classmethod
    def inject_epub_metadata(cls, epub_path: str, metadata: MangaStructuredMetadata) -> bool:
        """ Updates or injects Dublin Core & Calibre metadata into EPUB's content.opf """
        p = Path(epub_path)
        if not p.exists() or p.suffix.lower() != '.epub':
            return False

        tmp_p = p.with_name(f"{p.name}.tmp_epub_{int(os.path.getmtime(p)*1000)}")
        try:
            with zipfile.ZipFile(p, 'r') as in_z:
                entries = in_z.infolist()
                opf_path = None
                
                # 1. Locate root opf file from META-INF/container.xml
                try:
                    container_xml = in_z.read("META-INF/container.xml")
                    c_root = ET.fromstring(container_xml)
                    for elem in c_root.iter():
                        if elem.tag.endswith("rootfile") and elem.attrib.get("media-type") == "application/oebps-package+xml":
                            opf_path = elem.attrib.get("full-path")
                            break
                except Exception:
                    pass

                # Fallback scan for .opf
                if not opf_path:
                    for e in entries:
                        if e.filename.lower().endswith(".opf"):
                            opf_path = e.filename
                            break

                if not opf_path:
                    opf_path = "content.opf"
                    opf_bytes = cls.generate_calibre_opf_bytes(metadata)
                else:
                    try:
                        raw_opf = in_z.read(opf_path).decode("utf-8", errors="ignore")
                        # Register namespaces
                        ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")
                        ET.register_namespace("opf", "http://www.idpf.org/2007/opf")
                        root = ET.fromstring(raw_opf)
                        
                        # Find or create metadata tag
                        meta_elem = None
                        for child in root:
                            if child.tag.endswith("metadata"):
                                meta_elem = child
                                break
                        if meta_elem is None:
                            meta_elem = ET.SubElement(root, "metadata")

                        # Update dc:title
                        title_elem = None
                        for elem in meta_elem:
                            if elem.tag.endswith("title"):
                                title_elem = elem
                                break
                        if title_elem is None:
                            title_elem = ET.SubElement(meta_elem, "{http://purl.org/dc/elements/1.1/}title")
                        title_elem.text = metadata.title or metadata.series or "Untitled"

                        # Update dc:creator
                        creator_elem = None
                        for elem in meta_elem:
                            if elem.tag.endswith("creator"):
                                creator_elem = elem
                                break
                        if creator_elem is None:
                            creator_elem = ET.SubElement(meta_elem, "{http://purl.org/dc/elements/1.1/}creator")
                        creator_elem.text = metadata.author or "Unknown"

                        # Update calibre:series
                        for elem in list(meta_elem):
                            if elem.tag.endswith("meta") and elem.attrib.get("name") in ("calibre:series", "calibre:series_index"):
                                meta_elem.remove(elem)

                        series_name = metadata.series or metadata.title
                        if series_name:
                            s_meta = ET.SubElement(meta_elem, "meta")
                            s_meta.set("name", "calibre:series")
                            s_meta.set("content", series_name)

                            i_meta = ET.SubElement(meta_elem, "meta")
                            i_meta.set("name", "calibre:series_index")
                            i_meta.set("content", str(metadata.volume if metadata.volume is not None else 1))

                        raw_str = ET.tostring(root, encoding="utf-8")
                        parsed = minidom.parseString(raw_str)
                        opf_bytes = parsed.toprettyxml(indent="  ", encoding="utf-8")
                    except Exception:
                        opf_bytes = cls.generate_calibre_opf_bytes(metadata)

                # Write out updated EPUB archive
                with zipfile.ZipFile(tmp_p, 'w', compression=zipfile.ZIP_DEFLATED) as out_z:
                    for e in entries:
                        if e.filename != opf_path and e.filename.lower() != "comicinfo.xml":
                            out_z.writestr(e, in_z.read(e.filename))
                    out_z.writestr(opf_path, opf_bytes)

            os.replace(tmp_p, p)
            return True
        except Exception:
            if tmp_p.exists():
                try:
                    tmp_p.unlink()
                except Exception:
                    pass
            return False

    @classmethod
    def write_metadata_for_target(cls, target_path: str, metadata: MangaStructuredMetadata) -> bool:
        """ Universal injector routing by target file or directory type """
        p = Path(target_path)
        if not p.exists():
            return False

        if p.is_dir():
            # Write both metadata.opf (for Calibre) and ComicInfo.xml inside the folder
            try:
                opf_file = p / "metadata.opf"
                opf_file.write_bytes(cls.generate_calibre_opf_bytes(metadata))

                ci_file = p / "ComicInfo.xml"
                ci_file.write_bytes(ComicInfoGenerator.generate_xml_bytes(metadata))
                return True
            except Exception:
                return False

        ext = p.suffix.lower()
        if ext in ('.cbz', '.zip'):
            # Inject ComicInfo.xml + metadata.opf into archive
            ok = ComicInfoGenerator.inject_into_archive(str(p), metadata)
            # Also create companion metadata.opf next to archive for Calibre batch import
            try:
                opf_companion = p.with_suffix(".opf")
                opf_companion.write_bytes(cls.generate_calibre_opf_bytes(metadata))
            except Exception:
                pass
            return ok
        elif ext == '.epub':
            ok = cls.inject_epub_metadata(str(p), metadata)
            try:
                opf_companion = p.with_suffix(".opf")
                opf_companion.write_bytes(cls.generate_calibre_opf_bytes(metadata))
            except Exception:
                pass
            return ok
        elif ext in ('.pdf', '.mobi', '.7z', '.rar'):
            # Generate companion metadata.opf alongside the file for Calibre
            try:
                opf_companion = p.with_suffix(".opf")
                opf_companion.write_bytes(cls.generate_calibre_opf_bytes(metadata))
                return True
            except Exception:
                return False
        return False
