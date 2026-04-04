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
