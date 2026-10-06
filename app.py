import streamlit as st
from groq import Groq
from fpdf import FPDF

st.set_page_config(
    page_title="KashCook | Smart Kitchen",
    page_icon="🍳",
    layout="wide"
)

st.title("🍳 KashCook AI")
st.markdown("Tu sistema inteligente de planificación culinaria y financiera.")
st.markdown("---")

# Carga automática desde los secretos de Streamlit Cloud, o input manual de respaldo
groq_key = st.secrets.get("GROQ_API_KEY", "")

if not groq_key:
    groq_key = st.text_input("🔑 Ingresa tu Groq API Key (gsk_...):", type="password")

if groq_key:
    try:
        client = Groq(api_key=groq_key.strip())
    except Exception as e:
        st.error(f"Error al inicializar el cliente: {e}")

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
        st.subheader("👥 2. Comensales y Presupuesto")
        personas = st.slider("¿Para cuántas personas se va a cocinar?", 1, 10, 2)
        
        presupuesto = st.number_input(
            "💰 Presupuesto máximo (MXN):", 
            min_value=200, 
            max_value=10000, 
            value=1500, 
            step=100,
            help="Cantidad total en pesos mexicanos destinada para la compra en el súper."
        )

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

    if st.button("🚀 Generar Plan Inteligente, Recetas y Presupuesto en PDF"):
        if not tiempos or not tiendas_seleccionadas or not estilos_seleccionados:
            st.warning("⚠ Por favor selecciona al menos un tiempo, un supermercado y un estilo culinario.")
        else:
            with st.spinner("🤖 KashCook calculando costos de insumos, recetas y generando tu documento PDF..."):
                prompt_text = (
                    f"Actúa como un Chef experto y asesor financiero de hogar para la app KashCook. "
                    f"Genera un plan de menús detallado con recetas y una lista de compras con costos exacta para {dias} días para {personas} personas, "
                    f"respetando estrictamente un presupuesto máximo de **${presupuesto} pesos mexicanos (MXN)**. "
                    f"- Supermercados de referencia: {', '.join(tiendas_seleccionadas)} (Chihuahua, Chihuahua, México) "
                    f"- Estilos culinarios: {', '.join(estilos_seleccionados)} "
                    f"- Tiempos incluidos: {', '.join(tiempos)} "
                    f"- Utensilios disponibles: {', '.join(utensilios)} "
                    f"- Restricciones / Alergias: {restringidos if restringidos else 'Ninguna'} "
                    "\nEstructura tu respuesta exactamente en dos secciones claras:"
                    "\n1. **Plan de Menús y Recetas por Día** (nombre del platillo, ingredientes con cantidades por persona y pasos de preparación rápida)."
                    "\n2. **Lista de Compras y Costos de Insumos** (producto, cantidad exacta requerida y costo estimado unitario/total en MXN basado en precios reales de Chihuahua, asegurando que el total sumado no rebase los $" + str(presupuesto) + " MXN)."
                )
                
                try:
                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "user", "content": prompt_text}
                        ],
                        temperature=0.7,
                    )
                    
                    content = completion.choices[0].message.content
                    st.success("¡Tu plan culinario, recetas y cotización están listos! 🎉")
                    st.markdown("---")
                    st.markdown(content)
                    
                    # Generación del PDF con FPDF
                    class PDF(FPDF):
                        def header(self):
                            self.set_font('helvetica', 'B', 14)
                            self.cell(0, 10, 'KashCook - Plan de Compras, Recetas y Presupuesto', 0, 1, 'C')
                            self.set_font('helvetica', 'I', 10)
                            self.cell(0, 6, 'Chihuahua, Chihuahua, Mexico', 0, 1, 'C')
                            self.ln(5)

                        def footer(self):
                            self.set_y(-15)
                            self.set_font('helvetica', 'I', 8)
                            self.cell(0, 10, f'Generado por KashCook AI - Página {self.page_no()}', 0, 0, 'C')

                    pdf = PDF()
                    pdf.add_page()
                    pdf.set_font('helvetica', '', 10)
                    
                    # Limpieza de caracteres para compatibilidad de codificación en PDF
                    safe_text = content.encode('latin-1', 'replace').decode('latin-1')
                    
                    for line in safe_text.split('\n'):
                        pdf.multi_cell(0, 5, line)
                    
                    pdf_bytes = pdf.output()

                    # Botón de descarga en PDF
                    st.download_button(
                        label="📄 Descargar Recetas, Costos y Menú en PDF",
                        data=pdf_bytes,
                        file_name="KashCook_Recetas_Presupuesto.pdf",
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"Error al conectar con Groq o generar PDF: {e}")
else:
    st.info("👋 Configura tu clave en Streamlit Secrets o ingrésala para comenzar.")
