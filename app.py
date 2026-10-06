import io
import json
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
    LongTable,
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
# CONFIGURACIÓN GENERAL
# ============================================================

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

TIENDAS_DISPONIBLES = [
    "Alsuper",
    "Walmart",
    "Soriana",
    "Bodega Aurrerá",
]

TOLERANCIA_PRESUPUESTO = 100.00


# ============================================================
# CATÁLOGOS
#
# Los productos tienen:
# - URL oficial
# - precio de respaldo
#
# El sistema intenta primero obtener el precio de la página.
# Si no lo consigue, utiliza el precio de respaldo.
# ============================================================


PRODUCTOS_ALSUPER = [

    # POLLO
    {
        "tienda": "Alsuper",
        "categoria": "Pollo",
        "nombre_referencia": "Caderita de Pollo",
        "presentacion": "Caderita de pollo",
        "url": "https://alsuper.com/producto/caderita-de-pollo-44400",
        "precio_respaldo": 44.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Pollo",
        "nombre_referencia": "Ala de Pollo Premium",
        "presentacion": "Ala de pollo premium",
        "url": "https://alsuper.com/producto/ala-de-pollo-premium-352077",
        "precio_respaldo": 114.90,
    },

    # RES
    {
        "tienda": "Alsuper",
        "categoria": "Res",
        "nombre_referencia": "Pata de Res",
        "presentacion": "Pata de res",
        "url": "https://alsuper.com/producto/pata-de-res-9216",
        "precio_respaldo": 109.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Res",
        "nombre_referencia": "Puchero de Res",
        "presentacion": "Puchero de res",
        "url": "https://alsuper.com/producto/puchero-de-res-14038",
        "precio_respaldo": 259.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Res",
        "nombre_referencia": "Carne para Jugo",
        "presentacion": "Carne para jugo",
        "url": "https://alsuper.com/producto/carne-para-jugo-421810",
        "precio_respaldo": 319.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Res",
        "nombre_referencia": "Sábana de Res",
        "presentacion": "Sábana de res",
        "url": "https://alsuper.com/producto/sabana-de-res-497606",
        "precio_respaldo": 169.90,
    },

    # PUERCO
    {
        "tienda": "Alsuper",
        "categoria": "Puerco",
        "nombre_referencia": "Filete de Cerdo",
        "presentacion": "Filete de cerdo",
        "url": "https://alsuper.com/producto/filete-de-cerdo-371873",
        "precio_respaldo": 154.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Puerco",
        "nombre_referencia": "Molida de Puerco",
        "presentacion": "Carne molida de puerco",
        "url": "https://alsuper.com/producto/molida-de-puerco-13817",
        "precio_respaldo": 114.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Puerco",
        "nombre_referencia": "Milanesa de Puerco",
        "presentacion": "Milanesa de puerco",
        "url": "https://alsuper.com/producto/milanesa-de-puerco-3405",
        "precio_respaldo": 114.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Puerco",
        "nombre_referencia": "Carne de Cerdo para Disco",
        "presentacion": "Carne de cerdo para disco",
        "url": "https://alsuper.com/producto/carne-de-cerdo-para-disco-406195",
        "precio_respaldo": 119.90,
    },

    # PESCADO
    {
        "tienda": "Alsuper",
        "categoria": "Pescado",
        "nombre_referencia": "Pescado Rodajeado",
        "presentacion": "Pescado rodajeado",
        "url": "https://alsuper.com/producto/pescado-rodajeado-391892",
        "precio_respaldo": 84.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Pescado",
        "nombre_referencia": "Filete de Bagre Basa",
        "presentacion": "Filete de bagre basa",
        "url": "https://alsuper.com/producto/filete-de-bagre-basa-3834",
        "precio_respaldo": 84.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Pescado",
        "nombre_referencia": "Filete de Pescado Finas Hierbas",
        "presentacion": "Filete de pescado con finas hierbas",
        "url": "https://alsuper.com/producto/filete-de-pescado-finas-hierbas-369673",
        "precio_respaldo": 129.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Pescado",
        "nombre_referencia": "Filete de Pescado Pimienta Limón",
        "presentacion": "Filete de pescado pimienta limón 500 g",
        "url": "https://alsuper.com/producto/filete-de-pescado-pimienta-limon-352746",
        "precio_respaldo": 139.90,
    },

    # HUEVO
    {
        "tienda": "Alsuper",
        "categoria": "Huevo",
        "nombre_referencia": "Huevo Blanco San Juan",
        "presentacion": "12 piezas",
        "url": "https://alsuper.com/producto/huevo-blanco-12-piezas-322894",
        "precio_respaldo": 32.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Huevo",
        "nombre_referencia": "Huevo Blanco MyBrand",
        "presentacion": "12 piezas",
        "url": "https://alsuper.com/producto/huevo-blanco-12-piezas-409497",
        "precio_respaldo": 29.90,
    },

    # ATÚN
    {
        "tienda": "Alsuper",
        "categoria": "Atún",
        "nombre_referencia": "Atún El Dorado en Agua",
        "presentacion": "130 g",
        "url": "https://alsuper.com/producto/atun-449782",
        "precio_respaldo": 12.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Atún",
        "nombre_referencia": "Atún Mazatún en Agua",
        "presentacion": "130 g",
        "url": "https://alsuper.com/producto/atun-446574",
        "precio_respaldo": 18.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Atún",
        "nombre_referencia": "Atún Dolores en Agua",
        "presentacion": "130 g",
        "url": "https://alsuper.com/producto/atun--455238",
        "precio_respaldo": 19.90,
    },

    # ARROZ
    {
        "tienda": "Alsuper",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Cazerola",
        "presentacion": "907 g",
        "url": "https://alsuper.com/producto/arroz-379848",
        "precio_respaldo": 22.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Largo SOS",
        "presentacion": "907 g",
        "url": "https://alsuper.com/producto/arroz-largo-388114",
        "precio_respaldo": 29.90,
    },

    # FRIJOL
    {
        "tienda": "Alsuper",
        "categoria": "Despensa",
        "nombre_referencia": "Frijol Pinto Alsuper",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/frijol-pinto-409",
        "precio_respaldo": 24.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Despensa",
        "nombre_referencia": "Frijol Pinto Cazerola",
        "presentacion": "907 g",
        "url": "https://alsuper.com/producto/frijol-pinto-379849",
        "precio_respaldo": 24.90,
    },

    # TORTILLA
    {
        "tienda": "Alsuper",
        "categoria": "Despensa",
        "nombre_referencia": "Tortilla de Maíz Alsuper",
        "presentacion": "500 g",
        "url": "https://alsuper.com/producto/tortilla-de-maiz-380479",
        "precio_respaldo": 17.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Despensa",
        "nombre_referencia": "Tortilla de Maíz Alsuper",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/tortilla-de-maiz-380477",
        "precio_respaldo": 25.90,
    },

    # VERDURAS
    {
        "tienda": "Alsuper",
        "categoria": "Verdura",
        "nombre_referencia": "Papa Morena",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/papa-morena-6",
        "precio_respaldo": 13.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Verdura",
        "nombre_referencia": "Tomate Bola",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/tomate-2",
        "precio_respaldo": 29.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Verdura",
        "nombre_referencia": "Tomate Saladet",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/tomate-saladet-98",
        "precio_respaldo": 29.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Verdura",
        "nombre_referencia": "Cebolla Blanca",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/cebolla-blanca-9",
        "precio_respaldo": 49.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Verdura",
        "nombre_referencia": "Brócoli",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/brocoli-71",
        "precio_respaldo": 44.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Verdura",
        "nombre_referencia": "Pimiento Morrón Rojo",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/pimiento-morron-rojo-63",
        "precio_respaldo": 59.90,
    },

    # LÁCTEOS
    {
        "tienda": "Alsuper",
        "categoria": "Lácteo",
        "nombre_referencia": "Queso Panela Alsuper",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/queso-panela-402102",
        "precio_respaldo": 124.90,
    },
    {
        "tienda": "Alsuper",
        "categoria": "Lácteo",
        "nombre_referencia": "Queso Chihuahua Alsuper",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/queso-chihuahua-508053",
        "precio_respaldo": 194.90,
    },

    # AJO
    {
        "tienda": "Alsuper",
        "categoria": "Despensa",
        "nombre_referencia": "Ajo Extra",
        "presentacion": "1 kg",
        "url": "https://alsuper.com/producto/ajo-extra-80",
        "precio_respaldo": 189.90,
    },
]


# ============================================================
# WALMART
# ============================================================

PRODUCTOS_WALMART = [

    {
        "tienda": "Walmart",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Great Value Súper Extra",
        "presentacion": "1 kg",
        "url": "https://www.walmart.com.mx/ip/Arroz-Great-Value-Super-Extra-1-kg/00750649507086",
        "precio_respaldo": 15.00,
    },
    {
        "tienda": "Walmart",
        "categoria": "Despensa",
        "nombre_referencia": "Frijol Great Value Pinto",
        "presentacion": "900 g",
        "url": "https://www.walmart.com.mx/browse/abarrotes/arroz-frijol-y-semillas/frijol/120005_120067_120194",
        "precio_respaldo": 25.00,
    },
    {
        "tienda": "Walmart",
        "categoria": "Despensa",
        "nombre_referencia": "Frijol Negro Aurrera",
        "presentacion": "900 g",
        "url": "https://www.walmart.com.mx/browse/abarrotes/arroz-frijol-y-semillas/frijol/120005_120067_120194",
        "precio_respaldo": 21.00,
    },
    {
        "tienda": "Walmart",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Verde Valle Súper Extra",
        "presentacion": "1 kg",
        "url": "https://www.walmart.com.mx/browse/abarrotes/arroz-frijol-y-semillas/arroz/120005_120067_120195",
        "precio_respaldo": 37.00,
    },
    {
        "tienda": "Walmart",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Schettino Súper Extra",
        "presentacion": "907 g",
        "url": "https://www.walmart.com.mx/browse/abarrotes/arroz-frijol-y-semillas/arroz/120005_120067_120195",
        "precio_respaldo": 19.00,
    },
    {
        "tienda": "Walmart",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Italriso Súper Extra",
        "presentacion": "900 g",
        "url": "https://www.walmart.com.mx/browse/abarrotes/arroz-frijol-y-semillas/arroz/120005_120067_120195",
        "precio_respaldo": 20.00,
    },
    {
        "tienda": "Walmart",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz La Merced",
        "presentacion": "907 g",
        "url": "https://www.walmart.com.mx/browse/abarrotes/arroz-frijol-y-semillas/arroz/120005_120067_120195",
        "precio_respaldo": 21.00,
    },
    {
        "tienda": "Walmart",
        "categoria": "Despensa",
        "nombre_referencia": "Lentejas Verde Valle",
        "presentacion": "500 g",
        "url": "https://www.walmart.com.mx/content/abarrotes/arroz-frijol-y-semillas/120005_120067",
        "precio_respaldo": 20.00,
    },
    {
        "tienda": "Walmart",
        "categoria": "Atún",
        "nombre_referencia": "Atún",
        "presentacion": "Lata",
        "url": "https://www.walmart.com.mx/browse/abarrotes/enlatados-y-conservas/atunes/120005_120069_120189",
        "precio_respaldo": 24.00,
    },
]


# ============================================================
# BODEGA AURRERÁ
# ============================================================

PRODUCTOS_AURRERA = [

    {
        "tienda": "Bodega Aurrerá",
        "categoria": "Atún",
        "nombre_referencia": "Atún Dolores Aleta Amarilla",
        "presentacion": "140 g",
        "url": "https://despensa.bodegaaurrera.com.mx/content/despensa-y-abarrotes/06",
        "precio_respaldo": 21.00,
    },
    {
        "tienda": "Bodega Aurrerá",
        "categoria": "Atún",
        "nombre_referencia": "Atún Dolores Aleta Amarilla",
        "presentacion": "295 g",
        "url": "https://despensa.bodegaaurrera.com.mx/content/despensa-y-abarrotes/06",
        "precio_respaldo": 42.00,
    },
    {
        "tienda": "Bodega Aurrerá",
        "categoria": "Atún",
        "nombre_referencia": "Atún Tuny Clásico",
        "presentacion": "140 g",
        "url": "https://despensa.bodegaaurrera.com.mx/content/despensa-y-abarrotes/06",
        "precio_respaldo": 22.00,
    },
    {
        "tienda": "Bodega Aurrerá",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz Great Value",
        "presentacion": "900 g",
        "url": "https://www.bodegaaurrera.com.mx/content/abarrotes/arroz-frijol-y-semillas/120005_120067",
        "precio_respaldo": 24.00,
    },
    {
        "tienda": "Bodega Aurrerá",
        "categoria": "Despensa",
        "nombre_referencia": "Frijol Great Value Pinto",
        "presentacion": "900 g",
        "url": "https://www.bodegaaurrera.com.mx/content/abarrotes/arroz-frijol-y-semillas/120005_120067",
        "precio_respaldo": 32.00,
    },
    {
        "tienda": "Bodega Aurrerá",
        "categoria": "Despensa",
        "nombre_referencia": "Garbanzo Great Value",
        "presentacion": "500 g",
        "url": "https://www.bodegaaurrera.com.mx/content/abarrotes/arroz-frijol-y-semillas/120005_120067",
        "precio_respaldo": 35.00,
    },
]


# ============================================================
# SORIANA
#
# Se incluyen categorías oficiales como respaldo cuando la
# tienda no entrega fácilmente una URL individual.
# ============================================================

PRODUCTOS_SORIANA = [

    {
        "tienda": "Soriana",
        "categoria": "Despensa",
        "nombre_referencia": "Arroz",
        "presentacion": "Presentación disponible en tienda",
        "url": "https://www.soriana.com/despensa/arroz-frijol-y-semillas/arroz/",
        "precio_respaldo": 25.00,
    },
    {
        "tienda": "Soriana",
        "categoria": "Despensa",
        "nombre_referencia": "Frijol",
        "presentacion": "Presentación disponible en tienda",
        "url": "https://www.soriana.com/despensa/arroz-frijol-y-semillas/frijol/",
        "precio_respaldo": 30.00,
    },
    {
        "tienda": "Soriana",
        "categoria": "Atún",
        "nombre_referencia": "Atún",
        "presentacion": "Presentación disponible en tienda",
        "url": "https://www.soriana.com/despensa/enlatados-y-conservas/atunes/",
        "precio_respaldo": 25.00,
    },
]


TODOS_PRODUCTOS = (
    PRODUCTOS_ALSUPER
    + PRODUCTOS_WALMART
    + PRODUCTOS_SORIANA
    + PRODUCTOS_AURRERA
)


# ============================================================
# DESCARGAR PÁGINA
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def obtener_pagina(url):

    try:
        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=15,
        )

        respuesta.raise_for_status()

        return respuesta.text

    except Exception:
        return None


# ============================================================
# PRECIO
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


def extraer_precio_de_html(soup):

    precios = []

    # JSON-LD
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

    # META
    metas = [
        soup.find(
            "meta",
            property="product:price:amount",
        ),
        soup.find(
            "meta",
            attrs={"itemprop": "price"},
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

    # ITEMPROP
    elementos = soup.find_all(
        attrs={"itemprop": "price"}
    )

    for elemento in elementos:

        precio = convertir_precio(
            elemento.get("content")
            or elemento.get_text(
                " ",
                strip=True,
            )
        )

        if precio:
            precios.append(precio)

    # TEXTO
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

    precios = [
        p for p in precios
        if 0 < p < 10000
    ]

    if not precios:
        return None

    return precios[0]


# ============================================================
# EXTRAER PRODUCTO
# ============================================================

def extraer_producto(item):

    html_pagina = obtener_pagina(
        item["url"]
    )

    nombre = item.get(
        "nombre_referencia",
        "Producto",
    )

    descripcion = item.get(
        "presentacion",
        "",
    )

    precio = None
    fuente = "respaldo"

    if html_pagina:

        soup = BeautifulSoup(
            html_pagina,
            "html.parser",
        )

        # Nombre
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

        # Descripción
        meta_description = soup.find(
            "meta",
            attrs={"name": "description"},
        )

        if meta_description:

            descripcion = meta_description.get(
                "content",
                descripcion,
            )

        # Precio
        precio = extraer_precio_de_html(
            soup
        )

        if precio is not None:
            fuente = "en línea"

    # Respaldo
    if precio is None:

        precio_respaldo = item.get(
            "precio_respaldo"
        )

        if precio_respaldo:
            precio = float(
                precio_respaldo
            )

    if precio is None:
        return None

    return {
        "tienda": item["tienda"],
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": round(precio, 2),
        "categoria": item["categoria"],
        "url": item["url"],
        "fuente_precio": fuente,
    }


# ============================================================
# CATÁLOGO DE UNA TIENDA
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def crear_catalogo_tienda(nombre_tienda):

    productos = [
        p
        for p in TODOS_PRODUCTOS
        if p["tienda"] == nombre_tienda
    ]

    catalogo = []

    for item in productos:

        producto = extraer_producto(
            item
        )

        if producto:
            catalogo.append(
                producto
            )

    # No duplicar
    resultado = []
    vistos = set()

    for producto in catalogo:

        clave = (
            producto["tienda"].lower()
            + "|"
            + producto["nombre"].lower()
            + "|"
            + producto["descripcion"].lower()
        )

        if clave in vistos:
            continue

        vistos.add(clave)
        resultado.append(producto)

    return resultado


# ============================================================
# CREAR CATÁLOGO DE LAS TIENDAS SELECCIONADAS
# ============================================================

def crear_catalogo_seleccionado(
    tiendas,
):

    catalogo = []

    progreso = st.progress(
        0,
        text="Preparando catálogos...",
    )

    total = len(tiendas)

    for i, tienda in enumerate(tiendas):

        progreso.progress(
            int(
                (i / max(total, 1)) * 100
            ),
            text=(
                f"Consultando {tienda}..."
            ),
        )

        productos = crear_catalogo_tienda(
            tienda
        )

        catalogo.extend(
            productos
        )

    progreso.progress(
        100,
        text="Catálogos listos.",
    )

    progreso.empty()

    return catalogo


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

    walmart = st.checkbox(
        "Walmart",
        value=False,
    )

    soriana = st.checkbox(
        "Soriana",
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
        "💰 Presupuesto objetivo (MXN):",
        min_value=200,
        max_value=10000,
        value=600,
        step=50,
    )

    st.caption(
        f"Tolerancia máxima permitida: "
        f"${TOLERANCIA_PRESUPUESTO:,.2f} "
        f"adicionales."
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
    tienda
    for tienda, seleccionada in [
        ("Alsuper", alsuper),
        ("Walmart", walmart),
        ("Soriana", soriana),
        ("Bodega Aurrerá", aurrera),
    ]
    if seleccionada
]


estilos_seleccionados = [
    estilo
    for estilo, seleccionada in [
        ("Mexicana Tradicional", est_mex),
        ("Regional Norteña", est_nor),
        ("Asiática", est_asi),
        ("Italiana", est_ita),
        ("Saludable / Fitness", est_fit),
    ]
    if seleccionada
]


tiempos = [
    tiempo
    for tiempo, seleccionada in [
        ("Desayuno", c_des),
        ("Comida", c_com),
        ("Cena", c_cen),
    ]
    if seleccionada
]


# ============================================================
# UTILIDADES JSON
# ============================================================

def extraer_json(texto):

    if not texto:
        return None

    texto = texto.strip()

    texto = re.sub(
        r"^```json\s*",
        "",
        texto,
        flags=re.IGNORECASE,
    )

    texto = re.sub(
        r"^```\s*",
        "",
        texto,
    )

    texto = re.sub(
        r"\s*```$",
        "",
        texto,
    )

    # Intento directo
    try:
        return json.loads(texto)
    except Exception:
        pass

    # Buscar primer objeto JSON
    inicio = texto.find("{")
    final = texto.rfind("}")

    if inicio >= 0 and final > inicio:

        candidato = texto[
            inicio:final + 1
        ]

        try:
            return json.loads(
                candidato
            )
        except Exception:
            pass

    return None


def numero_seguro(valor):

    try:

        if isinstance(valor, str):

            valor = (
                valor
                .replace("$", "")
                .replace(",", "")
                .strip()
            )

        return float(valor)

    except Exception:
        return 0.0


# ============================================================
# CALCULAR COMPRA
# ============================================================

def calcular_compra(
    plan,
    catalogo,
):

    mapa = {
        str(p["id"]): p
        for p in catalogo
    }

    compras = []

    lista_original = plan.get(
        "shopping_list",
        [],
    )

    for item in lista_original:

        producto_id = str(
            item.get(
                "producto_id",
                "",
            )
        )

        producto = mapa.get(
            producto_id
        )

        if not producto:
            continue

        cantidad = numero_seguro(
            item.get(
                "cantidad",
                1,
            )
        )

        if cantidad <= 0:
            cantidad = 1

        unidad = str(
            item.get(
                "unidad",
                "pieza",
            )
        ).strip()

        total = round(
            cantidad
            * producto["precio"],
            2,
        )

        compras.append(
            {
                "producto_id": producto_id,
                "tienda": producto["tienda"],
                "producto": producto["nombre"],
                "descripcion": producto["descripcion"],
                "cantidad": cantidad,
                "unidad": unidad,
                "precio_unitario": producto["precio"],
                "total": total,
                "url": producto["url"],
                "fuente_precio": producto[
                    "fuente_precio"
                ],
            }
        )

    return compras


def total_compra(compras):

    return round(
        sum(
            item["total"]
            for item in compras
        ),
        2,
    )


# ============================================================
# NORMALIZAR PLAN
# ============================================================

def normalizar_plan(
    plan,
    catalogo,
    dias,
    tiempos,
):

    if not isinstance(
        plan,
        dict,
    ):
        return None

    if "days" not in plan:
        return None

    if not isinstance(
        plan["days"],
        list,
    ):
        return None

    # IDs para que Groq pueda elegir productos reales
    for i, producto in enumerate(
        catalogo,
        start=1,
    ):
        producto["id"] = i

    compras = calcular_compra(
        plan,
        catalogo,
    )

    plan["shopping_list"] = compras

    # Asegurar días
    plan["days"] = plan["days"][:dias]

    return plan


# ============================================================
# VALIDAR PRESUPUESTO
# ============================================================

def evaluar_presupuesto(
    compras,
    presupuesto,
):

    total = total_compra(
        compras
    )

    limite = (
        presupuesto
        + TOLERANCIA_PRESUPUESTO
    )

    return {
        "total": total,
        "presupuesto": float(
            presupuesto
        ),
        "limite": limite,
        "dentro_objetivo": (
            total <= presupuesto
        ),
        "dentro_tolerancia": (
            total <= limite
        ),
        "diferencia": round(
            total - presupuesto,
            2,
        ),
    }


# ============================================================
# PDF
# ============================================================

def limpiar_texto_pdf(
    texto
):

    if texto is None:
        return ""

    texto = str(texto)

    texto = html.escape(
        texto,
        quote=False,
    )

    return texto.strip()


def generar_pdf(
    plan,
    dias,
    personas,
    presupuesto,
    tiendas,
    evaluacion,
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
        spaceAfter=4,
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor(
            "#555555"
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
        spaceBefore=12,
        spaceAfter=8,
    )

    header_style = ParagraphStyle(
        "Header",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=colors.white,
        alignment=TA_CENTER,
    )

    table_style = ParagraphStyle(
        "Table",
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
                f"Plan alimenticio | "
                f"{dias} días | "
                f"{personas} persona(s)<br/>"
                f"Tiendas seleccionadas: "
                f"{', '.join(tiendas)}<br/>"
                f"Presupuesto objetivo: "
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
    # DÍAS
    # --------------------------------------------------------

    for indice_dia, dia in enumerate(
        plan.get(
            "days",
            [],
        )
    ):

        if indice_dia > 0:
            story.append(
                PageBreak()
            )

        numero_dia = dia.get(
            "day",
            indice_dia + 1,
        )

        encabezado_dia = Table(
            [
                [
                    Paragraph(
                        f"DÍA {numero_dia}",
                        day_style,
                    )
                ]
            ],
            colWidths=[540],
        )

        encabezado_dia.setStyle(
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
            encabezado_dia
        )

        comidas = dia.get(
            "meals",
            [],
        )

        for comida in comidas:

            tipo = str(
                comida.get(
                    "tipo",
                    "",
                )
            ).upper()

            platillo = comida.get(
                "platillo",
                "Platillo",
            )

            story.append(
                Paragraph(
                    tipo,
                    meal_style,
                )
            )

            story.append(
                Paragraph(
                    limpiar_texto_pdf(
                        platillo
                    ),
                    dish_style,
                )
            )

            story.append(
                Paragraph(
                    "<b>Ingredientes</b>",
                    body_style,
                )
            )

            ingredientes = comida.get(
                "ingredientes",
                [],
            )

            for ingrediente in ingredientes:

                story.append(
                    Paragraph(
                        "• "
                        + limpiar_texto_pdf(
                            ingrediente
                        ),
                        body_style,
                    )
                )

            story.append(
                Spacer(
                    1,
                    3,
                )
            )

            story.append(
                Paragraph(
                    "<b>Preparación</b>",
                    body_style,
                )
            )

            pasos = comida.get(
                "preparacion",
                [],
            )

            for numero, paso in enumerate(
                pasos,
                start=1,
            ):

                story.append(
                    Paragraph(
                        f"{numero}. "
                        + limpiar_texto_pdf(
                            paso
                        ),
                        body_style,
                    )
                )

    # --------------------------------------------------------
    # LISTA DE COMPRAS
    # --------------------------------------------------------

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "LISTA DE COMPRAS",
            section_style,
        )
    )

    compras = plan.get(
        "shopping_list",
        [],
    )

    datos = [
        [
            Paragraph(
                "Tienda",
                header_style,
            ),
            Paragraph(
                "Producto",
                header_style,
            ),
            Paragraph(
                "Presentación",
                header_style,
            ),
            Paragraph(
                "Cantidad",
                header_style,
            ),
            Paragraph(
                "Precio",
                header_style,
            ),
            Paragraph(
                "Total",
                header_style,
            ),
        ]
    ]

    for item in compras:

        cantidad = (
            f"{item['cantidad']:g} "
            f"{item['unidad']}"
        )

        datos.append(
            [
                Paragraph(
                    limpiar_texto_pdf(
                        item["tienda"]
                    ),
                    table_style,
                ),
                Paragraph(
                    limpiar_texto_pdf(
                        item["producto"]
                    ),
                    table_style,
                ),
                Paragraph(
                    limpiar_texto_pdf(
                        item["descripcion"]
                    ),
                    table_style,
                ),
                Paragraph(
                    limpiar_texto_pdf(
                        cantidad
                    ),
                    table_style,
                ),
                Paragraph(
                    f"${item['precio_unitario']:,.2f}",
                    table_style,
                ),
                Paragraph(
                    f"${item['total']:,.2f}",
                    table_style,
                ),
            ]
        )

    tabla = LongTable(
        datos,
        colWidths=[
            72,
            120,
            115,
            65,
            75,
            75,
        ],
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
    # RESUMEN
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            18,
        )
    )

    story.append(
        Paragraph(
            "RESUMEN DEL PRESUPUESTO",
            section_style,
        )
    )

    total = evaluacion[
        "total"
    ]

    diferencia = evaluacion[
        "diferencia"
    ]

    if evaluacion[
        "dentro_objetivo"
    ]:

        estado = (
            "Dentro del presupuesto objetivo."
        )

    elif evaluacion[
        "dentro_tolerancia"
    ]:

        estado = (
            "Dentro de la tolerancia máxima de $100."
        )

    else:

        estado = (
            "Fuera del límite permitido."
        )

    resumen = [
        [
            Paragraph(
                "<b>Presupuesto objetivo</b>",
                table_style,
            ),
            Paragraph(
                f"${presupuesto:,.2f}",
                table_style,
            ),
        ],
        [
            Paragraph(
                "<b>Total de compras</b>",
                table_style,
            ),
            Paragraph(
                f"${total:,.2f}",
                table_style,
            ),
        ],
        [
            Paragraph(
                "<b>Diferencia</b>",
                table_style,
            ),
            Paragraph(
                f"${diferencia:,.2f}",
                table_style,
            ),
        ],
        [
            Paragraph(
                "<b>Límite máximo</b>",
                table_style,
            ),
            Paragraph(
                f"${evaluacion['limite']:,.2f}",
                table_style,
            ),
        ],
        [
            Paragraph(
                "<b>Estado</b>",
                table_style,
            ),
            Paragraph(
                limpiar_texto_pdf(
                    estado
                ),
                table_style,
            ),
        ],
    ]

    tabla_resumen = Table(
        resumen,
        colWidths=[
            220,
            320,
        ],
    )

    tabla_resumen.setStyle(
        TableStyle(
            [
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
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#F0F4F8"
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
                    6,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    story.append(
        tabla_resumen
    )

    # --------------------------------------------------------
    # APROVECHAMIENTO
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            14,
        )
    )

    story.append(
        Paragraph(
            "APROVECHAMIENTO",
            section_style,
        )
    )

    aprovechamiento = plan.get(
        "aprovechamiento",
        "",
    )

    story.append(
        Paragraph(
            limpiar_texto_pdf(
                aprovechamiento
            ),
            body_style,
        )
    )

    # --------------------------------------------------------
    # NOTA
    # --------------------------------------------------------

    story.append(
        Spacer(
            1,
            12,
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
                "Los precios utilizados corresponden a "
                "precios consultados en catálogos públicos "
                "o a precios de respaldo previamente "
                "verificados. Los precios pueden cambiar "
                "por promociones, existencias, zona y "
                "fecha de compra."
            ),
            small_style,
        )
    )

    # --------------------------------------------------------
    # PIE
    # --------------------------------------------------------

    def pie_pagina(
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

    doc.build(
        story,
        onFirstPage=pie_pagina,
        onLaterPages=pie_pagina,
    )

    return pdf_buffer.getvalue()


# ============================================================
# MOSTRAR PLAN
# ============================================================

def mostrar_plan(
    plan,
    evaluacion,
):

    st.success(
        "🎉 Plan generado correctamente."
    )

    st.markdown("---")

    # --------------------------------------------------------
    # RESUMEN SUPERIOR
    # --------------------------------------------------------

    total = evaluacion[
        "total"
    ]

    diferencia = evaluacion[
        "diferencia"
    ]

    limite = evaluacion[
        "limite"
    ]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Presupuesto",
            f"${evaluacion['presupuesto']:,.2f}",
        )

    with c2:
        st.metric(
            "Compra",
            f"${total:,.2f}",
        )

    with c3:
        st.metric(
            "Diferencia",
            f"${diferencia:,.2f}",
        )

    with c4:
        st.metric(
            "Límite máximo",
            f"${limite:,.2f}",
        )

    if evaluacion[
        "dentro_objetivo"
    ]:

        st.success(
            "✅ El plan quedó dentro del presupuesto."
        )

    elif evaluacion[
        "dentro_tolerancia"
    ]:

        st.warning(
            "⚠️ El plan utiliza parte de la "
            "tolerancia de $100 permitida."
        )

    else:

        st.error(
            "❌ El plan supera la tolerancia permitida."
        )

    # --------------------------------------------------------
    # DÍAS
    # --------------------------------------------------------

    for dia in plan.get(
        "days",
        [],
    ):

        numero = dia.get(
            "day",
            "",
        )

        st.markdown(
            f"## 📅 Día {numero}"
        )

        for comida in dia.get(
            "meals",
            [],
        ):

            tipo = comida.get(
                "tipo",
                "",
            )

            platillo = comida.get(
                "platillo",
                "",
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {tipo}: {platillo}"
                )

                st.markdown(
                    "**Ingredientes**"
                )

                for ingrediente in comida.get(
                    "ingredientes",
                    [],
                ):

                    st.markdown(
                        f"- {ingrediente}"
                    )

                st.markdown(
                    "**Preparación**"
                )

                for numero_paso, paso in enumerate(
                    comida.get(
                        "preparacion",
                        [],
                    ),
                    start=1,
                ):

                    st.markdown(
                        f"{numero_paso}. {paso}"
                    )

    # --------------------------------------------------------
    # COMPRAS
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        "## 🛒 Lista de compras"
    )

    compras = plan.get(
        "shopping_list",
        [],
    )

    if compras:

        filas = []

        for item in compras:

            filas.append(
                {
                    "Tienda": item[
                        "tienda"
                    ],
                    "Producto": item[
                        "producto"
                    ],
                    "Presentación": item[
                        "descripcion"
                    ],
                    "Cantidad": (
                        f"{item['cantidad']:g} "
                        f"{item['unidad']}"
                    ),
                    "Precio": (
                        f"${item['precio_unitario']:,.2f}"
                    ),
                    "Total": (
                        f"${item['total']:,.2f}"
                    ),
                }
            )

        st.dataframe(
            filas,
            use_container_width=True,
            hide_index=True,
        )

    # --------------------------------------------------------
    # APROVECHAMIENTO
    # --------------------------------------------------------

    st.markdown(
        "## ♻️ Aprovechamiento"
    )

    st.write(
        plan.get(
            "aprovechamiento",
            "",
        )
    )


# ============================================================
# GENERACIÓN
# ============================================================

if st.button(
    "🚀 Generar Plan Inteligente",
    use_container_width=True,
):

    # --------------------------------------------------------
    # VALIDACIONES
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # LÍMITE
    # --------------------------------------------------------

    limite_presupuesto = (
        float(presupuesto)
        + TOLERANCIA_PRESUPUESTO
    )

    # --------------------------------------------------------
    # CATÁLOGO
    # --------------------------------------------------------

    with st.spinner(
        "🛒 Consultando productos y precios..."
    ):

        catalogo = crear_catalogo_seleccionado(
            tiendas_seleccionadas
        )

    if not catalogo:

        st.error(
            "❌ No fue posible obtener productos "
            "de las tiendas seleccionadas."
        )

        st.stop()

    # --------------------------------------------------------
    # ASIGNAR ID
    # --------------------------------------------------------

    for indice, producto in enumerate(
        catalogo,
        start=1,
    ):

        producto["id"] = indice

    # --------------------------------------------------------
    # CATALOGO PARA GROQ
    # --------------------------------------------------------

    catalogo_texto = "\n".join(
        [
            (
                f"ID={p['id']} | "
                f"Tienda={p['tienda']} | "
                f"Categoría={p['categoria']} | "
                f"Producto={p['nombre']} | "
                f"Presentación={p['descripcion']} | "
                f"Precio=${p['precio']:.2f} | "
                f"Fuente={p['fuente_precio']}"
            )
            for p in catalogo
        ]
    )

    # --------------------------------------------------------
    # PROTEÍNAS
    # --------------------------------------------------------

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
                f"ID={p['id']} | "
                f"{p['categoria']} | "
                f"{p['nombre']} | "
                f"{p['descripcion']} | "
                f"${p['precio']:.2f}"
            )
            for p in categorias_proteina
        ]
    )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt_text = f"""
Eres KashCook AI, un chef profesional y planificador
de alimentación familiar.

Tu trabajo es crear un menú REALISTA, completo y
económicamente controlado.

========================================================
DATOS DEL USUARIO
========================================================

Personas: {personas}

Días: {dias}

Presupuesto objetivo:
${presupuesto:.2f} MXN

Tolerancia máxima:
${TOLERANCIA_PRESUPUESTO:.2f}

Límite absoluto:
${limite_presupuesto:.2f}

Tiempos:
{', '.join(tiempos)}

Estilos:
{', '.join(estilos_seleccionados)}

Utensilios:
{', '.join(utensilios)}

Restricciones:
{restringidos if restringidos else 'Ninguna'}

TIENDAS SELECCIONADAS POR EL USUARIO:
{', '.join(tiendas_seleccionadas)}

========================================================
REGLA FUNDAMENTAL DE TIENDAS
========================================================

El usuario eligió las tiendas.

NO compares precios entre tiendas.

NO decidas qué tienda es más barata.

NO cambies de tienda buscando el menor precio.

Puedes utilizar productos únicamente de las tiendas
seleccionadas.

Si hay varias tiendas seleccionadas, puedes utilizar
productos de cualquiera de ellas.

========================================================
CATÁLOGO REAL
========================================================

Los siguientes productos son los únicos productos
que puedes utilizar para generar la lista de compras.

NO inventes productos.

NO inventes precios.

NO inventes marcas.

NO inventes presentaciones.

CATÁLOGO:

{catalogo_texto}

========================================================
PROTEÍNAS DISPONIBLES
========================================================

{proteinas_texto}

========================================================
REGLAS DEL MENÚ
========================================================

Genera exactamente {dias} días.

Cada día debe contener exactamente estos tiempos:

{', '.join(tiempos)}

NO utilices "Almuerzo".

Varía las proteínas.

NO hagas pollo todos los días.

Utiliza, cuando el presupuesto lo permita:

- pollo
- res
- puerco
- pescado
- atún
- huevo

Intenta utilizar al menos 4 fuentes diferentes
de proteína durante todo el plan cuando haya
suficientes productos disponibles.

No repitas exactamente el mismo platillo.

Reutiliza ingredientes inteligentemente para reducir
desperdicio.

Respeta estrictamente las restricciones y alergias.

Utiliza únicamente los utensilios disponibles.

========================================================
PRESUPUESTO
========================================================

Presupuesto objetivo:
${presupuesto:.2f}

Límite absoluto:
${limite_presupuesto:.2f}

PRIORIDAD:

1. Intenta quedar por debajo o igual al presupuesto
   objetivo.

2. Si es imposible, puedes superar el presupuesto.

3. JAMÁS superes el límite de:
   ${limite_presupuesto:.2f}

La tolerancia de $100 NO significa que debas gastar
los $100 adicionales.

Úsala solamente cuando sea necesario.

========================================================
RECETAS
========================================================

Las recetas deben ser COMPLETAS.

Cada comida debe contener:

Ingredientes:
- cantidades
- ingredientes

Preparación:
- pasos numerados
- orden lógico
- tiempos aproximados cuando sean útiles
- cocción adecuada

NO resumas.

NO omitas pasos.

NO uses frases vacías como:
"cocina hasta que esté listo".

========================================================
LISTA DE COMPRAS
========================================================

La lista debe contener solamente los productos
realmente necesarios.

MUY IMPORTANTE:

Cada producto debe utilizar el ID exacto del catálogo.

No inventes IDs.

No utilices productos fuera del catálogo.

Para cada producto indica:

producto_id
cantidad
unidad

Ejemplo:

{{
  "producto_id": 17,
  "cantidad": 2,
  "unidad": "latas"
}}

La cantidad representa cuántas unidades de esa
presentación se deben comprar.

========================================================
APROVECHAMIENTO
========================================================

Explica cómo aprovechar ingredientes sobrantes.

========================================================
FORMATO JSON OBLIGATORIO
========================================================

RESPONDE ÚNICAMENTE JSON.

NO Markdown.

NO explicaciones antes del JSON.

NO explicaciones después del JSON.

La estructura EXACTA debe ser:

{{
  "days": [
    {{
      "day": 1,
      "meals": [
        {{
          "tipo": "DESAYUNO",
          "platillo": "Nombre",
          "ingredientes": [
            "2 huevos",
            "1 tomate"
          ],
          "preparacion": [
            "Paso 1",
            "Paso 2",
            "Paso 3"
          ]
        }}
      ]
    }}
  ],
  "shopping_list": [
    {{
      "producto_id": 1,
      "cantidad": 1,
      "unidad": "kg"
    }}
  ],
  "aprovechamiento": "Explicación..."
}}

========================================================
REGLA CRÍTICA
========================================================

No inventes precios.

No inventes productos.

No inventes IDs.

No superes ${limite_presupuesto:.2f}.

Primero intenta quedar en ${presupuesto:.2f} o menos.

Las recetas deben estar completas.
"""

    # --------------------------------------------------------
    # LLAMAR GROQ
    # --------------------------------------------------------

    with st.spinner(
        "🤖 KashCook está diseñando tu plan..."
    ):

        try:

            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Responde únicamente JSON válido."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt_text,
                    },
                ],
                temperature=0.15,
                max_tokens=14000,
            )

            respuesta = (
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

    # --------------------------------------------------------
    # PARSEAR
    # --------------------------------------------------------

    plan = extraer_json(
        respuesta
    )

    if plan is None:

        st.error(
            "❌ KashCook recibió una respuesta que "
            "no pudo convertir a JSON."
        )

        st.code(
            respuesta,
            language="text",
        )

        st.stop()

    # --------------------------------------------------------
    # NORMALIZAR
    # --------------------------------------------------------

    plan = normalizar_plan(
        plan,
        catalogo,
        dias,
        tiempos,
    )

    if plan is None:

        st.error(
            "❌ El plan generado no tiene la "
            "estructura esperada."
        )

        st.stop()

    # --------------------------------------------------------
    # VALIDAR DÍAS
    # --------------------------------------------------------

    if len(
        plan.get(
            "days",
            [],
        )
    ) < dias:

        st.error(
            "❌ KashCook no generó todos los días "
            "solicitados."
        )

        st.stop()

    # --------------------------------------------------------
    # PRESUPUESTO
    # --------------------------------------------------------

    evaluacion = evaluar_presupuesto(
        plan.get(
            "shopping_list",
            [],
        ),
        presupuesto,
    )

    # --------------------------------------------------------
    # SI SUPERA $100
    # --------------------------------------------------------

    if not evaluacion[
        "dentro_tolerancia"
    ]:

        st.warning(
            "⚠️ El primer plan supera la tolerancia "
            "de $100. KashCook intentará reajustarlo."
        )

        prompt_ajuste = f"""
Revisa el siguiente plan de alimentación.

Presupuesto objetivo:
${presupuesto:.2f}

Límite absoluto:
${limite_presupuesto:.2f}

El plan actual supera el límite.

Debes reducir el costo sin eliminar comidas
ni días.

Prioriza:

1. reducir cantidades excesivas;
2. utilizar productos del mismo catálogo;
3. mantener variedad de proteínas;
4. reutilizar ingredientes;
5. conservar recetas realistas.

NO cambies de tienda.

NO inventes productos.

NO inventes precios.

UTILIZA ÚNICAMENTE LOS IDs DEL CATÁLOGO.

Debes devolver ÚNICAMENTE JSON válido con esta estructura:

{{
  "days": [...],
  "shopping_list": [
    {{
      "producto_id": 1,
      "cantidad": 1,
      "unidad": "kg"
    }}
  ],
  "aprovechamiento": "..."
}}

PLAN ACTUAL:

{json.dumps(plan, ensure_ascii=False)}

CATÁLOGO:

{catalogo_texto}
"""

        try:

            ajuste = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Responde únicamente JSON válido."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt_ajuste,
                    },
                ],
                temperature=0.10,
                max_tokens=14000,
            )

            respuesta_ajuste = (
                ajuste
                .choices[0]
                .message
                .content
            )

            plan_ajustado = extraer_json(
                respuesta_ajuste
            )

            if plan_ajustado:

                plan_ajustado = normalizar_plan(
                    plan_ajustado,
                    catalogo,
                    dias,
                    tiempos,
                )

                nueva_evaluacion = evaluar_presupuesto(
                    plan_ajustado.get(
                        "shopping_list",
                        [],
                    ),
                    presupuesto,
                )

                if nueva_evaluacion[
                    "dentro_tolerancia"
                ]:

                    plan = plan_ajustado
                    evaluacion = nueva_evaluacion

        except Exception:
            pass

    # --------------------------------------------------------
    # VALIDACIÓN FINAL
    # --------------------------------------------------------

    if not evaluacion[
        "dentro_tolerancia"
    ]:

        st.error(
            "❌ No fue posible generar un plan dentro "
            "del presupuesto + $100 de tolerancia."
        )

        st.info(
            "Prueba aumentando el presupuesto, "
            "reduciendo personas o disminuyendo días."
        )

        st.stop()

    # --------------------------------------------------------
    # MOSTRAR
    # --------------------------------------------------------

    mostrar_plan(
        plan,
        evaluacion,
    )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    with st.spinner(
        "📄 Preparando PDF completo..."
    ):

        try:

            pdf_bytes = generar_pdf(
                plan,
                dias,
                personas,
                presupuesto,
                tiendas_seleccionadas,
                evaluacion,
            )

            st.download_button(
                label=(
                    "📄 Descargar Plan KashCook en PDF"
                ),
                data=pdf_bytes,
                file_name="KashCook_Plan.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as e:

            st.error(
                f"Error al generar PDF: {e}"
            )
