import json
import re
from typing import Any, Dict, Optional

class JSONRepair:
    """ Fault-tolerant JSON parser with automatic syntax correction for LLM outputs """

    @staticmethod
    def safe_parse(raw_text: str) -> Dict[str, Any]:
        if not raw_text or not raw_text.strip():
            raise ValueError("AI returned empty content")

        cleaned = raw_text.strip()

        # 1. Remove Markdown code block fences
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        cleaned = cleaned.strip()

        # 2. Extract outermost JSON object if surrounded by extra commentary
        match = re.search(r'(\{[\s\S]*\})', cleaned)
        if match:
            cleaned = match.group(1)

        # 3. Direct parse attempt
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # 4. Repair: remove trailing commas before closing braces/brackets
        cleaned = re.sub(r',\s*([\]\}])', r'\1', cleaned)

        # 5. Repair: replace single quotes around keys/values with double quotes
        cleaned = re.sub(r"([{,]\s*)'([^']+)'\s*:", r'\1"\2":', cleaned)
        cleaned = re.sub(r":\s*'([^']*)'([,}])", r': "\1"\2', cleaned)

        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # 6. Repair: balance unclosed brackets
        open_braces = cleaned.count('{') - cleaned.count('}')
        if open_braces > 0:
            cleaned += '}' * open_braces

        open_brackets = cleaned.count('[') - cleaned.count(']')
        if open_brackets > 0:
            cleaned += ']' * open_brackets

        return json.loads(cleaned)
