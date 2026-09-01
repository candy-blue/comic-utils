from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class MangaStructuredMetadata:
    """ Structured manga metadata parsed by AI Engine """
    title: str = ""
    series: str = ""
    original_title: Optional[str] = None
    author: str = ""
    circle: Optional[str] = None
    volume: Optional[int] = None
    volume_end: Optional[int] = None
    chapter: Optional[float] = None
    scanlation_group: Optional[str] = None
    language: str = "zh-CN"
    summary: str = ""
    tags: List[str] = field(default_factory=list)
    publish_year: Optional[int] = None
    age_rating: str = "Unknown" # 'Unknown', 'Everyone', 'Teen', 'Mature 17+', 'Adults Only 18+'

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "series": self.series or self.title,
            "original_title": self.original_title,
            "author": self.author,
            "circle": self.circle,
            "volume": self.volume,
            "volume_end": self.volume_end,
            "chapter": self.chapter,
            "scanlation_group": self.scanlation_group,
            "language": self.language,
            "summary": self.summary,
            "tags": self.tags,
            "publish_year": self.publish_year,
            "age_rating": self.age_rating
        }

@dataclass
class AIModelConfig:
    provider: str = "openai_compatible" # 'openai_compatible', 'google_gemini'
    model_name: str = "deepseek-chat"
    base_url: str = "https://api.deepseek.com/v1"
    api_key: str = ""
    temperature: float = 0.1
    timeout_ms: int = 30000

@dataclass
class AIPromptContext:
    raw_file_name: str = ""
    parent_folder_name: str = ""
    target_language: str = "zh-CN"

@dataclass
class AIRenameResult:
    original_name: str = ""
    new_name: str = ""
    metadata: Optional[MangaStructuredMetadata] = None
    success: bool = True
    from_cache: bool = False
    error_message: Optional[str] = None
