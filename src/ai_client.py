from __future__ import annotations

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def _get_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        raise RuntimeError(
            "OpenAI APIキーが設定されていません。.env に OPENAI_API_KEY を設定してください。"
        )

    dummy_markers = [
        "your_api_key_here",
        "your_api",
        "sk-xxxx",
        "sk-your",
        "ここに",
    ]
    lower_key = api_key.lower()

    if any(marker in lower_key for marker in dummy_markers):
        raise RuntimeError(
            "OpenAI APIキーがダミー値のままです。.env の OPENAI_API_KEY を本物のキーに置き換えてください。"
        )

    return api_key


def get_model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()


def is_ai_enabled() -> bool:
    use_ai = os.getenv("USE_AI", "true").strip().lower()
    return use_ai in {"1", "true", "yes", "on"}


def get_openai_client() -> OpenAI:
    return OpenAI(api_key=_get_api_key())


def generate_json_from_prompt(prompt: str) -> dict[str, Any]:
    client = get_openai_client()
    model = get_model_name()

    response = client.responses.create(
        model=model,
        input=prompt,
        text={"format": {"type": "json_object"}},
    )

    output_text = getattr(response, "output_text", None)
    if not output_text:
        raise RuntimeError("OpenAIからの応答テキストが空でした。")

    try:
        return json.loads(output_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            "OpenAIの応答をJSONとして読み取れませんでした。"
            f"\n応答内容:\n{output_text}"
        ) from e
