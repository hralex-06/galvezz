import streamlit as st
import google.generativeai as genai
import os

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="GalvezAI",
    page_icon="logo.png",
    layout="wide"
)

# =========================================================
# LIGHT MINIMAL GEMINI STYLE
# =========================================================

st.markdown("""
<style>

/* ---------- GLOBAL ---------- */

html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

.stApp {
    background-color: #ffffff;
    color: #111827;
}

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e5e7eb;
}

/* ---------- TITLES ---------- */

h1, h2, h3 {
    color: #111827 !important;
    font-weight: 700;
}

/* ---------- TEXT ---------- */

p, span, div, label {
    color: #111827 !important;
}

/* ---------- CHAT ---------- */

.stChatMessage {
    border-radius: 18px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: none;
}

/* USER MESSAGE */

div[data-testid="stChatMessageUser"] {
    background-color: #f3f4f6;
}

/* AI MESSAGE */

div[data-testid="stChatMessageAssistant"] {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
}

/* ---------- INPUT ---------- */

.stChatInput input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-radius: 18px !important;
    border: 1px solid #d1d5db !important;
}

/* ---------- BUTTONS ---------- */

.stButton button {
    width: 100%;
    border-radius: 14px;
    background-color: white;
    color: #111827;
    border: 1px solid #d1d5db;
    transition: 0.2s;
}

.stButton button:hover {
    border: 1px solid #2563eb;
    color: #2563eb;
}

/* ---------- SCROLLBAR ---------- */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #f3f4f6;
}

::-webkit-scrollbar-thumb {
    background: #d1d5db;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE GEMINI CONFIG
# =========================================================

API_KEY = "AIzaSyAzUFMDQfuZpZaEohaJ5M6dBD_HGXeNcFo"
genai.configure(api_key=API_KEY)

# =========================================================
# AI PERSONALITY
# =========================================================

SYSTEM_PROMPT = """
You are GalvezAI.

You always speak in the same language as the user.

You are funny, intelligent and slightly sarcastic.
You tease the user sometimes but never in a cruel way.
You speak naturally like a real friend.

Do not sound corporate.
Do not sound robotic.
Keep responses modern and natural.

If the user is sad or worried:
- become more supportive
- avoid harsh jokes
- help seriously

You also have strong judgement:
- if the user wants to do something stupid,
explain clearly why it's a bad idea.
"""

# NOU MODEL: "gemini-pro" per a màxima compatibilitat amb servidors i llibreries velles
model = genai.GenerativeModel(
    model_name="gemini-pro",
    system_instruction=SYSTEM_PROMPT
)

# =========================================================
# SESSION STATE (MEMÒRIA DE LA IA)
# =========================================================

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)

    st.markdown("## GalvezAI")

    st.caption(
        "An AI with humor and common sense. "
        "A statistical anomaly on the internet."
    )

    st.markdown("---")

    if st.button("🧹 Clear chat"):
        st.session_state.gemini_history = []
        st.rerun()

    st.markdown("---")

    st.markdown("""
    ### About

    - Gemini Pro
    - Streamlit
    - Minimal UI
    - Smart humor
    - No corporate personality
    """)

# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([1, 8])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)

with col2:
    st.title("GalvezAI")
    st.caption(
        "Ask anything. The AI will silently judge your decisions."
    )

# =========================================================
# DISPLAY MESSAGES FROM MEMORY
# =========================================================

for msg in st.session_state.gemini_history:
    st_role = "user" if msg["role"] == "user" else "assistant"
    with st.chat_message(st_role):
        st.markdown(msg["parts"][0])

# =========================================================
# USER INPUT & RESPONSE GENERATION
# =========================================================

if prompt := st.chat_input("Type something..."):

    # 1. Mostrar el missatge de l'usuari a la pantalla
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Afegir el missatge a la memòria persistent
    st.session_state.gemini_history.append({
        "role": "user",
        "parts": [prompt]
    })

    # 3. Generar la resposta de la IA
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(
                st.session_state.gemini_history,
                stream=True
            )

            full_response = ""
            placeholder = st.empty()

            for chunk in response:
                if hasattr(chunk, "text"):
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

            # 4. Desar la resposta de la IA a la memòria
            st.session_state.gemini_history.append({
                "role": "model",
                "parts": [full_response]
            })

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "GalvezAI © 2026 • Built with Streamlit + Gemini • "
    "Humanity allowed this AI to have sarcasm."
)
