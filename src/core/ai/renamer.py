import re
from typing import Optional
from src.core.ai.models import MangaStructuredMetadata

class TemplateRenamer:
    """ Formats structured manga metadata into standardized file names via placeholder templates """

    DEFAULT_TEMPLATE = "[{author}] {title} - Vol.{vol:02d} [{group}]"

    @classmethod
    def render(cls, metadata: MangaStructuredMetadata, template: str = DEFAULT_TEMPLATE, 
               extension: str = ".cbz") -> str:
        if not template:
            template = cls.DEFAULT_TEMPLATE

        # Prepare context variables
        author = metadata.author or "未知作者"
        circle = metadata.circle or ""
        title = metadata.title or "未命名作品"
        series = metadata.series or metadata.title or "未命名作品"
        group = metadata.scanlation_group or ""
        year = str(metadata.publish_year) if metadata.publish_year else ""
        lang = metadata.language or "zh-CN"

        vol_int = metadata.volume if metadata.volume is not None else 1
        vol_str = f"{vol_int:02d}"
        if metadata.volume_end and metadata.volume_end != vol_int:
            vol_str = f"{vol_int:02d}-{metadata.volume_end:02d}"

        ch_str = f"{metadata.chapter:02g}" if metadata.chapter is not None else ""

        # Mapping for replacement
        mapping = {
            "{author}": author,
            "{circle}": circle,
            "{title}": title,
            "{series}": series,
            "{vol:02d}": vol_str,
            "{vol}": str(metadata.volume) if metadata.volume is not None else "",
            "{ch:02d}": ch_str,
            "{ch}": str(metadata.chapter) if metadata.chapter is not None else "",
            "{group}": group,
            "{year}": year,
            "{lang}": lang,
        }

        result = template
        for placeholder, value in mapping.items():
            result = result.replace(placeholder, value)

        # Clean empty brackets/parentheses caused by missing optional fields (e.g. "[]" or "()")
        result = re.sub(r'\[\s*\]', '', result)
        result = re.sub(r'\(\s*\)', '', result)
        result = re.sub(r'\s{2,}', ' ', result).strip()

        # Sanitize Windows illegal file name characters: \ / : * ? " < > |
        result = re.sub(r'[\\/:*?"<>|]', '_', result)

        if extension:
            if not extension.startswith('.'):
                extension = '.' + extension
            result = f"{result}{extension}"

        return result
