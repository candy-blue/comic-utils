import json
from typing import Tuple, Dict, Any
from src.core.network.http_client import HttpClient
from src.core.ai.models import AIPromptContext, AIModelConfig, MangaStructuredMetadata
from src.core.ai.providers.base import IAIProvider
from src.core.ai.prompt import build_system_prompt, build_user_prompt, MANGA_PARSER_SYSTEM_PROMPT
from src.core.ai.json_repair import JSONRepair

class GoogleGeminiProvider(IAIProvider):
    """ Native Google Gemini REST Provider (Gemini 2.0 Flash / Pro) """

    @property
    def provider_id(self) -> str:
        return "google_gemini"

    @property
    def provider_name(self) -> str:
        return "Google Gemini (2.0 Flash / Pro)"

    def test_connection(self, config: AIModelConfig) -> Tuple[bool, str]:
        if not config.api_key:
            return False, "Gemini API Key 不能为空"

        client = HttpClient(timeout=10)
        model = config.model_name or "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={config.api_key}"
        body = {
            "contents": [{"parts": [{"text": "Ping test. Please reply with 'pong'."}]}]
        }

        try:
            resp_bytes = client.post_json(url, body)
            if not resp_bytes:
                return False, "服务器未返回有效响应"
            data = json.loads(resp_bytes.decode("utf-8"))
            if "candidates" in data and len(data["candidates"]) > 0:
                return True, "连接成功！Gemini 模型响应正常"
            elif "error" in data:
                return False, f"Gemini 报错: {data['error'].get('message', '未知错误')}"
            return True, "连接成功！"
        except Exception as e:
            return False, f"连接失败: {str(e)}"

    def parse_manga_metadata(self, context: AIPromptContext, config: AIModelConfig) -> MangaStructuredMetadata:
        client = HttpClient(timeout=int(config.timeout_ms / 1000))
        model = config.model_name or "gemini-2.0-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={config.api_key}"
        
        target_lang = getattr(context, 'target_language', 'auto')
        sys_prompt = build_system_prompt(target_lang)
        user_prompt = build_user_prompt(context.raw_file_name, context.parent_folder_name, target_lang)
        prompt_text = f"{sys_prompt}\n\n{user_prompt}"
        body = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": config.temperature,
                "maxOutputTokens": 2048
            }
        }

        resp_bytes = client.post_json(url, body)
        if not resp_bytes:
            raise RuntimeError("Empty response from Gemini API")

        data = json.loads(resp_bytes.decode("utf-8"))
        if "error" in data:
            raise RuntimeError(f"Gemini Error: {data['error'].get('message', 'Unknown')}")

        raw_content = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed_dict = JSONRepair.safe_parse(raw_content)

        return MangaStructuredMetadata(
            title=parsed_dict.get("title", ""),
            series=parsed_dict.get("series", "") or parsed_dict.get("title", ""),
            original_title=parsed_dict.get("original_title"),
            author=parsed_dict.get("author", ""),
            circle=parsed_dict.get("circle"),
            volume=parsed_dict.get("volume"),
            volume_end=parsed_dict.get("volume_end"),
            chapter=parsed_dict.get("chapter"),
            scanlation_group=parsed_dict.get("scanlation_group"),
            language=parsed_dict.get("language", "zh-CN"),
            summary=parsed_dict.get("summary", ""),
            tags=parsed_dict.get("tags", []) if isinstance(parsed_dict.get("tags"), list) else [],
            publish_year=parsed_dict.get("publish_year"),
            age_rating=parsed_dict.get("age_rating", "Unknown")
        )
