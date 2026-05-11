import streamlit as st
import google.generativeai as genai
import time

# --- ESTIL ---
st.set_page_config(page_title="GalvezzAI", page_icon="🤖")
st.markdown("<style>.stApp { background-color: #0e1117; color: white !important; } p, span, div { color: white !important; }</style>", unsafe_allow_html=True)
st.title("🤖 GalvezzAI")

# 1. API KEY
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Posa la clau API als Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. SELECCIÓ DE MODEL RESISTENT
# Usem el 'gemini-1.5-flash' o el 'gemini-pro' com a fallback directe
MODEL_NAME = 'gemini-1.5-flash' 

# 3. PERSONALITAT (Injectada a cada missatge per no perdre context)
PERSONALITAT = "Ets en GalvezzAI, millor amic de l'Alex. Sigues proper, intel·ligent i amb humor. Vacil·la’m quan digui ximpleries. Respon sempre en català."

# 4. MISSATGES
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. LÒGICA DE XAT
if prompt := st.chat_input("Digues quelcom..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        try:
            # Creem el model de zero en cada petició per evitar sessions corruptes
            model = genai.GenerativeModel(MODEL_NAME)
            
            # Petita pausa d'un segon per no saturar Google
            time.sleep(1)
            
            response = model.generate_content(f"{PERSONALITAT}\n\nAlex diu: {prompt}")
            
            resposta_final = response.text
            st.write(resposta_final)
            st.session_state.messages.append({"role": "assistant", "content": resposta_final})
            
        except Exception as e:
            # Si el Flash falla, provem el Pro automàticament
            try:
                model_alt = genai.GenerativeModel('gemini-pro')
                response = model_alt.generate_content(f"{PERSONALITAT}\n\nAlex diu: {prompt}")
                st.write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error("Google està totalment saturat ara mateix. Espera un parell de minuts.")
