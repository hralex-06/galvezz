import streamlit as st
import google.generativeai as genai
import uuid
import time

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="GalvezzAI", page_icon="🤖", layout="wide")

# --- CSS MODERN (FORÇANT TEXT BLANC I COLORS VIUS) ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(145deg, #0f0c29, #1a1a2e); color: white !important; }
    
    /* Barra lateral */
    section[data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #333; }
    
    /* Missatges més estilitzats */
    .stChatMessage { border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem; border: 1px solid rgba(255,255,255,0.05); }
    div[data-testid="stChatMessageUser"] { background-color: rgba(0, 255, 204, 0.05) !important; border-right: 4px solid #00ffcc; }
    div[data-testid="stChatMessageAssistant"] { background-color: rgba(88, 166, 255, 0.05) !important; border-left: 4px solid #58a6ff; }
    
    /* Forçar blanc a tot el text */
    p, span, div, label, .stMarkdown { color: #ffffff !important; font-size: 1.1rem; line-height: 1.6; }
    h1 { color: #00ffcc !important; font-weight: 800; text-shadow: 0px 0px 10px rgba(0,255,204,0.3); }
    
    /* Input xat */
    .stChatInput textarea { color: white !important; background-color: #1a1d23 !important; border: 1px solid #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIGURACIÓ GOOGLE AI ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura la teva API KEY als Secrets de Streamlit!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Configuración de generación para ahorrar cuota
generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "max_output_tokens": 800, # Respostes no massa llargues per no saturar
}

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config=generation_config
)

# --- 2. GESTIÓ DE SESSIONS ---
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- 3. SIDEBAR AMB HISTORIAL ---
with st.sidebar:
    st.title("🤖 GalvezzAI")
    
    if st.button("➕ Nova Conversa"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"titol": "Xat nou", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()
    
    st.markdown("---")
    st.subheader("Converses")
    
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

# --- 4. LÒGICA PRINCIPAL ---
PERSONALITAT = (
    "Actua com el millor amic de l'Alex. Sigues proper, intel·ligent i amb humor. "
    "Vacil·la’m quan digui ximpleries, però sense mala llet. Ajuda’m a prendre bones decisions "
    "i a estudiar estratègicament. Respon sempre en català."
)

if st.session_state.current_chat_id:
    chat_data = st.session_state.chats[st.session_state.current_chat_id]
    st.title(chat_data["titol"])
    
    # Mostrar missatges
    for msg in chat_data["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Entrada de text
    if prompt := st.chat_input("Digues quelcom, crack..."):
        chat_data["messages"].append({"role": "user", "content": prompt})
        
        # Títol automàtic
        if len(chat_data["messages"]) <= 1:
            chat_data["titol"] = prompt[:20]
            
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            try:
                # CONTEXT MINIMALISTA: Només enviem la personalitat + l'últim missatge
                # Això redueix el consum de l'API dràsticament
                full_query = f"{PERSONALITAT}\n\nAlex diu: {prompt}"
                
                # Petita pausa de seguretat per enganyar el limitador
                time.sleep(0.5) 
                
                response = model.generate_content(full_query)
                
                text_resposta = response.text
                st.markdown(text_resposta)
                chat_data["messages"].append({"role": "assistant", "content": text_resposta})
                
            except Exception as e:
                if "429" in str(e):
                    st.error("⚠️ Massa ràpid! Google s'ha atabalat. Espera 10 segons.")
                else:
                    st.error(f"S'ha desconnectat: {e}")
else:
    st.info("👋 Ei! Crea un xat nou a la barra lateral per començar.")
