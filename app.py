from __future__ import annotations

import pandas as pd
import streamlit as st

from src.ai_client import is_ai_enabled, get_model_name
from src.event_generator import generate_event
from src.game_state import init_state, get_game, reset_state, apply_judgment, final_rank
from src.judge_engine import judge_choice


st.set_page_config(page_title="Team Guardian RPG", page_icon="🛡️", layout="wide")

init_state()
game = get_game()


def sidebar_controls() -> None:
    with st.sidebar:
        st.title("🛡️ Team Guardian RPG")
        st.caption("有害行動からチームを守る防衛型RPG")
        st.divider()

        ai_mode = is_ai_enabled()
        st.write(f"AIモード: {'ON' if ai_mode else 'OFF'}")
        if ai_mode:
            st.caption(f"Model: {get_model_name()}")

        difficulty_options = ["易しい", "標準", "難しい"]
        team_options = ["コンサル会社", "学校組織", "病院", "スタートアップ", "行政組織"]

        current_difficulty = game.get("difficulty", "標準")
        if current_difficulty not in difficulty_options:
            current_difficulty = "標準"

        current_team = game.get("team_type", "コンサル会社")
        if current_team not in team_options:
            current_team = "コンサル会社"

        game["difficulty"] = st.selectbox(
            "難易度",
            difficulty_options,
            index=difficulty_options.index(current_difficulty),
        )

        game["team_type"] = st.selectbox(
            "チームタイプ",
            team_options,
            index=team_options.index(current_team),
        )

        if st.button("ゲームをリセット", use_container_width=True):
            reset_state()
            st.rerun()

        st.divider()
        st.metric("Turn", f"{game.get('turn', 1)} / {game.get('max_turns', 10)}")
        st.metric("信頼", game.get("trust", 50))
        st.metric("心理的安全性", game.get("safety", 50))
        st.metric("業績", game.get("performance", 50))
        st.metric("透明性", game.get("transparency", 50))
        st.metric("離職リスク", game.get("attrition_risk", 50))
        st.metric("派閥化リスク", game.get("faction_risk", 50))
        st.metric("不正リスク", game.get("misconduct_risk", 50))


def render_home() -> None:
    st.title("🛡️ Team Guardian RPG")
    st.subheader("操作・分断・責任転嫁から、あなたのチームを守る")
    st.write(
        "このゲームは、架空のチームに起きる有害行動への対応を学ぶ教育用シミュレーターです。"
        " 実在人物の診断ではなく、行動パターンと組織防衛の訓練を目的としています。"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.info(
            "**プレイヤーの役割**\n"
            "- マネージャー\n"
            "- PM\n"
            "- HR\n"
            "- 現場リーダー"
        )
    with col2:
        st.warning(
            "**勝利条件の目安**\n"
            "- 信頼と心理的安全性を維持\n"
            "- 業績と透明性を確保\n"
            "- 離職・派閥化・不正リスクを抑制"
        )

    st.success("左のサイドバーで難易度やチームタイプを設定し、[プレイ] タブへ進んでください。")


def render_play() -> None:
    st.header("🎮 プレイ")

    if game.get("game_over", False):
        st.error("ゲームは終了しています。左のサイドバーからリセットしてください。")
        st.subheader("最終評価")
        st.write(final_rank())
        return

    try:
        event = generate_event(game)
    except Exception as e:
        st.error(f"イベント生成に失敗しました: {e}")
        st.stop()

    event_title = event.get("event_title", "イベント")
    summary = event.get("summary", "")
    risk_tags = event.get("risk_tags", [])
    npcs = event.get("npcs", [])
    choices = event.get("choices", [])

    st.subheader(f"Turn {game.get('turn', 1)}: {event_title}")
    st.write(summary)

    tags_text = " / ".join(risk_tags) if risk_tags else "なし"
    st.caption(f"リスクタグ: {tags_text}")

    with st.expander("NPCの様子"):
        if npcs:
            for npc in npcs:
                name = npc.get("name", "不明")
                role = npc.get("role", "役割不明")
                stance = npc.get("stance", "立場不明")
                dialogue = npc.get("dialogue", "")
                st.markdown(f"**{name}**（{role} / {stance}）")
                if dialogue:
                    st.write(f"「{dialogue}」")
        else:
            st.write("NPC情報はありません。")

    st.markdown("### 対応を選んでください")

    if not choices:
        st.warning("選択肢が生成されませんでした。")
        return

    for idx, choice in enumerate(choices, start=1):
        if st.button(f"{idx}. {choice}", key=f"choice_{game.get('turn', 1)}_{idx}", use_container_width=True):
            result = judge_choice(game, event, choice)
            if hasattr(result, "model_dump"):
                result_dict = result.model_dump()
            elif isinstance(result, dict):
                result_dict = result
            else:
                result_dict = {
                    "score": 0,
                    "reason": str(result),
                    "lesson": "",
                    "effects": {},
                }

            apply_judgment(result_dict, choice)
            st.session_state["last_result"] = result_dict
            st.rerun()

    if "last_result" in st.session_state:
        st.divider()
        st.markdown("### 直前ターンの判定")
        last_result = st.session_state["last_result"]
        st.write(last_result.get("reason", "理由はありません。"))
        lesson = last_result.get("lesson", "")
        if lesson:
            st.info(lesson)


def render_status() -> None:
    st.header("📊 チーム状態")

    metrics = pd.DataFrame(
        {
            "指標": ["信頼", "心理的安全性", "業績", "透明性", "離職リスク", "派閥化リスク", "不正リスク"],
            "値": [
                game.get("trust", 50),
                game.get("safety", 50),
                game.get("performance", 50),
                game.get("transparency", 50),
                game.get("attrition_risk", 50),
                game.get("faction_risk", 50),
                game.get("misconduct_risk", 50),
            ],
        }
    )
    st.bar_chart(metrics.set_index("指標"))

    st.subheader("フラグ")
    st.json(game.get("flags", {}))

    st.subheader("行動ログ")
    history = game.get("history", [])
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True)
    else:
        st.write("まだログはありません。")

    if game.get("game_over", False):
        st.success(f"最終評価: {final_rank()}")


def render_learning() -> None:
    st.header("📘 学習モード")
    st.markdown(
        """
### このゲームで学ぶこと
- **事実確認の重要性**: 記録、議事録、成果物履歴は防衛の基礎です。
- **犯人探しより構造是正**: 問題を個人攻撃だけで捉えると、組織がさらに壊れやすくなります。
- **心理的安全性と透明性**: 声を上げやすい場と、情報共有の仕組みは分断対策に有効です。
- **高業績者の例外化を避ける**: 短期成果を理由に規範逸脱を免責すると、長期的損失が大きくなります。

### 発展案
- チームタイプごとのイベント差分
- 証拠ポイント、被害者保護ポイントなどの隠し変数
- レポート出力機能
- イベントCSV蓄積と分析
        """
    )


def render_settings() -> None:
    st.header("⚙️ 設定")
    st.write("アプリは、APIキーなしでも固定イベントで動作します。")
    st.code(
        "OPENAI_API_KEY=sk-あなたの本物のキー\nOPENAI_MODEL=gpt-4.1-mini\nUSE_AI=true",
        language="bash",
    )
    st.write("`.env` をプロジェクト直下に置くと、AI生成モードを利用できます。")
    st.write(f"現在のAI利用状態: {'有効' if is_ai_enabled() else '無効'}")
    if is_ai_enabled():
        st.write(f"現在のモデル: {get_model_name()}")


sidebar_controls()

pages = {
    "ホーム": render_home,
    "プレイ": render_play,
    "状態": render_status,
    "学習": render_learning,
    "設定": render_settings,
}

selected = st.radio("ページ", list(pages.keys()), horizontal=True, label_visibility="collapsed")
pages[selected]()
