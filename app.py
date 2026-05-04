import streamlit as st
import google.generativeai as genai

# CONFIGURACIÓ DE LA PÀGINA
st.set_page_config(page_title="GalvezzAI", page_icon="🤖")
st.title("🤖 GalvezzAI")

# 1. CLAU DE SEGURETAT
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Falta la clau API! Posa-la a 'Manage app > Settings > Secrets'.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. DEFINICIÓ DE LA PERSONALITAT VACIL·LA
PERSONALITAT = (
    "Ets en GalvezzAI, una IA molt intel·ligent però també molt vacil·la, sarcàstica i divertida. "
    "Parles en català col·loquial. No ets gens seriós. T'agrada fer bromes i riure't de l'usuari amb bon rotllo. "
    "Sempre respons amb ironia. Si et demanen una imatge, intenta descriure-la amb molt de sarcasme "
    "o digues que avui no t'han pagat prou per dibuixar."
)

# 3. DETECTAR EL MILLOR MODEL DISPONIBLE
if "model_actiu" not in st.session_state:
    try:
        # Busquem models que suportin generació de contingut
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Prioritat: 1.5-flash (el més ràpid i modern)
        flash_models = [m for m in models if '1.5-flash' in m]
        st.session_state.model_actiu = flash_models[0] if flash_models else models[0]
    except Exception:
        st.session_state.model_actiu = 'models/gemini-1.5-flash'

# Inicialitzem el model amb les instruccions de sistema
model = genai.GenerativeModel(
    model_name=st.session_state.model_actiu,
    system_instruction=PERSONALITAT
)

st.caption(f"Motor: {st.session_state.model_actiu} | Estil: Vacil·la actiu ✅")

# 4. GESTIÓ DE L'HISTORIAL
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar missatges previs
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 5. LÒGICA DEL XAT
if prompt := st.chat_input("Escriu aquí per ser vacil·lat..."):
    # Guardem i mostrem el missatge de l'usuari
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # Preparem l'historial (només els últims 6 missatges per no saturar la quota 429)
            history = []
            for m in st.session_state.messages[-7:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                history.append({"role": role, "parts": [m["content"]]})
            
            # Iniciem xat i enviem missatge
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            
            resposta_text = response.text
            st.write(resposta_text)
            
            # Guardar la resposta
            st.session_state.messages.append({"role": "assistant", "content": resposta_text})
            
        except Exception as e:
            if "429" in str(e):
                st.error("Ep! M'has atabalat. Espera 30 segons i torna a provar-ho, que la versió gratis de Google no dóna per més!")
            else:
                st.error(f"S'ha trencat alguna cosa: {e}")
