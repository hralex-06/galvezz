import streamlit as st
import google.generativeai as genai
import os

# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="GalvezAI",
    page_icon="logo.png",
    layout="wide"
)

# IMPORTANT: usa secrets o variable d'entorn
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction="""
Ets GalvezAI.

Parles sempre en el mateix idioma que l'usuari.
Ets divertit, intel·ligent i una mica sarcàstic.
Ets com un amic real.

Si l'usuari està malament, ajudes de debò.
Si fa tonteries, li dius clarament.
"""
)

# =========================
# SESSION STATE
# =========================

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# UI
# =========================

st.title("GalvezAI")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# =========================
# INPUT
# =========================

if prompt := st.chat_input("Escriu..."):

    # user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini call (AIXÒ ÉS EL CANVI IMPORTANT)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            response = st.session_state.chat.send_message(prompt, stream=True)

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    placeholder.markdown(full_response + "▌")

            placeholder.markdown(full_response)

        except Exception as e:
            full_response = "S'ha trencat. Probablement Gemini està en mode drama."
            placeholder.markdown(full_response)
            st.error(e)

    # save assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
