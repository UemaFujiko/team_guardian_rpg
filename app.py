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

    turn_key = f"selected_choice_{game.get('turn', 1)}"

    selected_choice = st.radio(
        "対応を1つ選択してください",
        choices,
        key=turn_key,
        label_visibility="collapsed",
    )

    if selected_choice:
        st.markdown(
            f"""
            <div style="
                background-color:#fff3cd;
                border-left:6px solid #ffb703;
                padding:12px;
                border-radius:8px;
                margin-top:8px;
                margin-bottom:12px;
            ">
                <b>選択中の対応：</b><br>
                {selected_choice}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("この対応で実行", use_container_width=True):
        choice = selected_choice
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
        st.session_state["last_selected_choice"] = choice
        st.rerun()

    if "last_selected_choice" in st.session_state:
        st.markdown(
            f"""
            <div style="
                background-color:#d1ecf1;
                border-left:6px solid #0c5460;
                padding:12px;
                border-radius:8px;
                margin-top:8px;
                margin-bottom:12px;
            ">
                <b>直前に選択した対応：</b><br>
                {st.session_state["last_selected_choice"]}
            </div>
            """,
            unsafe_allow_html=True,
        )

    if "last_result" in st.session_state:
        st.divider()
        st.markdown("### 直前ターンの判定")
        last_result = st.session_state["last_result"]
        st.write(last_result.get("reason", "理由はありません。"))
        lesson = last_result.get("lesson", "")
        if lesson:
            st.info(lesson)