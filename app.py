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
    ("証拠保全", "evidence"),
    ("境界設定", "boundaries"),
    ("被害保護", "protection"),
]

RISK_METRICS = [
    ("報復リスク", "retaliation_risk"),
    ("組織汚染度", "contamination_risk"),
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
        "evidence": "記録・証拠保全の強さ",
        "boundaries": "逸脱への線引きの強さ",
        "protection": "被害者・通報者保護の強さ",
        "retaliation_risk": "報復が起きる危険",
        "contamination_risk": "例外化や隠蔽が広がる危険",
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

    # 防衛ゲージ
    target.markdown("### 防衛ゲージ")
    target.write(f"証拠保全: {game.get('evidence', 0)}/100")
    target.progress(int(game.get("evidence", 0)) / 100)

    target.write(f"境界設定: {game.get('boundary', 0)}/100")
    target.progress(int(game.get("boundary", 0)) / 100)

    target.write(f"被害者保護: {game.get('protection', 0)}/100")
    target.progress(int(game.get("protection", 0)) / 100)

    target.markdown("---")

    # 危機ゲージ
    target.markdown("### 危機ゲージ")
    target.write(f"組織汚染: {game.get('pollution', 0)}/100")
    target.progress(int(game.get("pollution", 0)) / 100)

    target.write(f"報復リスク: {game.get('retaliation', 0)}/100")
    target.progress(int(game.get("retaliation", 0)) / 100)

    target.write(f"分析リスク: {game.get('analysis_risk', 0)}/100")
    target.progress(int(game.get("analysis_risk", 0)) / 100)



def sidebar_controls() -> None:
    game = st.session_state.game

    # 3ターン固定
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
        st.header("ミッション情報")
        st.write(f"現在ターン: {safe_turn} / {max_turns}")
        st.write(f"現在フェーズ: {stage_name}")

        difficulty = game.get("difficulty", "標準")
        team_type = game.get("team_type", "コンサル会社")
        st.write(f"難易度: {difficulty}")
        st.write(f"組織タイプ: {team_type}")

        st.divider()
        st.subheader("防衛ゲージ")

        evidence = int(game.get("evidence", 0))
        boundaries = int(game.get("boundaries", 0))
        protection = int(game.get("protection", 0))

        st.progress(max(0.0, min(evidence / 100, 1.0)))
        st.caption(f"証拠保全: {evidence}")

        st.progress(max(0.0, min(boundaries / 100, 1.0)))
        st.caption(f"境界設定: {boundaries}")

        st.progress(max(0.0, min(protection / 100, 1.0)))
        st.caption(f"被害者保護: {protection}")

        st.divider()
        st.subheader("危機ゲージ")

        retaliation_risk = int(game.get("retaliation_risk", 0))
        contamination_risk = int(game.get("contamination_risk", 0))
        faction_risk = int(game.get("faction_risk", 0))

        st.progress(max(0.0, min(retaliation_risk / 100, 1.0)))
        st.caption(f"報復リスク: {retaliation_risk}")

        st.progress(max(0.0, min(contamination_risk / 100, 1.0)))
        st.caption(f"組織汚染度: {contamination_risk}")

        st.progress(max(0.0, min(faction_risk / 100, 1.0)))
        st.caption(f"分断リスク: {faction_risk}")

        if st.button("最初からやり直す", width="stretch"):
            reset_state()
            st.rerun()

def render_home() -> None:
    st.title("🛡️ Team Guardian RPG - 3 Turn Mission")
    st.subheader("3ターン完結版")
    st.write("「兆候把握 → 構造理解 → 組織防衛」の最終判断まで行います。")
    st.write("このゲームは、職場を壊しやすい高操作・低共感な行動パターンをとりやすいヒトへの対応をみるゲームです。")
    st.write(" 個人の診断や人格断定ではなく、観察できる行動・構造・防衛策に焦点を当て、学びへつなげてください。")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.info("**TURN 1: 異変の兆候**\n- 何が不穏かを見抜く\n- レッドフラッグを拾う\n- 初動を誤らない")
    with c2:
        st.warning("**TURN 2: 圧力の本体**\n- 分断や責任転嫁が見える\n- 誰が何を曖昧にしているか確認\n- 記録と共有で包囲する")
    with c3:
        st.success("**TURN 3: 最終防衛**\n- 被害保護と再発防止\n- 例外扱いを止める\n- エンディングへ")

    st.markdown("### この版で強めたUI")
    st.markdown(
        "- **危機ゲージ**: 報復リスク・組織汚染度・分断リスクを可視化\n"
        "- **コマンド選択**: 選択肢を RPG の行動コマンド風に表示\n"
        "- **戦闘ログ風判定**: 防衛成功 / 損害 / 次善策の3段で結果を表示\n"
        "- **短編ミッション化**: 3ターンで起承転結が出る構成"
    )



def render_mission_panel() -> None:
    st.subheader("ミッション進行")

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
        st.json(useful)



def render_play() -> None:
    game = st.session_state.game

    st.header("🎮 ミッション")
    render_mission_panel()

    if game.get("game_over", False):
        st.subheader("エンディング")
        st.write(final_rank())
        render_last_result()
        return

    event = generate_event(game)
    turn = game.get("turn", 1)
    stage_name = STAGE_LABELS[turn]

    top1, top2 = st.columns([1.45, 1])
    with top1:
        st.subheader(f"TURN {turn}: {stage_name}")
        st.markdown(f"### {event.get('event_title', 'イベント')}")
        st.write(event.get("summary", ""))
        st.caption(f"リスクタグ: {' / '.join(event.get('risk_tags', []))}")
        st.caption(f"兆候: {' / '.join(event.get('worldview_markers', []))}")

    with top2:
        st.info(
            f"**深刻度**: {event.get('severity', '中')}\n\n"
            f"**防衛重点**: {', '.join(event.get('defense_focus', []))}"
        )
        if event.get("red_flags"):
            st.markdown("**レッドフラッグ**")
            for item in event["red_flags"]:
                st.write(f"- {item}")

    mid1, mid2 = st.columns(2)
    with mid1:
        st.markdown("### 危機ゲージ")
        gauge("報復リスク", game.get("retaliation_risk", 50), inverse=True)
        gauge("組織汚染度", game.get("contamination_risk", 50), inverse=True)
        gauge("分断リスク", game.get("faction_risk", 50), inverse=True)

    with mid2:
        st.markdown("### 防衛ゲージ")
        gauge("証拠保全", game.get("evidence", 45), inverse=True)
        gauge("境界設定", game.get("boundaries", 45), inverse=True)
        gauge("被害保護", game.get("protection", 45), inverse=True)

    st.markdown("### 現場ログ")
    st.divider()

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
        st.caption("現場ログはありません。")

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

    render_last_result()



def render_status() -> None:
    st.header("📊 状況確認")
    rows = []
    for label, key in POSITIVE_METRICS + RISK_METRICS:
        rows.append({"指標": label, "値": game.get(key, 50), "区分": "防衛" if key in dict(POSITIVE_METRICS).values() else "危機"})
    df = pd.DataFrame(rows)
    st.bar_chart(df.set_index("指標")[["値"]])
    st.subheader("防衛フラグ")
    st.json(game.get("flags", {}))
    st.subheader("行動履歴")
    if game.get("history"):
        st.dataframe(pd.DataFrame(game["history"]), use_container_width=True)
    else:
        st.write("まだ行動履歴はありません。")



def render_learning() -> None:
    st.header("📘 学習メモ")
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



def main() -> None:
    sidebar_controls()
    tabs = st.tabs(["ホーム", "ミッション", "状況", "学習"])
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
