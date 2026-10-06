import io
import re
import html
import requests
from bs4 import BeautifulSoup

from groq import Groq

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
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
    "Accept-Language": "es-MX,es;q=0.9",
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/webp,*/*;q=0.8"
    ),
}


# ============================================================
# CATÁLOGO REAL ALSUPER
#
# IMPORTANTE:
# - Se intenta obtener el precio directamente de Alsuper.
# - precio_respaldo sirve cuando la página carga el precio
#   mediante JavaScript y requests no logra encontrarlo.
# - Estos precios fueron verificados en páginas públicas
#   de Alsuper al preparar esta versión.
# ============================================================

PRODUCTOS_ALSUPER = [

    # --------------------------------------------------------
    # POLLO
    # --------------------------------------------------------

    {
        "categoria": "Pollo",
        "nombre_referencia": "Caderita de Pollo",
        "presentacion": "Caderita de pollo",
        "url": (
            "https://alsuper.com/producto/"
            "caderita-de-pollo-44400"
        ),
        "precio_respaldo": 44.90,
    },

    {
        "categoria": "Pollo",
        "nombre_referencia": "Ala de Pollo Premium",
        "presentacion": "Ala de pollo premium",
        "url": (
            "https://alsuper.com/producto/"
            "ala-de-pollo-premium-352077"
        ),
        "precio_respaldo": 114.90,
    },


    # --------------------------------------------------------
    # RES
    # --------------------------------------------------------

    {
        "categoria": "Res",
        "nombre_referencia": "Pata de Res",
        "presentacion": "Pata de res",
        "url": (
            "https://alsuper.com/producto/"
            "pata-de-res-9216"
        ),
        "precio_respaldo": 109.90,
    },

    {
        "categoria": "Res",
        "nombre_referencia": "Puchero de Res",
        "presentacion": "Puchero de res",
        "url": (
            "https://alsuper.com/producto/"
            "puchero-de-res-14038"
        ),
        "precio_respaldo": 259.90,
    },

    {
        "categoria": "Res",
        "nombre_referencia": "Carne para Jugo",
        "presentacion": "Carne para jugo",
        "url": (
            "https://alsuper.com/producto/"
            "carne-para-jugo-421810"
        ),
        "precio_respaldo": 319.90,
    },

    {
        "categoria": "Res",
        "nombre_referencia": "Sábana de Res",
        "presentacion": "Sábana de res",
        "url": (
            "https://alsuper.com/producto/"
            "sabana-de-res-497606"
        ),
        "precio_respaldo": 169.90,
    },


    # --------------------------------------------------------
    # PUERCO
    # --------------------------------------------------------

    {
        "categoria": "Puerco",
        "nombre_referencia": "Filete de Cerdo",
        "presentacion": "Filete de cerdo",
        "url": (
            "https://alsuper.com/producto/"
            "filete-de-cerdo-371873"
        ),
        "precio_respaldo": 154.90,
    },

    {
        "categoria": "Puerco",
        "nombre_referencia": "Molida de Puerco",
        "presentacion": "Carne molida de puerco",
        "url": (
            "https://alsuper.com/producto/"
            "molida-de-puerco-13817"
        ),
        "precio_respaldo": 114.90,
    },

    {
        "categoria": "Puerco",
        "nombre_referencia": "Milanesa de Puerco",
        "presentacion": "Milanesa de puerco",
        "url": (
            "https://alsuper.com/producto/"
            "milanesa-de-puerco-3405"
        ),
        "precio_respaldo": 114.90,
    },

    {
        "categoria": "Puerco",
        "nombre_referencia": "Carne de Cerdo para Disco",
        "presentacion": "Carne de cerdo para disco",
        "url": (
            "https://alsuper.com/producto/"
            "carne-de-cerdo-para-disco-406195"
        ),
        "precio_respaldo": 119.90,
    },


    # --------------------------------------------------------
    # PESCADO
    # --------------------------------------------------------

    {
        "categoria": "Pescado",
        "nombre_referencia": "Pescado Rodajeado",
        "presentacion": "Pescado rodajeado",
        "url": (
            "https://alsuper.com/producto/"
            "pescado-rodajeado-391892"
        ),
        "precio_respaldo": 84.90,
    },

    {
        "categoria": "Pescado",
        "nombre_referencia": "Filete de Bagre Basa",
        "presentacion": "Filete de bagre basa",
        "url": (
            "https://alsuper.com/producto/"
            "filete-de-bagre-basa-3834"
        ),
        "precio_respaldo": 84.90,
    },

    {
        "categoria": "Pescado",
        "nombre_referencia": "Filete de Pescado Finas Hierbas",
        "presentacion": "Filete de pescado con finas hierbas",
        "url": (
            "https://alsuper.com/producto/"
            "filete-de-pescado-finas-hierbas-369673"
        ),
        "precio_respaldo": 129.90,
    },

    {
        "categoria": "Pescado",
        "nombre_referencia": "Filete de Pescado Pimienta Limón",
        "presentacion": "Filete de pescado pimienta limón 500 g",
        "url": (
            "https://alsuper.com/producto/"
            "filete-de-pescado-pimienta-limon-352746"
        ),
        "precio_respaldo": 139.90,
    },


    # --------------------------------------------------------
    # HUEVO
    # --------------------------------------------------------

    {
        "categoria": "Huevo",
        "nombre_referencia": "Huevo Blanco San Juan",
        "presentacion": "12 piezas",
        "url": (
            "https://alsuper.com/producto/"
            "huevo-blanco-12-piezas-322894"
        ),
        "precio_respaldo": 32.90,
    },

    {
        "categoria": "Huevo",
        "nombre_referencia": "Huevo Blanco MyBrand",
        "presentacion": "12 piezas",
        "url": (
            "https://alsuper.com/producto/"
            "huevo-blanco-12-piezas-409497"
        ),
        "precio_respaldo": 29.90,
    },


    # --------------------------------------------------------
    # ATÚN
    # --------------------------------------------------------

    {
        "categoria": "Atún",
        "nombre_referencia": "Atún El Dorado en Agua",
        "presentacion": "130 g",
        "url": (
            "https://alsuper.com/producto/"
            "atun-449782"
        ),
        "precio_respaldo": 12.90,
    },

    {
        "categoria": "Atún",
        "nombre_referencia": "Atún Mazatún en Agua",
        "presentacion": "130 g",
        "url": (
            "https://alsuper.com/producto/"
            "atun-446574"
        ),
        "precio_respaldo": 18.90,
    },

    {
        "categoria": "Atún",
        "nombre_referencia": "Atún Dolores en Agua",
        "presentacion": "130 g",
        "url": (
            "https://alsuper.com/producto/"
            "atun--455238"
        ),
        "precio_respaldo": 19.90,
    },


    # --------------------------------------------------------
    # ARROZ
    # --------------------------------------------------------

    {
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Cazerola",
        "presentacion": "907 g",
        "url": (
            "https://alsuper.com/producto/"
            "arroz-379848"
        ),
        "precio_respaldo": 22.90,
    },

    {
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Largo SOS",
        "presentacion": "907 g",
        "url": (
            "https://alsuper.com/producto/"
            "arroz-largo-388114"
        ),
        "precio_respaldo": 29.90,
    },


    # --------------------------------------------------------
    # FRIJOL
    # --------------------------------------------------------

    {
        "categoria": "Despensa",
        "nombre_referencia": "Frijol Pinto Alsuper",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "frijol-pinto-409"
        ),
        "precio_respaldo": 24.90,
    },

    {
        "categoria": "Despensa",
        "nombre_referencia": "Frijol Pinto Cazerola",
        "presentacion": "907 g",
        "url": (
            "https://alsuper.com/producto/"
            "frijol-pinto-379849"
        ),
        "precio_respaldo": 24.90,
    },


    # --------------------------------------------------------
    # TORTILLA
    # --------------------------------------------------------

    {
        "categoria": "Despensa",
        "nombre_referencia": "Tortilla de Maíz Alsuper",
        "presentacion": "500 g",
        "url": (
            "https://alsuper.com/producto/"
            "tortilla-de-maiz-380479"
        ),
        "precio_respaldo": 17.90,
    },

    {
        "categoria": "Despensa",
        "nombre_referencia": "Tortilla de Maíz Alsuper",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "tortilla-de-maiz-380477"
        ),
        "precio_respaldo": 25.90,
    },


    # --------------------------------------------------------
    # PAPA
    # --------------------------------------------------------

    {
        "categoria": "Verdura",
        "nombre_referencia": "Papa Morena",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "papa-morena-6"
        ),
        "precio_respaldo": 13.90,
    },


    # --------------------------------------------------------
    # TOMATE
    # --------------------------------------------------------

    {
        "categoria": "Verdura",
        "nombre_referencia": "Tomate Bola",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "tomate-2"
        ),
        "precio_respaldo": 29.90,
    },

    {
        "categoria": "Verdura",
        "nombre_referencia": "Tomate Saladet",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "tomate-saladet-98"
        ),
        "precio_respaldo": 29.90,
    },


    # --------------------------------------------------------
    # CEBOLLA
    # --------------------------------------------------------

    {
        "categoria": "Verdura",
        "nombre_referencia": "Cebolla Blanca",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "cebolla-blanca-9"
        ),
        "precio_respaldo": 49.90,
    },

    {
        "categoria": "Verdura",
        "nombre_referencia": "Cebolla Amarilla",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "cebolla-amarilla-150"
        ),
        "precio_respaldo": 34.90,
    },


    # --------------------------------------------------------
    # QUESO
    # --------------------------------------------------------

    {
        "categoria": "Lácteo",
        "nombre_referencia": "Queso Panela Alsuper",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "queso-panela-402102"
        ),
        "precio_respaldo": 124.90,
    },

    {
        "categoria": "Lácteo",
        "nombre_referencia": "Queso Chihuahua Alsuper",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "queso-chihuahua-508053"
        ),
        "precio_respaldo": 194.90,
    },


    # --------------------------------------------------------
    # BRÓCOLI
    # --------------------------------------------------------

    {
        "categoria": "Verdura",
        "nombre_referencia": "Brócoli",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "brocoli-71"
        ),
        "precio_respaldo": 44.90,
    },


    # --------------------------------------------------------
    # PIMIENTO
    # --------------------------------------------------------

    {
        "categoria": "Verdura",
        "nombre_referencia": "Pimiento Morrón Rojo",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "pimiento-morron-rojo-63"
        ),
        "precio_respaldo": 59.90,
    },


    # --------------------------------------------------------
    # AJO
    # --------------------------------------------------------

    {
        "categoria": "Despensa",
        "nombre_referencia": "Ajo Extra",
        "presentacion": "1 kg",
        "url": (
            "https://alsuper.com/producto/"
            "ajo-extra-80"
        ),
        "precio_respaldo": 189.90,
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
            timeout=20,
        )

        respuesta.raise_for_status()

        return respuesta.text

    except Exception:

        return None


# ============================================================
# CONVERTIR PRECIO
# ============================================================

def convertir_precio(valor):

    if valor is None:
        return None

    texto = str(valor)

    texto = (
        texto
        .replace("$", "")
        .replace(",", "")
        .replace("MXN", "")
        .replace("mxn", "")
        .strip()
    )

    match = re.search(
        r"(\d+(?:\.\d{1,2})?)",
        texto,
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
# EXTRAER PRECIO
# ============================================================

def extraer_precio_de_html(soup):

    precios = []


    # --------------------------------------------------------
    # JSON-LD
    # --------------------------------------------------------

    scripts = soup.find_all(
        "script",
        type="application/ld+json",
    )

    for script in scripts:

        contenido = script.string

        if not contenido:
            continue

        encontrados = re.findall(
            r'"price"\s*:\s*"?'
            r'(?:MXN\s*)?'
            r'([0-9]+(?:\.[0-9]{1,2})?)',
            contenido,
            flags=re.IGNORECASE,
        )

        for valor in encontrados:

            precio = convertir_precio(valor)

            if precio:
                precios.append(precio)


    # --------------------------------------------------------
    # META PRODUCT PRICE
    # --------------------------------------------------------

    metas = [
        soup.find(
            "meta",
            property="product:price:amount",
        ),
        soup.find(
            "meta",
            attrs={
                "itemprop": "price"
            },
        ),
    ]

    for meta in metas:

        if not meta:
            continue

        precio = convertir_precio(
            meta.get("content")
        )

        if precio:
            precios.append(precio)


    # --------------------------------------------------------
    # ELEMENTOS CON PRICE
    # --------------------------------------------------------

    elementos = soup.find_all(
        attrs={
            "itemprop": "price"
        }
    )

    for elemento in elementos:

        precio = convertir_precio(
            elemento.get(
                "content"
            )
            or elemento.get_text(
                " ",
                strip=True,
            )
        )

        if precio:
            precios.append(precio)


    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    texto = soup.get_text(
        " ",
        strip=True,
    )

    encontrados = re.findall(
        r"\$\s*"
        r"([0-9]{1,5}"
        r"(?:\.[0-9]{1,2})?)",
        texto,
    )

    for valor in encontrados:

        precio = convertir_precio(valor)

        if precio:
            precios.append(precio)


    # --------------------------------------------------------
    # FILTRAR
    # --------------------------------------------------------

    precios = [
        p
        for p in precios
        if 0 < p < 10000
    ]


    if not precios:
        return None


    # El primer precio suele ser el precio actual.
    return precios[0]


# ============================================================
# EXTRAER PRODUCTO
# ============================================================

def extraer_producto_alsuper(item):

    url = item["url"]

    html = obtener_pagina(url)

    nombre = item.get(
        "nombre_referencia",
        "Producto Alsuper",
    )

    descripcion = item.get(
        "presentacion",
        "",
    )

    precio = None


    if html:

        soup = BeautifulSoup(
            html,
            "html.parser",
        )


        # ----------------------------------------------------
        # NOMBRE
        # ----------------------------------------------------

        h1 = soup.find("h1")

        if h1:

            nombre_extraido = h1.get_text(
                " ",
                strip=True,
            )

            if nombre_extraido:

                nombre = nombre_extraido


        if not nombre:

            meta = soup.find(
                "meta",
                property="og:title",
            )

            if meta:

                nombre = meta.get(
                    "content",
                    nombre,
                )


        # ----------------------------------------------------
        # DESCRIPCIÓN
        # ----------------------------------------------------

        meta_description = soup.find(
            "meta",
            attrs={
                "name": "description"
            },
        )

        if meta_description:

            descripcion = meta_description.get(
                "content",
                descripcion,
            )


        # ----------------------------------------------------
        # PRECIO
        # ----------------------------------------------------

        precio = extraer_precio_de_html(
            soup
        )


    # --------------------------------------------------------
    # PRECIO DE RESPALDO
    #
    # Esto evita "PRECIO NO DISPONIBLE" cuando Alsuper
    # entrega la página pero oculta el precio mediante JS.
    # --------------------------------------------------------

    precio_respaldo = item.get(
        "precio_respaldo"
    )

    if precio is None and precio_respaldo:

        precio = float(
            precio_respaldo
        )


    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    if precio is None:

        return None


    return {
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": precio,
        "categoria": item["categoria"],
        "url": url,
        "precio_respaldo": (
            precio_respaldo
        ),
    }


# ============================================================
# CREAR CATÁLOGO
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def crear_catalogo_alsuper():

    catalogo = []

    total = len(
        PRODUCTOS_ALSUPER
    )

    progreso = st.progress(
        0,
        text="Consultando productos de Alsuper...",
    )


    for i, item in enumerate(
        PRODUCTOS_ALSUPER
    ):

        producto = extraer_producto_alsuper(
            item
        )

        if producto:

            catalogo.append(
                producto
            )


        progreso.progress(
            int(
                ((i + 1) / total) * 100
            ),
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

    vistos = set()

    for producto in catalogo:

        clave = (
            producto["nombre"]
            .strip()
            .lower()
        )

        if clave in vistos:
            continue

        vistos.add(
            clave
        )

        resultado.append(
            producto
        )


    return resultado


# ============================================================
# GROQ
# ============================================================

groq_key = st.secrets.get(
    "GROQ_API_KEY",
    "",
)

if not groq_key:

    groq_key = st.text_input(
        "🔑 Ingresa tu Groq API Key:",
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
# FUNCIONES PDF
# ============================================================

def limpiar_texto_pdf(texto):

    if texto is None:
        return ""

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

    texto = html.escape(
        texto,
        quote=False,
    )

    return texto.strip()


def agregar_parrafo_seguro(
    story,
    texto,
    estilo,
):

    texto = limpiar_texto_pdf(
        texto
    )

    if not texto:
        return

    story.append(
        Paragraph(
            texto,
            estilo,
        )
    )


def agregar_buffer(
    story,
    buffer,
    estilo,
):

    for texto in buffer:

        texto = texto.strip()

        if not texto:
            continue

        agregar_parrafo_seguro(
            story,
            texto,
            estilo,
        )

    return []


# ============================================================
# GENERAR PDF
# ============================================================

def generar_pdf(
    content,
    dias,
    personas,
    presupuesto,
):

    pdf_buffer = io.BytesIO()


    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=40,
        bottomMargin=40,
        title="KashCook AI",
        author="KashCook AI",
    )


    styles = getSampleStyleSheet()


    # --------------------------------------------------------
    # ESTILOS
    # --------------------------------------------------------

    title_style = ParagraphStyle(
        "KashTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#1B3B6F"
        ),
        spaceAfter=8,
    )


    subtitle_style = ParagraphStyle(
        "KashSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor(
            "#666666"
        ),
        spaceAfter=15,
    )


    day_style = ParagraphStyle(
        "Day",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=4,
    )


    meal_style = ParagraphStyle(
        "Meal",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor(
            "#065A82"
        ),
        spaceBefore=12,
        spaceAfter=5,
    )


    dish_style = ParagraphStyle(
        "Dish",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor(
            "#222222"
        ),
        spaceAfter=6,
    )


    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor(
            "#222222"
        ),
        spaceAfter=5,
    )


    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor(
            "#444444"
        ),
        spaceAfter=4,
    )


    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor(
            "#1B3B6F"
        ),
        spaceBefore=14,
        spaceAfter=8,
    )


    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.white,
        alignment=TA_CENTER,
    )


    table_body_style = ParagraphStyle(
        "TableBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor(
            "#222222"
        ),
    )


    story = []


    # --------------------------------------------------------
    # PORTADA
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "KASHCOOK AI",
            title_style,
        )
    )


    story.append(
        Paragraph(
            (
                f"Plan alimenticio y lista de compras | "
                f"{dias} días | "
                f"{personas} persona(s) | "
                f"Presupuesto máximo "
                f"${presupuesto:,.2f} MXN"
            ),
            subtitle_style,
        )
    )


    story.append(
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor(
                "#065A82"
            ),
            spaceAfter=15,
        )
    )


    # --------------------------------------------------------
    # ESTADO
    # --------------------------------------------------------

    dia_actual = None
    buffer = []
    tabla_compras = []
    en_tabla_compras = False


    lineas = content.split(
        "\n"
    )


    # --------------------------------------------------------
    # RECORRER RESPUESTA
    # --------------------------------------------------------

    for linea_original in lineas:

        linea = linea_original.strip()


        if not linea:
            continue


        if linea.startswith(
            "```"
        ):
            continue


        # ====================================================
        # DÍA
        # ====================================================

        match_dia = re.match(
            r"^#+\s*D[ÍI]A\s+(\d+)",
            linea,
            flags=re.IGNORECASE,
        )


        if match_dia:

            buffer = agregar_buffer(
                story,
                buffer,
                body_style,
            )


            # cerrar tabla pendiente
            if tabla_compras:

                # no hacemos nada aquí;
                # la tabla se genera en LISTA DE COMPRAS.
                pass


            dia_numero = match_dia.group(
                1
            )


            if dia_actual is not None:

                story.append(
                    PageBreak()
                )


            dia_actual = dia_numero


            tabla_dia = Table(
                [
                    [
                        Paragraph(
                            f"DÍA {dia_numero}",
                            day_style,
                        )
                    ]
                ],
                colWidths=[
                    540
                ],
            )


            tabla_dia.setStyle(
                TableStyle(
                    [
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, -1),
                            colors.HexColor(
                                "#065A82"
                            ),
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "MIDDLE",
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            8,
                        ),
                    ]
                )
            )


            story.append(
                tabla_dia
            )


            continue


        # ====================================================
        # TIEMPO
        # ====================================================

        match_comida = re.match(
            r"^#+\s*(DESAYUNO|COMIDA|CENA)",
            linea,
            flags=re.IGNORECASE,
        )


        if match_comida:

            buffer = agregar_buffer(
                story,
                buffer,
                body_style,
            )


            comida = (
                match_comida
                .group(1)
                .upper()
            )


            story.append(
                Paragraph(
                    comida,
                    meal_style,
                )
            )


            continue


        # ====================================================
        # LISTA DE COMPRAS
        # ====================================================

        if re.match(
            r"^#+\s*LISTA DE COMPRAS",
            linea,
            flags=re.IGNORECASE,
        ):

            buffer = agregar_buffer(
                story,
                buffer,
                body_style,
            )


            story.append(
                PageBreak()
            )


            story.append(
                Paragraph(
                    "LISTA DE COMPRAS",
                    section_style,
                )
            )


            en_tabla_compras = True
            tabla_compras = []


            continue


        # ====================================================
        # RESUMEN
        # ====================================================

        if re.match(
            r"^#+\s*RESUMEN DEL PRESUPUESTO",
            linea,
            flags=re.IGNORECASE,
        ):

            # Generar tabla de compras
            if tabla_compras:

                datos_tabla = []


                encabezado = [
                    "Producto",
                    "Descripción / Presentación",
                    "Cantidad",
                    "Precio unitario",
                    "Total",
                ]


                datos_tabla.append(
                    [
                        Paragraph(
                            limpiar_texto_pdf(x),
                            table_header_style,
                        )
                        for x in encabezado
                    ]
                )


                for fila in tabla_compras:

                    if len(fila) < 5:
                        continue


                    datos_tabla.append(
                        [
                            Paragraph(
                                limpiar_texto_pdf(x),
                                table_body_style,
                            )
                            for x in fila[:5]
                        ]
                    )


                tabla = Table(
                    datos_tabla,
                    colWidths=[
                        90,
                        170,
                        70,
                        90,
                        80,
                    ],
                    repeatRows=1,
                    splitByRow=1,
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
                                "GRID",
                                (0, 0),
                                (-1, -1),
                                0.4,
                                colors.HexColor(
                                    "#CCCCCC"
                                ),
                            ),
                            (
                                "VALIGN",
                                (0, 0),
                                (-1, -1),
                                "TOP",
                            ),
                            (
                                "TOPPADDING",
                                (0, 0),
                                (-1, -1),
                                4,
                            ),
                            (
                                "BOTTOMPADDING",
                                (0, 0),
                                (-1, -1),
                                4,
                            ),
                        ]
                    )
                )


                story.append(
                    tabla
                )


            tabla_compras = []
            en_tabla_compras = False


            story.append(
                Spacer(
                    1,
                    15,
                )
            )


            story.append(
                Paragraph(
                    "RESUMEN DEL PRESUPUESTO",
                    section_style,
                )
            )


            continue


        # ====================================================
        # APROVECHAMIENTO
        # ====================================================

        if re.match(
            r"^#+\s*APROVECHAMIENTO",
            linea,
            flags=re.IGNORECASE,
        ):

            buffer = agregar_buffer(
                story,
                buffer,
                body_style,
            )


            story.append(
                Spacer(
                    1,
                    10,
                )
            )


            story.append(
                Paragraph(
                    "APROVECHAMIENTO",
                    section_style,
                )
            )


            continue


        # ====================================================
        # NOTA DE PRECIOS
        # ====================================================

        if re.match(
            r"^#+\s*NOTA SOBRE PRECIOS",
            linea,
            flags=re.IGNORECASE,
        ):

            buffer = agregar_buffer(
                story,
                buffer,
                body_style,
            )


            story.append(
                Spacer(
                    1,
                    10,
                )
            )


            story.append(
                Paragraph(
                    "NOTA SOBRE PRECIOS",
                    section_style,
                )
            )


            continue


        # ====================================================
        # TABLA DE COMPRAS
        # ====================================================

        if en_tabla_compras and "|" in linea:

            partes = [
                x.strip()
                for x in linea.split("|")
            ]


            partes = [
                x
                for x in partes
                if x
            ]


            if not partes:
                continue


            # ignorar separador Markdown
            es_separador = all(
                set(
                    x.replace(
                        " ",
                        "",
                    )
                ) <= {
                    "-",
                    ":",
                }
                for x in partes
            )


            if es_separador:
                continue


            # ignorar encabezado
            if (
                partes[0].lower()
                == "producto"
            ):
                continue


            if len(partes) >= 5:

                tabla_compras.append(
                    partes[:5]
                )


            continue


        # ====================================================
        # TÍTULOS INTERNOS
        # ====================================================

        if linea.startswith(
            "###"
        ):

            buffer = agregar_buffer(
                story,
                buffer,
                body_style,
            )


            texto = re.sub(
                r"^#+\s*",
                "",
                linea,
            )


            story.append(
                Paragraph(
                    limpiar_texto_pdf(
                        texto
                    ),
                    dish_style,
                )
            )


            continue


        # ====================================================
        # INGREDIENTES / PREPARACIÓN
        # ====================================================

        if (
            linea.lower().startswith(
                "ingredientes:"
            )
            or linea.lower().startswith(
                "preparación:"
            )
        ):

            buffer = agregar_buffer(
                story,
                buffer,
                body_style,
            )


            story.append(
                Paragraph(
                    limpiar_texto_pdf(
                        linea
                    ),
                    dish_style,
                )
            )


            continue


        # ====================================================
        # LISTAS
        # ====================================================

        if linea.startswith(
            "-"
        ):

            buffer.append(
                linea
            )

            continue


        # ====================================================
        # TEXTO NORMAL
        # ====================================================

        buffer.append(
            linea
        )


    # ========================================================
    # FINAL
    # ========================================================

    buffer = agregar_buffer(
        story,
        buffer,
        body_style,
    )


    # Si quedó tabla de compras al final
    if tabla_compras:

        datos_tabla = []


        encabezado = [
            "Producto",
            "Descripción / Presentación",
            "Cantidad",
            "Precio unitario",
            "Total",
        ]


        datos_tabla.append(
            [
                Paragraph(
                    limpiar_texto_pdf(x),
                    table_header_style,
                )
                for x in encabezado
            ]
        )


        for fila in tabla_compras:

            if len(fila) < 5:
                continue


            datos_tabla.append(
                [
                    Paragraph(
                        limpiar_texto_pdf(x),
                        table_body_style,
                    )
                    for x in fila[:5]
                ]
            )


        tabla = Table(
            datos_tabla,
            colWidths=[
                90,
                170,
                70,
                90,
                80,
            ],
            repeatRows=1,
            splitByRow=1,
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
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.HexColor(
                            "#CCCCCC"
                        ),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )


        story.append(
            tabla
        )


    # --------------------------------------------------------
    # NOTA FINAL
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            15,
        )
    )


    story.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor(
                "#CCCCCC"
            ),
        )
    )


    story.append(
        Spacer(
            1,
            6,
        )
    )


    story.append(
        Paragraph(
            (
                "Los precios utilizados corresponden "
                "a productos consultados en el catálogo "
                "público de Alsuper. Pueden cambiar por "
                "promociones, existencias, zona y fecha "
                "de compra."
            ),
            small_style,
        )
    )


    # --------------------------------------------------------
    # PIE DE PÁGINA
    # --------------------------------------------------------

    def agregar_pie_pagina(
        canvas,
        doc,
    ):

        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            7,
        )

        canvas.setFillColor(
            colors.HexColor(
                "#777777"
            )
        )

        canvas.drawCentredString(
            letter[0] / 2,
            20,
            (
                f"KashCook AI | "
                f"Página {doc.page}"
            ),
        )

        canvas.restoreState()


    # --------------------------------------------------------
    # CREAR
    # --------------------------------------------------------

    doc.build(
        story,
        onFirstPage=agregar_pie_pagina,
        onLaterPages=agregar_pie_pagina,
    )


    return pdf_buffer.getvalue()


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

        st.stop()


    if not tiendas_seleccionadas:

        st.warning(
            "Selecciona al menos un supermercado."
        )

        st.stop()


    if not estilos_seleccionados:

        st.warning(
            "Selecciona al menos un estilo culinario."
        )

        st.stop()


    if client is None:

        st.error(
            "❌ Ingresa una Groq API Key válida."
        )

        st.stop()


    # ========================================================
    # PRODUCTOS
    # ========================================================

    catalogo = []


    if alsuper:

        with st.spinner(
            "🛒 Consultando productos y precios de Alsuper..."
        ):

            catalogo = crear_catalogo_alsuper()


    if not catalogo:

        st.error(
            "❌ No fue posible obtener productos "
            "de Alsuper."
        )

        st.info(
            "No se generará un presupuesto inventado."
        )

        st.stop()


    # ========================================================
    # CATALOGAR INTERNAMENTE
    # ========================================================

    catalogo_texto = "\n".join(
        [
            (
                f"- Categoría: {p['categoria']} | "
                f"Producto: {p['nombre']} | "
                f"Presentación: {p['descripcion']} | "
                f"Precio: ${p['precio']:.2f} MXN | "
                f"URL: {p['url']}"
            )
            for p in catalogo
        ]
    )


    # ========================================================
    # PROTEÍNAS DISPONIBLES
    # ========================================================

    categorias_proteina = [
        p
        for p in catalogo
        if p["categoria"]
        in [
            "Pollo",
            "Res",
            "Puerco",
            "Pescado",
            "Atún",
            "Huevo",
        ]
    ]


    proteinas_texto = "\n".join(
        [
            (
                f"- {p['categoria']}: "
                f"{p['nombre']} | "
                f"{p['descripcion']} | "
                f"${p['precio']:.2f}"
            )
            for p in categorias_proteina
        ]
    )


    # ========================================================
    # PROMPT
    # ========================================================

    prompt_text = f"""
Eres KashCook AI.

Eres chef profesional especializado en:
- planeación de comidas
- cocina mexicana
- cocina económica
- aprovechamiento de ingredientes
- control de presupuesto familiar


========================================================
DATOS DEL USUARIO
========================================================

Personas: {personas}

Días: {dias}

Presupuesto máximo:
${presupuesto:.2f} MXN

Tiempos seleccionados:
{', '.join(tiempos)}

Estilos:
{', '.join(estilos_seleccionados)}

Utensilios disponibles:
{', '.join(utensilios)}

Alimentos prohibidos o alergias:
{restringidos if restringidos else 'Ninguna'}


========================================================
PRODUCTOS REALES DISPONIBLES
========================================================

UTILIZA SOLAMENTE productos de este catálogo
cuando necesites asignar precio.

NO inventes productos.

NO inventes precios.

NO cambies precios.

NO redondees precios.

NO pongas "precio no disponible" si el producto
está en el catálogo.

CATÁLOGO:

{catalogo_texto}


========================================================
PROTEÍNAS DISPONIBLES
========================================================

{proteinas_texto}


========================================================
REGLAS DEL MENÚ
========================================================

Planea EXACTAMENTE {dias} días.

Cada día debe contener exactamente estos tiempos:

{', '.join(tiempos)}

NO utilices "Almuerzo".

DEBES VARIAR LAS PROTEÍNAS.

No hagas pollo todos los días.

En comidas principales procura utilizar una
combinación de:

- Pollo
- Res
- Puerco
- Pescado
- Atún
- Huevo

Siempre que el presupuesto lo permita.

Intenta que durante el plan aparezcan al menos
4 fuentes de proteína diferentes.

No repitas el mismo platillo salvo que sea necesario.

Reutiliza ingredientes para disminuir desperdicio.

Las recetas deben ser realistas.

Utiliza únicamente los utensilios disponibles.

Respeta estrictamente las alergias y restricciones.


========================================================
RECETAS
========================================================

CADA RECETA DEBE SER COMPLETA.

Para cada platillo incluye:

Ingredientes:
- cantidades aproximadas
- ingredientes necesarios

Preparación:
- pasos completos
- orden de preparación
- tiempos aproximados cuando sean útiles
- cocción adecuada

NO RESUMAS las recetas.

NO OMITAS pasos.

NO pongas simplemente:
"cocinar hasta que esté listo".

Explica cómo preparar el platillo.


========================================================
LISTA DE COMPRAS
========================================================

La lista debe contener SOLAMENTE los productos
necesarios para preparar el menú.

No hagas una lista genérica.

Para cada producto indica:

Producto
Descripción / presentación
Cantidad
Precio unitario
Total

Utiliza exactamente el nombre y presentación
del catálogo cuando exista.

IMPORTANTE:

Si necesitas arroz, utiliza un arroz del catálogo.

Si necesitas frijol, utiliza un frijol del catálogo.

Si necesitas tortilla, utiliza una tortilla del catálogo.

Si necesitas atún, utiliza uno de los atunes
del catálogo.

No inventes marcas.

No inventes presentaciones.

No inventes precios.


========================================================
PRESUPUESTO
========================================================

El presupuesto máximo es:

${presupuesto:.2f}

Procura que el total de compras NO exceda
el presupuesto.

Calcula:

Presupuesto máximo
Total de compras
Dinero restante
Costo por día
Costo por persona


========================================================
FORMATO OBLIGATORIO
========================================================

# DÍA 1

## DESAYUNO

### Nombre del platillo

Ingredientes:
- cantidad ingrediente
- cantidad ingrediente
- cantidad ingrediente

Preparación:
1. Primer paso.
2. Segundo paso.
3. Tercer paso.
4. Paso final.


## COMIDA

### Nombre del platillo

Ingredientes:
- cantidad ingrediente
- cantidad ingrediente

Preparación:
1. Paso.
2. Paso.
3. Paso.


## CENA

### Nombre del platillo

Ingredientes:
- cantidad ingrediente
- cantidad ingrediente

Preparación:
1. Paso.
2. Paso.
3. Paso.


Repite exactamente el mismo formato hasta:

# DÍA {dias}


========================================================
DESPUÉS DE LOS DÍAS
========================================================

# LISTA DE COMPRAS

| Producto | Descripción / Presentación | Cantidad | Precio unitario | Total |
| Producto | Presentación | Cantidad | $0.00 | $0.00 |


# RESUMEN DEL PRESUPUESTO

Presupuesto máximo:
Total de compras:
Dinero restante:
Costo por día:
Costo por persona:


# APROVECHAMIENTO

Explica cómo utilizar los ingredientes sobrantes
en otras comidas.


# NOTA SOBRE PRECIOS

Indica que los precios corresponden a productos
consultados en el catálogo público de Alsuper y
pueden cambiar por promociones, existencias,
zona y fecha de compra.


========================================================
REGLA CRÍTICA
========================================================

NO inventes precios.

NO pongas "precio no disponible" para productos
que sí aparecen en el catálogo.

Las recetas deben aparecer COMPLETAS.

No cortes las recetas.

No resumas las preparaciones.

Cada día debe estar claramente separado.
"""


    # ========================================================
    # GROQ
    # ========================================================

    with st.spinner(
        "🤖 KashCook está diseñando tu plan..."
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
                temperature=0.15,
                max_tokens=12000,
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


    # ========================================================
    # MOSTRAR
    # ========================================================

    st.success(
        "🎉 Plan generado correctamente."
    )


    st.markdown("---")


    st.markdown(
        content
    )


    # ========================================================
    # PDF
    # ========================================================

    with st.spinner(
        "📄 Preparando PDF completo..."
    ):

        try:

            pdf_bytes = generar_pdf(
                content,
                dias,
                personas,
                presupuesto,
            )


            st.download_button(
                label=(
                    "📄 Descargar Plan KashCook en PDF"
                ),
                data=pdf_bytes,
                file_name=(
                    "KashCook_Plan.pdf"
                ),
                mime="application/pdf",
                use_container_width=True,
            )


        except Exception as e:

            st.error(
                f"Error al generar PDF: {e}"
            )
