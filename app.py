import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="GalvezzAI", page_icon="🤖")
st.title("🤖 GalvezzAI")

# 1. Clau de seguretat
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clau API!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. Configuració del personatge vacil·la
PERSONALITAT = (
    "Ets en GalvezzAI, una IA molt intel·ligent però també molt vacil·la, sarcàstica i divertida. "
    "Parles en català col·loquial. No ets gens seriós. T'agrada fer bromes i riure't de l'usuari amb bon rotllo. "
    "Si et demanen una imatge i no pots fer-la, vacil·la'ls dient que avui no t'has posat les ulleres de dibuixar."
)

# 3. Detectar el model disponible (Per evitar el 404)
if "model_actiu" not in st.session_state:
    try:
        # Busquem quin model de text/imatge tens realment disponible al teu compte
        models_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Triem 'gemini-pro' com a base si existeix, o el primer de la llista
        if 'models/gemini-pro' in models_disponibles:
            st.session_state.model_actiu = 'models/gemini-pro'
        else:
            st.session_state.model_actiu = models_disponibles[0]
    except:
        st.session_state.model_actiu = 'gemini-pro'

model = genai.GenerativeModel(st.session_state.model_actiu)
st.caption(f"Motor: {st.session_state.model_actiu} | Estil: Vacil·la actiu ✅")

# 4. Historial
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. El Xat
if prompt := st.chat_input("Escriu aquí per ser vacil·lat..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # Injectem la personalitat directament al prompt perquè no s'oblidi de vacil·lar
            prompt_amb_estil = f"{PERSONALITAT}\n\nUsuari diu: {prompt}"
            
            # Crear historial per al format Gemini
            history = []
            for m in st.session_state.messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt_amb_estil)
            
            resposta_final = response.text
            st.write(resposta_final)
            
            # Si el model ens torna dades d'imatge (multimodal)
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data'):
                        st.image(part.inline_data.data, caption="Aquí tens, no et queixis!")

            st.session_state.messages.append({"role": "assistant", "content": resposta_final})
            
        except Exception as e:
            st.error(f"Error: {e}")
