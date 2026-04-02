from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class JudgmentResult:
    score: int
    reason: str
    lesson: str
    effects: dict[str, int]

    def model_dump(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "reason": self.reason,
            "lesson": self.lesson,
            "effects": self.effects,
        }


GOOD_HINTS = [
    "共有", "確認", "記録", "全員", "事実", "議事", "透明", "保護", "再発防止"
]
BAD_HINTS = [
    "静観", "流し", "先送り", "非公開", "隠す", "黙", "放置"
]


def judge_choice(game: dict[str, Any], event: dict[str, Any], choice: str) -> JudgmentResult:
    score = 0
    effects = {
        "trust": 0,
        "safety": 0,
        "performance": 0,
        "transparency": 0,
        "attrition_risk": 0,
        "faction_risk": 0,
        "misconduct_risk": 0,
    }

    for hint in GOOD_HINTS:
        if hint in choice:
            score += 2

    for hint in BAD_HINTS:
        if hint in choice:
            score -= 2

    if score >= 3:
        effects.update(
            {
                "trust": 8,
                "safety": 8,
                "performance": 3,
                "transparency": 10,
                "attrition_risk": -6,
                "faction_risk": -8,
                "misconduct_risk": -4,
            }
        )
        reason = "事実確認と透明性の確保に向かう選択です。組織防衛として筋が良く、分断の拡大を抑えやすい対応でした。"
        lesson = "記録・共有・再確認は、防衛の初動として非常に強い手です。"
    elif score >= 0:
        effects.update(
            {
                "trust": 2,
                "safety": 1,
                "performance": 1,
                "transparency": 1,
                "attrition_risk": 0,
                "faction_risk": -1,
                "misconduct_risk": 0,
            }
        )
        reason = "大きく崩す対応ではありませんが、構造是正としてはやや弱めです。"
        lesson = "個別対応だけで終わらず、記録とルール整備につなげると強くなります。"
    else:
        effects.update(
            {
                "trust": -6,
                "safety": -7,
                "performance": -2,
                "transparency": -8,
                "attrition_risk": 6,
                "faction_risk": 7,
                "misconduct_risk": 4,
            }
        )
        reason = "問題を見えにくくする方向の対応です。短期的には静かでも、後で責任転嫁や不信が強まりやすくなります。"
        lesson = "非公開処理・先送り・黙らせる対応は、組織の損傷を深めやすい点に注意が必要です。"

    return JudgmentResult(
        score=score,
        reason=reason,
        lesson=lesson,
        effects=effects,
    )
