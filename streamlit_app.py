import os
import sys
import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

load_dotenv()

# Online: read the key from Streamlit secrets. Locally: from .env
try:
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SYSTEM_PROMPT = (
    "You are a helpful assistant. Detect the language of the user's "
    "latest message and ALWAYS reply in that same language and script. "
    "If the user writes in Tamil, reply in Tamil script. "
    "If in Hindi, reply in Hindi. If in English, reply in English. "
    "If the user mixes languages (e.g. Tanglish: Tamil in English letters), "
    "reply in the same mixed style. "
    "Tool results may be in English; translate them into the user's language. "
    "Keep numbers as digits (e.g. 96, 31°C)."
)

st.set_page_config(page_title="MCP Agent", page_icon="🤖")
st.title("🤖 MCP Math & Weather Agent")
st.caption("Ask a math question or the weather in any city, in any language.")

if not os.getenv("GROQ_API_KEY"):
    st.error("GROQ_API_KEY is missing. Add it to .env (local) or Secrets (online).")
    st.stop()


async def ask_agent(question: str) -> str:
    client = MultiServerMCPClient(
        {
            "math": {
                "command": sys.executable,
                "args": [os.path.join(BASE_DIR, "mathserver.py")],
                "transport": "stdio",
            },
            "weather": {
                "command": sys.executable,
                "args": [os.path.join(BASE_DIR, "weather.py"), "stdio"],
                "transport": "stdio",
            },
        }
    )
    tools = await client.get_tools()
    model = ChatGroq(model="openai/gpt-oss-120b")
    agent = create_react_agent(model, tools, prompt=SYSTEM_PROMPT)
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    return response["messages"][-1].content


# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask in any language / எந்த மொழியிலும் கேளுங்கள்")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                answer = asyncio.run(ask_agent(question))
            except Exception as e:
                answer = f"Error: {e}"
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})