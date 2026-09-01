import json
from typing import Tuple, Dict, Any
from src.core.network.http_client import HttpClient
from src.core.ai.models import AIPromptContext, AIModelConfig, MangaStructuredMetadata
from src.core.ai.providers.base import IAIProvider
from src.core.ai.prompt import build_system_prompt, build_user_prompt, MANGA_PARSER_SYSTEM_PROMPT
from src.core.ai.json_repair import JSONRepair

class OpenAICompatibleProvider(IAIProvider):
    """ Provider for OpenAI-compatible APIs (DeepSeek, ChatGPT, OneAPI, Ollama, Qwen, etc.) """

    @property
    def provider_id(self) -> str:
        return "openai_compatible"

    @property
    def provider_name(self) -> str:
        return "OpenAI-Compatible (DeepSeek / ChatGPT / Ollama)"

    def test_connection(self, config: AIModelConfig) -> Tuple[bool, str]:
        if not config.api_key and not "localhost" in config.base_url and not "127.0.0.1" in config.base_url:
            return False, "API Key 不能为空"

        client = HttpClient(timeout=10)
        url = config.base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.api_key}"
        }
        body = {
            "model": config.model_name,
            "messages": [
                {"role": "user", "content": "Ping test. Please reply with 'pong'."}
            ],
            "max_tokens": 10
        }

        try:
            resp_bytes = client.post_json(url, body, headers=headers)
            if not resp_bytes:
                return False, "服务器未返回有效响应"
            data = json.loads(resp_bytes.decode("utf-8"))
            if "choices" in data and len(data["choices"]) > 0:
                return True, "连接成功！模型响应正常"
            elif "error" in data:
                return False, f"API 报错: {data['error'].get('message', '未知错误')}"
            return True, "连接成功！"
        except Exception as e:
            return False, f"连接失败: {str(e)}"

    def parse_manga_metadata(self, context: AIPromptContext, config: AIModelConfig) -> MangaStructuredMetadata:
        client = HttpClient(timeout=int(config.timeout_ms / 1000))
        url = config.base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {config.api_key}"
        }
        sys_prompt = build_system_prompt(getattr(context, 'target_language', 'auto'))
        user_prompt = build_user_prompt(
            context.raw_file_name, 
            context.parent_folder_name, 
            getattr(context, 'target_language', 'auto')
        )
        body = {
            "model": config.model_name,
            "messages": [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": config.temperature,
            "response_format": {"type": "json_object"}
        }

        resp_bytes = client.post_json(url, body, headers=headers)
        if not resp_bytes:
            raise RuntimeError("Empty response from AI API")

        data = json.loads(resp_bytes.decode("utf-8"))
        if "error" in data:
            raise RuntimeError(f"AI API Error: {data['error'].get('message', 'Unknown')}")

        raw_content = data["choices"][0]["message"]["content"]
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
