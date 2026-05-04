import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="GalvezzAI", page_icon="🤖")
st.title("🤖 GalvezzAI")

# 1. Configuració de la clau
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clau! Posa-la a Manage app > Settings > Secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Personalitat
instruccions = (
    "Ets en GalvezzAI, una IA molt intel·ligent però també molt vacil·la, sarcàstica i divertida. "
    "Parles en català col·loquial. No ets gens seriós. T'agrada fer bromes i riure't de l'usuari amb bon rotllo."
)

# 3. Carregar el model (amb fallback)
if "model_choice" not in st.session_state:
    # Provem primer el més nou, si no, el pro
    try:
        # Intentem el flash-latest que és el que sol funcionar al núvol
        m = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=instruccions)
        m.generate_content("test") # Prova ràpida
        st.session_state.model_choice = 'gemini-1.5-flash-latest'
    except:
        st.session_state.model_choice = 'gemini-pro'

model = genai.GenerativeModel(
    model_name=st.session_state.model_choice,
    system_instruction=instruccions if st.session_state.model_choice != 'gemini-pro' else None
)

st.caption(f"Actiu: {st.session_state.model_choice} | Estil: Vacil·la ✅")

# 4. Historial
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. Xat
if prompt := st.chat_input("Escriu aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # Si el model és vell (gemini-pro), li hem de passar la personalitat al prompt
            final_prompt = prompt
            if st.session_state.model_choice == 'gemini-pro':
                final_prompt = f"Recorda el teu estil vacil·la i respon en català: {prompt}"
            
            # Historial per al xat
            history = []
            for m in st.session_state.messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            response = chat.send_message(final_prompt)
            
            st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
