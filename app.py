import streamlit as st
import requests
import json

st.set_page_config(
    page_title="KashCook | Smart Kitchen",
    page_icon="🍳",
    layout="wide"
)

st.title("🍳 KashCook AI")
st.markdown("Tu sistema inteligente de planificación culinaria.")
st.markdown("---")

# Caja para tu token que empieza con AQ...
token_input = st.text_input("🔑 Ingresa tu token (AQ...):", type="password")

if token_input:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏪 1. Elige tu Supermercado")
        alsuper = st.checkbox("Alsuper", value=True)
        smart = st.checkbox("Smart", value=False)
        soriana = st.checkbox("Soriana", value=False)
        walmart = st.checkbox("Walmart", value=False)
        aurrera = st.checkbox("Bodega Aurrerá", value=False)
        
        dias = st.slider("Días a planificar:", 1, 7, 3)

    with col2:
        st.subheader("👥 2. Comensales")
        personas = st.slider("¿Para cuántas personas se va a cocinar?", 1, 10, 2)

        st.subheader("🍲 3. Estilos Culinarios")
        est_mex = st.checkbox("Mexicana Tradicional", value=True)
        est_nor = st.checkbox("Regional Norteña", value=True)
        est_asi = st.checkbox("Asiática", value=False)
        est_ita = st.checkbox("Italiana", value=False)
        est_fit = st.checkbox("Saludable / Fitness", value=False)

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

    tiendas_seleccionadas = [t for t, sel in [("Alsuper", alsuper), ("Smart", smart), ("Soriana", soriana), ("Walmart", walmart), ("Bodega Aurrerá", aurrera)] if sel]
    estilos_seleccionados = [e for e, sel in [("Mexicana Tradicional", est_mex), ("Regional Norteña", est_nor), ("Asiática", est_asi), ("Italiana", est_ita), ("Saludable / Fitness", est_fit)] if sel]
    tiempos = [t for t, sel in [("Desayuno", c_des), ("Almuerzo", c_alm), ("Cena", c_cen)] if sel]

    if st.button("🚀 Generar Plan Inteligente con KashCook"):
        if not tiempos or not tiendas_seleccionadas or not estilos_seleccionados:
            st.warning("⚠ Por favor selecciona al menos un tiempo, un supermercado y un estilo culinario.")
        else:
            with st.spinner("🤖 KashCook analizando costos, inventarios y diseñando tu menú..."):
                prompt_text = (
                    f"Actúa como un Chef experto para la app KashCook. "
                    f"Genera un plan de menús detallado para {dias} días para {personas} personas. "
                    f"- Supermercados: {', '.join(tiendas_seleccionadas)} (Chihuahua, México) "
                    f"- Estilos: {', '.join(estilos_seleccionados)} "
                    f"- Tiempos: {', '.join(tiempos)} "
                    f"- Utensilios: {', '.join(utensilios)} "
                    f"- Restricciones: {restringidos if restringidos else 'Ninguna'} "
                    "Estructura cada día con nombre del platillo, ingredientes con cantidades y costos estimados en pesos mexicanos, y preparación rápida."
                )
                
                # Petición HTTP directa usando el token AQ como Bearer token de Vertex AI
                url = "https://us-central1-aiplatform.googleapis.com/v1/projects/1020780421572/locations/us-central1/publishers/google/models/gemini-1.5-flash:generateContent"
                
                headers = {
                    "Authorization": f"Bearer {token_input.strip()}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "contents": [{
                        "role": "user",
                        "parts": [{"text": prompt_text}]
                    }]
                }
                
                try:
                    response = requests.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        res_json = response.json()
                        content = res_json["candidates"][0]["content"]["parts"][0]["text"]
                        st.success("¡Tu plan culinario inteligente está listo! 🎉")
                        st.markdown("---")
                        st.markdown(content)
                    else:
                        st.error(f"Error de la API ({response.status_code}): {response.text}")
                except Exception as e:
                    st.error(f"Error al conectar con la IA: {e}")
else:
    st.info("👋 Ingresa tu token que empieza con 'AQ...' en el cuadro de arriba para comenzar.")
