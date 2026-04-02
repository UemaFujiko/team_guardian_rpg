# Team Guardian RPG

組織防衛シミュレーションRPGの簡易版です。

## 起動方法

```powershell
cd C:\Users\FujikoUema\OneDrive\ドキュメント\tech0\RPG
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

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
