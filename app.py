import streamlit as st
import google.generativeai as genai
import os
import uuid

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
html, body, [class*="css"] { font-family: "Segoe UI", sans-serif; }
.stApp { background-color: #ffffff; color: #111827; }
section[data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e5e7eb; }
h1, h2, h3 { color: #111827 !important; font-weight: 700; }
p, span, div, label { color: #111827 !important; }
.stChatMessage { border-radius: 18px; padding: 1rem; margin-bottom: 1rem; border: none; }
div[data-testid="stChatMessageUser"] { background-color: #f3f4f6; }
div[data-testid="stChatMessageAssistant"] { background-color: #ffffff; border: 1px solid #e5e7eb; }
.stChatInput input { background-color: #ffffff !important; color: #111827 !important; border-radius: 18px !important; border: 1px solid #d1d5db !important; }
.stButton button { width: 100%; border-radius: 14px; background-color: white; color: #111827; border: 1px solid #d1d5db; transition: 0.2s; }
.stButton button:hover { border: 1px solid #2563eb; color: #2563eb; }
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: #f3f4f6; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE GEMINI CONFIG
# =========================================================
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("GOOGLE_API_KEY is missing in Streamlit secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Cambiem a la versió Pro estable per saltar-nos el bloqueig del Flash
MODEL_NAME = "chat-bison-001"

# =========================================================
# AI PERSONALITY
# =========================================================
SYSTEM_PROMPT = """
Actua com el meu millor amic de tota la vida.
- Sigues proper, intel·ligent i amb humor. Vacil·la’m quan digui ximpleries, però sense mala llet.
- Ajuda’m a prendre bones decisions i atura’m si veus que puc cometre un error greu, explicant per què i les conseqüències.
- Ajuda’m a estudiar i preparar exàmens pensant en els professors i estratègies, sense fer exercicis fàcils ni absurd.
- Permet-me explicar situacions personals; corregeix-me quan calgui, anima’m i reconeix els meus progressos.
- Sigues un company real, amb criteri, humor i suport.
Parla sempre en català natural, de forma moderna, sense sonar robòtic ni corporatiu.
"""

# =========================================================
# SESSION STATE
# =========================================================
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)

    st.markdown("## GalvezAI")
    st.caption("Un amic amb criteri, humor i suport.")
    st.markdown("---")

    if st.button("➕ Nova conversa"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"titol": "Xat nou", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("### Les teves converses")
    
    for chat_id in list(st.session_state.chats.keys()):
        col_titol, col_boto = st.columns([0.8, 0.2])
        
        with col_titol:
            if st.button(st.session_state.chats[chat_id]["titol"][:18], key=f"select_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()
                
        with col_boto:
            if st.button("🗑️", key=f"delete_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.current_chat_id = None
                st.rerun()

    st.markdown("---")
    st.caption("Model actiu: " + MODEL_NAME)

# =========================================================
# HEADER PRINCIPAL
# =========================================================
col1, col2 = st.columns([1, 8])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)
with col2:
    st.title("GalvezAI")
    st.caption("Pregunta el que vulguis. El teu millor amic virtual no et jutjarà (gaire).")

# =========================================================
# ZONA DE XAT
# =========================================================
if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chats:
    chat_actual = st.session_state.chats[st.session_state.current_chat_id]
    
    st.write(f"💬 *Conversa activa: {chat_actual['titol']}*")
    
    for msg in chat_actual["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Digues alguna cosa..."):
        
        chat_actual["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if len(chat_actual["messages"]) <= 1:
            chat_actual["titol"] = prompt[:20] + ("..." if len(prompt) > 20 else "")
            st.rerun()

        with st.chat_message("assistant"):
            try:
                # Inicialitzem el model net amb instruccions de sistema
                model = genai.GenerativeModel(
                    model_name=MODEL_NAME,
                    system_instruction=SYSTEM_PROMPT
                )
                
                # Passem l'historial netejant estructures incompatibles
                history_payload = []
                for msg in chat_actual["messages"][:-1]:
                    history_payload.append({
                        "role": "user" if msg["role"] == "user" else "model",
                        "parts": [msg["content"]]
                    })
                
                chat_session = model.start_chat(history=history_payload)
                response = chat_session.send_message(prompt, stream=True)

                full_response = ""
                placeholder = st.empty()

                for chunk in response:
                    if hasattr(chunk, "text"):
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)

                chat_actual["messages"].append({
                    "role": "assistant",
                    "content": full_response
                })

            except Exception as e:
                # Si hi ha un error de quota real, el capturem i t'avisem netament
                if "429" in str(e) or "quota" in str(e).lower():
                    st.error("⚠️ Google ha congelat temporalment la clau API gratuïta per excés de peticions. Espera 1 minut complet sense enviar res i torna-ho a provar.")
                else:
                    st.error(f"Error del servidor: {e}")
else:
    st.info("👋 Ei Àlex! Crea una nova conversa o selecciona'n una des de la barra lateral per començar.")

st.markdown("---")
st.caption("GalvezAI © 2026 • Creat amb Streamlit + Gemini")
