import streamlit as st
import google.generativeai as genai
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Diagnóstico de Modelos", page_icon="🔍")

st.title("🔍 Explorador de Modelos Mágicos")
st.info("Este código te ayudará a ver exactamente qué modelos 've' tu API Key.")

# --- CONFIGURACIÓN DE API ---
# Intentamos obtener la clave de Secrets o Variables de Entorno
api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ No se encontró la API Key. Por favor, configúrala en los Secrets de Streamlit.")
    st.code("GOOGLE_API_KEY = 'tu_clave_aqui'", language="toml")
    st.stop()

genai.configure(api_key=api_key)

# --- LISTAR MODELOS ---
st.write("### 📜 Modelos disponibles para tu clave:")

try:
    modelos = list(genai.list_models())
    
    if not modelos:
        st.warning("⚠️ La API no devolvió ningún modelo. Es posible que tu clave sea inválida o no tenga permisos.")
    else:
        # Creamos una tabla para que sea fácil de leer
        datos_modelos = []
        for m in modelos:
            datos_modelos.append({
                "Nombre Técnico": m.name,
                "Versión": m.version,
                "Descripción": m.description,
                "Métodos Soportados": ", ".join(m.supported_generation_methods)
            })
        
        st.table(datos_modelos)
        
        # --- VERIFICACIÓN ESPECÍFICA ---
        nombres = [m.name for m in modelos]
        
        st.write("### ✅ Verificación de requisitos:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "models/gemini-1.5-flash" in nombres:
                st.success("Gemini 1.5 Flash está disponible.")
            else:
                st.error("Gemini 1.5 Flash NO encontrado.")
                
        with col2:
            # Buscamos cualquier variante de Imagen 3
            imagen_disponible = any("imagen" in n.lower() for n in nombres)
            if imagen_disponible:
                st.success("Un modelo de Imagen está disponible.")
            else:
                st.error("Imagen 3 (Nano Banana) NO encontrado.")

except Exception as e:
    st.error("Fallo total al intentar conectar con Google AI:")
    st.exception(e)

# --- BOTÓN DE PRUEBA RÁPIDA ---
st.write("---")
st.write("### ⚡ Prueba de ejecución rápida")
if st.button("Probar saludo del Hada"):
    try:
        # Intentamos usar el nombre que debería funcionar
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content("Saluda como un hada mágica de forma muy breve.")
        st.write("**Respuesta del Hada:**", response.text)
    except Exception as e:
        st.error(f"Error al intentar generar contenido: {e}")

st.sidebar.markdown("""
**Instrucciones:**
1. Copia los nombres técnicos que aparezcan en la tabla.
2. Esos son los nombres que debemos usar en `model_hada` y `model_artista`.
""")