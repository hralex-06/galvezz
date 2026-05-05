import streamlit as st
import google.generativeai as genai
import time

# --- CONFIGURACIÓ DE LA PÀGINA ---
st.set_page_config(page_title="GalvezzAI Pro", page_icon="🤖", layout="centered")

# Estil visual
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e6edf3; }
    .stChatMessage { border-radius: 15px; border: 1px solid #30363d; background-color: #161b22; }
    h1 { color: #58a6ff; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stCaption { text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 GalvezzAI")

# 1. CLAU API
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura la clau a Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. PERSONALITAT
PERSONALITAT = (
    "Ets en GalvezzAI, el millor amic de l'Alex. Sigues proper, intel·ligent i amb humor. "
    "Vacil·la'm quan digui ximpleries, però ajuda'm de veritat en els estudis i decisions. "
    "Ets un company real. Si et demano una imatge, descriu-la detalladament perquè soc capaç de generar-la."
)

# 3. BUSCADOR DE MODELS (Anti-404)
if "model_name" not in st.session_state:
    try:
        # Llistem tots els models que el teu compte pot usar
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Busquem el 1.5-flash, si no el trobem, el 1.0-pro, i si no, el primer que hi hagi
        if any('gemini-1.5-flash' in m for m in available_models):
            st.session_state.model_name = [m for m in available_models if 'gemini-1.5-flash' in m][0]
        elif any('gemini-pro' in m for m in available_models):
            st.session_state.model_name = [m for m in available_models if 'gemini-pro' in m][0]
        else:
            st.session_state.model_name = available_models[0]
    except:
        st.session_state.model_name = 'models/gemini-pro' # Fallback clàssic

model = genai.GenerativeModel(st.session_state.model_name, system_instruction=PERSONALITAT)

st.caption(f"🚀 Conectat via: {st.session_state.model_name} | Estat")

# 4. HISTORIAL
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. XAT
if prompt := st.chat_input("Digues quelcom..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # Pausa de seguretat (Quota 429)
            time.sleep(1)
            
            # Context curt per no saturar
            history = []
            for m in st.session_state.messages[-5:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            
            with st.spinner("Escoltant..."):
                # Enviem el prompt. Si demanes imatge, Gemini 1.5 sovint la genera sola si pot
                response = chat.send_message(prompt)
            
            st.write(response.text)
            
            # Intentar mostrar imatges si el model les ha generat (format part.inline_data)
            if hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data'):
                        st.image(part.inline_data.data)

            st.session_state.messages.append({"role": "assistant", "content": response.text})

        except Exception as e:
            if "429" in str(e):
                st.warning("M'has ratllat! Espera 20 segons.")
            else:
                st.error(f"Error: {e}. Prova de reiniciar l'app.")
