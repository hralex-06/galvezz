import streamlit as st
import google.generativeai as genai
import time

# --- CONFIGURACIÓ DE LA PÀGINA I ESTIL ---
st.set_page_config(page_title="GalvezzAI Pro", page_icon="🤖", layout="centered")

# CSS per tunejar la interfície
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #30363d; }
    .stTitle { color: #00ffcc; font-family: 'Courier New', Courier, monospace; text-shadow: 2px 2px #000; }
    div[data-testid="stStatusWidget"] { visibility: hidden; }
    .stActionButton { display: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 GalvezzAI")
st.markdown("---")

# 1. CLAU DE SEGURETAT
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clau API a Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. PERSONALITAT MILLORADA (El teu millor amic vacil·la)
PERSONALITAT = (
    "Actua com el millor amic de l'Alex. Sigues proper, intel·ligent i amb humor. "
    "Vacil·la'm quan digui ximpleries, però sense mala llet. "
    "Ajuda'm a estudiar i preparar exàmens pensant en estratègies de professors. "
    "Si et demano una imatge, genera-la amb la teva eina interna. "
    "Ets un company real, amb criteri i suport."
)

# 3. DETECTAR MODEL
if "model_actiu" not in st.session_state:
    st.session_state.model_actiu = 'gemini-1.5-flash'

# Inicialitzem el model
model = genai.GenerativeModel(
    model_name=st.session_state.model_actiu,
    system_instruction=PERSONALITAT
)

# 4. GESTIÓ DE L'HISTORIAL
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if "image" in msg:
            st.image(msg["image"])
        st.write(msg["content"])

# 5. XAT I IMATGES
if prompt := st.chat_input("Digues quelcom..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            # Petita pausa per no cremar la quota de Google (Anti-429)
            time.sleep(1) 
            
            # Historial ultra-curt per estalviar quota
            history = []
            for m in st.session_state.messages[-4:-1]: # Només últims 3 missatges
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            
            # Generar resposta
            with st.spinner("Pensant una resposta..."):
                response = chat.send_message(prompt)
            
            # Mostrar text
            st.write(response.text)
            
            # LOGICA D'IMATGES: Si la resposta conté una imatge
            image_found = None
            if hasattr(response, 'candidates'):
                for candidate in response.candidates:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data'):
                            image_found = part.inline_data.data
                            st.image(image_found, caption="Aquí tens el teu dibuix.")

            # Guardar a l'historial
            new_msg = {"role": "assistant", "content": response.text}
            if image_found:
                new_msg["image"] = image_found
            st.session_state.messages.append(new_msg)

        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ M'has saturat! torna a provar en 15 segons.")
            else:
                st.error(f"Error raro: {e}")

st.sidebar.caption(f"🚀 Versió Pro | {st.session_state.model_actiu}")
