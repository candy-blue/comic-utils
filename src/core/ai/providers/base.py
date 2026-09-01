from abc import ABC, abstractmethod
from typing import Tuple
from src.core.ai.models import AIPromptContext, AIModelConfig, MangaStructuredMetadata

class IAIProvider(ABC):
    """ Abstract base class for AI LLM providers """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def test_connection(self, config: AIModelConfig) -> Tuple[bool, str]:
        """ Test connection to the AI provider. Returns (success, message) """
        pass

    @abstractmethod
    def parse_manga_metadata(self, context: AIPromptContext, config: AIModelConfig) -> MangaStructuredMetadata:
        """ Parse raw manga file name into structured MangaStructuredMetadata """
        pass
