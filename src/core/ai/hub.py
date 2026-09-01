import os
from pathlib import Path
from typing import Tuple, Optional, Dict
from src.core.ai.models import (
    MangaStructuredMetadata, AIModelConfig, AIPromptContext, AIRenameResult
)
from src.core.ai.providers.base import IAIProvider
from src.core.ai.providers.openai_provider import OpenAICompatibleProvider
from src.core.ai.providers.gemini_provider import GoogleGeminiProvider
from src.core.ai.cache import AICacheManager
from src.core.ai.renamer import TemplateRenamer
from src.core.ai.metadata_writer import UniversalMetadataWriter

class AIEngineHub:
    """ Central coordinator for AI metadata extraction, caching, renaming and universal metadata injection """

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_manager = AICacheManager(cache_dir)
        self.providers: Dict[str, IAIProvider] = {
            "openai_compatible": OpenAICompatibleProvider(),
            "google_gemini": GoogleGeminiProvider()
        }

    def get_provider(self, provider_id: str) -> Optional[IAIProvider]:
        return self.providers.get(provider_id)

    def test_connection(self, config: AIModelConfig) -> Tuple[bool, str]:
        provider = self.get_provider(config.provider)
        if not provider:
            return False, f"未找到指定的 AI Provider: {config.provider}"
        return provider.test_connection(config)

    def parse_metadata(self, raw_name: str, parent_folder: str = "", 
                       config: Optional[AIModelConfig] = None, 
                       target_language: str = "auto",
                       use_cache: bool = True) -> AIRenameResult:
        if not config:
            config = AIModelConfig()

        raw_stem = Path(raw_name).stem if not Path(raw_name).is_dir() else raw_name

        # 1. Check SQLite Hash Cache
        cache_key = f"{raw_stem}_{target_language}"
        if use_cache:
            cached_dict = self.cache_manager.get(cache_key, config.model_name)
            if cached_dict:
                meta = MangaStructuredMetadata(**cached_dict)
                ext = Path(raw_name).suffix if not Path(raw_name).is_dir() else ""
                new_name = TemplateRenamer.render(meta, extension=ext)
                return AIRenameResult(
                    original_name=raw_name,
                    new_name=new_name,
                    metadata=meta,
                    success=True,
                    from_cache=True
                )

        # 2. Call AI Provider
        provider = self.get_provider(config.provider)
        if not provider:
            return AIRenameResult(
                original_name=raw_name,
                new_name=raw_name,
                success=False,
                error_message=f"Provider '{config.provider}' not registered"
            )

        try:
            ctx = AIPromptContext(
                raw_file_name=raw_stem, 
                parent_folder_name=parent_folder,
                target_language=target_language
            )
            meta = provider.parse_manga_metadata(ctx, config)

            # Store in cache
            if use_cache:
                self.cache_manager.put(cache_key, config.model_name, meta.to_dict())

            ext = Path(raw_name).suffix if not Path(raw_name).is_dir() else ""
            new_name = TemplateRenamer.render(meta, extension=ext)
            return AIRenameResult(
                original_name=raw_name,
                new_name=new_name,
                metadata=meta,
                success=True,
                from_cache=False
            )
        except Exception as e:
            return AIRenameResult(
                original_name=raw_name,
                new_name=raw_name,
                success=False,
                error_message=str(e)
            )

    def process_and_rename_file(self, file_path: str, config: AIModelConfig, 
                                template: str = TemplateRenamer.DEFAULT_TEMPLATE, 
                                target_language: str = "auto",
                                inject_comicinfo: bool = True,
                                override_metadata: Optional[MangaStructuredMetadata] = None) -> AIRenameResult:
        p = Path(file_path)
        if not p.exists():
            return AIRenameResult(original_name=file_path, success=False, error_message="File not found")

        parent_name = p.parent.name
        
        if override_metadata:
            meta = override_metadata
            res = AIRenameResult(original_name=p.name, metadata=meta, success=True)
        else:
            res = self.parse_metadata(p.name, parent_folder=parent_name, config=config, target_language=target_language, use_cache=True)
            if not res.success or not res.metadata:
                return res
            meta = res.metadata

        ext = p.suffix if not p.is_dir() else ""
        new_filename = TemplateRenamer.render(meta, template=template, extension=ext)
        res.new_name = new_filename

        # Universal metadata injection (Calibre OPF, ComicInfo, EPUB Dublin Core)
        if inject_comicinfo:
            UniversalMetadataWriter.write_metadata_for_target(str(p), meta)

        # Rename physical file or directory
        if new_filename != p.name:
            new_path = p.with_name(new_filename)
            try:
                os.replace(p, new_path)
            except Exception as e:
                res.error_message = f"重命名失败: {e}"
                res.success = False

        return res
