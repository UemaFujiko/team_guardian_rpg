from __future__ import annotations

from copy import deepcopy
from typing import Any

import streamlit as st


DEFAULT_GAME_STATE: dict[str, Any] = {
    "turn": 1,
    "max_turns": 10,
    "difficulty": "標準",
    "team_type": "コンサル会社",
    "trust": 50,
    "safety": 50,
    "performance": 50,
    "transparency": 50,
    "attrition_risk": 50,
    "faction_risk": 50,
    "misconduct_risk": 50,
    "flags": {},
    "history": [],
    "game_over": False,
}


def init_state() -> None:
    if "game" not in st.session_state:
        st.session_state["game"] = deepcopy(DEFAULT_GAME_STATE)


def get_game() -> dict[str, Any]:
    init_state()
    return st.session_state["game"]


def reset_state() -> None:
    st.session_state["game"] = deepcopy(DEFAULT_GAME_STATE)
    st.session_state.pop("last_result", None)


def _clamp(value: int, min_value: int = 0, max_value: int = 100) -> int:
    return max(min_value, min(max_value, int(value)))


def apply_judgment(result: dict[str, Any], choice: str) -> None:
    game = get_game()
    effects = result.get("effects", {})

    for key in [
        "trust",
        "safety",
        "performance",
        "transparency",
        "attrition_risk",
        "faction_risk",
        "misconduct_risk",
    ]:
        if key in effects:
            game[key] = _clamp(game.get(key, 50) + int(effects[key]))

    game["history"].append(
        {
            "turn": game["turn"],
            "choice": choice,
            "score": result.get("score", 0),
            "reason": result.get("reason", ""),
            "lesson": result.get("lesson", ""),
            "effects": effects,
        }
    )

    game["turn"] += 1

    if game["turn"] > game["max_turns"]:
        game["game_over"] = True

    if game["trust"] <= 10 or game["safety"] <= 10:
        game["game_over"] = True


def final_rank() -> str:
    game = get_game()

    positives = (
        game["trust"]
        + game["safety"]
        + game["performance"]
        + game["transparency"]
    )
    negatives = (
        game["attrition_risk"]
        + game["faction_risk"]
        + game["misconduct_risk"]
    )
    total = positives - negatives

    if total >= 120:
        return "S: 強い組織防衛。透明性と信頼の両立に成功。"
    if total >= 70:
        return "A: 安定した防衛。大きな崩れを防いでいる。"
    if total >= 20:
        return "B: 及第点。いくつかの火種が残っている。"
    if total >= -20:
        return "C: 不安定。対応が後手に回る場面があった。"
    return "D: 組織防衛に失敗。分断と不信が深刻化。"
