import streamlit as st
from groq import Groq
import io

# Importaciones de ReportLab para un PDF profesional y estructurado
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

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
            with st.spinner("🤖 KashCook calculando costos exactos en Alsuper y generando documento ejecutivo con ReportLab..."):
                prompt_text = (
                    f"Actúa como un Chef experto y asesor financiero de hogar para la app KashCook. "
                    f"Genera un plan de menús detallado con recetas y una lista de compras con costos obligatoria y detallada cotizada en **Alsuper (Chihuahua, Chih.)** para {dias} días y {personas} personas, "
                    f"respetando estrictamente un presupuesto máximo de **${presupuesto} pesos mexicanos (MXN)**. "
                    f"- Supermercado principal: Alsuper "
                    f"- Estilos culinarios: {', '.join(estilos_seleccionados)} "
                    f"- Tiempos incluidos: {', '.join(tiempos)} "
                    f"- Utensilios disponibles: {', '.join(utensilios)} "
                    f"- Restricciones / Alergias: {restringidos if restringidos else 'Ninguna'} "
                    "\nEstructura tu respuesta de forma clara separando en dos secciones obligatorias:"
                    "\n1. **PLAN DE MENÚS Y RECETAS POR DÍA** (nombre del platillo, ingredientes exactos y pasos de preparación enumerados)."
                    "\n2. **LISTA DE COMPRAS Y COSTOS EN ALSUPER (CHIHUAHUA)** (desglose de producto, cantidad y costo en MXN, cerrando con el costo total que no rebase los $" + str(presupuesto) + " MXN)."
                )
                
                try:
                    # Usamos el modelo de alta capacidad con compatibilidad garantizada
                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {"role": "user", "content": prompt_text}
                        ],
                        temperature=0.6,
                    )
                    
                    content = completion.choices[0].message.content
                    st.success("¡Plan culinario, cotización en Alsuper y recetas listos! 🎉")
                    st.markdown("---")
                    st.markdown(content)
                    
                    # Generación robusta del PDF con ReportLab
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(
                        pdf_buffer,
                        pagesize=letter,
                        rightMargin=36,
                        leftMargin=36,
                        topMargin=36,
                        bottomMargin=36
                    )
                    
                    styles = getSampleStyleSheet()
                    
                    title_style = ParagraphStyle(
                        'ReportTitle',
                        parent=styles['Heading1'],
                        fontName='Helvetica-Bold',
                        fontSize=15,
                        leading=18,
                        alignment=1,
                        textColor=colors.HexColor('#1B3B6F')
                    )
                    
                    subtitle_style = ParagraphStyle(
                        'ReportSubtitle',
                        parent=styles['Normal'],
                        fontName='Helvetica-Oblique',
                        fontSize=9.5,
                        leading=13,
                        alignment=1,
                        textColor=colors.HexColor('#6D7275')
                    )
                    
                    section_style = ParagraphStyle(
                        'SectionHeader',
                        parent=styles['Heading2'],
                        fontName='Helvetica-Bold',
                        fontSize=11,
                        leading=15,
                        textColor=colors.HexColor('#065A82'),
                        spaceBefore=10,
                        spaceAfter=4
                    )
                    
                    body_style = ParagraphStyle(
                        'ReportBody',
                        parent=styles['Normal'],
                        fontName='Helvetica',
                        fontSize=9,
                        leading=12.5,
                        textColor=colors.HexColor('#212529'),
                        spaceAfter=3
                    )
                    
                    story = []
                    story.append(Paragraph("KashCook - Plan de Compras, Recetas y Presupuesto", title_style))
                    story.append(Paragraph("Cotización Oficial en Alsuper (Chihuahua, Chih.) | Reporte Inteligente", subtitle_style))
                    story.append(Spacer(1, 8))
                    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CCCCCC'), spaceAfter=12))
                    
                    for raw_line in content.split('\n'):
                        clean_line = raw_line.replace('*', '').strip()
                        
                        if not clean_line:
                            story.append(Spacer(1, 4))
                            continue
                        
                        upper_line = clean_line.upper()
                        is_header = any(keyword in upper_line for keyword in ["DIA", "DÍA", "LISTA DE COMPRAS", "PLAN DE MENUS", "COSTOS", "PRESUPUESTO"])
                        
                        if is_header and len(clean_line) < 60:
                            story.append(Paragraph(clean_line, section_style))
                        else:
                            safe_line = clean_line.replace('&', '&').replace('<', '<').replace('>', '>')
                            story.append(Paragraph(safe_line, body_style))
                    
                    doc.build(story)
                    pdf_bytes = pdf_buffer.getvalue()

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
