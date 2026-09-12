import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
# Check local .env first, then fallback to Streamlit Cloud Secrets
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

st.set_page_config(page_title="Socratic Tutor AI", page_icon="🎓")
st.title("🎓 Autonomous Socratic Math Tutor")
st.caption("Tech Zephyr 4.0 Hackathon Prototype")

SOCRATIC_PROMPT = """
You are an autonomous Socratic math tutor.
Rules:
1. Analyze the student's problem or step.
2. DO NOT give the final numerical answer or full solution directly.
3. Ask a single leading question or provide a targeted hint to help the student find the answer themselves.
4. Remember the full equation context from previous messages.
5. Keep responses encouraging and short (2-3 sentences max).
"""

if not api_key:
    st.error("⚠️ GEMINI_API_KEY missing in .env file!")
    st.stop()

# Initialize Client on every rerun so connection never closes
client = genai.Client(api_key=api_key)

# Initialize history stores
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Stores Gemini SDK history

if "messages" not in st.session_state:
    st.session_state.messages = []      # Stores UI display text

# Render previous messages in UI
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your math problem or your next step here...")

if user_input:
    # 1. Render User Message in UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Append User Message to Gemini SDK History format
    st.session_state.chat_history.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)]
        )
    )

    # 3. Send Full History to Gemini
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your step..."):
            try:
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=st.session_state.chat_history,
                    config=types.GenerateContentConfig(
                        system_instruction=SOCRATIC_PROMPT,
                        temperature=0.2
                    )
                )
                
                bot_reply = response.text
                st.write(bot_reply)

                # 4. Save Assistant Reply to UI & SDK History
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.session_state.chat_history.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=bot_reply)]
                    )
                )

            except Exception as e:
                st.error(f"Error: {e}")