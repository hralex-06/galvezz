import streamlit as st
import google.generativeai as genai
import os
import uuid

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="GalvezAI",
    page_icon="logo.png",
    layout="wide"
)

# =========================================================
# LIGHT MINIMAL GEMINI STYLE
# =========================================================
st.markdown("""
<style>
/* ---------- GLOBAL ---------- */
html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif;
}
.stApp {
    background-color: #ffffff;
    color: #111827;
}
/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"] {
    background-color: #f8fafc;
    border-right: 1px solid #e5e7eb;
}
/* ---------- TITLES ---------- */
h1, h2, h3 {
    color: #111827 !important;
    font-weight: 700;
}
/* ---------- TEXT ---------- */
p, span, div, label {
    color: #111827 !important;
}
/* ---------- CHAT ---------- */
.stChatMessage {
    border-radius: 18px;
    padding: 1rem;
    margin-bottom: 1rem;
    border: none;
}
/* USER MESSAGE */
div[data-testid="stChatMessageUser"] {
    background-color: #f3f4f6;
}
/* AI MESSAGE */
div[data-testid="stChatMessageAssistant"] {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
}
/* ---------- INPUT ---------- */
.stChatInput input {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-radius: 18px !important;
    border: 1px solid #d1d5db !important;
}
/* ---------- BUTTONS ---------- */
.stButton button {
    width: 100%;
    border-radius: 14px;
    background-color: white;
    color: #111827;
    border: 1px solid #d1d5db;
    transition: 0.2s;
}
.stButton button:hover {
    border: 1px solid #2563eb;
    color: #2563eb;
}
/* ---------- SCROLLBAR ---------- */
::-webkit-scrollbar { width: 10px; }
::-webkit-scrollbar-track { background: #f3f4f6; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE GEMINI CONFIG
# =========================================================
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("GOOGLE_API_KEY is missing in Streamlit secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Definim el model per defecte per conversar de forma eficient
MODEL_NAME = "models/gemini-1.5-flash"

# =========================================================
# SESSION STATE (HISTORIAL DE CONVERSES INDIVIDUALS)
# =========================================================
if "chats" not in st.session_state:
    st.session_state.chats = {}  # Format: {chat_id: {"titol": str, "messages": []}}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# =========================================================
# AI PERSONALITY (D'ACORD AMB LES TEVES DIRECTRIUS)
# =========================================================
SYSTEM_PROMPT = """
Actua com el meu millor amic de tota la vida.
– Sigues proper, intel·ligent i amb humor. Vacil·la’m quan digui ximpleries, però sense mala llet.
– Ajuda’m a prendre bones decisions i atura’m si veus que puc cometre un error greu, explicant per què i les conseqüències.
– Ajuda’m a estudiar i preparar exàmens pensant en els professors i estratègies, sans fer exercicis fàcils ni absurd.
– Permet-me explicar situacions personals; corregeix-me quan calgui, anima’m i reconeix els meus progressos.
– Sigues un company real, amb criteri, humor i suport.
Parla sempre en català natural, sense sonar robòtic ni corporatiu.
"""

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)

    st.markdown("## GalvezAI")
    st.caption("Un amic amb criteri, humor i suport.")
    st.markdown("---")

    # Botó per crear un xat completament nou
    if st.button("➕ Nova conversa"):
        new_id = str(uuid.uuid4())
        st.session_state.chats[new_id] = {"titol": "Xat nou", "messages": []}
        st.session_state.current_chat_id = new_id
        st.rerun()

    st.markdown("### Les teves converses")
    
    # Renderitzem la llista de xats individuals amb opció d'eliminar
    for chat_id in list(st.session_state.chats.keys()):
        col_titol, col_boto = st.columns([0.8, 0.2])
        
        with col_titol:
            # Si fas clic al títol, es canvia a aquesta conversa
            if st.button(st.session_state.chats[chat_id]["titol"][:18], key=f"select_{chat_id}"):
                st.session_state.current_chat_id = chat_id
                st.rerun()
                
        with col_boto:
            # Botó individual per esborrar només aquest xat
            if st.button("🗑️", key=f"delete_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.current_chat_id == chat_id:
                    st.session_state.current_chat_id = None
                st.rerun()

    st.markdown("---")
    st.markdown("""
    ### About
    - Gemini 1.5 Flash
    - Streamlit
    - Minimal UI
    - Real Friend Mode
    """)

# =========================================================
# HEADER DE LA PÀGINA PRINCIPAL
# =========================================================
col1, col2 = st.columns([1, 8])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)
with col2:
    st.title("GalvezAI")
    st.caption("Pregunta el que vulguis. El teu millor amic virtual no et jutjarà (gaire).")

# =========================================================
# ÁREA DE CONVERSA ACTIVA
# =========================================================
if st.session_state.current_chat_id and st.session_state.current_chat_id in st.session_state.chats:
    chat_actual = st.session_state.chats[st.session_state.current_chat_id]
    
    # Canviem el títol central segons la conversa activa
    st.write(f"💬 *Conversa: {chat_actual['titol']}*")
    
    # Mostrar tots els missatges previs del xat seleccionat
    for msg in chat_actual["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # =========================================================
    # ENTRADA DE TEXT DE L'USUARI
    # =========================================================
    if prompt := st.chat_input("Digues alguna cosa..."):
        
        # 1. Guardar i mostrar el missatge de l'usuari al xat actual
        chat_actual["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Canviar el títol del xat automàticament basat en la primera frase
        if len(chat_actual["messages"]) <= 1:
            chat_actual["titol"] = prompt[:20] + ("..." if len(prompt) > 20 else "")
            st.rerun()

        # 3. Preparar l'estructura formal de continguts de Gemini (Evita col·lapses)
        # Convertim la llista plana del session_state al format que demana l'SDK de Google
        contents_payload = []
        for msg in chat_actual["messages"]:
            # El format oficial és 'user' o 'model'
            api_role = "user" if msg["role"] == "user" else "model"
            contents_payload.append({"role": api_role, "parts": [msg["content"]]})

        # Generar resposta de la IA de forma segura
        with st.chat_message("assistant"):
            try:
                # Inicialitzem el model injectant les directrius del sistema a la configuració base
                model = genai.GenerativeModel(
                    model_name=MODEL_NAME,
                    system_instruction=SYSTEM_PROMPT
                )
                
                # Passem tot l'historial estructurat de cop a generate_content
                response = model.generate_content(contents_payload, stream=True)

                full_response = ""
                placeholder = st.empty()

                for chunk in response:
                    if hasattr(chunk, "text"):
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")

                placeholder.markdown(full_response)

                # Guardar la resposta final de la IA al xat actual
                chat_actual["messages"].append({
                    "role": "assistant",
                    "content": full_response
                })

            except Exception as e:
                st.error(f"Error generant la resposta: {e}")
else:
    # Missatge inicial si no hi ha cap xat seleccionat
    st.info("👋 Ei! Crea una nova conversa o selecciona'n una existent des de la barra lateral per començar.")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    "GalvezAI © 2026 • Creat amb Streamlit + Gemini • Un company de veritat."
)
