import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="GalvezzAI", page_icon="🤖")
st.title("🤖 GalvezzAI")

# 1. Configuració de la clau
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura GOOGLE_API_KEY a .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. DETECTIU DE MODELS: Busquem quin model tens realment
if "model_name" not in st.session_state:
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Triem el primer que sigui 'flash' o 'pro', i si no, el primer de la llista
        flash_models = [m for m in models if 'flash' in m]
        st.session_state.model_name = flash_models[0] if flash_models else models[0]
    except Exception as e:
        st.error(f"No s'han pogut llistar els models: {e}")
        st.stop()

model = genai.GenerativeModel(st.session_state.model_name)
st.caption(f"Connectat via: {st.session_state.model_name}")

# 3. Historial
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 4. Xat
if prompt := st.chat_input("Escriu aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # Adaptar historial
            history = []
            for m in st.session_state.messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error en la resposta: {e}")
