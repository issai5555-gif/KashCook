import streamlit as st
from google import genai

# Configuración de la página
st.set_page_config(page_title="KashCook", page_icon="🍳", layout="centered")

st.title("🍳 KashCook")
st.subheader("Tu Asistente Inteligente de Cocina y Menús")

# Cargar la API Key de forma segura desde los secretos de Streamlit
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = st.text_input("Ingresa tu Google Gemini API Key:", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

    st.markdown("---")
    st.header("1. Personaliza tu Plan")
    
    col1, col2 = st.columns(2)
    with col1:
        tienda = st.selectbox("Supermercado / Tienda:", ["Alsuper", "Smart", "Walmart", "Mercado Local"])
        dias = st.slider("¿Para cuántos días vas a planear?", 1, 7, 3)
    with col2:
        tipo_cocina = st.selectbox("Tipo de Cocina:", ["Mexicana Tradicional", "Regional Norteña", "Asiática", "Italiana", "Saludable / Fitness", "Sorpréndeme"])
        tiempos = st.multiselect("Tiempos de comida:", ["Desayuno", "Almuerzo", "Cena"], default=["Almuerzo", "Cena"])

    st.header("2. Tus Herramientas y Restricciones")
    col3, col4 = st.columns(2)
    with col3:
        utensilios = st.multiselect("Aparatos disponibles:", ["Estufa", "Licuadora", "Freidora de aire", "Horno", "Microondas", "Sartén básico"], default=["Estufa", "Sartén básico"])
    with col4:
        restringidos = st.text_input("Alimentos que NO te gustan o alergias (separados por coma):", "Cebolla, mariscos")

    if st.button("Generar mi Menú Inteligente con KashCook", type="primary"):
        if not tiempos:
            st.warning("Por favor selecciona al menos un tiempo de comida.")
        else:
            with st.spinner("KashCook está diseñando tu menú y calculando costos..."):
                prompt = f"""
                Actúa como un Chef experto y un sistema de inteligencia para la app KashCook.
                Genera un plan de menús detallado para {dias} días.
                - Tienda seleccionada: {tienda}
                - Tipo de cocina: {tipo_cocina}
                - Tiempos de comida incluidos: {', '.join(tiempos)}
                - Utensilios disponibles en cocina: {', '.join(utensilios)}
                - Alimentos prohibidos / restricciones: {restringidos}

                Para cada día y tiempo de comida, incluye:
                1. Nombre del platillo.
                2. Ingredientes necesarios y su costo estimado en pesos mexicanos adaptado a {tienda}.
                3. Pasos de preparación breves usando ÚNICAMENTE los utensilios enlistados.
                
                Usa un formato limpio, visual y estructurado en Markdown.
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    st.success("¡Menú generado con éxito!")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Ocurrió un error al generar el menú: {e}")
else:
    st.info("👆 Por favor ingresa tu API Key de Gemini para activar el motor de KashCook.")
