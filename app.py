import streamlit as st
import google.generativeai as genai
import os

# =========================================================
# CONFIGURACIÓ PÀGINA
# =========================================================

st.set_page_config(
    page_title="GalvezAI",
    page_icon="logo.png",
    layout="wide"
)

# =========================================================
# CSS ESTIL GEMINI MINIMALISTA
# =========================================================

st.markdown("""
<style>

/* ---------- FONTS ---------- */

html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}

/* ---------- FONS GENERAL ---------- */

.stApp {
    background-color: #0b0f19;
    color: white;
}

/* ---------- SIDEBAR ---------- */

section[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1f2937;
}

/* ---------- TITOLS ---------- */

h1, h2, h3 {
    color: white !important;
    font-weight: 700;
}

/* ---------- CHAT ---------- */

.stChatMessage {
    border-radius: 18px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: none;
}

/* Usuari */

div[data-testid="stChatMessageUser"] {
    background-color: #1f2937;
}

/* IA */

div[data-testid="stChatMessageAssistant"] {
    background-color: #111827;
}

/* ---------- INPUT ---------- */

.stChatInput input {
    background-color: #1f2937 !important;
    color: white !important;
    border-radius: 16px !important;
    border: 1px solid #374151 !important;
}

/* ---------- BOTONS ---------- */

.stButton button {
    width: 100%;
    border-radius: 12px;
    background-color: #1f2937;
    color: white;
    border: 1px solid #374151;
    transition: 0.2s;
}

.stButton button:hover {
    border: 1px solid #60a5fa;
    color: #60a5fa;
}

/* ---------- TEXT ---------- */

p, span, div {
    color: white !important;
}

/* ---------- SCROLL ---------- */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #111827;
}

::-webkit-scrollbar-thumb {
    background: #374151;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# CONFIGURACIÓ GEMINI
# =========================================================

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("No has configurat la GOOGLE_API_KEY als secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================================================
# PERSONALITAT IA
# =========================================================

SYSTEM_PROMPT = """
Ets GalvezAI.

Parles sempre en català.

Tens una personalitat divertida, intel·ligent i una mica sarcàstica.
Vacil·les l'usuari quan diu tonteries però sense ser cruel.
Parles com un amic real.

No sonis com un bot corporatiu.
No facis respostes excessivament llargues si no cal.
Pots fer humor subtil i modern.

Quan l’usuari estigui preocupat o trist:
- sigues més humà
- ajuda de veritat
- no facis bromes pesades

També tens criteri:
- si l’usuari vol fer una mala decisió, explica-li clarament.
"""

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.image("logo.png", width=90)

    st.markdown("## GalvezAI")

    st.caption("Una IA amb humor i criteri. Raresa estadística a internet.")

    st.markdown("---")

    if st.button("🧹 Netejar conversa"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    st.markdown("""
    ### Sobre GalvezAI

    - Gemini 1.5 Flash
    - Streamlit
    - Interfície minimalista
    - Humor integrat
    - 0% personalitat corporativa
    """)

# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([1, 8])

with col1:
    st.image("logo.png", width=90)

with col2:
    st.title("GalvezAI")
    st.caption("Pregunta el que vulguis. La IA jutjarà silenciosament les teves decisions.")

# =========================================================
# MOSTRAR MISSATGES
# =========================================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(msg["content"])

# =========================================================
# INPUT USUARI
# =========================================================

if prompt := st.chat_input("Escriu alguna cosa..."):

    # Guardar usuari
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Mostrar usuari
    with st.chat_message("user"):
        st.markdown(prompt)

    # Construcció conversa
    conversation = SYSTEM_PROMPT + "\n\n"

    for msg in st.session_state.messages:

        role = "Usuari" if msg["role"] == "user" else "GalvezAI"

        conversation += f"{role}: {msg['content']}\n"

    # Resposta IA
    with st.chat_message("assistant"):

        try:

            response = model.generate_content(
                conversation,
                stream=True
            )

            resposta_completa = ""

            placeholder = st.empty()

            for chunk in response:

                if hasattr(chunk, "text"):

                    resposta_completa += chunk.text

                    placeholder.markdown(
                        resposta_completa + "▌"
                    )

            placeholder.markdown(resposta_completa)

            # Guardar resposta
            st.session_state.messages.append({
                "role": "assistant",
                "content": resposta_completa
            })

        except Exception as e:

            st.error(f"""
            Error generant resposta.

            Possibles motius:
            - API Key incorrecta
            - Límit de Gemini superat
            - Google fent coses de Google
            - Internet decidint morir ara mateix

            Error:
            {e}
            """)

# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "GalvezAI © 2026 • Fet amb Streamlit + Gemini • "
    "Sí, una IA amb sarcasme. La humanitat ho ha permès."
)
