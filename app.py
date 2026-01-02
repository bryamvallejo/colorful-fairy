import streamlit as st
import google.generativeai as genai
import os
import json
from datetime import datetime
import time

# --- CONFIGURACIÓN DE API ---
# Asegúrate de tener tu GOOGLE_API_KEY en los Secrets de Streamlit
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key, transport='rest')

# USAMOS LOS ALIASES INTELIGENTES
# Estos nombres le dicen al SDK: "Busca la versión que funcione (v1 o v1beta)"
NOMBRE_HADA = 'gemini-flash-latest' 
NOMBRE_ARTISTA = 'imagen-4.0-fast-generate-001' # Este modelo es el estándar para imágenes en 2026

# --- INICIALIZACIÓN DE MODELOS ---
try:
    # Inicializamos usando los nombres que el servidor mapea automáticamente
    model_hada = genai.GenerativeModel(model_name=NOMBRE_HADA)
    model_artista = genai.GenerativeModel(model_name=NOMBRE_ARTISTA)
except Exception as e:
    st.error(f"Error al conectar con los modelos: {e}")
    st.stop()

# --- FUNCIONES ---

def guardar_log(prompt, estado):
    log_entry = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "prompt": prompt, "estado": estado}
    if not os.path.exists("historial.json"):
        with open("historial.json", "w") as f: json.dump([], f)
    with open("historial.json", "r+") as f:
        data = json.load(f)
        data.append(log_entry)
        f.seek(0)
        json.dump(data, f, indent=4)

def validar_hada_de_colores(prompt):
    system_prompt = (
        "Eres el 'Hada de los Colores'. Si el mensaje es seguro para una niña, responde solo 'APROBADO'. "
        "Si es triste o feo, responde con un consejo dulce."
    )
    response = model_hada.generate_content(f"{system_prompt}\n\nUsuario: {prompt}")
    return response.text

def generar_imagen_magica(prompt):
# Enriquecemos el prompt para calidad artística
    prompt_final = f"GENERATE_IMAGE: Children's book illustration style, vibrant colors, whimsical: {prompt}"
    
    # Manejo de cuota (429) con reintento automático
    for intento in range(2):
        try:
            # En 2026, Gemini 2.0 Flash genera la imagen directamente
            response = model_artista.generate_content(prompt_final)
            return response.candidates[0].content.parts[0].inline_data.data
        except Exception as e:
            if "429" in str(e):
                time.sleep(15) # Espera obligatoria por cuota
                continue
            raise e

# --- INTERFAZ ---
st.set_page_config(page_title="Mundo Mágico 2026", page_icon="🎨")

st.markdown("""
    <style>
    .stApp { background-color: #fdf2f8; }
    h1 { color: #db2777; font-family: 'Comic Sans MS', cursive; }
    .stButton>button { background-color: #db2777; color: white; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

if "view" not in st.session_state: st.session_state.view = "nena"

if st.session_state.view == "nena":
    st.title("🎨 Mi Estudio de Arte Mágico")
    prompt = st.text_input("¿Qué quieres que el Hada dibuje hoy?", placeholder="Un gato en la luna...")

    if st.button("✨ ¡Crear Magia! ✨"):
        if prompt:
            # res_hada = validar_hada_de_colores(prompt)
            # if "APROBADO" in res_hada.upper():
            with st.spinner("🍌 Nano Banana está pintando para ti..."):
                try:
                    img_data = generar_imagen_magica(prompt)
                    st.image(img_data, caption="¡Mira tu dibujo!")
                    st.balloons()
                    guardar_log(prompt, "Aprobado")
                except Exception as e:
                    # Aquí capturamos el error REAL (429, 404, 500, etc.)
                    st.error(f"🔍 ERROR DETECTADO: {type(e).__name__}")
                    st.error(f"📝 DETALLE TÉCNICO: {str(e)}")
                    
                    # Si es un error de cuota, lo explicamos sencillo
                    if "429" in str(e):
                        st.warning("Es un error de CUOTA (429). Google pide esperar unos segundos.")
            # else:
            #    st.warning(res_hada)
            #    guardar_log(prompt, "Bloqueado")

elif st.session_state.view == "padre":
    st.title("🛡️ Panel Parental")
    if st.text_input("Contraseña:", type="password") == os.getenv("PARENT_PASSWORD", "magia2025"):
        if os.path.exists("historial.json"):
            with open("historial.json", "r") as f:
                logs = json.load(f)
                for l in reversed(logs):
                    st.write(f"**{l['fecha']}** - {l['prompt']} ({l['estado']})")

st.sidebar.markdown("---")
if st.sidebar.button("Ir a Vista Padres"): st.session_state.view = "padre"
if st.sidebar.button("Volver a Galería"): st.session_state.view = "nena"