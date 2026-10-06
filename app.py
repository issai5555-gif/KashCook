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
            with st.spinner("🤖 KashCook calculando costos exactos de insumos en Alsuper y generando tu documento PDF..."):
                prompt_text = (
                    f"Actúa como un Chef experto y asesor financiero de hogar para la app KashCook. "
                    f"Genera un plan de menús detallado con recetas y una lista de compras con costos estimada obligatoria para cada ingrediente cotizada en **Alsuper (Chihuahua, Chih.)** para {dias} días y {personas} personas, "
                    f"respetando estrictamente un presupuesto máximo de **${presupuesto} pesos mexicanos (MXN)**. "
                    f"- Supermercado principal: Alsuper "
                    f"- Estilos culinarios: {', '.join(estilos_seleccionados)} "
                    f"- Tiempos incluidos: {', '.join(tiempos)} "
                    f"- Utensilios disponibles: {', '.join(utensilios)} "
                    f"- Restricciones / Alergias: {restringidos if restringidos else 'Ninguna'} "
                    "\nDebes estructurar tu respuesta de forma completa incluyendo dos secciones obligatorias y explícitas:"
                    "\n1. **PLAN DE MENÚS Y RECETAS POR DÍA** (nombre del platillo, ingredientes con cantidades exactas y pasos de preparación enumerados)."
                    "\n2. **LISTA DE COMPRAS Y COSTOS EN ALSUPER (CHIHUAHUA)** (desglose detallado de cada producto, cantidad a comprar y costo estimado en pesos mexicanos, cerrando con el costo total que no rebase los $" + str(presupuesto) + " MXN)."
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
                    st.success("¡Tu plan culinario, cotización en Alsuper y recetas están listos! 🎉")
                    st.markdown("---")
                    st.markdown(content)
                    
                    # Generación profesional de PDF blindada contra desbordamiento horizontal
                    pdf = FPDF(orientation='P', unit='mm', format='A4')
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()
                    
                    # Encabezado formal del reporte institucional
                    pdf.set_font('helvetica', 'B', 15)
                    pdf.cell(0, 8, 'KashCook - Plan de Compras, Recetas y Presupuesto', 0, 1, 'C')
                    pdf.set_font('helvetica', 'I', 10)
                    pdf.cell(0, 6, 'Cotizacion Oficial en Alsuper (Chihuahua, Chih.) | Reporte Inteligente', 0, 1, 'C')
                    pdf.ln(4)
                    pdf.set_draw_color(180, 180, 180)
                    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                    pdf.ln(6)
                    
                    # Procesamiento seguro de líneas para evitar el error de caracteres anchos o espacios
                    pdf.set_font('helvetica', '', 9.5)
                    
                    cleaned_content = content.encode('latin-1', 'ignore').decode('latin-1')
                    
                    for raw_line in cleaned_content.split('\n'):
                        line = raw_line.replace('*', '').replace('#', '').strip()
                        
                        if not line:
                            pdf.ln(3)
                            continue
                        
                        # Detectar títulos de sección o encabezados principales
                        is_header = any(keyword in raw_line.upper() for keyword in ["DÍA", "DIA", "LISTA DE COMPRAS", "PLAN DE MENÚS", "COSTOS", "RECETAS"])
                        
                        if is_header and len(line) < 60:
                            pdf.ln(3)
                            pdf.set_font('helvetica', 'B', 11)
                            pdf.set_text_color(20, 80, 120)
                            pdf.cell(0, 6, line[:90], 0, 1)
                            pdf.set_font('helvetica', '', 9.5)
                            pdf.set_text_color(0, 0, 0)
                        else:
                            # Cortar de forma segura líneas largas para prevenir errores de ancho en FPDF
                            while len(line) > 95:
                                split_idx = line[:95].rfind(' ')
                                if split_idx == -1: 
                                    split_idx = 95
                                pdf.cell(0, 5, line[:split_idx], 0, 1)
                                line = line[split_idx:].strip()
                            if line:
                                pdf.cell(0, 5, line, 0, 1)
                    
                    # Extracción formal y segura del flujo de bytes
                    pdf_output = pdf.output(dest='S')
                    if isinstance(pdf_output, str):
                        pdf_bytes = pdf_output.encode('latin-1', 'ignore')
                    else:
                        pdf_bytes = bytes(pdf_output)

                    st.download_button(
                        label="📄 Descargar Recetas, Lista de Alsuper y Presupuesto en PDF",
                        data=pdf_bytes,
                        file_name="KashCook_Alsuper_Presupuesto.pdf",
                        mime="application/pdf"
                    )
                    
                except Exception as e:
                    st.error(f"Error al conectar con Groq o generar PDF: {e}")
else:
    st.info("👋 Configura tu clave en Streamlit Secrets o ingrésala para comenzar.")
