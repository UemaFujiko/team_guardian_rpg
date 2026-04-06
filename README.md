# Team Guardian RPG

組織防衛シミュレーションRPGの簡易版です。

## 起動方法

### 仮想環境が未作成の場合
まだ `C:\venvs\rpg_env` を作っていない場合は、先に以下を **1回だけ** 実行してください。

```powershell
py -m venv C:\venvs\rpg_env
```

### 初回のみ
PowerShell で以下を実行してください。

```powershell
cd ご自身の好みのフォルダー\team_guardian_rpg
C:\venvs\rpg_env\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### 2回目以降
ライブラリの再インストールは不要です。PowerShell で以下を実行してください。

```powershell
cd ご自身の好みのフォルダー\team_guardian_rpg
C:\venvs\rpg_env\Scripts\Activate.ps1
streamlit run app.py
```

## 補足
- Python の仮想環境は、プロジェクトフォルダ内ではなく `C:\venvs\rpg_env` を使用します。
- ターミナルの先頭に `(rpg_env)` と表示されれば、正しい仮想環境が有効化されています。
- VSCode では、Python Interpreter に `C:\venvs\rpg_env\Scripts\python.exe` を選択してください。

## AIを使わずに試す
`.env.example` を参考に `.env` を作り、以下を設定してください。

```env
USE_AI=false
```

## AIを使う
`.env` に本物の OpenAI API キーを設定してください。

```env
OPENAI_API_KEY=sk-あなたの本物のキー
OPENAI_MODEL=gpt-4.1-mini
USE_AI=true
```


# Team Guardian RPG（3ターン専用版）

組織内で発生する有害な行動パターンに対して、
**記録・境界設定・被害者保護・制度対応** を学ぶための、短編ミッション型の Streamlit アプリです。

本版は、3ターンで完結する構成に整理し、短時間でも
**「兆候の把握 → 構造の理解 → 組織防衛の判断」**
を体験できるように改修しています。

---

## 今回の修正概要

### 1. 3ターン固定の短編ミッション型に変更
従来の長めの進行ではなく、以下の3段構成に整理しました。

- **Turn 1：異変の兆候**
  - 不自然な圧力、印象操作、分断の兆候を観察する段階
- **Turn 2：圧力の構造が見える**
  - 責任転嫁、報復示唆、例外化などの構造を見抜く段階
- **Turn 3：組織防衛の最終判断**
  - 記録保全、境界設定、保護、正式対応を選ぶ段階

これにより、短い時間でも起承転結が明確になりました。

### 2. UIをミッション型に再構成
画面を、単なるイベント表示ではなく、
**短時間で没入しやすいゲーム風UI** に寄せています。

主な変更点:
- 進行状況の表示を3ターン前提に整理
- コマンド風の選択肢表示
- 戦闘ログ風の判定表示
- 危機の進行が見えるゲージ表示

### 3. 判定指標を「組織防衛」中心に再設計
「正しそうな発言」よりも、
**組織をどれだけ守れたか** を重視する設計にしています。

主な観点:
- 証拠保全
- 境界設定
- 被害者保護
- 報復リスクの抑制
- 組織汚染の拡大防止

### 4. エンディング分岐を追加
3ターン終了後、選択結果に応じて複数の結末に分岐します。

例:
- 防衛成功エンド
- 表面沈静化エンド
- 報復拡大型エンド
- 制度介入エンド

### 5. AI未使用でも体験可能
OpenAI APIを使わなくても、
**固定イベントでプレイ可能** な設計です。

そのため、
- APIキー未設定でも最低限の動作確認ができる
- 研修や授業の事前デモに使いやすい
- ローカル開発時の切り分けがしやすい

---

## ファイル構成（主要部分）

```text
team_guardian_rpg/
├─ app.py
├─ requirements.txt
├─ README.md
├─ prompts/
│  └─ event_prompt.txt
├─ src/
│  ├─ __init__.py
│  ├─ ai_client.py
│  ├─ event_generator.py
│  ├─ game_state.py
│  └─ judge_engine.py
└─ docs/
   ├─ modification_notes.md
   ├─ team_guardian_system_design_3turn.pptx
   └─ team_guardian_system_design_3turn.pdf


   各ファイルの役割
app.py

画面表示、ターン進行、ボタン選択、結果表示を担当します。
ユーザーが直接触るメイン画面です。

src/game_state.py

ゲーム全体の状態を管理します。
ターン数、各種メトリクス、エンディング判定などを扱います。

src/judge_engine.py

プレイヤーの選択に対して、
どの指標がどう動くかを判定するロジックです。

src/event_generator.py

各ターンで発生するイベントを生成します。
AI利用時はプロンプトを使い、未利用時は固定イベントを返します。

src/ai_client.py

OpenAI APIとの接続を担当します。
APIを使う場合のみ利用されます。

prompts/event_prompt.txt

AIにどのような形式でイベントを作らせるかを指定する指示文です。

docs/modification_notes.md

今回の修正点と、その効果を整理したメモです。