import xml.etree.ElementTree as ET
from xml.dom import minidom
import zipfile
import io
import os
from pathlib import Path
from typing import Optional, Any
from src.core.ai.models import MangaStructuredMetadata

class ComicInfoGenerator:
    """ Generates standard ComicInfo.xml v2.1 compliant with Komga, Kavita & Mihon """

    @classmethod
    def generate_xml_bytes(cls, metadata: MangaStructuredMetadata, page_count: Optional[int] = None) -> bytes:
        root = ET.Element("ComicInfo")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")

        def add_tag(tag_name: str, value: Any):
            if value is not None and str(value).strip() != "":
                elem = ET.SubElement(root, tag_name)
                elem.text = str(value).strip()

        add_tag("Title", metadata.title)
        add_tag("Series", metadata.series or metadata.title)
        if metadata.volume is not None:
            add_tag("Volume", metadata.volume)
            add_tag("Number", metadata.volume)
        elif metadata.chapter is not None:
            add_tag("Number", metadata.chapter)

        add_tag("Summary", metadata.summary)
        add_tag("Writer", metadata.author)
        add_tag("Penciller", metadata.author)
        add_tag("Translator", metadata.scanlation_group)
        if metadata.publish_year:
            add_tag("Year", metadata.publish_year)

        if metadata.tags:
            add_tag("Genre", ", ".join(metadata.tags[:4]))
            add_tag("Tags", ", ".join(metadata.tags))

        add_tag("LanguageISO", "zh" if "zh" in metadata.language.lower() else metadata.language)
        add_tag("Manga", "YesAndRightToLeft")
        add_tag("AgeRating", metadata.age_rating)
        if page_count and page_count > 0:
            add_tag("PageCount", page_count)

        raw_str = ET.tostring(root, encoding="utf-8")
        parsed = minidom.parseString(raw_str)
        return parsed.toprettyxml(indent="  ", encoding="utf-8")

    @classmethod
    def inject_into_archive(cls, archive_path: str, metadata: MangaStructuredMetadata) -> bool:
        """ Atomically injects or replaces ComicInfo.xml inside a CBZ/ZIP archive """
        p = Path(archive_path)
        if not p.exists() or p.suffix.lower() not in ('.cbz', '.zip'):
            return False

        tmp_p = p.with_name(f"{p.name}.tmp_ci_{int(os.path.getmtime(p)*1000)}")
        try:
            page_count = 0
            with zipfile.ZipFile(p, 'r') as in_z:
                entries = in_z.infolist()
                for e in entries:
                    if not e.is_dir() and not e.filename.startswith("__MACOSX/") and e.filename.lower() != "comicinfo.xml":
                        ext = os.path.splitext(e.filename)[1].lower()
                        if ext in ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif'):
                            page_count += 1

                xml_bytes = cls.generate_xml_bytes(metadata, page_count=page_count)

                with zipfile.ZipFile(tmp_p, 'w', compression=zipfile.ZIP_DEFLATED) as out_z:
                    # Write ComicInfo.xml at root
                    out_z.writestr("ComicInfo.xml", xml_bytes)
                    for e in entries:
                        if e.filename.lower() != "comicinfo.xml":
                            out_z.writestr(e, in_z.read(e.filename))

            os.replace(tmp_p, p)
            return True
        except Exception:
            if tmp_p.exists():
                try:
                    tmp_p.unlink()
                except Exception:
                    pass
            return False
