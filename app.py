import io
from groq import Groq
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
import streamlit as st

st.set_page_config(
    page_title="KashCook | Smart Kitchen", page_icon="🍳", layout="wide"
)

st.title("🍳 KashCook AI")
st.markdown("Tu sistema inteligente de planificación culinaria y financiera.")
st.markdown("---")

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
    dias = st.slider("Días a planificar:", 1, 7, 6)

  with col2:
    st.subheader("👥 2. Comensales y Presupuesto")
    personas = st.slider("¿Para cuántas personas se va a cocinar?", 1, 10, 1)
    presupuesto = st.number_input(
        "💰 Presupuesto máximo (MXN):",
        min_value=200,
        max_value=10000,
        value=600,
        step=50,
    )

    st.subheader("🍲 3. Estilos Culinarios")
    est_mex = st.checkbox("Mexicana Tradicional", value=True)
    est_nor = st.checkbox("Regional Norteña", value=True)
    est_asi = st.checkbox("Asiática", value=False)
    est_ita = st.checkbox("Italiana", value=False)
    est_fit = st.checkbox("Saludable / Fitness", value=False)

    st.subheader("🍽 4. Tiempos de Comida")
    c_des = st.checkbox("Desayuno", value=True)
    c_com = st.checkbox("Comida", value=True)
    c_cen = st.checkbox("Cena", value=True)

  st.markdown("---")
  st.subheader("⚡ 5. Herramientas y Restricciones")

  col3, col4 = st.columns(2)
  with col3:
    utensilios = st.multiselect(
        "Aparatos disponibles en casa:",
        [
            "Estufa",
            "Licuadora",
            "Freidora de aire",
            "Horno",
            "Microondas",
            "Sartén básico",
        ],
        default=["Estufa", "Sartén básico"],
    )
  with col4:
    restringidos = st.text_input(
        "Alimentos prohibidos o alergias:",
        placeholder="Ej. Cebolla, mariscos, lácteos",
    )

  tiendas_seleccionadas = [
      t
      for t, sel in [
          ("Alsuper", alsuper),
          ("Smart", smart),
          ("Soriana", soriana),
          ("Walmart", walmart),
          ("Bodega Aurrerá", aurrera),
      ]
      if sel
  ]
  estilos_seleccionados = [
      e
      for e, sel in [
          ("Mexicana Tradicional", est_mex),
          ("Regional Norteña", est_nor),
          ("Asiática", est_asi),
          ("Italiana", est_ita),
          ("Saludable / Fitness", est_fit),
      ]
      if sel
  ]
  tiempos = [
      t for t, sel in [("Desayuno", c_des), ("Comida", c_com), ("Cena", c_cen)] if sel
  ]

  if st.button("🚀 Generar Plan Inteligente, Recetas y Presupuesto en PDF"):
    if not tiempos or not tiendas_seleccionadas or not estilos_seleccionados:
      st.warning(
          "⚠ Por favor selecciona al menos un tiempo, un supermercado y un"
          " estilo culinario."
      )
    else:
      with st.spinner(
          "🤖 KashCook calculando costos reales actualizados en Alsuper"
          " (Chihuahua) y generando documento completo..."
      ):
        prompt_text = (
            "Actúa como un Chef experto y asesor financiero de hogar para la app"
            f" KashCook. Genera un plan de menús COMPLETAMENTE DESARROLLADO Y"
            f" DETALLADO para TODOS los {dias} días. IMPORTANTE: Utiliza"
            f" exclusivamente los tiempos: {', '.join(tiempos)} (Desayuno,"
            " Comida y Cena; NO uses Almuerzo). Varía las proteínas y carnes a"
            " lo largo de la semana: incluye res, cerdo, pescado,"
            " atún/sardinas y pollo, evitando depender únicamente del pollo."
            f" Usa precios estrictamente reales y vigentes en Alsuper"
            f" (Chihuahua, Chih.) para {personas} persona(s), respetando"
            f" estrictamente un presupuesto máximo de ${presupuesto} pesos"
            " mexicanos (MXN). - Supermercado principal: Alsuper. - Estilos:"
            f" {', '.join(estilos_seleccionados)}. - Utensilios:"
            f" {', '.join(utensilios)}. - Restricciones:"
            f" {restringidos if restringidos else 'Ninguna'}. \nEstructura"
            " tu respuesta usando tablas en formato Markdown con columnas"
            " separadas por pipes (|) para las secciones de menú y de lista de"
            " compras."
        )

        try:
          completion = client.chat.completions.create(
              model="openai/gpt-oss-120b",
              messages=[{"role": "user", "content": prompt_text}],
              temperature=0.4,
              max_tokens=6144,
          )

          content = completion.choices[0].message.content
          st.success(
              "¡Plan culinario detallado, cotización actualizada en Alsuper y"
              " recetas listos! 🎉"
          )
          st.markdown("---")
          st.markdown(content)
            pdf_buffer = io.BytesIO()
          doc = SimpleDocTemplate(
              pdf_buffer,
              pagesize=letter,
              rightMargin=30,
              leftMargin=30,
              topMargin=35,
              bottomMargin=35,
          )

          styles = getSampleStyleSheet()
          t_style = ParagraphStyle(
              "ReportTitle",
              parent=styles["Heading1"],
              fontName="Helvetica-Bold",
              fontSize=15,
              leading=18,
              alignment=1,
              textColor=colors.HexColor("#1B3B6F"),
              spaceAfter=4,
          )
          s_style = ParagraphStyle(
              "ReportSubtitle",
              parent=styles["Normal"],
              fontName="Helvetica-Oblique",
              fontSize=9.5,
              leading=13,
              alignment=1,
              textColor=colors.HexColor("#6D7275"),
              spaceAfter=10,
          )
          sec_style = ParagraphStyle(
              "SectionHeader",
              parent=styles["Heading2"],
              fontName="Helvetica-Bold",
              fontSize=11,
              leading=15,
              textColor=colors.HexColor("#065A82"),
              spaceBefore=12,
              spaceAfter=6,
          )
          b_style = ParagraphStyle(
              "ReportBody",
              parent=styles["Normal"],
              fontName="Helvetica",
              fontSize=9,
              leading=13,
              textColor=colors.HexColor("#212529"),
          )
          th_style = ParagraphStyle(
              "TableHeader",
              parent=styles["Normal"],
              fontName="Helvetica-Bold",
              fontSize=9,
              leading=12,
              textColor=colors.white,
              alignment=1,
          )

          story = [
              Paragraph(
                  "KashCook - Plan de Compras, Recetas y Presupuesto", t_style
              ),
              Paragraph(
                  f"Cotización Vigente en Alsuper (Chihuahua, Chih.) | {dias}"
                  f" Días | {personas} Persona(s)",
                  s_style,
              ),
              Spacer(1, 10),
              HRFlowable(
                  width="100%",
                  thickness=1.2,
                  color=colors.HexColor("#065A82"),
                  spaceAfter=12,
              ),
          ]

          def limpiar_texto(texto):
            if not isinstance(texto, str):
              texto = str(texto)
            texto = (
                texto.replace("
              ", " - ")
.replace("


", " - ")
.replace("


", " - ")
)
texto = texto.replace("•", "-")
texto = texto.replace("&", "y")
texto = texto.replace("*", "")
return texto

      table_data = []

      for raw_line in content.split("\n"):
        line = raw_line.strip()
        if not line:
          continue

        if (
            line.startswith("#")
            or "PLAN DE MENÚS" in line.upper()
            or "LISTA DE COMPRAS" in line.upper()
            or "COSTOS" in line.upper()
            or "MENÚ" in line.upper()
        ):
          if len(table_data) > 1:
            t = Table(table_data, colWidths=[95, 135, 145, 180])
            t.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065A82")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D3D3D3")),
                ])
            )
            story.append(t)
            story.append(Spacer(1, 10))
            table_data = []

          clean_header = line.replace("#", "").strip()
          story.append(Paragraph(limpiar_texto(clean_header), sec_style))

          if "MENÚ" in clean_header.upper() or "RECETA" in clean_header.upper():
            table_data.append([
                Paragraph("**Día / Tiempo**", th_style),
                Paragraph("**Platillo**", th_style),
                Paragraph("**Ingredientes**", th_style),
                Paragraph("**Preparación**", th_style),
            ])
          elif (
              "COMPRA" in clean_header.upper()
              or "COSTO" in clean_header.upper()
          ):
            table_data.append([
                Paragraph("**Artículo / Producto**", th_style),
                Paragraph("**Cantidad**", th_style),
                Paragraph("**Costo Unitario**", th_style),
                Paragraph("**Costo Total (Alsuper)**", th_style),
            ])
        else:
          parts = [p.strip() for p in line.split("|") if p.strip()]
          if len(parts) >= 2 and not ("---" in parts[0]):
            row_cells = [
                Paragraph(limpiar_texto(p), b_style) for p in parts[:4]
            ]
            while len(row_cells) < 4:
              row_cells.append(Paragraph("", b_style))
            table_data.append(row_cells)
          elif not ("---" in line):
            if len(table_data) > 1:
              t = Table(table_data, colWidths=[95, 135, 145, 180])
              t.setStyle(
                  TableStyle([
                      ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065A82")),
                      ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                      ("VALIGN", (0, 0), (-1, -1), "TOP"),
                      ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                      ("TOPPADDING", (0, 0), (-1, -1), 5),
                      ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D3D3D3")),
                  ])
              )
              story.append(t)
              story.append(Spacer(1, 10))
              table_data = []
            story.append(Paragraph(limpiar_texto(line), b_style))

      if len(table_data) > 1:
        t = Table(table_data, colWidths=[95, 135, 145, 180])
        t.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#065A82")),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D3D3D3")),
            ])
        )
        story.append(t)

      doc.build(story)
      pdf_bytes = pdf_buffer.getvalue()

      st.download_button(
          label=(
              "📄 Descargar Recetas Completas, Lista de Alsuper y Presupuesto"
              " en PDF"
          ),
          data=pdf_bytes,
          file_name="KashCook_Alsuper_Presupuesto.pdf",
          mime="application/pdf",
      )

    except Exception as e:
      st.error(f"Error al conectar con Groq o generar PDF: {e}")
else:
st.info(
"👋 Configura tu clave en Streamlit Secrets o ingrésala para comenzar."
)
