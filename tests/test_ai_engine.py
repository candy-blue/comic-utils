import unittest
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.core.ai.models import MangaStructuredMetadata, AIModelConfig, AIPromptContext
from src.core.ai.json_repair import JSONRepair
from src.core.ai.renamer import TemplateRenamer
from src.core.ai.comicinfo import ComicInfoGenerator
from src.core.ai.metadata_writer import UniversalMetadataWriter
from src.core.ai.cache import AICacheManager
from src.core.ai.hub import AIEngineHub

class TestAIEngine(unittest.TestCase):

    def test_json_repair(self):
        # 1. Markdown with trailing comma and unclosed brace
        raw = """```json
        {
          "title": "鬼灭之刃",
          "author": "吾峠呼世晴",
          "volume": 1,
          "tags": ["热血", "少年",]
        """
        data = JSONRepair.safe_parse(raw)
        self.assertEqual(data["title"], "鬼灭之刃")
        self.assertEqual(data["author"], "吾峠呼世晴")
        self.assertEqual(data["volume"], 1)
        self.assertEqual(len(data["tags"]), 2)

    def test_template_renamer(self):
        meta = MangaStructuredMetadata(
            title="鬼灭之刃",
            series="鬼灭之刃",
            author="吾峠呼世晴",
            circle="集英社",
            volume=2,
            scanlation_group="极影汉化",
            publish_year=2016
        )

        name1 = TemplateRenamer.render(meta, template="[{author}] {title} - Vol.{vol:02d} [{group}]", extension=".cbz")
        self.assertEqual(name1, "[吾峠呼世晴] 鬼灭之刃 - Vol.02 [极影汉化].cbz")

        name2 = TemplateRenamer.render(meta, template="{series} 第{vol}卷 [{group}]", extension=".zip")
        self.assertEqual(name2, "鬼灭之刃 第2卷 [极影汉化].zip")

    def test_comicinfo_generator(self):
        meta = MangaStructuredMetadata(
            title="鬼灭之刃 第01卷 残酷",
            series="鬼灭之刃",
            author="吾峠呼世晴",
            volume=1,
            summary="少年炭治郎的灭鬼传奇",
            tags=["热血", "奇幻", "战斗"]
        )

        xml_bytes = ComicInfoGenerator.generate_xml_bytes(meta, page_count=192)
        xml_str = xml_bytes.decode('utf-8')
        self.assertIn("<Title>鬼灭之刃 第01卷 残酷</Title>", xml_str)
        self.assertIn("<Series>鬼灭之刃</Series>", xml_str)
        self.assertIn("<Writer>吾峠呼世晴</Writer>", xml_str)
        self.assertIn("<Volume>1</Volume>", xml_str)
        self.assertIn("<PageCount>192</PageCount>", xml_str)

    def test_universal_metadata_writer(self):
        meta = MangaStructuredMetadata(
            title="进击的巨人",
            series="进击的巨人",
            author="谏山创",
            volume=34,
            summary="人类与巨人的绝望之战",
            tags=["黑暗奇幻", "战斗", "悬疑"],
            publish_year=2021
        )

        # 1. Calibre OPF format test
        opf_bytes = UniversalMetadataWriter.generate_calibre_opf_bytes(meta)
        opf_str = opf_bytes.decode('utf-8')
        self.assertIn("<dc:title>进击的巨人</dc:title>", opf_str)
        self.assertIn("<dc:creator opf:role=\"aut\" opf:file-as=\"谏山创\">谏山创</dc:creator>", opf_str)
        self.assertIn("<meta name=\"calibre:series\" content=\"进击的巨人\"/>", opf_str)
        self.assertIn("<meta name=\"calibre:series_index\" content=\"34\"/>", opf_str)

        # 2. Target Directory test
        with tempfile.TemporaryDirectory() as tmp_dir:
            folder = Path(tmp_dir) / "TestMangaFolder"
            folder.mkdir()
            ok = UniversalMetadataWriter.write_metadata_for_target(str(folder), meta)
            self.assertTrue(ok)
            self.assertTrue((folder / "metadata.opf").exists())
            self.assertTrue((folder / "ComicInfo.xml").exists())

        # 3. EPUB injection test
        with tempfile.TemporaryDirectory() as tmp_dir:
            epub_path = Path(tmp_dir) / "test_book.epub"
            with zipfile.ZipFile(epub_path, 'w') as z:
                z.writestr("mimetype", "application/epub+zip")
                z.writestr("META-INF/container.xml", """<?xml version="1.0"?>
                <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
                  <rootfiles>
                    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
                  </rootfiles>
                </container>""")
                z.writestr("OEBPS/content.opf", """<?xml version="1.0" encoding="utf-8"?>
                <package xmlns="http://www.idpf.org/2007/opf" version="2.0">
                  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
                    <dc:title>Old Title</dc:title>
                  </metadata>
                </package>""")

            ok = UniversalMetadataWriter.write_metadata_for_target(str(epub_path), meta)
            self.assertTrue(ok)

            with zipfile.ZipFile(epub_path, 'r') as z:
                content_opf = z.read("OEBPS/content.opf").decode("utf-8")
                self.assertIn("进击的巨人", content_opf)
                self.assertIn("谏山创", content_opf)
                self.assertIn("calibre:series", content_opf)

    def test_ai_cache_manager(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = f"{tmp_dir}/test_cache.db"
            cache = AICacheManager(db_path)
            
            sample = {"title": "海贼王", "author": "尾田荣一郎"}
            cache.put("[Oda] One Piece Vol.01", "deepseek-chat", sample)

            res = cache.get("[Oda] One Piece Vol.01", "deepseek-chat")
            self.assertIsNotNone(res)
            self.assertEqual(res["title"], "海贼王")
            self.assertEqual(res["author"], "尾田荣一郎")

            # Non-existent
            self.assertIsNone(cache.get("NonExistent", "deepseek-chat"))

if __name__ == '__main__':
    unittest.main()
