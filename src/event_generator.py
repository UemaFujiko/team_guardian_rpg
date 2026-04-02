from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ai_client import generate_json_from_prompt, is_ai_enabled


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "event_prompt.txt"


FALLBACK_EVENT = {
    "event_title": "会議後の違和感",
    "summary": "会議の議事メモが共有されず、一部メンバーの間だけで解釈が進み始めています。数名は『聞いていない』と不満を持ち、責任の所在も曖昧です。",
    "risk_tags": ["情報隠し", "分断", "責任転嫁"],
    "npcs": [
        {
            "name": "佐藤",
            "role": "PM",
            "stance": "防御的",
            "dialogue": "必要な人には伝えたつもりです。全員に送る必要まではないかと……。"
        },
        {
            "name": "田中",
            "role": "メンバー",
            "stance": "不安",
            "dialogue": "認識合わせがないまま進むと、あとで私たちの責任にされそうです。"
        },
    ],
    "choices": [
        "議事メモを即日共有し、事実関係と決定事項を全員で確認する",
        "まずPMだけを呼び、非公開で事情を聞く",
        "その場は流して、次回の会議でまとめて扱う",
        "不満を言っているメンバーに、今は静観するよう伝える",
    ],
    "gm_hint": "透明性を高めつつ、個人攻撃ではなくプロセス是正に向かわせるのが望ましい。",
}


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _build_prompt(game: dict[str, Any]) -> str:
    template = _load_prompt()

    game_state_text = json.dumps(game, ensure_ascii=False, indent=2)
    difficulty = str(game.get("difficulty", "標準"))

    return (
        template
        .replace("__GAME_STATE__", game_state_text)
        .replace("__DIFFICULTY__", difficulty)
    )


def _validate_event_payload(data: dict[str, Any]) -> dict[str, Any]:
    required_keys = [
        "event_title",
        "summary",
        "risk_tags",
        "npcs",
        "choices",
        "gm_hint",
    ]

    missing = [key for key in required_keys if key not in data]
    if missing:
        raise RuntimeError(f"イベントJSONに不足キーがあります: {missing}")

    if not isinstance(data["risk_tags"], list):
        raise RuntimeError("risk_tags は list である必要があります。")

    if not isinstance(data["npcs"], list):
        raise RuntimeError("npcs は list である必要があります。")

    if not isinstance(data["choices"], list):
        raise RuntimeError("choices は list である必要があります。")

    if len(data["choices"]) < 2:
        raise RuntimeError("choices は少なくとも2件必要です。")

    return data


def generate_event(game: dict[str, Any]) -> dict[str, Any]:
    if not is_ai_enabled():
        return FALLBACK_EVENT

    prompt = _build_prompt(game)
    event = generate_json_from_prompt(prompt)
    return _validate_event_payload(event)
