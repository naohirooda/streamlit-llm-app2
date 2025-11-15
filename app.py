import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# .env の読み込み（OPENAI_API_KEY を環境変数にセット）
load_dotenv()

# --- 専門家プロンプト（ラジオの選択肢に応じて切り替え） ---
ROLE_PROMPTS = {
    "営業企画・RevOpsの専門家": (
        "あなたはB2B SaaSの営業企画・RevOpsの専門家です。"
        "KPI設計、MQL/SQL、インサイドセールス運用、架電スクリプト、GAS/Sheets自動化に明るく、"
        "実務で使える提案・具体ステップ・例を日本語で簡潔に提示してください。"
    ),
    "Python & データ整形の専門家": (
        "あなたはPythonによるデータ整形/ETLの専門家です。"
        "pandas/GAS/CSV前処理、正規表現、品質チェックの観点で、"
        "最小再現コード例と手順、注意点を日本語でわかりやすく提示してください。"
    ),
}

# --- LLM呼び出し関数（要件：引数 = 入力テキスト & ラジオ選択値 / 戻り値 = 回答文字列） ---
def ask_llm(user_text: str, role_key: str) -> str:
    """選択された専門家ロールでシステムメッセージを切り替え、LLM回答を返す"""
    if not user_text:
        return "入力テキストが空です。内容を入力してください。"
    system_msg = ROLE_PROMPTS.get(role_key, ROLE_PROMPTS["営業企画・RevOpsの専門家"])

    llm = ChatOpenAI(  # Lesson8 と同じ LangChain の使い方
        model_name="gpt-4o-mini",
        temperature=0.3,
    )
    messages = [
        SystemMessage(content=system_msg),
        HumanMessage(content=user_text),
    ]
    result = llm(messages)
    return result.content

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="LangChain × Streamlit サンプル", page_icon="🧪", layout="centered")

st.title("🧪 LangChain × Streamlit サンプルアプリ")
st.write(
    """
**概要**
- 下の入力フォームにお題や質問を入力すると、選んだ「専門家の視点」で回答します。
- 右側のラジオで専門家の種類を選んでから「実行」を押してください。

**使い方**
1. 専門家の種類を選ぶ
2. テキストを入力
3. **実行** ボタンを押す → 回答が表示されます
"""
)

# ラジオ（専門家の種類）
role = st.radio(
  "専門家の種類を選択してください：",
  list(ROLE_PROMPTS.keys()),
  horizontal=False,
)

# 入力フォーム
user_text = st.text_area("入力テキスト", height=180, placeholder="例）N-5定義の見直し手順を整理したい。運用観点・ダッシュボード整備も含めて提案して。")

# 実行ボタン
if st.button("実行"):
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI_API_KEY が設定されていません。.env に設定し、再実行してください。")
    elif not user_text.strip():
        st.warning("テキストを入力してください。")
    else:
        with st.spinner("LLM に問い合わせ中..."):
            try:
                answer = ask_llm(user_text.strip(), role)
                st.success("回答")
                st.markdown(answer)
            except Exception as e:
                st.error(f"エラーが発生しました：{e}")

# サイドバー：小さなヘルプ
with st.sidebar:
    st.subheader("ℹ️ About")
    st.caption("このアプリは入力文と役割選択をもとにLLMが回答します。APIキーはローカルの .env を使用します。")
