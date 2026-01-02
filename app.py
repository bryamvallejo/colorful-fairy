import streamlit as st
import google.generativeai as genai
import os
import json
from datetime import datetime
import time
# --- NUEVA LIBRERÍA PARA IMAGEN 4.0 ---
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

# --- CONFIGURACIÓN DE API ---
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
project_id = st.secrets.get("GOOGLE_PROJECT_ID") # Necesitas tu ID de proyecto de Google Cloud

# Configuración para Gemini (Hada)
genai.configure(api_key=api_key, transport='rest')

# Configuración para Imagen (Artista) vía Vertex AI
vertexai.init(project=project_id, location="us-central1")

NOMBRE_HADA = 'gemini-1.5-flash' 
NOMBRE_ARTISTA = 'imagen-4.0-fast-generate-001' 

# --- INICIALIZACIÓN DE MODELOS ---
try:
    # El Hada sigue usando la API de GenerativeAI
    model_hada = genai.GenerativeModel(model_name=NOMBRE_HADA)
    
    # El Artista ahora usa el SDK de Vertex AI
    model_artista = ImageGenerationModel.from_pretrained(NOMBRE_ARTISTA)
except Exception as e:
    st.error(f"Error al conectar con los modelos: {e}")
    st.stop()

# --- FUNCIONES ---

def guardar_log(prompt, estado):
    log_entry = {"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "prompt": prompt, "estado": estado}
    if not os.path.exists("historial.json"):
        with open("historial.json", "w") as f: json.dump([], f)
    with open("historial.json", "r+") as f:
        try:
            data = json.load(f)
        except:
            data = []
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
    prompt_final = f"Children's book illustration style, vibrant colors, whimsical, high quality: {prompt}"
    
    for intento in range(2):
        try:
            # Cambio de método: Vertex AI usa 'generate_images'
            # No se usa generate_content para modelos de imagen
            response = model_artista.generate_images(
                prompt=prompt_final,
                number_of_images=1,
                aspect_ratio="1:1"
            )
            # Retornamos los bytes directamente
            return response[0]._image_bytes
        except Exception as e:
            if "429" in str(e):
                st.info("El Hada está descansando un momento (Cuota)... reintentando.")
                time.sleep(10)
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
            # Primero validamos con el Hada
            res_hada = validar_hada_de_colores(prompt)
            
            if "APROBADO" in res_hada.upper():
                with st.spinner("🎨 Mi pincel mágico está trabajando..."):
                    try:
                        img_data = generar_imagen_magica(prompt)
                        st.image(img_data, caption="¡Mira tu dibujo!")
                        st.balloons()
                        guardar_log(prompt, "Aprobado")
                    except Exception as e:
                        st.error(f"📝 ERROR TÉCNICO: {str(e)}")
            else:
                st.warning(res_hada)
                guardar_log(prompt, f"Bloqueado: {res_hada}")

elif st.session_state.view == "padre":
    st.title("🛡️ Panel Parental")
    pass_input = st.text_input("Contraseña:", type="password")
    if pass_input == "magia2025":
        if os.path.exists("historial.json"):
            with open("historial.json", "r") as f:
                logs = json.load(f)
                for l in reversed(logs):
                    color = "🟢" if "Aprobado" in l['estado'] else "🔴"
                    st.write(f"{color} **{l['fecha']}**: {l['prompt']}")

st.sidebar.markdown("---")
if st.sidebar.button("Ir a Vista Padres"): st.session_state.view = "padre"
if st.sidebar.button("Volver a Galería"): st.session_state.view = "nena"