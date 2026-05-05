import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓ DE PÀGINA I ESTIL ---
st.set_page_config(page_title="GalvezzAI", page_icon="🤖")

st.markdown("""
    <style>
    /* Interfície Minimalista */
    .stApp { background-color: #0b0e11; }
    .stChatMessage { background-color: #1a1d21; border-radius: 10px; border: none; margin-bottom: 10px; }
    .stChatInput { border-radius: 20px; }
    h1 { color: #ffffff; font-weight: 700; letter-spacing: -1px; }
    .stCaption { color: #666; }
    /* Amagar menús innecessaris */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("GalvezzAI")
st.caption("Connexió directa | Mode Fluït Activat")

# 1. API KEY
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clau API!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. CONFIGURACIÓ DEL MOTOR (Sense sobrecarregar)
# Utilitzem el 1.5-Flash que és el més estable per a respostes ràpides
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel('gemini-1.5-flash')

# Personalitat curta (com més curta, menys error 429)
PERSONALITAT = "Ets en GalvezzAI, millor amic de tothom. Sigues proper, vacil·la amb humor i ajuda en estudis. Respon sempre en l'idioma demanat i sigues directe."

# 3. HISTORIAL INTEL·LIGENT
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrem la conversa
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. LÒGICA DE XAT (OPTIMITZADA)
if prompt := st.chat_input("Escriu un missatge..."):
    # Afegim missatge usuari
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # OPTIMITZACIÓ CLAU: 
            # Només enviem els últims 2 missatges per mantenir el context sense saturar la quota.
            context_recent = st.session_state.messages[-3:-1]
            history = []
            for m in context_recent:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            # Iniciem xat amb historial mínim
            chat = st.session_state.model.start_chat(history=history)
            
            # Injectem la personalitat de forma lleugera només si és el primer missatge o cada X temps
            full_prompt = f"{PERSONALITAT}\n\nL'Alex diu: {prompt}"
            
            response = chat.send_message(full_prompt, stream=False)
            
            # Mostrar i guardar
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

        except Exception as e:
            if "429" in str(e):
                st.error("Quota temporal esgotada. Espera 10 segons.")
            else:
                st.error(f"Error de connexió. Torna-ho a provar.")
