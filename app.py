import streamlit as st
import google.generativeai as genai
import uuid
import time

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="GalvezzAI", page_icon="🤖", layout="wide")

# --- CSS DEFINITIU (TEXT BLANC I COLORS VIUS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(145deg, #0f0c29, #1a1a2e); color: white !important; }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] { background-color: #050505 !important; border-right: 1px solid #333; }
    
    /* Missatges estil targeta */
    .stChatMessage { border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.1); }
    div[data-testid="stChatMessageUser"] { background-color: rgba(0, 255, 204, 0.1) !important; border-right: 4px solid #00ffcc; }
    div[data-testid="stChatMessageAssistant"] { background-color: rgba(88, 166, 255, 0.1) !important; border-left: 4px solid #58a6ff; }
    
    /* Lletres Blanques i llegibles */
    p, span, div, label, .stMarkdown { color: #ffffff !important; font-size: 1.1rem; }
    h1 { color: #00ffcc !important; font-weight: 800; text-shadow: 0px 0px 10px rgba(0,255,204,0.3); }
    
    /* Botons sidebar */
    .stButton>button { width: 100%; border-radius: 8px; background-color: #21262d; color: white; border: 1px solid #444; }
    .stButton>button:hover { border-color: #00ffcc; color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIGURACIÓ GOOGLE AI ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura la API KEY als Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Intentem carregar el model 1.5-flash, si no, el Pro
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# --- 2. GESTIÓ D'HISTORIAL (SESSIONS) ---
if "chats" not in st.session_state:
    st.session_state.chats = {} # {id: {"titol": str, "messages": []}}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 3. BARRA LATERAL AMB SUBMENÚ D'ELIMINACIÓ ---
with st.sidebar:
    st.title("🤖 GalvezzAI")
    
    if st.button("➕ Nova Conversa"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"titol": "Xat nou", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
    
    st.markdown("---")
    st.subheader("Les teves xerrades")
    
    for chat_id in list(st.session_state.chats.keys()):
        col_t, col_b = st.columns([0.8, 0.2])
        with col_t:
            if st.button(st.session_state.chats[chat_id]["titol"][:18], key=f"sel_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        with col_b:
            if st.button("🗑️", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.current_chat_id = None
                st.rerun()

# --- 4. LÒGICA DE XAT I PERSONALITAT ---
PERSONALITAT = (
    "Actua com el meu millor amic de tota la vida. Sigues proper, intel·ligent i amb humor. "
    "Vacil·la’m quan digui ximpleries, però sense mala llet. Ajuda’m a prendre bones decisions, "
    "atura’m si veus que puc cometre un error greu. Ajuda’m a estudiar estratègicament. "
    "Respon sempre en català."
)

if st.session_state.current_chat_id:
    chat_data = st.session_state.chats[st.session_state.current_chat_id]
    st.title(chat_data["titol"])
    
    # Mostrar missatges guardats
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada de text
    if prompt := st.chat_input("Digues quelcom, Alex..."):
        # Guardem usuari
        chat_data["messages"].append({"role": "user", "content": prompt})
        if len(chat_data["messages"]) <= 1:
            chat_data["titol"] = prompt[:20]
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            try:
                # Per evitar el 429, enviem la personalitat + l'últim missatge
                # Si vols que recordi més, podem posar els últims 2, però risc de saturació.
                time.sleep(0.5) # Pausa de seguretat
                response = model.generate_content(f"{PERSONALITAT}\n\nAlex diu: {prompt}")
                
                resposta = response.text
                st.markdown(resposta)
                chat_data["messages"].append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error("Google s'ha atabalat. Espera 10 segons.")
else:
    st.info("👋 ey! Tira cap a la barra lateral i crea un xat nou per començar a xerrar.")
