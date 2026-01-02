import streamlit as st
import google.generativeai as genai
from google.generativeai import ImageGenerationModel
import os
import json
import base64
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD ---
# Cambia esto por tu contraseña preferida para el panel de padres
PASSWORD_PADRE = os.getenv("PARENT_PASSWORD", "magia2025") 

# Configuración del API
try:
    # Hada de los Colores (Texto)
    model_hada = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # Artista (Nano Banana / Imagen 3)
    # Lo llamamos directamente desde genai para evitar el ImportError
    model_artista = genai.ImageGenerationModel("imagen-3.0-generate-001")
except Exception as e:
    st.error("Error al despertar a los modelos mágicos.")
    st.stop()

# Filtros de seguridad de nivel de sistema (Google)
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]

# Inicialización de modelos
# Gemini Flash para el filtro de texto (Hada de los Colores)
# model_hada = genai.GenerativeModel('gemini-1.5-flash')
# Imagen 3 para la generación de imágenes
# model_imagen = genai.GenerativeModel('gemini-1.5-flash') # El SDK usa el mismo punto para llamar a Imagen 3

# Cambia estas líneas en tu app.py
# model_hada = genai.GenerativeModel('models/gemini-1.5-flash')
# model_artista = ImageGenerationModel("imagen-3.0-generate-001")
# --- FUNCIONES INTERNAS ---

def guardar_log(prompt, estado, imagen_b64=None):
    log_entry = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "estado": estado,
        "imagen": imagen_b64
    }
    if not os.path.exists("historial.json"):
        with open("historial.json", "w") as f: json.dump([], f)
    
    with open("historial.json", "r+") as f:
        data = json.load(f)
        data.append(log_entry)
        f.seek(0)
        json.dump(data, f, indent=4)

def validar_hada_de_colores(prompt):
    system_prompt = (
        "Eres el 'Hada de los Colores', una asistente mágica para una niña de 7 años. "
        "Tu misión es cuidar que su mundo sea siempre brillante y seguro. "
        "Si el mensaje es seguro, responde solo 'APROBADO'. "
        "Si contiene algo triste o violento, responde con una alternativa dulce: "
        "'¡Oh, esa idea suena oscura! ¿Por qué no mejor pintamos un unicornio?'"
    )
    response = model_hada.generate_content(f"{system_prompt}\n\nUsuario: {prompt}")
    return response.text

def generar_imagen_magica(prompt_niña):
    # Enriquecemos el prompt
    prompt_final = f"Children's book illustration, vibrant pastel colors, magical and safe for kids: {prompt_niña}"
    
    # Generar
    response = model_artista.generate_images(
        prompt=prompt_final,
        number_of_images=1,
    )
    
    # Retornar la imagen (formato PIL)
    return response.images[0].image

# --- INTERFAZ ---

st.set_page_config(page_title="Mundo Mágico de Imágenes", page_icon="🎨")

# CSS para que sea vea hermoso
st.markdown("""
    <style>
    .stApp { background-color: #fdf2f8; }
    h1 { color: #db2777; font-family: 'Comic Sans MS'; }
    .stButton>button { background-color: #db2777; color: white; border-radius: 20px; border: none; }
    </style>
    """, unsafe_allow_html=True)

# Lógica de navegación simple
if "view" not in st.session_state: st.session_state.view = "nena"

# --- VISTA DE LA NIÑA ---
if st.session_state.view == "nena":
    st.title("🎨 Mi Estudio de Arte Mágico")
    prompt = st.text_input("¿Qué quieres que dibuje hoy?", placeholder="Ej. Un perrito con alas de mariposa")

    if st.button("✨ ¡Crear Magia! ✨"):
        if prompt:
            # 1. El Hada valida el texto
            res_hada = validar_hada_de_colores(prompt)
            
            if "APROBADO" in res_hada.upper():
                with st.spinner("🍌 Nano Banana está pintando..."):
                    try:
                        # 2. Nano Banana crea la imagen
                        imagen_resultado = generar_imagen_magica(prompt)
                        
                        # 3. Mostrar la imagen (el objeto imagen de Google es compatible con st.image)
                        st.image(imagen_resultado._pil_image, caption="¡Tu dibujo mágico!")
                        st.balloons()
                        
                        # Guardar en log (opcional)
                        guardar_log(prompt, "Aprobado")
                        
                    except Exception as e:
                        st.error("¡Ups! Se acabó la purpurina técnica.")
                        st.caption(f"Error: {e}")
            else:
                st.warning(res_hada)
        else:
            st.info("Escribe algo para empezar la magia.")

# --- VISTA DEL PADRE ---
elif st.session_state.view == "padre":
    st.title("🛡️ Panel de Control Parental")
    pass_input = st.text_input("Contraseña secreta:", type="password")
    
    if pass_input == PASSWORD_PADRE:
        st.write("### Historial de Creaciones")
        if os.path.exists("historial.json"):
            with open("historial.json", "r") as f:
                logs = json.load(f)
                for l in reversed(logs):
                    st.write(f"**[{l['fecha']}]** - {l['prompt']} | **Estado:** {l['estado']}")
        else:
            st.info("Aún no hay dibujos registrados.")
    elif pass_input:
        st.error("Contraseña incorrecta")

# Botones de navegación (ocultos abajo)
st.sidebar.markdown("---")
if st.sidebar.button("Ir a Vista Padres"): st.session_state.view = "padre"
if st.sidebar.button("Volver a Galería"): st.session_state.view = "nena"