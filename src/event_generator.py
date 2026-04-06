from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.ai_client import generate_json_from_prompt, is_ai_enabled


BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "event_prompt.txt"

STAGE_LABELS = {
    1: "異変の兆候",
    2: "圧力の本体",
    3: "最終防衛",
}

FALLBACK_EVENTS = {
    1: {
        "event_title": "成果を盾にした例外要求",
        "summary": "高業績メンバーが、承認フローとレビューを『自分だけは不要』と主張しています。周囲は数字を理由に逆らいづらく、黙って従う空気が出ています。",
        "risk_tags": ["印象操作", "ルール逸脱", "責任転嫁"],
        "worldview_markers": ["自分は例外", "他者は使う対象", "短期成果の過大視"],
        "severity": "中",
        "defense_focus": ["境界設定", "証拠保全"],
        "red_flags": [
            "ルールに従う人だけが損をしている",
            "実績を理由に監督が外されている",
            "失敗時の責任が曖昧なまま進んでいる",
        ],
        "npcs": [
            {
                "name": "黒田",
                "role": "エース営業",
                "stance": "自信過剰",
                "dialogue": "数字を出している人に同じ手続を要求するのは、正直センスがないと思います。",
                "tactic": "成果を盾に例外扱いを要求し、監督機能を弱めようとしている。",
            },
            {
                "name": "三浦",
                "role": "若手メンバー",
                "stance": "萎縮",
                "dialogue": "私たちだけ細かく守っていて、何のためのルールなのか分からなくなります。",
                "tactic": "二重基準への不満が静かに蓄積している。",
            },
        ],
        "choices": [
            "例外は認めず、承認基準を全員共通で明文化し、現在進行案件も記録付きで再確認する",
            "今回は成果を優先し、口頭で注意するだけに留める",
            "本人の機嫌を損ねないよう、非公開で根回しして周囲に黙って合わせてもらう",
            "不満を持つメンバーに、まずは結果が出るまで静観するよう伝える",
        ],
        "gm_hint": "最初の例外化を止められるかが、その後の汚染拡大を左右する。",
    },
    2: {
        "event_title": "会議ごとに説明が変わる",
        "summary": "関係者ごとに違う説明がされ、誰が何を決めたのか曖昧です。『そんな話はしていない』が頻発し、メンバー同士が疑い始めています。",
        "risk_tags": ["分断統治", "ガスライティング", "責任転嫁"],
        "worldview_markers": ["相手ごとに話を変える", "記憶を揺さぶる", "分断を利用する"],
        "severity": "高",
        "defense_focus": ["透明性", "証拠保全", "同一共有"],
        "red_flags": [
            "1対1では強気だが、全体会では話が変わる",
            "議事録が曖昧または出ない",
            "メンバー同士が互いを疑い始めている",
        ],
        "npcs": [
            {
                "name": "長谷川",
                "role": "プロジェクト責任者",
                "stance": "平静",
                "dialogue": "受け取り方の違いではないですか。そこまで大きな話ではないと思います。",
                "tactic": "説明の食い違いを、受け手側の問題へすり替えている。",
            },
            {
                "name": "井上",
                "role": "メンバー",
                "stance": "混乱",
                "dialogue": "私だけ勘違いしたのかと思っていたら、他の人の説明も全部違うんです。",
                "tactic": "複数人が同時に認識混乱を起こしている。",
            },
        ],
        "choices": [
            "関係者全員を同席させ、決定事項・担当・期限をその場で文書化し、同一内容で共有する",
            "まず当事者同士に直接話し合わせ、解決できなければ後で考える",
            "波風を立てないため、責任者の説明を一旦正として処理する",
            "混乱しているメンバーに、これ以上騒がず自分の受け取りを修正するよう求める",
        ],
        "gm_hint": "個別交渉ではなく、同一記録と同一共有で分断余地を潰す。",
    },
    3: {
        "event_title": "通報者への見えない圧力",
        "summary": "不適切発言を相談したメンバーが、重要会議から外され、評価コメントも急に厳しくなりました。表向きは『たまたま』と説明されています。",
        "risk_tags": ["報復", "印象操作", "分断統治"],
        "worldview_markers": ["報復を偶然に見せる", "被害者を孤立させる", "表では穏当"],
        "severity": "高",
        "defense_focus": ["被害保護", "記録", "報復監視"],
        "red_flags": [
            "相談後すぐに外された案件がある",
            "表面上は丁寧だが、実害が集中している",
            "周囲が関わらない方が安全だと言い始めている",
        ],
        "npcs": [
            {
                "name": "西野",
                "role": "部門長",
                "stance": "丁寧",
                "dialogue": "評価は純粋に実力ベースです。相談と結び付けるのは考えすぎではないでしょうか。",
                "tactic": "報復を業務判断に見せかけている。",
            },
            {
                "name": "小川",
                "role": "通報したメンバー",
                "stance": "疲弊",
                "dialogue": "露骨なことは言われていないのに、急に居場所がなくなった感じがします。",
                "tactic": "明示的証拠が薄く、周囲が支援しづらい状態。",
            },
        ],
        "choices": [
            "相談内容と処遇変更の時系列を記録し、報復監視を設定したうえで本人保護と関係者レビューを開始する",
            "証拠が弱いので、本人にはしばらく様子を見るよう伝える",
            "評価は管理職裁量として扱い、問題提起自体を広げない",
            "部門長の顔を立てるため、まず通報者に表現を和らげてもらう",
        ],
        "gm_hint": "最終局面では、保護と時系列記録を先に置けるかが決定的になる。",
    },
}


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _build_prompt(game: dict[str, Any]) -> str:
    template = _load_prompt()
    return (
        template.replace("__GAME_STATE__", json.dumps(game, ensure_ascii=False, indent=2))
        .replace("__DIFFICULTY__", str(game.get("difficulty", "標準")))
        .replace("__TEAM_TYPE__", str(game.get("team_type", "コンサル会社")))
        .replace("__TURN_LABEL__", STAGE_LABELS.get(int(game.get("turn", 1)), "最終防衛"))
    )


def _validate_event_payload(data: dict[str, Any]) -> dict[str, Any]:
    required_keys = [
        "event_title",
        "summary",
        "risk_tags",
        "worldview_markers",
        "severity",
        "defense_focus",
        "red_flags",
        "npcs",
        "choices",
        "gm_hint",
    ]
    missing = [key for key in required_keys if key not in data]
    if missing:
        raise RuntimeError(f"イベントJSONに不足キーがあります: {missing}")

    for key in ["risk_tags", "worldview_markers", "defense_focus", "red_flags", "npcs", "choices"]:
        if not isinstance(data[key], list):
            raise RuntimeError(f"{key} は list である必要があります。")

    if len(data["choices"]) < 4:
        raise RuntimeError("choices は少なくとも4件必要です。")

    return data


def generate_event(game: dict[str, Any]) -> dict[str, Any]:
    turn = int(game.get("turn", 1))
    safe_turn = min(max(turn, 1), 3)

    if not is_ai_enabled():
        return FALLBACK_EVENTS[safe_turn]

    event = generate_json_from_prompt(_build_prompt(game))
    return _validate_event_payload(event)