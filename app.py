import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓ DE PÀGINA ---
st.set_page_config(page_title="GalvezzAI", page_icon="🤖", layout="wide")

# CSS PER FORÇAR LLEGIBILITAT I COLORS
st.markdown("""
    <style>
    /* Fons i lletra general */
    .stApp { background-color: #0e1117; color: #ffffff !important; }
    
    /* Forçar text blanc a tot arreu */
    p, span, div, label { color: #ffffff !important; }
    
    /* Estil dels missatges */
    .stChatMessage { background-color: #1d222b !important; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    
    /* Títol i Sidebar */
    h1 { color: #58a6ff !important; font-weight: 800; }
    .css-1d391kg { background-color: #161b22 !important; } /* Fons sidebar */
    
    /* Input del xat */
    .stChatInput textarea { color: #ffffff !important; background-color: #21262d !important; }
    </style>
    """, unsafe_allow_html=True)

# 1. API KEY
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clau API!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. CONFIGURACIÓ MODEL
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel('gemini-1.5-flash')

PERSONALITAT = "Ets en GalvezzAI, millor amic de l'Alex. Vacil·la'l amb humor, sigues directe i parla sempre en català."

# 3. GESTIÓ HISTORIAL I SIDEBAR
if "messages" not in st.session_state:
    st.session_state.messages = []

# BARRA LATERAL
with st.sidebar:
    st.title("📚 Historial")
    if st.button("🗑️ Esborrar tot"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    # Mostrar un resum de les preguntes de l'usuari
    user_prompts = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    for i, p in enumerate(reversed(user_prompts)):
        st.caption(f"{len(user_prompts)-i}. {p[:30]}...")

# 4. AREA CENTRAL
st.title("GalvezzAI")

# Mostrar missatges
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. LÒGICA DE XAT
if prompt := st.chat_input("Digues quelcom, Alex..."):
    # Usuari
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistent
    with st.chat_message("assistant"):
        try:
            # Enviem només l'últim context per evitar el maleït 429
            response = st.session_state.model.generate_content(f"{PERSONALITAT}\nAlex diu: {prompt}")
            
            resposta_neta = response.text
            st.markdown(resposta_neta)
            st.session_state.messages.append({"role": "assistant", "content": resposta_neta})
            
        except Exception as e:
            st.error("Google està saturat. Espera 10 segons i reintenta.")
