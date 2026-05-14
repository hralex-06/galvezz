import streamlit as st
import google.generativeai as genai
import os
import uuid

# Configura la pàgina de l'aplicació
st.set_page_config(page_title="GalvezAI", page_icon="logo.png", layout="wide")

# Estils bàsics per evitar pantalles fosques estranyes
st.markdown("""
<style>
.stApp { background-color: #ffffff; color: #111827; }
section[data-testid="stSidebar"] { background-color: #f8fafc; border-right: 1px solid #e5e7eb; }
p, span, div, label, h1, h2, h3 { color: #111827 !important; }
.stChatMessage { border-radius: 18px; padding: 1rem; margin-bottom: 1rem; }
div[data-testid="stChatMessageUser"] { background-color: #f3f4f6; }
div[data-testid="stChatMessageAssistant"] { background-color: #ffffff; border: 1px solid #e5e7eb; }
</style>
""", unsafe_allow_html=True)

# Comprovació de la Clau API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la GOOGLE_API_KEY als Secrets de Streamlit.")
    st.stop()

# Configura directament la llibreria oficial
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Definim el model per a la nova llibreria actualitzada
MODEL_NAME = "gemini-1.5-flash"

SYSTEM_PROMPT = """
Actua com el meu millor amic de tota la vida. Sigues proper, intel·ligent i amb humor. 
Vacil·la’m quan digui ximpleries, dona'm suport i anima'm. Parla sempre en català natural i informal.
"""

# Inicialització del sistema de converses
if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Barra lateral
with st.sidebar:
    st.markdown("## GalvezAI")
    st.caption("Un amic amb criteri, humor i suport.")
    st.markdown("---")
    
    if st.button("➕ Nova conversa"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"titol": "Xat nou", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    for chat_id in list(st.session_state.chats.keys()):
        col_t, col_b = st.columns([0.8, 0.2])
        with col_t:
            if st.button(st.session_state.chats[chat_id]["titol"][:15], key=f"sel_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with col_b:
            if st.button("🗑️", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.current_chat_id = None
                st.rerun()

st.title("🤖 GalvezAI")

# Lògica del xat actiu
if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chats:
    chat_actual = st.session_state.chats[st.session_state.current_chat_id]
    
    for msg in chat_actual["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Digues alguna cosa..."):
        chat_actual["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if len(chat_actual["messages"]) <= 1:
            chat_actual["titol"] = prompt[:15]
            st.rerun()

        with st.chat_message("assistant"):
            try:
                # Inicialitzem el model net usant l'estructura estàndard oficial
                model = genai.GenerativeModel(
                    model_name=MODEL_NAME,
                    system_instruction=SYSTEM_PROMPT
                )
                
                # Executem la generació de text directa en format llista per evitar incompatibilitats
                history_payload = []
                for msg in chat_actual["messages"][:-1]:
                    history_payload.append({
                        "role": "user" if msg["role"] == "user" else "model",
                        "parts": [msg["content"]]
                    })
                
                chat_session = model.start_chat(history=history_payload)
                response = chat_session.send_message(prompt)
                
                resposta_text = response.text
                st.markdown(resposta_text)
                
                chat_actual["messages"].append({"role": "assistant", "content": resposta_text})
                
            except Exception as e:
                st.error(f"Error connectant amb Google: {e}")
else:
    st.info("👋 Hola! Crea una nova conversa a la barra lateral per començar.")
