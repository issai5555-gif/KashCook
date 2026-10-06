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
# ALSUPER
# ============================================================

ALSUPER_URL = "https://alsuper.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/154.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "es-MX,es;q=0.9",
    "Cache-Control": "no-cache",
}


# ============================================================
# PRODUCTOS REALES DE ALSUPER
#
# Son páginas individuales del catálogo público de Alsuper.
# La aplicación consulta directamente estas páginas.
#
# IMPORTANTE:
# Los precios se vuelven a consultar al ejecutar la aplicación.
# ============================================================

PRODUCTOS_ALSUPER = [
    {
        "categoria": "Pollo",
        "url": "https://alsuper.com/producto/caderita-de-pollo-44400",
    },
    {
        "categoria": "Pollo",
        "url": "https://alsuper.com/producto/pierna-con-muslo-de-pollo-297766",
    },
    {
        "categoria": "Pollo",
        "url": "https://alsuper.com/producto/ala-de-pollo-premium-352077",
    },
    {
        "categoria": "Pollo",
        "url": "https://alsuper.com/producto/pollo-para-asar-norte%C3%B1o-444492",
    },
    {
        "categoria": "Huevo",
        "url": "https://alsuper.com/producto/huevo-blanco-12-piezas-655",
    },
    {
        "categoria": "Huevo",
        "url": "https://alsuper.com/producto/huevo-blanco-con-30-323673",
    },
    {
        "categoria": "Huevo",
        "url": "https://alsuper.com/producto/huevo-blanco-con-30-653",
    },
    {
        "categoria": "Huevo",
        "url": "https://alsuper.com/producto/huevo-blanco-30-piezas-410581",
    },
    {
        "categoria": "Arroz",
        "url": "https://alsuper.com/producto/arroz-grano-grueso-259582",
    },
    {
        "categoria": "Arroz",
        "url": "https://alsuper.com/producto/arroz-integral-388116",
    },
    {
        "categoria": "Arroz",
        "url": "https://alsuper.com/producto/arroz-super-extra-374296",
    },
    {
        "categoria": "Frijol",
        "url": "https://alsuper.com/producto/frijol-pinto-409",
    },
    {
        "categoria": "Frijol",
        "url": "https://alsuper.com/producto/frijol-pinto-379849",
    },
    {
        "categoria": "Frijol",
        "url": "https://alsuper.com/producto/frijol-negro-313823",
    },
    {
        "categoria": "Frijol",
        "url": "https://alsuper.com/producto/frijol-peruano-389288",
    },
    {
        "categoria": "Frijol",
        "url": "https://alsuper.com/producto/frijol-cocido-entero-494447",
    },
    {
        "categoria": "Pescado",
        "url": "https://alsuper.com/producto/milanesa-de-pollo-460445",
    },
    {
        "categoria": "Atún",
        "url": "https://alsuper.com/producto/atun",
    },
]


# ============================================================
# DESCARGAR PÁGINA
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def obtener_pagina(url):

    try:

        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=25,
        )

        respuesta.raise_for_status()

        return respuesta.text

    except Exception:
        return None


# ============================================================
# CONVERTIR TEXTO A PRECIO
# ============================================================

def convertir_precio(valor):

    if valor is None:
        return None

    valor = str(valor).strip()

    valor = (
        valor.replace("$", "")
        .replace("MXN", "")
        .replace(",", "")
        .strip()
    )

    match = re.search(
        r"(\d+(?:\.\d{1,2})?)",
        valor,
    )

    if not match:
        return None

    try:

        precio = float(match.group(1))

        if 0 < precio < 10000:
            return precio

    except Exception:
        pass

    return None


# ============================================================
# EXTRAER PRODUCTO
# ============================================================

def extraer_producto_alsuper(url, categoria=""):

    html = obtener_pagina(url)

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    producto = {
        "nombre": None,
        "precio": None,
        "precio_anterior": None,
        "categoria": categoria,
        "url": url,
    }


    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    h1 = soup.find("h1")

    if h1:

        nombre = h1.get_text(
            " ",
            strip=True,
        )

        if nombre:
            producto["nombre"] = nombre


    if not producto["nombre"]:

        meta = soup.find(
            "meta",
            property="og:title",
        )

        if meta:

            producto["nombre"] = meta.get(
                "content"
            )


    # --------------------------------------------------------
    # JSON-LD
    # --------------------------------------------------------

    scripts = soup.find_all(
        "script",
        type="application/ld+json",
    )

    precios_json = []

    for script in scripts:

        try:

            contenido = script.string

            if not contenido:
                continue

            # Buscar precios dentro del JSON-LD
            encontrados = re.findall(
                r'"price"\s*:\s*"?(?:MXN\s*)?'
                r'([0-9]+(?:\.[0-9]{1,2})?)',
                contenido,
                flags=re.IGNORECASE,
            )

            for valor in encontrados:

                precio = convertir_precio(
                    valor
                )

                if precio:
                    precios_json.append(precio)

        except Exception:
            pass


    # --------------------------------------------------------
    # META PRODUCT PRICE
    # --------------------------------------------------------

    meta_precio = soup.find(
        "meta",
        property="product:price:amount",
    )

    if meta_precio:

        precio = convertir_precio(
            meta_precio.get("content")
        )

        if precio:
            precios_json.append(precio)


    # --------------------------------------------------------
    # TEXTO DE LA PÁGINA
    # --------------------------------------------------------

    texto = soup.get_text(
        " ",
        strip=True,
    )


    # Buscar precios con $
    precios_texto = re.findall(
        r"\$\s*([0-9]{1,5}(?:\.[0-9]{1,2})?)",
        texto,
    )

    for valor in precios_texto:

        precio = convertir_precio(
            valor
        )

        if precio:
            precios_json.append(precio)


    # --------------------------------------------------------
    # ELEGIR PRECIO
    # --------------------------------------------------------

    precios_validos = [
        p
        for p in precios_json
        if 0 < p < 10000
    ]


    if precios_validos:

        # En las páginas de Alsuper normalmente
        # el precio promocional aparece primero.
        producto["precio"] = precios_validos[0]


    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------

    if not producto["nombre"]:
        return None

    if producto["precio"] is None:
        return None

    return producto


# ============================================================
# CREAR CATÁLOGO
# ============================================================

def crear_catalogo_alsuper():

    catalogo = []

    progreso = st.progress(
        0,
        text="Consultando catálogo de Alsuper...",
    )

    total = len(
        PRODUCTOS_ALSUPER
    )

    for i, item in enumerate(
        PRODUCTOS_ALSUPER
    ):

        producto = extraer_producto_alsuper(
            item["url"],
            item["categoria"],
        )

        if producto:

            catalogo.append(
                producto
            )

        porcentaje = int(
            ((i + 1) / total) * 100
        )

        progreso.progress(
            porcentaje,
            text=(
                f"Consultando producto "
                f"{i + 1} de {total}"
            ),
        )

    progreso.empty()


    # --------------------------------------------------------
    # ELIMINAR DUPLICADOS
    # --------------------------------------------------------

    resultado = []

    urls_vistas = set()

    for producto in catalogo:

        url = producto["url"]

        if url in urls_vistas:
            continue

        urls_vistas.add(url)

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
        placeholder=(
            "Ej. cebolla, mariscos, lácteos"
        ),
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
        # ALSUPER
        # ====================================================

        catalogo = []

        if alsuper:

            with st.spinner(
                "🛒 Consultando precios publicados por Alsuper..."
            ):

                catalogo = (
                    crear_catalogo_alsuper()
                )


        # ====================================================
        # NO HAY PRODUCTOS
        # ====================================================

        if not catalogo:

            st.error(
                "❌ KashCook no pudo obtener precios "
                "de las páginas de productos de Alsuper."
            )

            st.info(
                "No se generará un presupuesto porque "
                "KashCook no debe inventar precios."
            )

            st.stop()


        # ====================================================
        # MOSTRAR CATÁLOGO REAL ENCONTRADO
        # ====================================================

        st.success(
            f"✅ Se encontraron "
            f"{len(catalogo)} productos con precio."
        )

        st.subheader(
            "🛒 Productos y precios encontrados"
        )


        tabla_catalogo = []

        for p in catalogo:

            tabla_catalogo.append(
                {
                    "Categoría": p["categoria"],
                    "Producto": p["nombre"],
                    "Precio MXN": (
                        f"${p['precio']:,.2f}"
                    ),
                }
            )


        st.dataframe(
            tabla_catalogo,
            use_container_width=True,
            hide_index=True,
        )


        # ====================================================
        # CATÁLOGO PARA GROQ
        # ====================================================

        catalogo_texto = "\n".join(
            [
                (
                    f"- CATEGORÍA: {p['categoria']} | "
                    f"PRODUCTO: {p['nombre']} | "
                    f"PRECIO: ${p['precio']:.2f} MXN | "
                    f"URL: {p['url']}"
                )
                for p in catalogo
            ]
        )


        # ====================================================
        # PROMPT
        # ====================================================

        prompt_text = f"""
Eres KashCook AI.

Eres un chef experto y especialista en
optimización de presupuestos familiares.

REGLA ABSOLUTA SOBRE PRECIOS:

Los precios que aparecen en el catálogo fueron
obtenidos directamente de páginas de productos
publicadas por Alsuper.

NO INVENTES PRECIOS.

NO MODIFIQUES PRECIOS.

NO ESTIMES PRECIOS.

NO PROMEDIES PRECIOS.

NO CREES PRODUCTOS QUE NO APAREZCAN
EN EL CATÁLOGO.

Si necesitas un producto que no está en el catálogo,
escribe:

PRECIO NO DISPONIBLE

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


CATÁLOGO DE ALSUPER:

{catalogo_texto}


OBJETIVO:

Diseña un plan alimenticio para:

{dias} días
{personas} persona(s)

Utiliza únicamente:

{', '.join(tiempos)}

Evita utilizar la palabra "Almuerzo".

PRIORIDAD:

1. No superar el presupuesto.
2. Utilizar productos del catálogo.
3. Reutilizar ingredientes.
4. Reducir desperdicio.
5. Mantener variedad.
6. Mantener comidas realistas.
7. Utilizar preparaciones económicas.

PROTEÍNAS:

Procura variar entre:

- Pollo
- Huevo
- Res
- Cerdo
- Pescado
- Atún
- Otras proteínas presentes en el catálogo

No utilices únicamente pollo.

IMPORTANTE:

La lista de compras debe utilizar
las presentaciones reales mostradas
en el catálogo.

No inventes presentaciones.

Si un producto cuesta $74.90,
el precio unitario debe permanecer
en $74.90.

Si una presentación no indica cantidad,
no inventes el gramaje.

FORMATO DE RESPUESTA:

# PLAN DE MENÚS

| Día | Tiempo | Platillo | Ingredientes | Preparación |

# LISTA DE COMPRAS

| Producto | Cantidad | Precio unitario | Total |

# RESUMEN DEL PRESUPUESTO

Presupuesto máximo:
Total calculado:
Dinero restante:
Costo por día:
Costo por persona:

# RECETAS

Explica cada receta.

# APROVECHAMIENTO

Explica cómo reutilizar ingredientes.

# ADVERTENCIA DE PRECIOS

Indica que los precios publicados por Alsuper
pueden cambiar por promociones, existencias,
zona y fecha de compra.

MUY IMPORTANTE:

El total debe calcularse utilizando únicamente
los precios proporcionados.

Si no puedes calcular correctamente un producto,
marca:

PRECIO NO DISPONIBLE
"""


        # ====================================================
        # GROQ
        # ====================================================

        with st.spinner(
            "🤖 KashCook está calculando el menú..."
        ):

            try:

                completion = (
                    client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "user",
                                "content": prompt_text,
                            }
                        ],
                        temperature=0.1,
                        max_tokens=8000,
                    )
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


        # ====================================================
        # RESULTADO
        # ====================================================

        st.success(
            "🎉 Plan generado utilizando precios "
            "obtenidos de productos de Alsuper."
        )

        st.markdown("---")

        st.markdown(
            content
        )


        # ====================================================
        # PDF
        # ====================================================

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
                    f"Alsuper | "
                    f"{dias} días | "
                    f"{personas} persona(s) | "
                    f"Presupuesto "
                    f"${presupuesto:,.2f} MXN"
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


        # ====================================================
        # LIMPIEZA
        # ====================================================

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


        # ====================================================
        # TABLAS PDF
        # ====================================================

        table_data = []


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


        # ====================================================
        # PROCESAR MARKDOWN
        # ====================================================

        for raw_line in content.split("\n"):

            line = raw_line.strip()

            if not line:
                continue


            # --------------------------------------------
            # ENCABEZADOS
            # --------------------------------------------

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


            # --------------------------------------------
            # SEPARADORES
            # --------------------------------------------

            if "---" in line:
                continue


            # --------------------------------------------
            # TABLA
            # --------------------------------------------

            if "|" in line:

                partes = [
                    p.strip()
                    for p in line.split("|")
                ]

                partes = [
                    p
                    for p in partes
                    if p
                ]

                if not partes:
                    continue


                # Separador Markdown

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
                        limpiar_texto(p),
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


        # ====================================================
        # CREAR PDF
        # ====================================================

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
