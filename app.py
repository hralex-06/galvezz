import streamlit as st
import google.generativeai as genai
import uuid

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="GalvezzAI", page_icon="🤖", layout="wide")

# --- CSS PERSONALITZAT (MODERN & LLEGIBLE) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white !important; }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] { background-color: rgba(20, 20, 30, 0.8) !important; border-right: 1px solid #444; }
    
    /* Missatges */
    .stChatMessage { border-radius: 20px; padding: 20px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1); }
    div[data-testid="stChatMessageUser"] { background-color: rgba(88, 166, 255, 0.15) !important; border-left: 5px solid #58a6ff; }
    div[data-testid="stChatMessageAssistant"] { background-color: rgba(255, 255, 255, 0.05) !important; border-left: 5px solid #00ffcc; }
    
    /* Textos */
    p, span, div, label { color: #ffffff !important; font-family: 'Inter', sans-serif; font-size: 1.05rem; }
    h1 { background: -webkit-linear-gradient(#00ffcc, #58a6ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; }
    
    /* Botons sidebar */
    .stButton>button { width: 100%; border-radius: 10px; background-color: transparent; border: 1px solid #444; color: white; }
    .stButton>button:hover { border-color: #58a6ff; color: #58a6ff; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIGURACIÓ GOOGLE AI ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clau API!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. GESTIÓ D'ESTAT (SESSIONS I HISTORIAL) ---
if "chats" not in st.session_state:
    # Estructura: {id: {"titol": str, "messages": list}}
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 3. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🤖 GalvezzAI")
    
    if st.button("➕ Nou Xat"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"titol": "Conversa nova", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
    
    st.markdown("---")
    st.subheader("Historial")
    
    # Llista de xats amb opció d'eliminar
    for chat_id in list(st.session_state.chats.keys()):
        col_text, col_del = st.columns([0.8, 0.2])
        
        with col_text:
            if st.button(st.session_state.chats[chat_id]["titol"][:20], key=f"sel_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()
        
        with col_del:
            if st.button("❌", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.current_chat_id = None
                st.rerun()

# --- 4. AREA DE CONVERSA ---
PERSONALITAT = (
    "Actua com el meu millor amic de tota la vida. Sigues proper, intel·ligent i amb humor. "
    "Vacil·la’m quan digui ximpleries, però sense mala llet. Ajuda’m a prendre bones decisions, "
    "atura’m si veus errors greus i ajuda’m a estudiar estratègicament. Respon sempre en català."
)

if st.session_state.current_chat_id:
    chat_data = st.session_state.chats[st.session_state.current_chat_id]
    
    # Títol dinàmic
    st.title(chat_data["titol"])
    
    # Mostrar missatges del xat seleccionat
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input del xat
    if prompt := st.chat_input("Digues quelcom, Alex..."):
        # Guardar missatge usuari
        chat_data["messages"].append({"role": "user", "content": prompt})
        
        # Actualitzar títol si és el primer missatge
        if len(chat_data["messages"]) <= 1:
            chat_data["titol"] = prompt[:25]
            
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            try:
                # Enviem només el missatge actual + personalitat (Estalvi de quota = Adéu 429)
                response = model.generate_content(f"{PERSONALITAT}\nL'Alex diu: {prompt}")
                
                resposta = response.text
                st.markdown(resposta)
                chat_data["messages"].append({"role": "assistant", "content": resposta})
                
            except Exception as e:
                st.error("el motor de Google està saturat. Espera 5 segons.")
else:
    st.info("👋 Hola! Selecciona un xat de la barra lateral o crea'n un de nou per començar a parlar.")
