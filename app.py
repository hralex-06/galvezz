import streamlit as st
import google.generativeai as genai
import uuid
import time

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="GalvezzAI", page_icon="🤖", layout="wide")

# --- CSS ULTRA-LLEGIBLE (TEXT BLANC PUR) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(145deg, #0f0c29, #1a1a2e); color: white !important; }
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #333; }
    .stChatMessage { border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.1); }
    div[data-testid="stChatMessageUser"] { background-color: rgba(0, 255, 204, 0.1) !important; border-right: 4px solid #00ffcc; }
    div[data-testid="stChatMessageAssistant"] { background-color: rgba(88, 166, 255, 0.1) !important; border-left: 4px solid #58a6ff; }
    p, span, div, label, .stMarkdown { color: #ffffff !important; font-size: 1.1rem; }
    h1 { color: #00ffcc !important; font-weight: 800; }
    .stChatInput textarea { color: white !important; background-color: #1a1d23 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIGURACIÓ AI AMB AUTO-DETECCIÓ ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Posa la clau a Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

def get_working_model():
    # Intentem trobar un model que funcioni de veritat
    intentos = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.0-pro']
    for m_name in intentos:
        try:
            m = genai.GenerativeModel(model_name=m_name)
            # Fem una mini prova silenciosa
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m_name
        except:
            continue
    return 'gemini-pro' # Últim recurs

if "active_model_name" not in st.session_state:
    st.session_state.active_model_name = get_working_model()

model = genai.GenerativeModel(st.session_state.active_model_name)

# --- 2. PERSONALITAT I SESSIONS ---
PERSONALITAT = (
    "Actua com el millor amic de l'Alex. Sigues proper, intel·ligent i amb humor. "
    "Vacil·la’m quan digui ximpleries, però sense mala llet. Ajuda’m a prendre bones decisions "
    "i a estudiar estratègicament. Respon sempre en català."
)

if "chats" not in st.session_state:
    st.session_state.chats = {}
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🤖 GalvezzAI")
    st.caption(f"Motor actiu: {st.session_state.active_model_name}")
    
    if st.button("➕ Nova Conversa"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"titol": "Xat nou", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
    
    st.markdown("---")
    for chat_id in list(st.session_state.chats.keys()):
        cols = st.columns([0.8, 0.2])
        with cols[0]:
            if st.button(st.session_state.chats[chat_id]["titol"][:18], key=f"s_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with cols[1]:
            if st.button("🗑️", key=f"d_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.current_chat_id = None
                st.rerun()

# --- 4. XAT ---
if st.session_state.current_chat_id:
    chat_data = st.session_state.chats[st.session_state.current_chat_id]
    st.title(chat_data["titol"])
    
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Digues quelcom, crack..."):
        chat_data["messages"].append({"role": "user", "content": prompt})
        if len(chat_data["messages"]) <= 1:
            chat_data["titol"] = prompt[:20]
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            try:
                # Enviem el context net per evitar el 429
                response = model.generate_content(f"{PERSONALITAT}\n\nAlex diu: {prompt}")
                st.markdown(response.text)
                chat_data["messages"].append({"role": "assistant", "content": response.text})
            except Exception as e:
                if "429" in str(e):
                    st.error("Google diu que vas massa ràpid! Espera 10 segons.")
                else:
                    st.error("S'ha perdut la connexió. Prova de crear un Xat Nou.")
else:
    st.info("👋 Ey! Crea un xat nou per començar.")
