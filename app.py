import io
import re
import requests
from bs4 import BeautifulSoup

from groq import Groq

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

import streamlit as st


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="KashCook | Smart Kitchen",
    page_icon="🍳",
    layout="wide",
)

st.title("🍳 KashCook AI")
st.markdown(
    "Tu sistema inteligente de planificación culinaria y financiera."
)

st.markdown("---")


# ============================================================
# FUNCIONES ALSUPER
# ============================================================

ALSUPER_URL = "https://alsuper.com"


def obtener_pagina(url):
    """
    Descarga una página pública de Alsuper.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/154.0 Safari/537.36"
        ),
        "Accept-Language": "es-MX,es;q=0.9",
    }

    try:
        respuesta = requests.get(
            url,
            headers=headers,
            timeout=20,
        )

        respuesta.raise_for_status()

        return respuesta.text

    except Exception:
        return None


def extraer_producto_alsuper(url):
    """
    Intenta obtener nombre y precio desde una página individual
    de producto de Alsuper.
    """

    html = obtener_pagina(url)

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    texto = soup.get_text(
        " ",
        strip=True,
    )

    producto = {
        "nombre": None,
        "precio": None,
        "url": url,
    }

    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    h1 = soup.find("h1")

    if h1:
        producto["nombre"] = h1.get_text(
            " ",
            strip=True,
        )

    if not producto["nombre"]:
        meta_title = soup.find(
            "meta",
            property="og:title",
        )

        if meta_title:
            producto["nombre"] = meta_title.get(
                "content"
            )

    # --------------------------------------------------------
    # PRECIO
    # --------------------------------------------------------

    patrones = [
        r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"MXN\s*([0-9]+(?:\.[0-9]{1,2})?)",
    ]

    for patron in patrones:

        encontrados = re.findall(
            patron,
            texto,
            flags=re.IGNORECASE,
        )

        if encontrados:

            try:

                precios = [
                    float(x)
                    for x in encontrados
                ]

                # Evitamos tomar cantidades absurdamente altas
                precios_validos = [
                    p
                    for p in precios
                    if 0 < p < 10000
                ]

                if precios_validos:

                    producto["precio"] = min(
                        precios_validos
                    )

                    break

            except Exception:
                pass

    if not producto["nombre"]:
        return None

    return producto


def buscar_productos_alsuper(termino):
    """
    Busca productos en el sitio público de Alsuper.

    Dependiendo de cómo entregue actualmente los resultados el sitio,
    puede requerir ajustes futuros.
    """

    termino_url = termino.replace(
        " ",
        "%20",
    )

    posibles_urls = [
        f"{ALSUPER_URL}/buscar?q={termino_url}",
        f"{ALSUPER_URL}/search?q={termino_url}",
    ]

    for url in posibles_urls:

        html = obtener_pagina(url)

        if not html:
            continue

        soup = BeautifulSoup(
            html,
            "html.parser",
        )

        resultados = []

        # Buscar enlaces que parezcan productos
        enlaces = soup.find_all(
            "a",
            href=True,
        )

        for enlace in enlaces:

            href = enlace.get(
                "href",
                "",
            )

            texto = enlace.get_text(
                " ",
                strip=True,
            )

            if "/producto/" not in href:
                continue

            if not texto:
                continue

            if href.startswith("/"):
                href = ALSUPER_URL + href

            resultados.append(
                {
                    "nombre": texto,
                    "url": href,
                }
            )

        # Eliminar duplicados
        unicos = []

        urls_vistas = set()

        for item in resultados:

            if item["url"] in urls_vistas:
                continue

            urls_vistas.add(
                item["url"]
            )

            unicos.append(item)

        productos = []

        for item in unicos[:15]:

            producto = extraer_producto_alsuper(
                item["url"]
            )

            if producto:

                productos.append(
                    producto
                )

        if productos:
            return productos

    return []


# ============================================================
# PRODUCTOS BÁSICOS PARA KASHCOOK
# ============================================================

PRODUCTOS_BASE = [
    "pollo",
    "carne de res",
    "carne de cerdo",
    "pescado",
    "atun",
    "sardina",
    "huevo",
    "arroz",
    "frijol",
    "tortilla",
    "papa",
    "tomate",
    "cebolla",
    "zanahoria",
    "calabaza",
    "chile",
    "leche",
    "queso",
    "crema",
    "pan",
    "avena",
    "platano",
    "manzana",
]


def crear_catalogo_alsuper():

    catalogo = []

    progreso = st.progress(
        0,
        text="Consultando productos de Alsuper...",
    )

    total = len(PRODUCTOS_BASE)

    for i, termino in enumerate(
        PRODUCTOS_BASE
    ):

        productos = buscar_productos_alsuper(
            termino
        )

        catalogo.extend(
            productos
        )

        progreso.progress(
            (i + 1) / total,
            text=f"Consultando: {termino}",
        )

    progreso.empty()

    # Eliminar duplicados
    resultado = []

    nombres = set()

    for producto in catalogo:

        nombre = producto.get(
            "nombre",
            "",
        ).strip().lower()

        if not nombre:
            continue

        if nombre in nombres:
            continue

        nombres.add(
            nombre
        )

        resultado.append(
            producto
        )

    return resultado


# ============================================================
# API GROQ
# ============================================================

groq_key = st.secrets.get(
    "GROQ_API_KEY",
    "",
)

if not groq_key:

    groq_key = st.text_input(
        "🔑 Ingresa tu Groq API Key (gsk_...):",
        type="password",
    )

client = None

if groq_key:

    try:

        client = Groq(
            api_key=groq_key.strip()
        )

    except Exception as e:

        st.error(
            f"Error al inicializar Groq: {e}"
        )


# ============================================================
# INTERFAZ
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "🏪 1. Supermercado"
    )

    alsuper = st.checkbox(
        "Alsuper",
        value=True,
    )

    smart = st.checkbox(
        "Smart",
        value=False,
    )

    soriana = st.checkbox(
        "Soriana",
        value=False,
    )

    walmart = st.checkbox(
        "Walmart",
        value=False,
    )

    aurrera = st.checkbox(
        "Bodega Aurrerá",
        value=False,
    )

    dias = st.slider(
        "Días a planificar:",
        1,
        7,
        6,
    )


with col2:

    st.subheader(
        "👥 2. Personas y presupuesto"
    )

    personas = st.slider(
        "¿Para cuántas personas?",
        1,
        10,
        1,
    )

    presupuesto = st.number_input(
        "💰 Presupuesto máximo (MXN):",
        min_value=200,
        max_value=10000,
        value=600,
        step=50,
    )

    st.subheader(
        "🍲 3. Estilos culinarios"
    )

    est_mex = st.checkbox(
        "Mexicana Tradicional",
        value=True,
    )

    est_nor = st.checkbox(
        "Regional Norteña",
        value=True,
    )

    est_asi = st.checkbox(
        "Asiática",
        value=False,
    )

    est_ita = st.checkbox(
        "Italiana",
        value=False,
    )

    est_fit = st.checkbox(
        "Saludable / Fitness",
        value=False,
    )

    st.subheader(
        "🍽 4. Tiempos de comida"
    )

    c_des = st.checkbox(
        "Desayuno",
        value=True,
    )

    c_com = st.checkbox(
        "Comida",
        value=True,
    )

    c_cen = st.checkbox(
        "Cena",
        value=True,
    )


# ============================================================
# RESTRICCIONES
# ============================================================

st.markdown("---")

st.subheader(
    "⚡ 5. Herramientas y restricciones"
)

col3, col4 = st.columns(2)


with col3:

    utensilios = st.multiselect(
        "Aparatos disponibles:",
        [
            "Estufa",
            "Licuadora",
            "Freidora de aire",
            "Horno",
            "Microondas",
            "Sartén básico",
        ],
        default=[
            "Estufa",
            "Sartén básico",
        ],
    )


with col4:

    restringidos = st.text_input(
        "Alimentos prohibidos o alergias:",
        placeholder="Ej. cebolla, mariscos, lácteos",
    )


# ============================================================
# LISTAS
# ============================================================

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
    t
    for t, sel in [
        ("Desayuno", c_des),
        ("Comida", c_com),
        ("Cena", c_cen),
    ]
    if sel
]


# ============================================================
# GENERACIÓN
# ============================================================

if st.button(
    "🚀 Generar Plan Inteligente",
    use_container_width=True,
):

    if not tiempos:

        st.warning(
            "Selecciona al menos un tiempo de comida."
        )

    elif not tiendas_seleccionadas:

        st.warning(
            "Selecciona al menos un supermercado."
        )

    elif not estilos_seleccionados:

        st.warning(
            "Selecciona al menos un estilo culinario."
        )

    elif client is None:

        st.error(
            "❌ Ingresa una Groq API Key válida."
        )

    else:

        # ====================================================
        # OBTENER PRECIOS
        # ====================================================

        catalogo = []

        if alsuper:

            with st.spinner(
                "🛒 Consultando catálogo público de Alsuper..."
            ):

                catalogo = crear_catalogo_alsuper()


        if not catalogo:

            st.warning(
                "⚠ No fue posible obtener productos y precios "
                "automáticamente desde Alsuper en esta ejecución."
            )

            st.info(
                "No se generará un presupuesto presentado como "
                "precio real. Esto evita que KashCook invente precios."
            )

        else:

            st.success(
                f"✅ Se obtuvieron {len(catalogo)} "
                "productos con información de Alsuper."
            )

            # ================================================
            # CATÁLOGO PARA GROQ
            # ================================================

            catalogo_texto = "\n".join(
                [
                    (
                        f"- {p['nombre']} | "
                        f"${p['precio']:.2f} MXN | "
                        f"{p['url']}"
                    )
                    for p in catalogo
                    if p.get("precio") is not None
                ]
            )

            if not catalogo_texto:

                st.error(
                    "Se encontraron productos, pero no fue posible "
                    "extraer precios confiables."
                )

                st.stop()


            # ================================================
            # PROMPT
            # ================================================

            prompt_text = f"""
Eres KashCook AI, un chef experto y especialista en
optimización de presupuestos familiares.

IMPORTANTE:

Los precios que aparecen abajo fueron obtenidos del catálogo
público de Alsuper.

NO inventes precios.

NO cambies los precios proporcionados.

NO agregues productos con precios inventados.

Si un ingrediente necesario no aparece en el catálogo,
indícalo como:

"PRECIO NO DISPONIBLE"

DATOS DEL USUARIO:

Supermercado:
Alsuper

Personas:
{personas}

Días:
{dias}

Presupuesto máximo:
${presupuesto:.2f} MXN

Tiempos:
{', '.join(tiempos)}

Estilos:
{', '.join(estilos_seleccionados)}

Utensilios:
{', '.join(utensilios)}

Restricciones:
{restringidos if restringidos else 'Ninguna'}

CATÁLOGO REAL OBTENIDO:

{catalogo_texto}

OBJETIVO:

Diseña un plan alimenticio para {dias} días para
{personas} persona(s).

Utiliza exclusivamente:
{', '.join(tiempos)}

Evita utilizar la palabra "Almuerzo".

Varía las proteínas.

Procura utilizar:

- Pollo
- Res
- Cerdo
- Pescado
- Atún
- Sardina
- Huevo
- Otras proteínas económicas

No dependas exclusivamente del pollo.

PRIORIDAD:

1. No superar el presupuesto.
2. Utilizar productos realmente encontrados.
3. Reutilizar ingredientes.
4. Reducir desperdicio.
5. Mantener variedad.
6. Mantener comidas realistas y fáciles de preparar.

IMPORTANTE SOBRE LAS CANTIDADES:

La lista de compras debe indicar la presentación
real que tendría que comprar el usuario.

Ejemplo:

2 paquetes de tortillas de 1 kg.

No supongas que el supermercado vende cantidades
fraccionadas si el producto se vende por paquete.

ENTREGA:

# PLAN DE MENÚS

Tabla:

| Día | Tiempo | Platillo | Ingredientes | Preparación |

# LISTA DE COMPRAS

Tabla:

| Producto | Cantidad | Precio unitario | Total |

# RESUMEN DEL PRESUPUESTO

Incluye:

Presupuesto máximo
Total calculado
Dinero restante
Costo por día
Costo por persona

# RECETAS

Explica cada receta.

# APROVECHAMIENTO

Explica cómo reutilizar ingredientes.

# ADVERTENCIA DE PRECIOS

Indica que los precios pueden cambiar por promociones,
existencias o actualización del sitio.
"""


            # ================================================
            # GROQ
            # ================================================

            with st.spinner(
                "🤖 KashCook está calculando el menú..."
            ):

                try:

                    completion = client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt_text,
                            }
                        ],
                        temperature=0.2,
                        max_tokens=8000,
                    )

                    content = (
                        completion
                        .choices[0]
                        .message
                        .content
                    )

                except Exception as e:

                    st.error(
                        f"Error al consultar Groq: {e}"
                    )

                    st.stop()


            # ================================================
            # MOSTRAR RESULTADO
            # ================================================

            st.success(
                "🎉 Plan generado utilizando datos obtenidos "
                "del catálogo de Alsuper."
            )

            st.markdown("---")

            st.markdown(
                content
            )


            # ================================================
            # PDF
            # ================================================

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

            title_style = ParagraphStyle(
                "Title",
                parent=styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=15,
                leading=18,
                alignment=1,
                textColor=colors.HexColor(
                    "#1B3B6F"
                ),
                spaceAfter=5,
            )

            subtitle_style = ParagraphStyle(
                "Subtitle",
                parent=styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=9,
                leading=12,
                alignment=1,
                textColor=colors.HexColor(
                    "#6D7275"
                ),
                spaceAfter=10,
            )

            section_style = ParagraphStyle(
                "Section",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=11,
                leading=14,
                textColor=colors.HexColor(
                    "#065A82"
                ),
                spaceBefore=12,
                spaceAfter=6,
            )

            body_style = ParagraphStyle(
                "Body",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=8.5,
                leading=12,
                textColor=colors.HexColor(
                    "#212529"
                ),
            )

            header_style = ParagraphStyle(
                "Header",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8.5,
                leading=11,
                textColor=colors.white,
                alignment=1,
            )

            story = [
                Paragraph(
                    "KashCook AI",
                    title_style,
                ),
                Paragraph(
                    (
                        f"Plan de compras y recetas | "
                        f"Alsuper Chihuahua | "
                        f"{dias} días | "
                        f"{personas} persona(s) | "
                        f"Presupuesto ${presupuesto:,.2f} MXN"
                    ),
                    subtitle_style,
                ),
                HRFlowable(
                    width="100%",
                    thickness=1.2,
                    color=colors.HexColor(
                        "#065A82"
                    ),
                    spaceAfter=12,
                ),
            ]


            # ================================================
            # LIMPIEZA
            # ================================================

            def limpiar_texto(texto):

                if not isinstance(
                    texto,
                    str,
                ):
                    texto = str(texto)

                texto = texto.replace(
                    "```markdown",
                    "",
                )

                texto = texto.replace(
                    "```",
                    "",
                )

                texto = texto.replace(
                    "**",
                    "",
                )

                texto = texto.replace(
                    "__",
                    "",
                )

                texto = texto.replace(
                    "•",
                    "-",
                )

                texto = texto.replace(
                    "&",
                    "y",
                )

                return texto.strip()


            # ================================================
            # TABLAS
            # ================================================

            def agregar_tabla(data):

                if len(data) <= 1:
                    return

                columnas = max(
                    len(row)
                    for row in data
                )

                if columnas > 4:

                    data = [
                        row[:4]
                        for row in data
                    ]

                    columnas = 4

                if columnas == 4:

                    widths = [
                        95,
                        135,
                        145,
                        180,
                    ]

                elif columnas == 3:

                    widths = [
                        120,
                        180,
                        255,
                    ]

                elif columnas == 2:

                    widths = [
                        180,
                        375,
                    ]

                else:

                    widths = [
                        555
                    ]

                tabla = Table(
                    data,
                    colWidths=widths,
                    repeatRows=1,
                )

                tabla.setStyle(
                    TableStyle(
                        [
                            (
                                "BACKGROUND",
                                (0, 0),
                                (-1, 0),
                                colors.HexColor(
                                    "#065A82"
                                ),
                            ),
                            (
                                "TEXTCOLOR",
                                (0, 0),
                                (-1, 0),
                                colors.white,
                            ),
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP",
                            ),
                            (
                                "ALIGN",
                                (0, 0),
                                (-1, -1),
                                "LEFT",
                            ),
                            (
                                "GRID",
                                (0, 0),
                                (-1, -1),
                                0.5,
                                colors.HexColor(
                                    "#D3D3D3"
                                ),
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                            (
                                "LEFTPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                            (
                                "RIGHTPADDING",
                                (0, 0),
                                (-1, -1),
                                5,
                            ),
                        ]
                    )
                )

                story.append(
                    tabla
                )

                story.append(
                    Spacer(
                        1,
                        10,
                    )
                )


            # ================================================
            # PROCESAR MARKDOWN
            # ================================================

            table_data = []

            for raw_line in content.split(
                "\n"
            ):

                line = raw_line.strip()

                if not line:
                    continue

                # Encabezado
                if line.startswith("#"):

                    agregar_tabla(
                        table_data
                    )

                    table_data = []

                    header = (
                        line
                        .replace(
                            "#",
                            "",
                        )
                        .strip()
                    )

                    story.append(
                        Paragraph(
                            limpiar_texto(
                                header
                            ),
                            section_style,
                        )
                    )

                    # Crear encabezado según sección
                    upper = header.upper()

                    if "MENÚ" in upper:

                        table_data.append(
                            [
                                Paragraph(
                                    "Día",
                                    header_style,
                                ),
                                Paragraph(
                                    "Tiempo / Platillo",
                                    header_style,
                                ),
                                Paragraph(
                                    "Ingredientes",
                                    header_style,
                                ),
                                Paragraph(
                                    "Preparación",
                                    header_style,
                                ),
                            ]
                        )

                    elif "COMPRA" in upper:

                        table_data.append(
                            [
                                Paragraph(
                                    "Producto",
                                    header_style,
                                ),
                                Paragraph(
                                    "Cantidad",
                                    header_style,
                                ),
                                Paragraph(
                                    "Precio unitario",
                                    header_style,
                                ),
                                Paragraph(
                                    "Total",
                                    header_style,
                                ),
                            ]
                        )

                    continue


                # Separadores
                if "---" in line:
                    continue


                # Tabla
                if "|" in line:

                    partes = [
                        p.strip()
                        for p in line.split(
                            "|"
                        )
                    ]

                    partes = [
                        p
                        for p in partes
                        if p
                    ]

                    if not partes:
                        continue

                    # Ignorar separadores Markdown
                    if all(
                        set(
                            p.replace(
                                " ",
                                "",
                            )
                        ) <= {
                            "-",
                            ":",
                        }
                        for p in partes
                    ):
                        continue

                    partes = partes[:4]

                    row = [
                        Paragraph(
                            limpiar_texto(
                                p
                            ),
                            body_style,
                        )
                        for p in partes
                    ]

                    while len(row) < 4:

                        row.append(
                            Paragraph(
                                "",
                                body_style,
                            )
                        )

                    table_data.append(
                        row
                    )

                else:

                    agregar_tabla(
                        table_data
                    )

                    table_data = []

                    story.append(
                        Paragraph(
                            limpiar_texto(
                                line
                            ),
                            body_style,
                        )
                    )


            agregar_tabla(
                table_data
            )


            # ================================================
            # CREAR PDF
            # ================================================

            try:

                doc.build(
                    story
                )

                pdf_bytes = (
                    pdf_buffer
                    .getvalue()
                )

                st.download_button(
                    label=(
                        "📄 Descargar "
                        "Plan KashCook en PDF"
                    ),
                    data=pdf_bytes,
                    file_name=(
                        "KashCook_"
                        "Alsuper_"
                        "Plan.pdf"
                    ),
                    mime="application/pdf",
                    use_container_width=True,
                )

            except Exception as e:

                st.error(
                    f"Error al generar PDF: {e}"
                )


else:

    st.info(
        "👋 Configura tu Groq API Key "
        "para comenzar."
    )
