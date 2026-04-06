from __future__ import annotations

import pandas as pd
import streamlit as st
import hashlib

from src.ai_client import get_model_name, is_ai_enabled
from src.event_generator import STAGE_LABELS, generate_event
from src.game_state import apply_judgment, final_rank, get_game, init_state, reset_state
from src.judge_engine import judge_choice


st.set_page_config(page_title="Team Guardian RPG", page_icon="🛡️", layout="wide")

init_state()
game = get_game()


POSITIVE_METRICS = [
    ("信頼", "trust"),
    ("心理的安全性", "safety"),
    ("業績", "performance"),
    ("透明性", "transparency"),
]

RISK_METRICS = [
    ("離職リスク", "attrition_risk"),
    ("組織汚染度", "misconduct_risk"),
    ("分断リスク", "faction_risk"),
]

COMMAND_LABELS = {
    "記録": "📝 記録する",
    "境界": "🛡️ 境界を引く",
    "保護": "🤝 守る",
    "連携": "📣 エスカレーションする",
    "静観": "👀 様子を見る",
}


def metric_caption(name: str) -> str:
    descriptions = {
        "trust": "協力と信頼の土台",
        "safety": "声を上げられる度合い",
        "performance": "短期の成果維持",
        "transparency": "意思決定の見える化",
        "attrition_risk": "離職や沈黙が進む危険",
        "misconduct_risk": "不適切行動や隠蔽が広がる危険",
        "faction_risk": "関係者が分断される危険",
    }
    return descriptions.get(name, "")


def gauge(label: str, value: int, inverse: bool = False) -> None:
    shown = max(0, min(100, value))
    if inverse:
        st.write(f"**{label}**  {shown}/100")
        st.progress(shown)
    else:
        safe = 100 - shown
        st.write(f"**{label}**  {shown}/100")
        st.progress(shown)


def render_gauges(game, in_sidebar=False):
    target = st.sidebar if in_sidebar else st

    target.markdown("### 防衛ゲージ")
    target.write(f"信頼: {game.get('trust', 50)}/100")
    target.progress(int(game.get("trust", 50)) / 100)

    target.write(f"心理的安全性: {game.get('safety', 50)}/100")
    target.progress(int(game.get("safety", 50)) / 100)

    target.write(f"透明性: {game.get('transparency', 50)}/100")
    target.progress(int(game.get("transparency", 50)) / 100)

    target.markdown("---")

    target.markdown("### 危機ゲージ")
    target.write(f"離職リスク: {game.get('attrition_risk', 50)}/100")
    target.progress(int(game.get("attrition_risk", 50)) / 100)

    target.write(f"組織汚染度: {game.get('misconduct_risk', 50)}/100")
    target.progress(int(game.get("misconduct_risk", 50)) / 100)

    target.write(f"分断リスク: {game.get('faction_risk', 50)}/100")
    target.progress(int(game.get("faction_risk", 50)) / 100)


def sidebar_controls() -> None:
    game = st.session_state.game

    game["max_turns"] = 3

    turn = int(game.get("turn", 1))
    if turn < 1:
        turn = 1
        game["turn"] = 1
    if turn > 3:
        turn = 3
        game["turn"] = 3

    max_turns = 3
    safe_turn = min(max(turn, 1), max_turns)
    stage_name = STAGE_LABELS.get(safe_turn, "最終防衛")

    with st.sidebar:
        st.header("ゲーム情報")
        st.write(f"現在ターン: {safe_turn} / {max_turns}")
        st.write(f"現在フェーズ: {stage_name}")

        difficulty = game.get("difficulty", "標準")
        team_type = game.get("team_type", "コンサル会社")
        st.write(f"難易度: {difficulty}")
        st.write(f"組織タイプ: {team_type}")

        st.divider()
        st.subheader("防衛ゲージ")

        trust = int(game.get("trust", 50))
        safety = int(game.get("safety", 50))
        transparency = int(game.get("transparency", 50))

        st.progress(max(0.0, min(trust / 100, 1.0)))
        st.caption(f"信頼: {trust}")

        st.progress(max(0.0, min(safety / 100, 1.0)))
        st.caption(f"心理的安全性: {safety}")

        st.progress(max(0.0, min(transparency / 100, 1.0)))
        st.caption(f"透明性: {transparency}")

        st.divider()
        st.subheader("危機ゲージ")

        attrition_risk = int(game.get("attrition_risk", 50))
        misconduct_risk = int(game.get("misconduct_risk", 50))
        faction_risk = int(game.get("faction_risk", 50))

        st.progress(max(0.0, min(attrition_risk / 100, 1.0)))
        st.caption(f"離職リスク: {attrition_risk}")

        st.progress(max(0.0, min(misconduct_risk / 100, 1.0)))
        st.caption(f"組織汚染度: {misconduct_risk}")

        st.progress(max(0.0, min(faction_risk / 100, 1.0)))
        st.caption(f"分断リスク: {faction_risk}")

        if st.button("最初からやり直す", width="stretch"):
            reset_state()
            st.rerun()


def render_home() -> None:
    st.title("🛡️ Team Guardian RPG - 3 Turn Mission")
    st.subheader("はじめに")
    st.write("このゲームは、職場を壊しやすい高操作・低共感な行動パターンをとりやすいヒトへの対応をみるゲームです。")
    st.write(" 個人の診断や人格断定ではなく、観察できる行動・構造・防衛策に焦点を当て、学びへつなげてください。")
    st.write("「兆候把握 → 構造理解 → 組織防衛」の3ターンで１ゲームとなっています。")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**TURN 1: 異変への気づき**\n- 何が不穏かを見抜く\n- レッドフラッグを拾う\n- 初動を誤らない")
    with c2:
        st.warning("**TURN 2: 本質的な原因を探る**\n- 分断や責任転嫁が見える\n- 誰が何を曖昧にしているか確認\n- 記録と共有で包囲する")
    with c3:
        st.success("**TURN 3: 組織とヒトを守る**\n- 被害保護と再発防止\n- 例外扱いを止める\n- エンディングへ")

    st.write("")
    st.subheader("主人公はあなた！営業部のチーフです！")
    st.write("チームメンバーを守り抜き、ヒトを定着させてください。")
    st.write("人財の確保はあなたの腕にかかっています。")
    
    st.write("")
    st.markdown("### さぁ、ゲームをはじめましょう♪")
    st.markdown(
        "- **「ゲーム」タブ**: ゲームが始まります。\n"
        "- **「パラメータ」タブ**: チーム環境が可視化されています。\n"
        "- **「ヒント」タブ**: チームとヒトを守るための行動のヒントがあります。\n"
        "- **サイドバー**: 防衛ゲージと危機ゲージが可視化されています。"
    )


def render_mission_panel(show_title: bool = True) -> None:
    if show_title:
        st.subheader("ゲーム進行")

    current_turn = int(st.session_state.game.get("turn", 1))
    max_turns = int(st.session_state.game.get("max_turns", 3))
    current_turn = min(max(current_turn, 1), max_turns)

    stages = []
    for idx in range(1, max_turns + 1):
        label = STAGE_LABELS.get(idx, f"TURN {idx}")
        if idx < current_turn:
            mark = "✅"
        elif idx == current_turn:
            mark = "🟨"
        else:
            mark = "⬜"
        stages.append(f"{mark} **TURN {idx}** {label}")

    st.markdown("  \n".join(stages))


def classify_choice(choice: str) -> str:
    if any(word in choice for word in ["記録", "議事", "文書", "時系列"]):
        return COMMAND_LABELS["記録"]
    if any(word in choice for word in ["例外", "基準", "ルール", "境界"]):
        return COMMAND_LABELS["境界"]
    if any(word in choice for word in ["保護", "本人", "通報", "監視"]):
        return COMMAND_LABELS["保護"]
    if any(word in choice for word in ["関係者", "全員", "共有", "レビュー"]):
        return COMMAND_LABELS["連携"]
    return COMMAND_LABELS["静観"]


def render_last_result() -> None:
    if "last_result" not in st.session_state:
        return

    last_result = st.session_state["last_result"]
    st.divider()
    st.markdown("### あなたの行動への分析")
    score = last_result.get("score", 0)
    if score >= 5:
        st.success(f"防衛成功: {last_result.get('reason', '')}")
    elif score >= 1:
        st.warning(f"部分成功: {last_result.get('reason', '')}")
    else:
        st.error(f"損害発生: {last_result.get('reason', '')}")

    lesson = last_result.get("lesson", "")
    if lesson:
        st.info(f"学び: {lesson}")
    if last_result.get("next_best_action"):
        st.write(f"**次善策**: {last_result['next_best_action']}")

    effects = last_result.get("effects", {})
    useful = {k: v for k, v in effects.items() if v != 0}
    if useful:
        st.markdown("### あなたの3つの対応がもたらしたチームの状況")
        st.info(summarize_effects_as_ai_feedback(useful))


def get_turn_event_for_hint(turn: int) -> dict:
    current_game = st.session_state.game
    temp_game = dict(current_game)
    temp_game["turn"] = turn

    try:
        event = generate_event(temp_game)
    except Exception:
        event = {}

    return event if isinstance(event, dict) else {}


def render_play() -> None:
    game = st.session_state.game

    top_left, top_right = st.columns([2.2, 1])

    with top_left:
        st.header("🎮 ゲーム")

    with top_right:
        st.markdown("### ゲーム進行")
        render_mission_panel(show_title=False)

    if game.get("game_over", False):
        st.subheader("エンディング")
        st.write(final_rank())
        render_last_result()
        return

    event = generate_event(game)
    turn = game.get("turn", 1)
    stage_name = STAGE_LABELS[turn]

    st.divider()
    st.subheader(f"TURN {turn}: {stage_name}")
    st.markdown(f"### {event.get('event_title', 'イベント')}")
    st.write(event.get("summary", ""))

    st.divider()
    st.markdown("### 現場の状況ログ")
   

    npcs = event.get("npcs", [])
    if npcs:
        for npc in npcs:
            st.markdown(
                f"**{npc.get('name', '不明')}**（{npc.get('role', '')} / {npc.get('stance', '')}）"
            )
            if npc.get("dialogue"):
                st.write(f"「{npc['dialogue']}」")
            if npc.get("tactic"):
                st.caption(f"観察メモ: {npc['tactic']}")
            st.markdown("---")
    else:
        st.caption("現場の状況ログはありません。")

    st.markdown("### あなたの対応を選んでください")
    choices = event.get("choices", [])
    for idx, choice in enumerate(choices, start=1):
        label = classify_choice(choice)
        if st.button(f"{label} - {choice}", key=f"choice_{turn}_{idx}", use_container_width=True):
            result = judge_choice(game, event, choice)
            result_dict = result.model_dump() if hasattr(result, "model_dump") else dict(result)
            apply_judgment(result_dict, choice)
            st.session_state["last_result"] = result_dict
            st.rerun()


def summarize_effects_as_ai_feedback(effects: dict) -> str:
    if not effects:
        return "今回の行動による目立った変化はありませんでした。"

    label_map = {
        "trust": "チームの信頼",
        "safety": "心理的安全性",
        "performance": "業績",
        "transparency": "透明性",
        "attrition_risk": "離職リスク",
        "misconduct_risk": "組織汚染度",
        "faction_risk": "分断リスク",
    }

    improved = []
    worsened = []

    for key, value in effects.items():
        if value == 0:
            continue

        label = label_map.get(key, key)

        if key in ["attrition_risk", "misconduct_risk", "faction_risk"]:
            if value < 0:
                improved.append(f"{label}は少し下がりました")
            else:
                worsened.append(f"{label}はやや高まりました")
        else:
            if value > 0:
                improved.append(f"{label}は少し改善しました")
            else:
                worsened.append(f"{label}はやや低下しました")

    parts = []

    if improved:
        parts.append("、".join(improved))
    if worsened:
        parts.append("、".join(worsened))

    if not parts:
        return "今回の行動による目立った変化はありませんでした。"

    return "" + "".join(parts) + "。"


    render_last_result()

    st.divider()
    st.subheader("行動履歴")
    if game.get("history"):
        st.dataframe(pd.DataFrame(game["history"]), use_container_width=True)
    else:
        st.write("まだ行動履歴はありません。")


def render_status() -> None:
    st.header("📊 パラメータ")
    rows = []
    for label, key in POSITIVE_METRICS + RISK_METRICS:
        rows.append({
            "指標": label,
            "値": game.get(key, 50),
            "区分": "防衛" if key in dict(POSITIVE_METRICS).values() else "危機"
        })
    df = pd.DataFrame(rows)
    st.bar_chart(df.set_index("指標")[["値"]])

    st.subheader("防衛フラグ")
    st.json(game.get("flags", {}))


def render_learning() -> None:
    st.header("📘 ヒント")
    st.markdown(
        """
### 3ターン版の学び
- **1ターン目**で初動を誤ると、2ターン目で説明が割れ、3ターン目で報復や隠蔽が強く出やすい。
- **高操作な相手との対処**は、説得勝負ではなく、記録・共有・保護・例外禁止の設計勝負になる。
- **被害者保護を後回し**にすると、短期的には静かでも、長期的には離職と沈黙が進む。

### 基本手順
1. 事実を切り分ける
2. 時系列と記録を残す
3. 関係者への同一共有を行う
4. 例外扱いを止める
5. 被害者・通報者を守る
6. 再発防止を制度化する
        """
    )

    st.divider()
    st.subheader("ターン解説")

    max_turns = int(st.session_state.game.get("max_turns", 3))

    for turn in range(1, max_turns + 1):
        event = get_turn_event_for_hint(turn)
        stage_name = STAGE_LABELS.get(turn, f"TURN {turn}")

        st.markdown(f"### TURN {turn}: {stage_name}")

        severity = event.get("severity", "中")
        defense_focus = event.get("defense_focus", [])
        risk_tags = event.get("risk_tags", [])
        worldview_markers = event.get("worldview_markers", [])
        red_flags = event.get("red_flags", [])

        st.info(
            f"**深刻度**: {severity}\n\n"
            f"**防衛重点**: {', '.join(defense_focus) if defense_focus else 'なし'}"
        )

        st.write(f"**リスクタグ**: {' / '.join(risk_tags) if risk_tags else 'なし'}")
        st.write(f"**兆候**: {' / '.join(worldview_markers) if worldview_markers else 'なし'}")

        st.markdown("**レッドフラッグ**")
        if red_flags:
            for item in red_flags:
                st.write(f"- {item}")
        else:
            st.write("- なし")

        st.divider()


def main() -> None:
    sidebar_controls()
    tabs = st.tabs(["はじめに", "ゲーム", "パラメータ", "ヒント"])
    with tabs[0]:
        render_home()
    with tabs[1]:
        render_play()
    with tabs[2]:
        render_status()
    with tabs[3]:
        render_learning()


if __name__ == "__main__":
    main()