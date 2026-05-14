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

# Solució al 404: Nom net sense el prefix "models/"
MODEL_NAME = "gemini-1.5-flash"

# =========================================================
# AI PERSONALITY
# =========================================================
SYSTEM_PROMPT = """
Actua com el meu millor amic de toda la vida.
- Sigues proper, intel·ligent i amb humor. Vacil·la’m quan digui ximpleries, però sense mala llet.
- Ajuda’m a prendre bones decisions i atura’m si veus que puc cometre un error greu, explicant per què i les conseqüències.
- Ajuda’m a estudiar i preparar exàmens pensant en els professors i estratègies, sense fer exercicis fàcils ni absurd.
- Permet-me explicar situacions personals; corregeix-me quan calgui, anima’m i reconeix els meus progressos.
- Sigues un company real, amb criteri, humor i suport.
Parla sempre en català natural, de forma moderna, sense sonar robòtic ni corporatiu.
"""

# =========================================================
# SESSION STATE (HISTORIAL AMB MEMÒRIA)
# =========================================================
if "chats" not in st.session_state:
    st.session_state.chats = {}  # {chat_id: {"titol": str, "messages": []}}

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

    # Botó per iniciar una conversa nova
    if st.button("➕ Nova conversa"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"titol": "Xat nou", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("### Les teves converses")
    
    # Llista de converses seleccionables i eliminables de manera individual
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
    st.markdown("""
    ### About
    - Gemini 1.5 Flash
    - Streamlit
    - Minimal UI
    - Real Friend Mode
    """)

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
# ZONA DE XAT ACTIU
# =========================================================
if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chats:
    chat_actual = st.session_state.chats[st.session_state.current_chat_id]
    
    st.write(f"💬 *Conversa activa: {chat_actual['titol']}*")
    
    # Mostrar missatges de la memòria d'aquest xat
    for msg in chat_actual["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada de l'usuari
    if prompt := st.chat_input("Digues alguna cosa..."):
        
        # Desar i pintar el missatge de l'usuari
        chat_actual["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Actualitzar el títol del xat a la barra lateral de forma automàtica
        if len(chat_actual["messages"]) <= 1:
            chat_actual["titol"] = prompt[:20] + ("..." if len(prompt) > 20 else "")
            st.rerun()

        # Generar la resposta de la IA
        with st.chat_message("assistant"):
            try:
                # Inicialitzem el model net i hi injectem la personalitat
                model = genai.GenerativeModel(
                    model_name=MODEL_NAME,
                    system_instruction=SYSTEM_PROMPT
                )
                
                # Reconstruïm l'historial per a l'objecte chat de Gemini
                history_payload = []
                for msg in chat_actual["messages"][:-1]:  # Tot menys l'últim prompt que l'enviem ara
                    history_payload.append({
                        "role": "user" if msg["role"] == "user" else "model",
                        "parts": [msg["content"]]
                    })
                
                # Iniciem el xat oficial amb la seva memòria interna integrada
                chat_session = model.start_chat(history=history_payload)
                
                # Enviem el text i fem l'efecte d'escriptura en temps real (streaming)
                response = chat_session.send_message(prompt, stream=True)

                full_response = ""
                placeholder = st.empty()

                for chunk in response:
                    if hasattr(chunk, "text"):
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)

                # Guardem la resposta al nostre historial de la sessió
                chat_actual["messages"].append({
                    "role": "assistant",
                    "content": full_response
                })

            except Exception as e:
                st.error(f"Error generant la resposta: {e}")
else:
    st.info("👋 Ei! Crea una nova conversa o selecciona'n una des de la barra lateral per començar a parlar.")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    "GalvezAI © 2026 • Creat amb Streamlit + Gemini • Un company de veritat."
)
