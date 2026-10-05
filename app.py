import os
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

api_key = st.text_input("🔑 Ingresa tu credencial o token:", type="password")

if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
    
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Error al inicializar el cliente: {e}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏪 1. Elige tu Supermercado")
        st.markdown("Selecciona el establecimiento:")
        tienda_col1, tienda_col2 = st.columns(2)
        with tienda_col1:
            alsuper = st.checkbox("Alsuper", value=True)
            smart = st.checkbox("Smart", value=False)
            soriana = st.checkbox("Soriana", value=False)
        with tienda_col2:
            walmart = st.checkbox("Walmart", value=False)
            aurrera = st.checkbox("Bodega Aurrerá", value=False)
        
        st.subheader("⏱ 2. Duración del Plan")
        dias = st.slider("Días a planificar:", 1, 7, 3)

    with col2:
        st.subheader("👥 3. Comensales")
        personas = st.slider("¿Para cuántas personas se va a cocinar?", 1, 10, 2)

        st.subheader("🍲 4. Estilos Culinarios (Puedes elegir varios)")
        est_mex = st.checkbox("Mexicana Tradicional", value=True)
        est_nor = st.checkbox("Regional Norteña", value=True)
        est_asi = st.checkbox("Asiática", value=False)
        est_ita = st.checkbox("Italiana", value=False)
        est_fit = st.checkbox("Saludable / Fitness", value=False)

        st.subheader("🍽️ 5. Tiempos de Comida")
        c_des = st.checkbox("Desayuno", value=False)
        c_alm = st.checkbox("Almuerzo / Comida", value=True)
        c_cen = st.checkbox("Cena", value=True)

    st.markdown("---")
    st.subheader("⚡ 6. Herramientas y Restricciones")
    
    col3, col4 = st.columns(2)
    with col3:
        utensilios = st.multiselect(
            "Aparatos disponibles en casa:",
            ["Estufa", "Licuadora", "Freidora de aire", "Horno", "Microondas", "Sartén básico"],
            default=["Estufa", "Sartén básico"]
        )
    with col4:
        restringidos = st.text_input("Alimentos prohibidos o alergias:", placeholder="Ej. Cebolla, mariscos, lácteos")

    tiendas_seleccionadas = []
    if alsuper: tiendas_seleccionadas.append("Alsuper")
    if smart: tiendas_seleccionadas.append("Smart")
    if soriana: tiendas_seleccionadas.append("Soriana")
    if walmart: tiendas_seleccionadas.append("Walmart")
    if aurrera: tiendas_seleccionadas.append("Bodega Aurrerá")

    estilos_seleccionados = []
    if est_mex: estilos_seleccionados.append("Mexicana Tradicional")
    if est_nor: estilos_seleccionados.append("Regional Norteña")
    if est_asi: estilos_seleccionados.append("Asiática")
    if est_ita: estilos_seleccionados.append("Italiana")
    if est_fit: estilos_seleccionados.append("Saludable / Fitness")

    tiempos = []
    if c_des: tiempos.append("Desayuno")
    if c_alm: tiempos.append("Almuerzo")
    if c_cen: tiempos.append("Cena")

    if st.button("🚀 Generar Plan Inteligente con KashCook"):
        if not tiempos:
            st.warning("⚠ Por favor selecciona al menos un tiempo de comida.")
        elif not tiendas_seleccionadas:
            st.warning("⚠ Por favor selecciona al menos un supermercado.")
        elif not estilos_seleccionados:
            st.warning("⚠ Por favor selecciona al menos un estilo culinario.")
        else:
            with st.spinner("🤖 KashCook analizando costos, inventarios y diseñando tu menú..."):
                prompt = (
                    f"Actúa como un Chef experto y un sistema de inteligencia artificial avanzado para la app KashCook. "
                    f"Genera un plan de menús detallado y vanguardista para {dias} días, diseñado exactamente para {personas} personas. "
                    f"- Supermercados de referencia: {', '.join(tiendas_seleccionadas)} (Chihuahua, México) "
                    f"- Estilos de cocina combinados: {', '.join(estilos_seleccionados)} "
                    f"- Tiempos de comida incluidos: {', '.join(tiempos)} "
                    f"- Utensilios disponibles: {', '.join(utensilios)} "
                    f"- Restricciones / Alergias: {restringidos if restringidos else 'Ninguna'} "
                    "Para cada día y tiempo, estructura: "
                    "1. Nombre del platillo con un toque moderno. "
                    f"2. Ingredientes con cantidades exactas para {personas} personas y costo estimado en pesos mexicanos adaptado a {', '.join(tiendas_seleccionadas)}. "
                    "3. Preparación rápida y limpia usando ÚNICAMENTE los utensilios enlistados. "
                    "Usa un formato en Markdown impecable."
                )
                
                try:
                    # Modelo altamente estable contra saturaciones
                    response = client.models.generate_content(
                        model='gemini-1.5-flash',
                        contents=prompt,
                    )
                    st.success("¡Tu plan culinario inteligente está listo! 🎉")
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error al conectar con la IA: {e}")
else:
    st.info("👋 Ingresa tu credencial en el cuadro de arriba para comenzar.")
