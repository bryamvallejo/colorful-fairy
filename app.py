import streamlit as st
import google.generativeai as genai
import os
import json
from datetime import datetime

# --- CONFIGURACIÓN DE SEGURIDAD Y API ---
# Se recomienda configurar GOOGLE_API_KEY en los Secrets de Streamlit
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("No se encontró la API Key de Google. Configúrala en los Secrets.")
    st.stop()

PASSWORD_PADRE = os.getenv("PARENT_PASSWORD", "magia2025") 

# --- INICIALIZACIÓN DE MODELOS DETALLADA ---
try:
    # 1. El Hada (Texto)
    model_hada = genai.GenerativeModel('models/gemini-1.5-flash')
    
    # 2. El Artista (Nano Banana / Imagen 3)
    # Intentamos cargar Nano Banana
    model_artista = genai.ImageGenerationModel("imagen-3.0-generate-001")
    
    # Prueba rápida de conexión
    st.sidebar.success("✨ ¡Modelos despertados con éxito!")
except Exception as e:
    st.error(f"❌ No pudimos despertar la magia. Error: {e}")
    st.info("Revisa si tu API Key es válida y si tienes acceso a Imagen 3 en AI Studio.")
    st.stop()
# --- FUNCIONES INTERNAS ---

def guardar_log(prompt, estado, imagen_b64=None):
    log_entry = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "estado": estado,
    }
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
        "Eres el 'Hada de los Colores', una asistente mágica para una niña de 7 años. "
        "Tu misión es cuidar que su mundo sea siempre brillante y seguro. "
        "Si el mensaje es seguro y alegre, responde solo la palabra 'APROBADO'. "
        "Si contiene algo triste, violento o no apto, responde con una alternativa dulce: "
        "'¡Oh, esa idea suena oscura! ¿Por qué no mejor pintamos un unicornio?'"
    )
    try:
        response = model_hada.generate_content(f"{system_prompt}\n\nUsuario: {prompt}")
        return response.text
    except Exception as e:
        return f"Error técnico del Hada: {e}"

def generar_imagen_magica(prompt_niña):
    # Enriquecemos el prompt para estilo libro de cuentos
    prompt_final = f"Children's book illustration, vibrant pastel colors, magical, whimsical and safe for kids, high resolution: {prompt_niña}"
    
    # Generar usando Nano Banana
    response = model_artista.generate_images(
        prompt=prompt_final,
        number_of_images=1,
    )
    
    # Retornar la imagen (formato PIL contenido en el objeto de respuesta)
    return response.images[0].image

# --- INTERFAZ ---

st.set_page_config(page_title="Mundo Mágico de Imágenes", page_icon="🎨")

# CSS para estilo infantil
st.markdown("""
    <style>
    .stApp { background-color: #fdf2f8; }
    h1 { color: #db2777; font-family: 'Comic Sans MS', cursive; }
    .stButton>button { 
        background-color: #db2777; 
        color: white; 
        border-radius: 20px; 
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

if "view" not in st.session_state: 
    st.session_state.view = "nena"

# --- VISTA DE LA NIÑA ---
if st.session_state.view == "nena":
    st.title("🎨 Mi Estudio de Arte Mágico")
    prompt_usuario = st.text_input("¿Qué quieres que dibuje hoy?", placeholder="Ej. Un perrito con alas de mariposa")

    if st.button("✨ ¡Crear Magia! ✨"):
        if prompt_usuario:
            res_hada = validar_hada_de_colores(prompt_usuario)
            
            if "APROBADO" in res_hada.upper():
                with st.spinner("🍌 Nano Banana está preparando sus pinceles..."):
                    try:
                        # Generación Real
                        img = generar_imagen_magica(prompt_usuario)
                        
                        # Mostrar resultado
                        st.image(img, caption=f"¡Tu dibujo de {prompt_usuario}!")
                        st.balloons()
                        
                        guardar_log(prompt_usuario, "Aprobado")
                    except Exception as e:
                        st.error("¡Ups! Se acabó la purpurina técnica. Intenta otra vez.")
                        st.caption(f"Detalle: {e}")
                        guardar_log(prompt_usuario, f"Error Imagen: {str(e)}")
            else:
                st.warning(res_hada)
                guardar_log(prompt_usuario, "Bloqueado por el Hada")
        else:
            st.info("¡Dime qué quieres dibujar!")

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
                    icon = "✅" if l['estado'] == "Aprobado" else "❌"
                    st.write(f"{icon} **[{l['fecha']}]** - {l['prompt']} | **Estado:** {l['estado']}")
        else:
            st.info("Aún no hay dibujos registrados.")
    elif pass_input:
        st.error("Contraseña incorrecta")

# Botones de navegación en barra lateral
st.sidebar.markdown("---")
if st.sidebar.button("Ir a Vista Padres"): st.session_state.view = "padre"
if st.sidebar.button("Volver a Galería"): st.session_state.view = "nena"