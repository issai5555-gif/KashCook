import streamlit as st
from google import genai

st.set_page_config(
    page_title="KashCook | Smart Kitchen",
    page_icon="🍳",
    layout="wide"
)

st.title("🍳 KashCook AI")
st.markdown("Tu sistema inteligente de planificación culinaria.")
st.markdown("---")

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = st.text_input("🔑 Ingresa tu Google Gemini API Key:", type="password")

if api_key:
    client = genai.Client(api_key=api_key)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏪 1. Elige tu Supermercado")
        tienda = st.radio(
            "Selecciona dónde harás tus compras:",
            ["Alsuper", "Smart", "Walmart", "Mercado Local"],
            horizontal=True
        )
        
        st.subheader("⏱ 2. Duración del Plan")
        dias = st.slider("Días a planificar:", 1, 7, 3)

    with col2:
        st.subheader("🍲 3. Estilo Culinario")
        tipo_cocina = st.selectbox(
            "Estilo:",
            ["Mexicana Tradicional", "Regional Norteña", "Asiática", "Italiana", "Saludable / Fitness", "Sorpréndeme"]
        )

        st.subheader("🍽️ 4. Tiempos de Comida")
        c_des = st.checkbox("Desayuno", value=False)
        c_alm = st.checkbox("Almuerzo / Comida", value=True)
        c_cen = st.checkbox("Cena", value=True)

    st.markdown("---")
    st.subheader("⚡ 5. Herramientas y Restricciones")
    
    col3, col4 = st.columns(2)
    with col3:
        utensilios = st.multiselect(
            "Aparatos disponibles en casa:",
            ["Estufa", "Licuadora", "Freidora de aire", "Horno", "Microondas", "Sartén básico"],
            default=["Estufa", "Sartén básico"]
        )
    with col4:
        restringidos = st.text_input("Alimentos prohibidos o alergias:", placeholder="Ej. Cebolla, mariscos, lácteos")

    tiempos = []
    if c_des:
        tiempos.append("Desayuno")
    if c_alm:
        tiempos.append("Almuerzo")
    if c_cen:
        tiempos.append("Cena")

    if st.button("🚀 Generar Plan Inteligente con KashCook"):
        if not tiempos:
            st.warning("⚠ Por favor selecciona al menos un tiempo de comida.")
        else:
            with st.spinner("🤖 KashCook analizando costos, inventarios y diseñando tu menú..."):
                prompt = (
                    f"Actúa como un Chef experto y un sistema de inteligencia artificial avanzado para la app KashCook. "
                    f"Genera un plan de menús detallado y vanguardista para {dias} días. "
                    f"- Tienda de referencia: {tienda} (Chihuahua, México) "
                    f"- Tipo de cocina: {tipo_cocina} "
                    f"- Tiempos de comida incluidos: {', '.join(tiempos)} "
                    f"- Utensilios disponibles: {', '.join(utensilios)} "
                    f"- Restricciones / Alergias: {restringidos if restringidos else 'Ninguna'} "
                    "Para cada día y tiempo, estructura: "
                    "1. Nombre del platillo con un toque moderno. "
                    f"2. Ingredientes precisos con costo estimado en pesos mexicanos adaptado a {tienda}. "
                    "3. Preparación rápida y limpia usando ÚNICAMENTE los utensilios enlistados. "
                    "Usa un formato en Markdown impecable."
                )
                
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    st.success("¡Tu plan culinario inteligente está listo! 🎉")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error al conectar con la IA: {e}")
else:
    st.info("👋 Ingresa tu API Key para desbloquear la experiencia KashCook.")
