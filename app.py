import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="GalvezzAI", page_icon="🤖")
st.title("🤖 GalvezzAI")

# 1. Configuració de la clau
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Configura GOOGLE_API_KEY a .streamlit/secrets.toml")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. DEFINICIÓ DE LA PERSONALITAT (Aquí és on el fem vacil·la)
instruccions_personalitat = (
    "Ets en GalvezzAI, una IA molt intel·ligent però també molt vacil·la, sarcàstica i divertida. "
    "Parles en català col·loquial. No ets gens seriós. T'agrada fer bromes, respondre amb ironia "
    "i si l'usuari et pregunta una tonteria, li has de fer saber amb humor. "
    "A vegades pots fer servir frases com 'Vatua l'olla', 'Això no t'ho creus ni tu' o 'Que t'ho has cregut?'. "
    "Sempre mantens el bon rotllo però amb un punt de superioritat robòtica graciosa."
)

# 3. Inicialitzar el model amb personalitat i capacitats d'imatge
if "model_name" not in st.session_state:
    # Intentem forçar el model 1.5 Flash que és el que millor funciona per a tot
    st.session_state.model_name = "gemini-1.5-flash"

try:
    model = genai.GenerativeModel(
        model_name=st.session_state.model_name,
        system_instruction=instruccions_personalitat # Li inflem l'ego aquí
    )
except Exception:
    # Si el 1.5 falla, anem al genèric
    model = genai.GenerativeModel(model_name="gemini-pro")

st.caption(f"Connectat via: {st.session_state.model_name} | Estil: Vacil·la actiu ✅")

# 4. Historial
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. Xat i Lògica
if prompt := st.chat_input("Escriu aquí per ser vacil·lat..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # Preparem l'historial per al xat
            history = []
            for m in st.session_state.messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            
            # Li diem que si li demanen una imatge, ho intenti fer (Imagen 3)
            # Nota: Google restringeix la generació d'imatges per API en algunes regions.
            # Si no pot, ell mateix et vacil·larà dient que no té mans.
            response = chat.send_message(prompt)
            
            # Mostrem la resposta
            st.write(response.text)
            
            # Si la resposta conté una imatge (multimodal)
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data'):
                        st.image(part.inline_data.data)

            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error en la resposta: {e}")
