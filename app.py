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
        
        st.subheader("⏱️ 2. Duración del Plan")
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
    if c_des: tiempos.append("Desayuno")
    if c_alm: tiempos.append("Almuerzo")
    if c_cen: tiempos.append("Cena")

    st.markdown("
