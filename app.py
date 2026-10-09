import io
import json
import math
import re
import html
import copy
import time
from datetime import datetime
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

import streamlit as st
from groq import Groq

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="KashCook AI",
    page_icon="🍳",
    layout="wide",
)

APP_BUILD = "2026.10.08-live-v4-reconstruida-2026.10.09"

TIENDAS_DISPONIBLES = [
    "Alsuper",
    "Walmart",
    "Soriana",
    "Bodega Aurrerá",
]

TOLERANCIA_PRESUPUESTO = 100.00

# Si el costo queda por debajo de este porcentaje,
# KashCook intentará mejorar el uso del presupuesto.
MIN_UTILIZACION_PRESUPUESTO = 0.90


# ============================================================
# FUNCIÓN PARA CREAR PRODUCTOS
# ============================================================

def producto(
    id_producto,
    tienda,
    nombre,
    categoria,
    ingrediente_base,
    presentacion,
    contenido,
    unidad_contenido,
    precio,
):
    return {
        "id": id_producto,
        "tienda": tienda,
        "nombre": nombre,
        "categoria": categoria,
        "ingrediente_base": ingrediente_base,
        "presentacion": presentacion,
        "contenido": float(contenido),
        "unidad_contenido": unidad_contenido,
        "precio": float(precio),
    }


# ============================================================
# CATÁLOGOS
# ============================================================

def crear_catalogos():

    catalogos = {}

    # ========================================================
    # ALSUPER
    # ========================================================

    catalogos["Alsuper"] = [

        producto(
            "alsuper_pollo",
            "Alsuper",
            "Pechuga de pollo",
            "proteina",
            "pollo",
            "Charola 1 kg",
            1,
            "kg",
            179,
        ),

        producto(
            "alsuper_muslo",
            "Alsuper",
            "Muslo y pierna de pollo",
            "proteina",
            "pollo",
            "Charola 1 kg",
            1,
            "kg",
            105,
        ),

        producto(
            "alsuper_res",
            "Alsuper",
            "Carne de res para guisar",
            "proteina",
            "res",
            "Charola 500 g",
            500,
            "g",
            115,
        ),

        producto(
            "alsuper_molida",
            "Alsuper",
            "Carne molida de res",
            "proteina",
            "res",
            "Charola 500 g",
            500,
            "g",
            105,
        ),

        producto(
            "alsuper_puerco",
            "Alsuper",
            "Carne de cerdo",
            "proteina",
            "cerdo",
            "Charola 500 g",
            500,
            "g",
            85,
        ),

        producto(
            "alsuper_pescado",
            "Alsuper",
            "Filete de pescado",
            "proteina",
            "pescado",
            "Bolsa 500 g",
            500,
            "g",
            125,
        ),

        producto(
            "alsuper_atun",
            "Alsuper",
            "Atún en agua",
            "proteina",
            "atun",
            "Lata 140 g",
            140,
            "g",
            28,
        ),

        producto(
            "alsuper_camaron",
            "Alsuper",
            "Camarón limpio",
            "proteina",
            "camaron",
            "Bolsa 500 g",
            500,
            "g",
            179,
        ),

        producto(
            "alsuper_sardina",
            "Alsuper",
            "Sardinas en tomate",
            "proteina",
            "sardina",
            "Lata 425 g",
            425,
            "g",
            32,
        ),

        producto(
            "alsuper_huevo",
            "Alsuper",
            "Huevo blanco",
            "proteina",
            "huevo",
            "Cartón 18 piezas",
            18,
            "pieza",
            68,
        ),

        producto(
            "alsuper_arroz",
            "Alsuper",
            "Arroz blanco",
            "cereal",
            "arroz",
            "Bolsa 1 kg",
            1,
            "kg",
            38,
        ),

        producto(
            "alsuper_frijol",
            "Alsuper",
            "Frijol pinto",
            "leguminosa",
            "frijol",
            "Bolsa 1 kg",
            1,
            "kg",
            42,
        ),

        producto(
            "alsuper_tortilla",
            "Alsuper",
            "Tortilla de maíz",
            "cereal",
            "tortilla",
            "Paquete 1 kg",
            1,
            "kg",
            30,
        ),

        producto(
            "alsuper_papa",
            "Alsuper",
            "Papa blanca",
            "verdura",
            "papa",
            "Bolsa 1 kg",
            1,
            "kg",
            34,
        ),

        producto(
            "alsuper_tomate",
            "Alsuper",
            "Tomate rojo",
            "verdura",
            "tomate",
            "Bolsa 1 kg",
            1,
            "kg",
            39,
        ),

        producto(
            "alsuper_cebolla",
            "Alsuper",
            "Cebolla blanca",
            "verdura",
            "cebolla",
            "Bolsa 1 kg",
            1,
            "kg",
            35,
        ),

        producto(
            "alsuper_zanahoria",
            "Alsuper",
            "Zanahoria",
            "verdura",
            "zanahoria",
            "Bolsa 1 kg",
            1,
            "kg",
            29,
        ),

        producto(
            "alsuper_lechuga",
            "Alsuper",
            "Lechuga romana",
            "verdura",
            "lechuga",
            "Pieza",
            1,
            "pieza",
            24,
        ),

        producto(
            "alsuper_calabaza",
            "Alsuper",
            "Calabacita",
            "verdura",
            "calabaza",
            "Bolsa 1 kg",
            1,
            "kg",
            42,
        ),

        producto(
            "alsuper_queso",
            "Alsuper",
            "Queso fresco",
            "lacteo",
            "queso",
            "Paquete 400 g",
            400,
            "g",
            75,
        ),

        producto(
            "alsuper_aceite",
            "Alsuper",
            "Aceite vegetal",
            "despensa",
            "aceite",
            "Botella 850 ml",
            850,
            "ml",
            42,
        ),
    ]

    # ========================================================
    # WALMART
    # ========================================================

    catalogos["Walmart"] = [

        producto(
            "walmart_pollo",
            "Walmart",
            "Pechuga de pollo",
            "proteina",
            "pollo",
            "Paquete 1 kg",
            1,
            "kg",
            185,
        ),

        producto(
            "walmart_muslo",
            "Walmart",
            "Muslo y pierna de pollo",
            "proteina",
            "pollo",
            "Paquete 1 kg",
            1,
            "kg",
            110,
        ),

        producto(
            "walmart_res",
            "Walmart",
            "Carne de res para guisar",
            "proteina",
            "res",
            "Paquete 500 g",
            500,
            "g",
            120,
        ),

        producto(
            "walmart_molida",
            "Walmart",
            "Carne molida de res",
            "proteina",
            "res",
            "Paquete 500 g",
            500,
            "g",
            110,
        ),

        producto(
            "walmart_puerco",
            "Walmart",
            "Carne de cerdo",
            "proteina",
            "cerdo",
            "Paquete 500 g",
            500,
            "g",
            88,
        ),

        producto(
            "walmart_pescado",
            "Walmart",
            "Filete de pescado",
            "proteina",
            "pescado",
            "Paquete 500 g",
            500,
            "g",
            130,
        ),

        producto(
            "walmart_atun",
            "Walmart",
            "Atún en agua",
            "proteina",
            "atun",
            "Lata 140 g",
            140,
            "g",
            30,
        ),

        producto(
            "walmart_camaron",
            "Walmart",
            "Camarón limpio",
            "proteina",
            "camaron",
            "Bolsa 500 g",
            500,
            "g",
            185,
        ),

        producto(
            "walmart_sardina",
            "Walmart",
            "Sardinas en tomate",
            "proteina",
            "sardina",
            "Lata 425 g",
            425,
            "g",
            35,
        ),

        producto(
            "walmart_huevo",
            "Walmart",
            "Huevo blanco",
            "proteina",
            "huevo",
            "Cartón 18 piezas",
            18,
            "pieza",
            70,
        ),

        producto(
            "walmart_arroz",
            "Walmart",
            "Arroz blanco",
            "cereal",
            "arroz",
            "Bolsa 1 kg",
            1,
            "kg",
            40,
        ),

        producto(
            "walmart_frijol",
            "Walmart",
            "Frijol pinto",
            "leguminosa",
            "frijol",
            "Bolsa 1 kg",
            1,
            "kg",
            45,
        ),

        producto(
            "walmart_tortilla",
            "Walmart",
            "Tortilla de maíz",
            "cereal",
            "tortilla",
            "Paquete 1 kg",
            1,
            "kg",
            32,
        ),

        producto(
            "walmart_papa",
            "Walmart",
            "Papa blanca",
            "verdura",
            "papa",
            "Bolsa 1 kg",
            1,
            "kg",
            36,
        ),

        producto(
            "walmart_tomate",
            "Walmart",
            "Tomate rojo",
            "verdura",
            "tomate",
            "Bolsa 1 kg",
            1,
            "kg",
            40,
        ),

        producto(
            "walmart_cebolla",
            "Walmart",
            "Cebolla blanca",
            "verdura",
            "cebolla",
            "Bolsa 1 kg",
            1,
            "kg",
            36,
        ),

        producto(
            "walmart_zanahoria",
            "Walmart",
            "Zanahoria",
            "verdura",
            "zanahoria",
            "Bolsa 1 kg",
            1,
            "kg",
            31,
        ),

        producto(
            "walmart_lechuga",
            "Walmart",
            "Lechuga romana",
            "verdura",
            "lechuga",
            "Pieza",
            1,
            "pieza",
            26,
        ),

        producto(
            "walmart_queso",
            "Walmart",
            "Queso fresco",
            "lacteo",
            "queso",
            "Paquete 400 g",
            400,
            "g",
            78,
        ),

        producto(
            "walmart_aceite",
            "Walmart",
            "Aceite vegetal",
            "despensa",
            "aceite",
            "Botella 850 ml",
            850,
            "ml",
            44,
        ),
    ]

    # ========================================================
    # SORIANA
    # ========================================================

    catalogos["Soriana"] = [

        producto(
            "soriana_pollo",
            "Soriana",
            "Pechuga de pollo",
            "proteina",
            "pollo",
            "Paquete 1 kg",
            1,
            "kg",
            182,
        ),

        producto(
            "soriana_muslo",
            "Soriana",
            "Muslo y pierna de pollo",
            "proteina",
            "pollo",
            "Paquete 1 kg",
            1,
            "kg",
            108,
        ),

        producto(
            "soriana_res",
            "Soriana",
            "Carne de res para guisar",
            "proteina",
            "res",
            "Paquete 500 g",
            500,
            "g",
            118,
        ),

        producto(
            "soriana_molida",
            "Soriana",
            "Carne molida de res",
            "proteina",
            "res",
            "Paquete 500 g",
            500,
            "g",
            108,
        ),

        producto(
            "soriana_puerco",
            "Soriana",
            "Carne de cerdo",
            "proteina",
            "cerdo",
            "Paquete 500 g",
            500,
            "g",
            86,
        ),

        producto(
            "soriana_pescado",
            "Soriana",
            "Filete de pescado",
            "proteina",
            "pescado",
            "Paquete 500 g",
            500,
            "g",
            128,
        ),

        producto(
            "soriana_atun",
            "Soriana",
            "Atún en agua",
            "proteina",
            "atun",
            "Lata 140 g",
            140,
            "g",
            29,
        ),

        producto(
            "soriana_camaron",
            "Soriana",
            "Camarón limpio",
            "proteina",
            "camaron",
            "Bolsa 500 g",
            500,
            "g",
            189,
        ),

        producto(
            "soriana_sardina",
            "Soriana",
            "Sardinas en tomate",
            "proteina",
            "sardina",
            "Lata 425 g",
            425,
            "g",
            33,
        ),

        producto(
            "soriana_huevo",
            "Soriana",
            "Huevo blanco",
            "proteina",
            "huevo",
            "Cartón 18 piezas",
            18,
            "pieza",
            69,
        ),

        producto(
            "soriana_arroz",
            "Soriana",
            "Arroz blanco",
            "cereal",
            "arroz",
            "Bolsa 1 kg",
            1,
            "kg",
            39,
        ),

        producto(
            "soriana_frijol",
            "Soriana",
            "Frijol pinto",
            "leguminosa",
            "frijol",
            "Bolsa 1 kg",
            1,
            "kg",
            44,
        ),

        producto(
            "soriana_tortilla",
            "Soriana",
            "Tortilla de maíz",
            "cereal",
            "tortilla",
            "Paquete 1 kg",
            1,
            "kg",
            31,
        ),

        producto(
            "soriana_papa",
            "Soriana",
            "Papa blanca",
            "verdura",
            "papa",
            "Bolsa 1 kg",
            1,
            "kg",
            35,
        ),

        producto(
            "soriana_tomate",
            "Soriana",
            "Tomate rojo",
            "verdura",
            "tomate",
            "Bolsa 1 kg",
            1,
            "kg",
            41,
        ),

        producto(
            "soriana_cebolla",
            "Soriana",
            "Cebolla blanca",
            "verdura",
            "cebolla",
            "Bolsa 1 kg",
            1,
            "kg",
            37,
        ),

        producto(
            "soriana_zanahoria",
            "Soriana",
            "Zanahoria",
            "verdura",
            "zanahoria",
            "Bolsa 1 kg",
            1,
            "kg",
            30,
        ),

        producto(
            "soriana_lechuga",
            "Soriana",
            "Lechuga romana",
            "verdura",
            "lechuga",
            "Pieza",
            1,
            "pieza",
            25,
        ),

        producto(
            "soriana_queso",
            "Soriana",
            "Queso fresco",
            "lacteo",
            "queso",
            "Paquete 400 g",
            400,
            "g",
            77,
        ),

        producto(
            "soriana_aceite",
            "Soriana",
            "Aceite vegetal",
            "despensa",
            "aceite",
            "Botella 850 ml",
            850,
            "ml",
            43,
        ),
    ]

    # ========================================================
    # BODEGA AURRERÁ
    # ========================================================

    catalogos["Bodega Aurrerá"] = [

        producto(
            "bodega_pollo",
            "Bodega Aurrerá",
            "Pechuga de pollo",
            "proteina",
            "pollo",
            "Paquete 1 kg",
            1,
            "kg",
            175,
        ),

        producto(
            "bodega_muslo",
            "Bodega Aurrerá",
            "Muslo y pierna de pollo",
            "proteina",
            "pollo",
            "Paquete 1 kg",
            1,
            "kg",
            99,
        ),

        producto(
            "bodega_res",
            "Bodega Aurrerá",
            "Carne de res para guisar",
            "proteina",
            "res",
            "Paquete 500 g",
            500,
            "g",
            112,
        ),

        producto(
            "bodega_molida",
            "Bodega Aurrerá",
            "Carne molida de res",
            "proteina",
            "res",
            "Paquete 500 g",
            500,
            "g",
            102,
        ),

        producto(
            "bodega_puerco",
            "Bodega Aurrerá",
            "Carne de cerdo",
            "proteina",
            "cerdo",
            "Paquete 500 g",
            500,
            "g",
            82,
        ),

        producto(
            "bodega_pescado",
            "Bodega Aurrerá",
            "Filete de pescado",
            "proteina",
            "pescado",
            "Paquete 500 g",
            500,
            "g",
            119,
        ),

        producto(
            "bodega_atun",
            "Bodega Aurrerá",
            "Atún en agua",
            "proteina",
            "atun",
            "Lata 140 g",
            140,
            "g",
            26,
        ),

        producto(
            "bodega_camaron",
            "Bodega Aurrerá",
            "Camarón limpio",
            "proteina",
            "camaron",
            "Bolsa 500 g",
            500,
            "g",
            175,
        ),

        producto(
            "bodega_sardina",
            "Bodega Aurrerá",
            "Sardinas en tomate",
            "proteina",
            "sardina",
            "Lata 425 g",
            425,
            "g",
            30,
        ),

        producto(
            "bodega_huevo",
            "Bodega Aurrerá",
            "Huevo blanco",
            "proteina",
            "huevo",
            "Cartón 18 piezas",
            18,
            "pieza",
            64,
        ),

        producto(
            "bodega_arroz",
            "Bodega Aurrerá",
            "Arroz blanco",
            "cereal",
            "arroz",
            "Bolsa 1 kg",
            1,
            "kg",
            35,
        ),

        producto(
            "bodega_frijol",
            "Bodega Aurrerá",
            "Frijol pinto",
            "leguminosa",
            "frijol",
            "Bolsa 1 kg",
            1,
            "kg",
            39,
        ),

        producto(
            "bodega_tortilla",
            "Bodega Aurrerá",
            "Tortilla de maíz",
            "cereal",
            "tortilla",
            "Paquete 1 kg",
            1,
            "kg",
            29,
        ),

        producto(
            "bodega_papa",
            "Bodega Aurrerá",
            "Papa blanca",
            "verdura",
            "papa",
            "Bolsa 1 kg",
            1,
            "kg",
            32,
        ),

        producto(
            "bodega_tomate",
            "Bodega Aurrerá",
            "Tomate rojo",
            "verdura",
            "tomate",
            "Bolsa 1 kg",
            1,
            "kg",
            37,
        ),

        producto(
            "bodega_cebolla",
            "Bodega Aurrerá",
            "Cebolla blanca",
            "verdura",
            "cebolla",
            "Bolsa 1 kg",
            1,
            "kg",
            33,
        ),

        producto(
            "bodega_zanahoria",
            "Bodega Aurrerá",
            "Zanahoria",
            "verdura",
            "zanahoria",
            "Bolsa 1 kg",
            1,
            "kg",
            28,
        ),

        producto(
            "bodega_lechuga",
            "Bodega Aurrerá",
            "Lechuga romana",
            "verdura",
            "lechuga",
            "Pieza",
            1,
            "pieza",
            23,
        ),

        producto(
            "bodega_queso",
            "Bodega Aurrerá",
            "Queso fresco",
            "lacteo",
            "queso",
            "Paquete 400 g",
            400,
            "g",
            72,
        ),

        producto(
            "bodega_aceite",
            "Bodega Aurrerá",
            "Aceite vegetal",
            "despensa",
            "aceite",
            "Botella 850 ml",
            850,
            "ml",
            40,
        ),
    ]

    return catalogos


CATALOGOS = crear_catalogos()

# Transparencia de precios: estos valores son referencias precargadas.
# Nunca se presentan como precios de caja verificados al momento de consulta.
for _lista in CATALOGOS.values():
    for _p in _lista:
        _p["estado_precio"] = "Referencia"
        _p["ultima_verificacion"] = None
        _p["fuente_precio"] = "Catálogo interno de referencia"


# ============================================================
# VERIFICACIÓN DE PRECIOS EN TIEMPO REAL
# ============================================================
# Regla de confianza: un precio solo entra al cálculo como "verificado" si
# fue encontrado durante esta consulta en el dominio oficial de la tienda.
# Si la tienda no responde o no podemos identificar con suficiente confianza
# el producto/precio, KashCook NO utiliza el precio de referencia.

PRECIO_CACHE = {}
PRECIO_CACHE_TTL = 15 * 60

BUSQUEDAS_TIENDA = {
    "Walmart": [
        "https://www.walmart.com.mx/search?q={q}",
        "https://www.walmart.com.mx/search?query={q}",
    ],
    "Bodega Aurrerá": [
        "https://www.bodegaaurrera.com.mx/search?q={q}",
        "https://www.bodegaaurrera.com.mx/search?query={q}",
    ],
    "Soriana": [
        "https://www.soriana.com/buscar?q={q}",
        "https://www.soriana.com/buscar?q={q}&search-button=",
    ],
    "Alsuper": [
        "https://alsuper.com/buscar?query={q}",
        "https://alsuper.com/search?search={q}",
        "https://alsuper.com/busqueda?query={q}",
    ],
}

DOMINIOS_OFICIALES = {
    "Walmart": "walmart.com.mx",
    "Bodega Aurrerá": "bodegaaurrera.com.mx",
    "Soriana": "soriana.com",
    "Alsuper": "alsuper.com",
}

CONSULTAS_PRECIO = {
    "pollo": "pechuga de pollo",
    "res": "carne de res",
    "molida": "carne molida de res",
    "puerco": "carne de cerdo",
    "pescado": "filete de pescado",
    "atun": "atun en agua",
    "camaron": "camaron limpio",
    "sardina": "sardinas en tomate",
    "huevo": "huevo blanco",
    "arroz": "arroz blanco",
    "frijol": "frijol pinto",
    "tortilla": "tortilla de maiz",
    "papa": "papa blanca",
    "tomate": "tomate rojo",
    "cebolla": "cebolla blanca",
    "zanahoria": "zanahoria",
    "lechuga": "lechuga romana",
    "calabaza": "calabacita",
    "queso": "queso fresco",
    "aceite": "aceite vegetal",
}


def _precio_float(valor):
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        txt = str(valor).replace("$", "").replace(",", "").strip()
        m = re.search(r"\d+(?:\.\d{1,2})?", txt)
        return float(m.group(0)) if m else None
    except Exception:
        return None


def _extraer_precio_oficial(html_text, query):
    """Extrae un precio de una página oficial sin aceptar datos de terceros."""
    soup = BeautifulSoup(html_text, "html.parser")
    candidatos = []

    # JSON-LD es preferible a texto libre.
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text(" ", strip=True)
        try:
            data = json.loads(raw)
        except Exception:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            obj = stack.pop()
            if isinstance(obj, dict):
                if "offers" in obj:
                    offers = obj["offers"]
                    if isinstance(offers, dict):
                        offers = [offers]
                    for offer in offers or []:
                        if isinstance(offer, dict):
                            val = _precio_float(offer.get("price") or offer.get("lowPrice"))
                            if val and val > 0:
                                candidatos.append(val)
                for v in obj.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(obj, list):
                stack.extend(obj)

    query_tokens = [x for x in normalizar_texto(query).split() if len(x) >= 3]
    def contexto_coincide(node):
        contexto = normalizar_texto(node.parent.get_text(" ", strip=True) if node.parent else node.get_text(" ", strip=True))
        # No exigimos todos los tokens para productos frescos, pero sí al menos
        # uno relevante y preferimos coincidencia de dos o más.
        hits = sum(tok in contexto for tok in query_tokens)
        return hits >= min(2, len(query_tokens)) if query_tokens else True

    for sel in [
        'meta[itemprop="price"]', 'meta[property="product:price:amount"]',
        '[itemprop="price"]', '[data-testid*="price"]', '[class*="price"]',
    ]:
        for node in soup.select(sel):
            if not contexto_coincide(node):
                continue
            val = _precio_float(node.get("content") or node.get_text(" ", strip=True))
            if val and val > 0:
                candidatos.append(val)

    # Último recurso: busca precios cerca de la consulta, no el menor precio
    # arbitrario de toda la página de resultados.
    texto = soup.get_text(" ", strip=True)
    for m in re.finditer(r".{0,260}\$\s*([0-9]{1,5}(?:[,][0-9]{3})*(?:\.[0-9]{1,2})?).{0,260}", texto, flags=re.I):
        contexto = normalizar_texto(m.group(0))
        if query_tokens and sum(tok in contexto for tok in query_tokens) < min(2, len(query_tokens)):
            continue
        val = _precio_float(m.group(1))
        if val and 1 <= val <= 10000:
            candidatos.append(val)

    if not candidatos:
        return None
    # Para búsquedas de alimentos, el menor precio positivo suele corresponder a
    # una presentación económica, pero nunca se mezcla con el catálogo interno.
    return min(candidatos)


def _consultar_precio_tienda(tienda, ingrediente_base):
    consulta = CONSULTAS_PRECIO.get(ingrediente_base, ingrediente_base.replace("_", " "))
    clave = (tienda, ingrediente_base)
    ahora = time.time()
    cache = PRECIO_CACHE.get(clave)
    if cache and ahora - cache["ts"] < PRECIO_CACHE_TTL:
        return cache["resultado"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36",
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
    }
    resultado = None
    errores = []
    for plantilla in BUSQUEDAS_TIENDA.get(tienda, []):
        url = plantilla.format(q=quote_plus(consulta))
        try:
            r = requests.get(url, headers=headers, timeout=9, allow_redirects=True)
            dominio = DOMINIOS_OFICIALES[tienda]
            if r.status_code != 200 or dominio not in r.url or dominio not in str(r.headers.get("Content-Type", "")) and not r.text:
                errores.append(f"HTTP {r.status_code}")
                continue
            precio = _extraer_precio_oficial(r.text, consulta)
            if precio is not None:
                texto_oficial = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True)
                texto_norm = normalizar_texto(texto_oficial)
                venta_por_kg = bool(re.search(r"por\s+(kilogramo|kg)|\$/?\s*kg|kg\s*$", texto_norm))
                resultado = {
                    "precio": round(precio, 2),
                    "venta_por_kg": venta_por_kg,
                    "estado": "Verificado",
                    "ultima_verificacion": datetime.now().astimezone().isoformat(timespec="minutes"),
                    "fuente": r.url,
                }
                break
            errores.append("sin precio identificable")
        except Exception as exc:
            errores.append(str(exc)[:80])

    if resultado is None:
        resultado = {
            "precio": None,
            "venta_por_kg": False,
            "estado": "No disponible",
            "ultima_verificacion": datetime.now().astimezone().isoformat(timespec="minutes"),
            "fuente": DOMINIOS_OFICIALES.get(tienda, ""),
            "error": "; ".join(errores[-2:]),
        }
    PRECIO_CACHE[clave] = {"ts": ahora, "resultado": resultado}
    return resultado



def _inferir_presentacion_producto(nombre, descripcion=""):
    """Obtiene una presentación comercial de un nombre real de supermercado."""
    texto = f"{nombre} {descripcion}".strip()
    patrones = [
        (r"(\d+(?:\.\d+)?)\s*(kg|kilo|kilogramos)\b", "kg", 1),
        (r"(\d+(?:\.\d+)?)\s*(g|gr|gramos)\b", "g", 1),
        (r"(\d+(?:\.\d+)?)\s*(l|lt|litro|litros)\b", "l", 1),
        (r"(\d+(?:\.\d+)?)\s*(ml|mililitros)\b", "ml", 1),
        (r"(\d+)\s*(pzas?|piezas|unidades|uds?)\b", "pieza", 1),
        (r"(\d+)\s*(latas?|paquetes?|sobres?|botellas?)\b", "pieza", 1),
    ]
    t = normalizar_texto(texto)
    for patron, unidad, _ in patrones:
        m = re.search(patron, t, re.I)
        if m:
            valor = float(m.group(1))
            return valor, unidad, m.group(0)
    return None, None, ""


def _marca_desde_producto(nombre, brand=None):
    if brand:
        if isinstance(brand, dict):
            brand = brand.get("name")
        if str(brand).strip():
            return str(brand).strip()
    # Algunas páginas no exponen Brand en JSON-LD. Intentamos identificar marcas
    # frecuentes, incluyendo marcas propias, sin inventar una marca desconocida.
    conocidas = [
        "MiMarca", "Great Value", "Aurrera", "Extra Especial", "Precissimo",
        "Verde Valle", "La Costeña", "Herdez", "Norteñita", "San Marcos",
        "Lala", "Alpura", "NocheBuena", "Capullo", "Nutrioli", "Mazola",
        "Tuny", "Dolores", "Calmex", "El Mexicano", "Bachoco", "Pilgrim's",
        "Member's Mark", "Soriana", "Walmart", "Alsuper",
    ]
    n = normalizar_texto(nombre)
    for marca in conocidas:
        if normalizar_texto(marca) in n:
            return marca
    # Si no podemos identificar la marca con evidencia, no la inventamos.
    return "Marca no identificada"


def _producto_candidato_desde_json(obj, tienda, pagina_url, query):
    if not isinstance(obj, dict):
        return None
    if str(obj.get("@type", "")).lower() not in {"product", "productgroup"} and not obj.get("name"):
        return None
    nombre = str(obj.get("name") or "").strip()
    if not nombre:
        return None
    texto = normalizar_texto(f"{nombre} {obj.get('description','')}")
    tokens = [x for x in normalizar_texto(query).split() if len(x) >= 3]
    if tokens and sum(t in texto for t in tokens) < 1:
        return None
    offers = obj.get("offers") or {}
    if isinstance(offers, list):
        ofertas = offers
    else:
        ofertas = [offers]
    precios = []
    url_producto = obj.get("url") or pagina_url
    for offer in ofertas:
        if not isinstance(offer, dict):
            continue
        precio = _precio_float(offer.get("price") or offer.get("lowPrice"))
        if precio and precio > 0:
            precios.append((precio, offer.get("url") or url_producto))
    if not precios:
        return None
    precio, url_producto = min(precios, key=lambda x: x[0])
    contenido, unidad, texto_presentacion = _inferir_presentacion_producto(nombre, obj.get("description", ""))
    base = normalizar_texto(query).split()[0] if query else "producto"
    if not contenido:
        # Productos frescos suelen cotizarse por kg. Solo lo usamos cuando el
        # propio nombre/página contiene una señal de precio por peso.
        desc = normalizar_texto(str(obj.get("description", "")))
        if re.search(r"por\s*(kg|kilogramo)|\bkg\b", desc) and base in {"pollo","res","molida","puerco","pescado","camaron","papa","tomate","cebolla","zanahoria","lechuga","calabaza"}:
            contenido, unidad = 1.0, "kg"
        else:
            return None
    return {
        "nombre": nombre,
        "marca": _marca_desde_producto(nombre, obj.get("brand")),
        "precio": round(float(precio), 2),
        "contenido": float(contenido),
        "unidad_contenido": unidad,
        "presentacion": texto_presentacion or f"{contenido:g} {unidad}",
        "fuente_precio": str(url_producto or pagina_url),
        "tienda": tienda,
    }


\

def _valor_precio_json(valor):
    """Normaliza precios embebidos en JSON de páginas de supermercado."""
    if isinstance(valor, dict):
        for k in ("current", "amount", "value", "sellingPrice", "salePrice", "price"):
            if k in valor:
                v = _valor_precio_json(valor[k])
                if v is not None:
                    return v
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        return _precio_float(valor)
    return None


def _extraer_candidatos_json_embebido(html_text, query, tienda, pagina_url):
    """Lee productos/precios de estados JSON embebidos además de JSON-LD.

    Muchas tiendas dibujan las tarjetas con React/Next y el HTML visible llega
    vacío desde requests, pero el nombre/precio/presentación ya están en un
    script JSON. Solo acepta datos contenidos en una respuesta del dominio
    oficial de la tienda.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    tokens = [x for x in normalizar_texto(query).split() if len(x) >= 3]
    found = []
    seen = set()
    name_keys = ("name", "productName", "product_name", "displayName", "display_name", "title", "shortDescription")
    price_keys = ("sellingPrice", "salePrice", "currentPrice", "finalPrice", "offerPrice", "price", "lowPrice", "priceValue", "specialPrice")
    desc_keys = ("description", "shortDescription", "productDescription", "size", "packageSize", "netContent", "weight", "volume", "presentation", "unitOfMeasure")
    brand_keys = ("brand", "brandName", "manufacturer")
    url_keys = ("productUrl", "canonicalUrl", "url", "pdpUrl", "productPageUrl", "slug")

    def walk(obj, depth=0):
        if depth > 30:
            return
        if isinstance(obj, dict):
            # First traverse children (schemas often wrap data several levels deep).
            name = next((obj.get(k) for k in name_keys if isinstance(obj.get(k), str) and obj.get(k).strip()), "")
            title = str(name).strip()
            if title:
                desc = " ".join(str(obj.get(k)) for k in desc_keys if obj.get(k) not in (None, "", {}, []))
                brand = next((obj.get(k) for k in brand_keys if obj.get(k) not in (None, "", {}, [])), None)
                blob = normalizar_texto(" ".join([title, desc, str(brand or "")]))
                if not tokens or any(t in blob for t in tokens):
                    price = None
                    for k in price_keys:
                        if k in obj:
                            price = _valor_precio_json(obj.get(k))
                            if price is not None and price > 0:
                                break
                    # A veces el precio está dentro de offers/pricing/priceInfo.
                    if price is None:
                        for k in ("offers", "pricing", "priceInfo", "prices", "priceRange"):
                            if k in obj:
                                price = _valor_precio_json(obj.get(k))
                                if price is not None and price > 0:
                                    break
                    if price is not None and 0 < price <= 10000:
                        combined = " ".join([title, desc, str(obj.get("size", "")), str(obj.get("weight", "")), str(obj.get("unitOfMeasure", ""))])
                        contenido, unidad, pres = _inferir_presentacion_producto(combined)
                        base_query = normalizar_texto(query).split()[0] if query else ""
                        fresh_bases = {"pollo", "res", "molida", "puerco", "pescado", "camaron", "papa", "tomate", "cebolla", "zanahoria", "lechuga", "calabaza"}
                        per_weight = any(k in obj for k in ("pricePerUnit", "unitPrice", "pricePerKilo")) or "por kilogramo" in normalizar_texto(desc)
                        if not contenido and per_weight and base_query in fresh_bases:
                            contenido, unidad, pres = 1.0, "kg", "1 kg (precio por kg)"
                        if contenido:
                            raw_url = next((obj.get(k) for k in url_keys if isinstance(obj.get(k), str) and obj.get(k).strip()), "")
                            if raw_url.startswith("/"):
                                raw_url = requests.compat.urljoin(pagina_url, raw_url)
                            if not raw_url or not DOMINIOS_OFICIALES.get(tienda, "") in raw_url:
                                raw_url = pagina_url
                            item = {
                                "nombre": title[:220],
                                "marca": _marca_desde_producto(title, brand),
                                "precio": round(float(price), 2),
                                "contenido": float(contenido),
                                "unidad_contenido": unidad,
                                "presentacion": pres or f"{contenido:g} {unidad}",
                                "fuente_precio": raw_url,
                                "tienda": tienda,
                                "metodo_verificacion": "JSON de producto embebido en página oficial",
                            }
                            if _candidato_compatible_base(item, {"ingrediente_base": next((b for b, q in CONSULTAS_PRECIO.items() if normalizar_texto(q) == normalizar_texto(query)), base_query)}):
                                key=(normalizar_texto(item["nombre"]), item["precio"], item["contenido"], item["unidad_contenido"])
                                if key not in seen:
                                    seen.add(key); found.append(item)
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    walk(value, depth + 1)
        elif isinstance(obj, list):
            for value in obj[:5000]:
                if isinstance(value, (dict, list)):
                    walk(value, depth + 1)

    for script in soup.find_all("script"):
        raw = script.string or script.get_text(" ", strip=True)
        if not raw or len(raw) < 2 or len(raw) > 8_000_000:
            continue
        typ = str(script.get("type", "")).lower()
        sid = str(script.get("id", "")).lower()
        if "json" not in typ and sid not in {"__next_data__", "__nuxt_data__", "__data"} and not raw.lstrip().startswith(("{", "[")):
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        walk(data)
    return found[:80]

def _extraer_candidatos_oficiales(html_text, query, tienda, pagina_url):
    """Extrae varios productos/precios de la página oficial, no un precio aislado."""
    soup = BeautifulSoup(html_text, "html.parser")
    candidatos = []
    vistos = set()
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text(" ", strip=True)
        try:
            data = json.loads(raw)
        except Exception:
            continue
        stack = data if isinstance(data, list) else [data]
        while stack:
            obj = stack.pop()
            if isinstance(obj, dict):
                # Graphs suelen guardar los productos dentro de @graph.
                if "@graph" in obj and isinstance(obj["@graph"], list):
                    stack.extend(obj["@graph"])
                cand = _producto_candidato_desde_json(obj, tienda, pagina_url, query)
                if cand:
                    key = (normalizar_texto(cand["nombre"]), cand["precio"], cand["contenido"], cand["unidad_contenido"])
                    if key not in vistos:
                        vistos.add(key)
                        candidatos.append(cand)
                for v in obj.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(obj, list):
                stack.extend(obj)

    # Fallback: tarjetas HTML con nombre + precio. Es menos preciso, por eso
    # solo acepta una tarjeta cuando contiene simultáneamente el nombre y precio.
    for node in soup.find_all(["article", "li", "div"]):
        texto = node.get_text(" ", strip=True)
        if len(texto) < 8 or len(texto) > 700:
            continue
        norm = normalizar_texto(texto)
        tokens = [x for x in normalizar_texto(query).split() if len(x) >= 3]
        if tokens and sum(t in norm for t in tokens) < 1:
            continue
        pm = re.search(r"\$\s*([0-9]{1,5}(?:[,][0-9]{3})*(?:\.[0-9]{1,2})?)", texto)
        if not pm:
            continue
        precio = _precio_float(pm.group(1))
        if not precio or precio <= 0 or precio > 10000:
            continue
        # Tomamos una ventana de texto razonable y exigimos presentación.
        contenido, unidad, pres = _inferir_presentacion_producto(texto)
        if not contenido:
            continue
        nombre = re.split(r"\$\s*[0-9]", texto)[0].strip(" -|•")[:180]
        cand = {
            "nombre": nombre,
            "marca": _marca_desde_producto(nombre),
            "precio": round(precio, 2),
            "contenido": float(contenido),
            "unidad_contenido": unidad,
            "presentacion": pres or f"{contenido:g} {unidad}",
            "fuente_precio": pagina_url,
            "tienda": tienda,
        }
        key = (normalizar_texto(cand["nombre"]), cand["precio"], cand["contenido"], cand["unidad_contenido"])
        if key not in vistos:
            vistos.add(key)
            candidatos.append(cand)
    return candidatos[:80]


def _extraer_candidatos_lineas(html_text, query, tienda, pagina_url):
    """Fallback robusto para páginas cuyo contenido no está en JSON-LD.
    Usa texto visible y líneas cercanas al precio; el precio sigue saliendo
    exclusivamente del dominio oficial consultado.
    """
    soup = BeautifulSoup(html_text, "html.parser")
    for bad in soup(["script", "style", "noscript"]):
        bad.decompose()
    raw_lines = [re.sub(r"\s+", " ", x).strip() for x in soup.stripped_strings]
    lines = [x for x in raw_lines if x]
    tokens = [t for t in normalizar_texto(query).split() if len(t) >= 3]
    aliases = {
        "huevo": ("huevo",), "tomate": ("tomate", "jitomate"),
        "cebolla": ("cebolla",), "aceite": ("aceite",),
        "pescado": ("pescado", "filete", "tilapia", "salmon", "salmón"),
        "molida": ("molida", "res"), "frijol": ("frijol",),
        "tortilla": ("tortilla",), "arroz": ("arroz",),
        "pollo": ("pollo",), "res": ("res",), "puerco": ("cerdo", "puerco"),
        "atun": ("atun", "atún"), "sardina": ("sardina",),
        "camaron": ("camaron", "camarón"), "calabaza": ("calabacita", "calabaza"),
        "queso": ("queso",), "papa": ("papa",), "zanahoria": ("zanahoria",),
        "lechuga": ("lechuga",),
    }
    alias = aliases.get(normalizar_texto(query).split()[0], tuple(tokens))
    out=[]; seen=set()
    for i,line in enumerate(lines):
        norm_line=normalizar_texto(line)
        if alias and not any(normalizar_texto(a) in norm_line for a in alias):
            continue
        # Los supermercados suelen separar nombre, presentación y precio en
        # bloques de varias líneas. Buscamos hasta 10 líneas alrededor del
        # nombre en lugar de exigir que estén pegadas.
        for j in range(i, min(len(lines), i+11)):
            candidate_block=" ".join(lines[i:j+1])
            pm=re.search(r"(?:precio\s*(?:actual|de venta)?\s*)?\$\s*([0-9]{1,5}(?:[,][0-9]{3})*(?:\.[0-9]{1,2})?)", candidate_block, flags=re.I)
            if not pm:
                continue
            precio=_precio_float(pm.group(1))
            if not precio or not (1 <= precio <= 10000):
                continue
            contenido,unidad,pres=_inferir_presentacion_producto(candidate_block)
            if not contenido:
                if re.search(r"\bpor\s*(kg|kilo|kilogramo)|\$\s*/?\s*kg\b", normalizar_texto(candidate_block)):
                    contenido,unidad,pres=1.0,"kg","1 kg"
                else:
                    continue
            # Preferimos como nombre la línea del producto y, si es demasiado
            # corta, incorporamos la línea de presentación.
            nombre=line.strip(" -|•:")
            if len(nombre)<4 or re.fullmatch(r"[0-9$., ]+", nombre):
                nombre=candidate_block[:candidate_block.find(pm.group(0))].strip(" -|•:")[-220:]
            if len(nombre)<4:
                continue
            marca=_marca_desde_producto(nombre)
            key=(normalizar_texto(nombre),round(precio,2),contenido,unidad)
            if key in seen:
                continue
            seen.add(key)
            out.append({"nombre":nombre,"marca":marca,"precio":round(precio,2),
                        "contenido":float(contenido),"unidad_contenido":unidad,
                        "presentacion":pres or f"{contenido:g} {unidad}",
                        "fuente_precio":pagina_url,"tienda":tienda})
            break
    return out[:80]


def _extraer_enlaces_productos(html_text, query, tienda, pagina_url):
    """Obtiene enlaces oficiales de producto para una segunda pasada.
    No toma precios del buscador; solo descubre URLs del mismo dominio."""
    soup=BeautifulSoup(html_text,"html.parser")
    dominio=DOMINIOS_OFICIALES.get(tienda,"")
    tokens=[t for t in normalizar_texto(query).split() if len(t)>=3]
    links=[]; seen=set()
    for a in soup.find_all("a", href=True):
        texto=normalizar_texto(a.get_text(" ",strip=True))
        href=a.get("href","")
        if tokens and not any(t in texto for t in tokens):
            continue
        if not href: continue
        if href.startswith("/"):
            href=requests.compat.urljoin(pagina_url,href)
        if dominio not in href: continue
        if not any(x in href.lower() for x in ("/producto/","/ip/","/product","/p/")):
            continue
        if href in seen: continue
        seen.add(href); links.append(href)
        if len(links)>=8: break
    return links



def _descubrir_urls_oficiales_por_busqueda_web(tienda, consulta, max_urls=5):
    """Descubre URLs de productos SOLO dentro del dominio oficial.

    El descubrimiento usa primero Jina como lector de buscadores porque en
    entornos cloud Google/Bing suelen devolver CAPTCHA/HTML incompleto a
    requests. Jina solo sirve para descubrir la URL; el precio se obtiene
    después desde la página oficial del supermercado.
    """
    dominio = DOMINIOS_OFICIALES.get(tienda, "")
    if not dominio:
        return []
    q = quote_plus(f'site:{dominio} "{consulta}"')
    urls, seen = [], set()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36",
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
    }

    def agregar(texto):
        # Markdown de Jina: [titulo](https://dominio/...)
        encontrados = re.findall(r'https?://[^\\s)<>\"]+', texto or "")
        for href in encontrados:
            href = href.rstrip('.,;]')
            if dominio not in href:
                continue
            low = href.lower()
            if any(x in low for x in ("/login", "/carrito", "/cart", "/ayuda", "/contacto", "/buscar", "/search")):
                continue
            href = href.split("#")[0]
            if href not in seen:
                seen.add(href)
                urls.append(href)
                if len(urls) >= max_urls:
                    return True
        return False

    # 1) Jina leyendo resultados de Google/Bing.
    for motor in (
        f"https://www.google.com/search?q={q}&num=10",
        f"https://www.bing.com/search?q={q}&count=10",
    ):
        try:
            rr = requests.get("https://r.jina.ai/" + motor, headers=headers, timeout=6.0)
            if rr.status_code == 200 and agregar(rr.text):
                return urls[:max_urls]
        except Exception:
            pass

    # 2) Motores directos como último recurso.
    for motor in (
        f"https://www.google.com/search?q={q}&num=10",
        f"https://www.bing.com/search?q={q}&count=10",
        f"https://html.duckduckgo.com/html/?q={q}",
    ):
        try:
            r = requests.get(motor, headers=headers, timeout=3.5, allow_redirects=True)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a.get("href", "")
                if href.startswith("//"):
                    href = "https:" + href
                if dominio not in href:
                    continue
                href = href.split("#")[0]
                low = href.lower()
                if any(x in low for x in ("/login", "/carrito", "/cart", "/ayuda", "/contacto", "/buscar", "/search")):
                    continue
                if href not in seen:
                    seen.add(href); urls.append(href)
                    if len(urls) >= max_urls:
                        return urls[:max_urls]
        except Exception:
            pass
    return urls[:max_urls]


def _consultar_url_oficial_producto(url, tienda, consulta, headers):
    """Lee una URL de producto oficial y obtiene nombre/presentación/precio.

    Si requests recibe una página vacía por renderizado JS, Jina actúa como
    transporte de lectura de ESA MISMA URL oficial. Nunca se toma el precio de
    un buscador o de un tercero.
    """
    dominio = DOMINIOS_OFICIALES.get(tienda, "")

    def extraer(texto, fuente):
        out = _extraer_candidatos_oficiales(texto, consulta, tienda, fuente)
        if not out:
            out = _extraer_candidatos_lineas(texto, consulta, tienda, fuente)
        if not out:
            soup = BeautifulSoup(texto, "html.parser")
            titulo = ""
            for sel in ('meta[property="og:title"]', 'meta[name="twitter:title"]', "title"):
                node = soup.select_one(sel)
                if node:
                    titulo = (node.get("content") or node.get_text(" ", strip=True)).strip()
                    if titulo:
                        break
            precios=[]
            for sel in ('meta[property="product:price:amount"]', 'meta[itemprop="price"]'):
                node=soup.select_one(sel)
                if node:
                    val=_precio_float(node.get("content") or node.get_text(" ",strip=True))
                    if val: precios.append(val)
            if not precios:
                precios=[v for v in re.findall(r"\$\s*([0-9]{1,5}(?:[,][0-9]{3})*(?:\.[0-9]{1,2})?)", soup.get_text(" ",strip=True))]
                precios=[_precio_float(v) for v in precios if _precio_float(v)]
            if titulo and precios:
                contenido,unidad,pres=_inferir_presentacion_producto(titulo+" "+soup.get_text(" ",strip=True)[:4000])
                if contenido:
                    out=[{"nombre":titulo,"marca":_marca_desde_producto(titulo),"precio":round(float(min(precios)),2),
                          "contenido":float(contenido),"unidad_contenido":unidad,"presentacion":pres or f"{contenido:g} {unidad}",
                          "fuente_precio":fuente,"tienda":tienda}]
        return out

    try:
        r=requests.get(url,headers=headers,timeout=4.5,allow_redirects=True)
        if r.status_code==200 and dominio in r.url and r.text.strip():
            out=extraer(r.text,r.url)
            if out:
                return out
    except Exception:
        pass

    try:
        rr=requests.get("https://r.jina.ai/"+url,
                        headers={"User-Agent":headers.get("User-Agent","Mozilla/5.0"),"Accept":"text/plain,text/markdown;q=0.9,*/*;q=0.8"},
                        timeout=7.0,allow_redirects=True)
        if rr.status_code==200 and rr.text.strip():
            out=extraer(rr.text,url)
            if out:
                return out
    except Exception:
        pass
    return []


def _extraer_urls_oficiales_desde_texto(texto, tienda, max_urls=8):
    """Extrae enlaces de producto del contenido devuelto por Jina/HTML.

    Jina puede devolver Markdown en vez de HTML. Por eso no dependemos de
    BeautifulSoup: primero buscamos cualquier URL y después validamos que
    pertenezca al dominio oficial de la tienda y tenga pinta de producto.
    """
    dominio = DOMINIOS_OFICIALES.get(tienda, "")
    if not dominio or not texto:
        return []
    encontrados = re.findall(r'https?://[^\s\)\]<>"\']+', texto)
    urls=[]; seen=set()
    for href in encontrados:
        href = href.rstrip('.,;:')
        if dominio not in href:
            continue
        low = href.lower()
        if any(x in low for x in ("/login", "/carrito", "/cart", "/ayuda", "/contacto", "/buscar", "/search")):
            continue
        # Los supermercados usan rutas distintas: /ip/, /producto/, /p/,
        # /products/, /catalog/, etc. No exigimos una sola convención.
        if not any(x in low for x in ("/ip/", "/producto", "/product", "/p/", "/catalog", "/item")):
            continue
        href = href.split("#")[0]
        if href not in seen:
            seen.add(href); urls.append(href)
            if len(urls) >= max_urls:
                break
    return urls


def _consultar_con_reader_oficial(tienda, ingrediente_base, headers):
    """Consulta el buscador oficial a través de Jina y después sus productos.

    Este es el camino principal cuando Streamlit Cloud no puede leer bien el
    HTML/JavaScript del supermercado. El precio solo se acepta si termina
    viniendo de una URL del dominio oficial de la tienda.
    """
    consulta = CONSULTAS_PRECIO.get(ingrediente_base, ingrediente_base.replace("_", " "))
    headers_reader = {
        "User-Agent": headers.get("User-Agent", "Mozilla/5.0"),
        "Accept": "text/plain,text/markdown;q=0.9,*/*;q=0.8",
    }
    for plantilla in BUSQUEDAS_TIENDA.get(tienda, []):
        url_oficial = plantilla.format(q=quote_plus(consulta))
        try:
            rr = requests.get("https://r.jina.ai/" + url_oficial,
                               headers=headers_reader, timeout=10.0, allow_redirects=True)
            if rr.status_code != 200 or not rr.text.strip():
                continue
            texto = rr.text

            # Primero intentamos extraer productos/precios directamente del
            # contenido de resultados que Jina ya convirtió a texto.
            candidatos = _extraer_candidatos_oficiales(texto, consulta, tienda, url_oficial)
            if not candidatos:
                candidatos = _extraer_candidatos_lineas(texto, consulta, tienda, url_oficial)

            # Si el buscador solo devuelve enlaces, abrimos las páginas reales
            # de producto mediante el mismo lector oficial.
            urls = _extraer_urls_oficiales_desde_texto(texto, tienda, max_urls=8)
            if urls:
                with ThreadPoolExecutor(max_workers=min(6, len(urls))) as ex:
                    futs=[ex.submit(_consultar_url_oficial_producto, u, tienda, consulta, headers) for u in urls]
                    for fut in as_completed(futs):
                        try:
                            candidatos.extend(fut.result())
                        except Exception:
                            pass

            compatibles=[c for c in candidatos if _candidato_compatible_base(c,{"ingrediente_base":ingrediente_base})]
            if compatibles:
                return compatibles
        except Exception:
            continue
    return []


def _buscar_candidatos_desde_busqueda_web(tienda, ingrediente_base, headers, max_resultados=12):
    """Último puente de precios cuando la tienda bloquea HTML/JS.

    Busca EXCLUSIVAMENTE resultados cuyo dominio sea el supermercado elegido.
    El precio se toma del fragmento que acompaña a ese resultado y la fuente
    guardada es la URL oficial del producto. No usa catálogos internos ni
    precios de terceros.

    Es una capa de contingencia: primero se intenta siempre la tienda oficial.
    """
    dominio=DOMINIOS_OFICIALES.get(tienda, "")
    consulta=CONSULTAS_PRECIO.get(ingrediente_base, ingrediente_base.replace("_"," "))
    if not dominio or not consulta:
        return []
    queries=[
        f'site:{dominio} "{consulta}" "$"',
        f'site:{dominio} "{consulta}" precio',
    ]
    motores=[
        "https://www.google.com/search?q={q}&num=10&hl=es",
        "https://www.bing.com/search?q={q}&count=10&setlang=es-MX",
    ]
    out=[]; seen=set()
    aliases={
        "tomate":("tomate","jitomate"), "cebolla":("cebolla",),
        "huevo":("huevo",), "aceite":("aceite",), "tortilla":("tortilla",),
        "arroz":("arroz",), "frijol":("frijol",), "papa":("papa",),
        "zanahoria":("zanahoria",), "calabaza":("calabaza","calabacita"),
        "queso":("queso",), "molida":("molida","res"), "res":("res",),
        "pollo":("pollo",), "puerco":("cerdo","puerco"),
        "pescado":("pescado","filete","tilapia","mojarra","salmon"),
        "atun":("atun","atún"), "sardina":("sardina",), "camaron":("camaron","camarón"),
    }
    alias=aliases.get(ingrediente_base,(normalizar_texto(consulta).split()[0],))
    for q0 in queries:
        q=quote_plus(q0)
        for plantilla in motores:
            try:
                r=requests.get(plantilla.format(q=q),headers=headers,timeout=6.0,allow_redirects=True)
                if r.status_code!=200 or not r.text: continue
                soup=BeautifulSoup(r.text,"html.parser")
                for a in soup.find_all("a",href=True):
                    href=a.get("href","")
                    texto=a.get_text(" ",strip=True)
                    if dominio not in href: continue
                    if not texto: continue
                    bloque=" ".join([texto, a.parent.get_text(" ",strip=True) if a.parent else ""])
                    norm=normalizar_texto(bloque)
                    if not any(normalizar_texto(x) in norm for x in alias): continue
                    pm=re.search(r"\$\s*([0-9]{1,5}(?:[,][0-9]{3})?(?:\.[0-9]{1,2})?)",bloque)
                    if not pm:
                        # A veces el precio aparece en el hermano/contenedor del resultado.
                        cont=a.find_parent(["div","li"])
                        if cont:
                            bloque=cont.get_text(" ",strip=True)
                            pm=re.search(r"\$\s*([0-9]{1,5}(?:[,][0-9]{3})?(?:\.[0-9]{1,2})?)",bloque)
                    if not pm: continue
                    precio=_precio_float(pm.group(1))
                    if not precio or not (1<=precio<=10000): continue
                    contenido,unidad,pres=_inferir_presentacion_producto(bloque)
                    if not contenido:
                        if re.search(r"\bpor\s*(kg|kilo|kilogramo)\b|\$/?\s*kg",normalizar_texto(bloque)):
                            contenido,unidad,pres=1.0,"kg","1 kg"
                        else:
                            continue
                    href=href.split("#")[0]
                    key=(href,round(precio,2),contenido,unidad)
                    if key in seen: continue
                    if not _candidato_compatible_base({"nombre":texto}, {"ingrediente_base":ingrediente_base}):
                        continue
                    seen.add(key)
                    out.append({"nombre":texto[:220],"marca":_marca_desde_producto(texto),"precio":round(precio,2),
                                "contenido":float(contenido),"unidad_contenido":unidad,
                                "presentacion":pres or f"{contenido:g} {unidad}",
                                "fuente_precio":href,"tienda":tienda,
                                "metodo_verificacion":"resultado web de página oficial"})
                    if len(out)>=max_resultados: return out
            except Exception:
                continue
        if out: return out
    return out

def _buscar_candidatos_tienda(tienda, ingrediente_base):
    """Obtiene productos/precios actuales de una tienda seleccionada.

    Orden de prioridad:
    1) HTML/JSON de la tienda;
    2) Jina leyendo el buscador oficial + páginas oficiales de producto;
    3) descubrimiento de URLs oficiales y lectura de esas páginas.

    Nunca usa el precio del catálogo de referencia como precio verificado.
    """
    consulta=CONSULTAS_PRECIO.get(ingrediente_base, ingrediente_base.replace("_"," "))
    clave=("candidatos",tienda,ingrediente_base)
    ahora=time.time()
    cache=PRECIO_CACHE.get(clave)
    # Solo reutilizar búsquedas que sí encontraron candidatos. Los fallos de red,
    # páginas JS y respuestas vacías NO se cachean 15 min: era una causa directa
    # de repetir "0 precios" aun cuando se corregía el parser o se reintentaba.
    if cache and ahora-cache["ts"]<PRECIO_CACHE_TTL and cache.get("resultado", {}).get("candidatos"):
        return cache["resultado"]

    headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/154 Safari/537.36",
             "Accept-Language":"es-MX,es;q=0.9,en;q=0.8",
             "Accept":"text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8"}
    dominio=DOMINIOS_OFICIALES.get(tienda,"")
    candidatos=[]; errores=[]

    # 1) Lectura directa del buscador oficial.
    for plantilla in BUSQUEDAS_TIENDA.get(tienda,[]):
        url=plantilla.format(q=quote_plus(consulta))
        try:
            r=requests.get(url,headers=headers,timeout=5.0,allow_redirects=True)
            if r.status_code!=200 or dominio not in r.url:
                errores.append(f"directo {r.status_code}")
                continue
            candidatos.extend(_extraer_candidatos_oficiales(r.text,consulta,tienda,r.url))
            if not candidatos:
                candidatos.extend(_extraer_candidatos_json_embebido(r.text,consulta,tienda,r.url))
            if not candidatos:
                candidatos.extend(_extraer_candidatos_lineas(r.text,consulta,tienda,r.url))
            if candidatos:
                break
        except Exception as exc:
            errores.append(f"directo: {str(exc)[:70]}")

    # 2) Camino robusto para JavaScript/anti-bot: Jina lee el buscador oficial,
    # encuentra enlaces reales y después se leen las páginas de producto.
    if not candidatos:
        try:
            candidatos.extend(_consultar_con_reader_oficial(tienda,ingrediente_base,headers))
        except Exception as exc:
            errores.append(f"reader: {str(exc)[:70]}")

    # 3) Último recurso: descubrir URLs oficiales mediante buscador y luego
    # consultar esas URLs oficiales. El buscador solo descubre; jamás aporta el precio.
    if not candidatos:
        try:
            urls=_descubrir_urls_oficiales_por_busqueda_web(tienda,consulta,max_urls=6)
            if urls:
                with ThreadPoolExecutor(max_workers=min(6,len(urls))) as ex:
                    futs=[ex.submit(_consultar_url_oficial_producto,u,tienda,consulta,headers) for u in urls]
                    for fut in as_completed(futs):
                        try:
                            candidatos.extend(fut.result())
                        except Exception:
                            pass
        except Exception as exc:
            errores.append(f"descubrimiento: {str(exc)[:70]}")

    # 4) Puente de contingencia: resultados de buscador que apuntan SOLO a la
    # tienda oficial. Esto evita que un bloqueo de JavaScript deje a KashCook
    # con cero precios aunque la tienda sí publique el producto y precio.
    if not candidatos:
        try:
            candidatos.extend(_buscar_candidatos_desde_busqueda_web(tienda, ingrediente_base, headers))
        except Exception as exc:
            errores.append(f"busqueda web: {str(exc)[:70]}")

    # Filtrado final: mismo ingrediente + presentación identificable + precio.
    unicos={}
    for c in candidatos:
        if not _candidato_compatible_base(c,{"ingrediente_base":ingrediente_base}):
            continue
        try:
            precio=float(c.get("precio"))
            contenido=float(c.get("contenido"))
        except Exception:
            continue
        if precio<=0 or contenido<=0:
            continue
        c["estado_precio"]="Verificado"
        c["ultima_verificacion"]=datetime.now().astimezone().isoformat(timespec="minutes")
        key=(normalizar_texto(c.get("nombre","")),contenido,c.get("unidad_contenido"))
        if key not in unicos or precio< float(unicos[key].get("precio",10**9)):
            unicos[key]=c

    resultado={"candidatos":sorted(unicos.values(),key=lambda x:x.get("precio",10**9))[:40],
               "ultima_verificacion":datetime.now().astimezone().isoformat(timespec="minutes"),
               "fuente":(next(iter(unicos.values())).get("fuente_precio",dominio) if unicos else dominio),
               "error":"; ".join(errores[-3:])}
    PRECIO_CACHE[clave]={"ts":ahora,"resultado":resultado}
    return resultado

def _buscar_candidatos_lote(tareas, max_workers=12):
    """Consulta tienda+ingrediente en paralelo para evitar esperas acumuladas."""
    resultados = {}
    pendientes = []
    for tienda, base in tareas:
        clave = (tienda, base)
        cache = PRECIO_CACHE.get(("candidatos", tienda, base))
        if (cache and time.time() - cache["ts"] < PRECIO_CACHE_TTL
                and cache.get("resultado", {}).get("candidatos")):
            resultados[clave] = cache["resultado"]
        else:
            pendientes.append((tienda, base))

    if pendientes:
        workers = min(max_workers, len(pendientes))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futuros = {executor.submit(_buscar_candidatos_tienda, tienda, base): (tienda, base)
                       for tienda, base in pendientes}
            for futuro in as_completed(futuros):
                tienda, base = futuros[futuro]
                try:
                    resultados[(tienda, base)] = futuro.result()
                except Exception as exc:
                    resultados[(tienda, base)] = {
                        "candidatos": [],
                        "ultima_verificacion": datetime.now().astimezone().isoformat(timespec="minutes"),
                        "fuente": DOMINIOS_OFICIALES.get(tienda, ""),
                        "error": str(exc)[:120],
                    }
    return resultados


def _candidato_compatible_base(candidato, producto_referencia):
    """Comprueba que el candidato siga representando el mismo ingrediente."""
    nombre = normalizar_texto(candidato.get("nombre", ""))
    base = producto_referencia.get("ingrediente_base", "")
    consultas = normalizar_texto(CONSULTAS_PRECIO.get(base, base)).split()
    if base == "molida":
        return "molida" in nombre and ("res" in nombre or "carne" in nombre)
    principal = consultas[0] if consultas else base
    aliases = {
        "atun": ("atun", "atún", "tuny"),
        "camaron": ("camaron", "camarón"),
        "puerco": ("cerdo", "puerco", "chuleta", "pierna de cerdo"),
        "pescado": ("pescado", "filete", "tilapia", "mojarra", "salmon", "salmón"),
        "arroz": ("arroz",), "frijol": ("frijol",), "tortilla": ("tortilla",),
        "huevo": ("huevo",), "queso": ("queso",), "aceite": ("aceite",),
        "tomate": ("tomate", "jitomate"), "cebolla": ("cebolla",),
        "calabaza": ("calabaza", "calabacita"), "papa": ("papa",),
        "zanahoria": ("zanahoria",), "lechuga": ("lechuga",),
        "pollo": ("pollo",), "res": ("res", "bistec", "carne de res"),
        "sardina": ("sardina",),
    }
    return any(normalizar_texto(a) in nombre for a in aliases.get(base, (principal,)))


def construir_catalogo_productos_optimo(catalogo, bases_necesarias=None, presupuesto=0):
    """Construye un catálogo con productos reales y múltiples marcas.

    La búsqueda se hace para todas las bases útiles del catálogo (o solo para
    las solicitadas) y en paralelo por tienda+ingrediente. Así KashCook puede
    descubrir marcas propias/económicas como MiMarca sin multiplicar el tiempo
    de espera por cada ingrediente.
    """
    resultado = []
    por_base = {}
    for p in catalogo:
        por_base.setdefault(p.get("ingrediente_base"), []).append(p)

    bases = sorted({b for b in (bases_necesarias or por_base.keys()) if b in por_base})
    tiendas = sorted({p.get("tienda") for p in catalogo if p.get("tienda")})
    tareas = [(tienda, base) for tienda in tiendas for base in bases]
    resultados_lote = _buscar_candidatos_lote(tareas, max_workers=12)

    for base in bases:
        referencias = por_base.get(base, [])
        candidatos = []
        for tienda in tiendas:
            res = resultados_lote.get((tienda, base), {})
            for c in res.get("candidatos", []):
                ref = next((x for x in referencias
                            if x.get("tienda") == tienda and _candidato_compatible_base(c, x)), None)
                if not ref:
                    continue
                cc = copy.deepcopy(ref)
                cc["id"] = f"{ref['id']}__live__{abs(hash((c['nombre'], c['precio'], c['contenido'], c['unidad_contenido']))) % 10**9}"
                cc["nombre"] = c["nombre"]
                cc["marca"] = c.get("marca", "Marca no identificada")
                cc["precio"] = float(c["precio"])
                cc["contenido"] = float(c["contenido"])
                cc["unidad_contenido"] = c["unidad_contenido"]
                cc["presentacion"] = c["presentacion"]
                cc["estado_precio"] = "Verificado"
                cc["ultima_verificacion"] = res.get("ultima_verificacion")
                cc["fuente_precio"] = c.get("fuente_precio", "")
                cc["venta_por_kg"] = cc["unidad_contenido"] == "kg" and base in {
                    "pollo","res","molida","puerco","pescado","camaron","papa","tomate","cebolla","zanahoria","lechuga","calabaza"
                }
                candidatos.append(cc)

        # SIEMPRE conservamos el producto de referencia como respaldo de
        # planificación. Esto evita el falso mensaje "no hay desayunos/comidas"
        # cuando una página del supermercado falla, cambia su HTML o bloquea una
        # consulta. Los precios de referencia jamás se usan como total final.
        ids_live = {p.get("id") for p in candidatos}
        for ref in referencias:
            if ref.get("id") not in ids_live:
                rr = copy.deepcopy(ref)
                rr["estado_precio"] = "Referencia"
                candidatos.append(rr)

        def costo_efectivo(x):
            contenido = max(float(x.get("contenido") or 1), 1e-9)
            unidad = x.get("unidad_contenido")
            try: precio=float(x.get("precio") or 10**9)
            except Exception: precio=10**9
            if unidad == "kg": return precio / contenido
            if unidad == "g": return precio / (contenido / 1000)
            if unidad == "l": return precio / contenido
            if unidad == "ml": return precio / (contenido / 1000)
            return precio

        # Primero verificadas y luego referencias; dentro de cada grupo, menor
        # costo efectivo. Así las marcas propias tienen oportunidad de ganar sin
        # hacer que una falla del buscador elimine recetas enteras.
        candidatos.sort(key=lambda x: (0 if x.get("estado_precio")=="Verificado" else 1, costo_efectivo(x)))
        resultado.extend(candidatos[:12])

    return resultado

def verificar_precios_tiendas(catalogo, bases_necesarias=None, ids_necesarios=None):
    """Verifica únicamente los ingredientes realmente utilizados.

    Esta función ahora SÍ ejecuta el verificador de tienda. La versión anterior
    solo marcaba referencias como no disponibles, aunque ya existía un buscador
    real en el archivo.
    """
    bases = set(bases_necesarias or [])
    actualizado = copy.deepcopy(catalogo)
    tiendas = sorted({p.get("tienda") for p in actualizado if p.get("tienda")})
    tareas = [(t, b) for t in tiendas for b in bases]
    lote = _buscar_candidatos_lote(tareas, max_workers=min(12, max(1, len(tareas))))
    por_base = {}
    for p in actualizado:
        if p.get("estado_precio") == "Verificado":
            por_base.setdefault(p.get("ingrediente_base"), []).append(p)
    for tienda, base in tareas:
        for c in lote.get((tienda, base), {}).get("candidatos", []):
            ref = next((p for p in actualizado if p.get("tienda") == tienda and p.get("ingrediente_base") == base), None)
            if not ref:
                continue
            cc = copy.deepcopy(ref)
            cc["id"] = f"{ref['id']}__live__{abs(hash((c.get('nombre'),c.get('precio'),c.get('contenido'),c.get('unidad_contenido')))) % 10**9}"
            cc["nombre"] = c.get("nombre", ref.get("nombre"))
            cc["marca"] = c.get("marca", "Marca no identificada")
            cc["precio"] = float(c["precio"])
            cc["contenido"] = float(c.get("contenido") or ref.get("contenido") or 1)
            cc["unidad_contenido"] = c.get("unidad_contenido") or ref.get("unidad_contenido")
            cc["presentacion"] = c.get("presentacion") or ref.get("presentacion")
            cc["estado_precio"] = "Verificado"
            cc["ultima_verificacion"] = lote.get((tienda,base),{}).get("ultima_verificacion")
            cc["fuente_precio"] = c.get("fuente_precio", "")
            actualizado.append(cc)
    return actualizado


def _reemplazar_productos_por_verificados(plan, catalogo_verificado):
    """Reasigna cada ingrediente del menú al producto verificado más económico.

    El menú se puede planificar aunque el buscador web haya fallado para alguna
    página. Antes del total final, cada ingrediente debe quedar ligado a una
    marca/presentación realmente verificada.
    """
    por_base={}
    for p in catalogo_verificado:
        if p.get("estado_precio") != "Verificado":
            continue
        por_base.setdefault(p.get("ingrediente_base"), []).append(p)
    nuevo=copy.deepcopy(plan)
    productos={p.get("id"):p for p in catalogo_verificado}
    for dia in nuevo.get("dias",[]):
        for comida in dia.get("comidas",[]):
            for ing in comida.get("ingredientes",[]):
                pid=ing.get("producto_id")
                original=productos.get(pid)
                base=original.get("ingrediente_base") if original else None
                if not base:
                    # Recuperar la base desde el catálogo de referencia por ID.
                    original_ref=next((p for p in catalogo_verificado if p.get("id")==pid),None)
                    base=original_ref.get("ingrediente_base") if original_ref else None
                opciones=por_base.get(base,[])
                if not opciones:
                    continue
                def costo(p):
                    try:
                        precio = float(p.get("precio") or 10**9)
                        contenido = max(float(p.get("contenido") or 1), 1e-9)
                        unidad = str(p.get("unidad_contenido") or "").lower()
                        if unidad == "g": return precio / (contenido / 1000.0)
                        if unidad == "ml": return precio / (contenido / 1000.0)
                        if unidad in {"kg", "l"}: return precio / contenido
                        return precio / contenido
                    except Exception: return 10**9
                elegido=min(opciones,key=costo)
                # Si cambia la presentación, recalcular la cantidad expresada en
                # gramos/kg para ingredientes que originalmente se daban por pieza
                # y cuya receta depende del contenido comercial.
                if str(ing.get("unidad","")).lower() in {"pieza","piezas","unidad","unidades"} and str(elegido.get("unidad_contenido","")).lower() in {"g","kg"}:
                    contenido_g=float(elegido.get("contenido") or 0)*(1000 if str(elegido.get("unidad_contenido")).lower()=="kg" else 1)
                    if contenido_g>0:
                        ing["cantidad_por_persona"]=float(ing.get("cantidad_por_persona",0))*contenido_g
                        ing["unidad"]="g"
                ing["producto_id"]=elegido["id"]
    return nuevo


def validar_precios_verificados(compra):
    """Devuelve el estado de verificacion sin bloquear la generacion del plan.

    Una falla del scraping de una tienda no debe impedir que KashCook entregue
    el menu y la lista de compras. Los items no verificados quedan claramente
    marcados y el total se considera PROVISIONAL.
    """
    faltantes = [x for x in compra if x.get("estado_precio") != "Verificado"]
    verificados = [x for x in compra if x.get("estado_precio") == "Verificado"]
    return {
        "ok": not faltantes,
        "verificados": len(verificados),
        "faltantes": len(faltantes),
        "nombres_faltantes": [x.get("producto", "producto") for x in faltantes],
    }


# ============================================================
# CLIENTE GROQ
# ============================================================

def obtener_cliente_groq():

    api_key = None

    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass

    if not api_key:

        api_key = st.text_input(
            "GROQ API Key",
            type="password",
        )

    if not api_key:
        return None

    return Groq(api_key=api_key)


# ============================================================
# LLAMADA A GROQ
# ============================================================

def llamar_groq(cliente, prompt, temperatura=0.4):

    respuesta = cliente.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres KashCook AI. Diseñas menús familiares, "
                    "recetas, cantidades y compras. Responde solo "
                    "JSON válido cuando se solicite un plan."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=temperatura,
        max_tokens=8000,
        response_format={"type": "json_object"},
    )

    contenido = respuesta.choices[0].message.content

    if not contenido:
        raise ValueError("Groq no devolvió contenido.")

    return contenido


# ============================================================
# EXTRAER JSON
# ============================================================

def extraer_json(texto):

    if not texto:
        raise ValueError(
            "La IA no devolvió contenido."
        )

    texto = texto.strip()

    # Intento directo
    try:
        return json.loads(texto)
    except Exception:
        pass

    # Eliminar Markdown
    texto_limpio = re.sub(
        r"```json",
        "",
        texto,
        flags=re.IGNORECASE,
    )

    texto_limpio = re.sub(
        r"```",
        "",
        texto_limpio,
    )

    texto_limpio = texto_limpio.strip()

    try:
        return json.loads(texto_limpio)
    except Exception:
        pass

    # Buscar objeto JSON
    inicio = texto_limpio.find("{")
    fin = texto_limpio.rfind("}")

    if inicio >= 0 and fin > inicio:

        posible_json = texto_limpio[
            inicio:fin + 1
        ]

        try:
            return json.loads(posible_json)
        except Exception:
            pass

    raise ValueError(
        "No fue posible interpretar la respuesta "
        "de la IA como JSON."
    )


# ============================================================
# NORMALIZAR PLAN
# ============================================================

def normalizar_plan(plan):

    if not isinstance(plan, dict):

        raise ValueError(
            "La respuesta de la IA no es un objeto JSON."
        )

    dias_originales = (
        plan.get("dias")
        or plan.get("days")
        or plan.get("semana")
        or plan.get("menu")
    )

    if not isinstance(
        dias_originales,
        list,
    ):

        raise ValueError(
            "La IA no devolvió una lista de días."
        )

    dias_normalizados = []

    for indice, dia in enumerate(
        dias_originales,
        1,
    ):

        if not isinstance(dia, dict):
            continue

        comidas_originales = (
            dia.get("comidas")
            or dia.get("comidas_del_dia")
            or dia.get("meals")
            or dia.get("recetas")
            or []
        )

        if not isinstance(
            comidas_originales,
            list,
        ):
            continue

        comidas_normalizadas = []

        for comida in comidas_originales:

            if not isinstance(
                comida,
                dict,
            ):
                continue

            tipo = (
                comida.get("tipo")
                or comida.get("meal_type")
                or comida.get("type")
                or "Comida"
            )

            nombre = (
                comida.get("nombre")
                or comida.get("name")
                or comida.get("receta")
                or "Receta"
            )

            ingredientes_originales = (
                comida.get("ingredientes")
                or comida.get("ingredients")
                or []
            )

            if not isinstance(
                ingredientes_originales,
                list,
            ):
                ingredientes_originales = []

            ingredientes_normalizados = []

            for ing in ingredientes_originales:

                if not isinstance(
                    ing,
                    dict,
                ):
                    continue

                producto_id = (
                    ing.get("producto_id")
                    or ing.get("product_id")
                    or ing.get("id")
                )

                cantidad = (
                    ing.get("cantidad_por_persona")
                    if ing.get(
                        "cantidad_por_persona"
                    ) is not None
                    else ing.get("cantidad")
                )

                if cantidad is None:
                    cantidad = ing.get(
                        "quantity",
                        0,
                    )

                unidad = (
                    ing.get("unidad")
                    or ing.get("unit")
                    or "pieza"
                )

                try:
                    cantidad = float(cantidad)
                except Exception:
                    cantidad = 0

                if producto_id and cantidad > 0:

                    ingredientes_normalizados.append(
                        {
                            "producto_id": str(
                                producto_id
                            ),
                            "cantidad_por_persona": cantidad,
                            "unidad": str(unidad),
                        }
                    )

            preparacion_original = (
                comida.get("preparacion")
                or comida.get("preparación")
                or comida.get("preparation")
                or comida.get("pasos")
                or []
            )

            if isinstance(
                preparacion_original,
                str,
            ):

                preparacion_normalizada = [
                    preparacion_original
                ]

            elif isinstance(
                preparacion_original,
                list,
            ):

                preparacion_normalizada = [
                    str(x)
                    for x in preparacion_original
                    if x
                ]

            else:

                preparacion_normalizada = []

            if ingredientes_normalizados:

                comidas_normalizadas.append(
                    {
                        "tipo": str(tipo),
                        "nombre": str(nombre),
                        "ingredientes": ingredientes_normalizados,
                        "preparacion": preparacion_normalizada,
                    }
                )

        if comidas_normalizadas:

            numero_dia = (
                dia.get("dia")
                or dia.get("day")
                or indice
            )

            dias_normalizados.append(
                {
                    "dia": numero_dia,
                    "comidas": comidas_normalizadas,
                }
            )

    if not dias_normalizados:

        raise ValueError(
            "La IA devolvió un JSON pero no contiene "
            "días y comidas utilizables."
        )

    return {
        "dias": dias_normalizados
    }


# ============================================================
# VALIDAR PLAN
# ============================================================

def validar_plan(plan):

    if not isinstance(
        plan,
        dict,
    ):
        return False

    dias = plan.get("dias")

    if not isinstance(
        dias,
        list,
    ):
        return False

    if len(dias) == 0:
        return False

    dias_validos = 0

    for dia in dias:

        if not isinstance(
            dia,
            dict,
        ):
            continue

        comidas = dia.get(
            "comidas",
            [],
        )

        if not isinstance(
            comidas,
            list,
        ):
            continue

        comidas_validas = 0

        for comida in comidas:

            if not isinstance(
                comida,
                dict,
            ):
                continue

            ingredientes = comida.get(
                "ingredientes",
                [],
            )

            if not isinstance(
                ingredientes,
                list,
            ):
                continue

            if len(ingredientes) == 0:
                continue

            comidas_validas += 1

        if comidas_validas > 0:
            dias_validos += 1

    return dias_validos > 0


def normalizar_texto(valor):
    texto = str(valor or "").strip().lower()
    for a, b in {"á":"a","é":"e","í":"i","ó":"o","ú":"u","ü":"u"}.items():
        texto = texto.replace(a, b)
    return texto


def validar_plan_completo(plan, dias_solicitados, comidas_solicitadas, catalogo):
    if not validar_plan(plan):
        return False, "El plan no contiene datos utilizables."

    dias = plan.get("dias", [])
    if len(dias) != int(dias_solicitados):
        return False, f"Se requieren exactamente {dias_solicitados} días y llegaron {len(dias)}."

    ids_validos = {p["id"] for p in catalogo}
    tipos_requeridos = {normalizar_texto(x) for x in comidas_solicitadas}

    for i, dia in enumerate(dias, 1):
        comidas = dia.get("comidas", [])
        tipos = [normalizar_texto(c.get("tipo")) for c in comidas]
        if len(comidas) != len(comidas_solicitadas) or set(tipos) != tipos_requeridos:
            return False, f"El día {i} no contiene exactamente las comidas solicitadas."

        for comida in comidas:
            if not comida.get("nombre"):
                return False, f"Falta nombre en una comida del día {i}."
            ingredientes = comida.get("ingredientes", [])
            if len(ingredientes) < 2:
                return False, f"Una comida del día {i} tiene menos de 2 ingredientes."
            if len(comida.get("preparacion", [])) < 2:
                return False, f"Una comida del día {i} tiene menos de 2 pasos."
            for ing in ingredientes:
                if ing.get("producto_id") not in ids_validos:
                    return False, f"Hay un producto_id inválido en el día {i}."
                try:
                    cantidad = float(ing.get("cantidad_por_persona", 0))
                    if cantidad <= 0:
                        return False, f"Hay una cantidad inválida en el día {i}."
                except Exception:
                    return False, f"Hay una cantidad inválida en el día {i}."

            # Controles mínimos de porción por persona para evitar menús
            # matemáticamente "válidos" pero absurdos en la práctica.
            mapa = {p["id"]: p for p in catalogo}
            for ing in ingredientes:
                prod = mapa.get(ing.get("producto_id"), {})
                base = prod.get("ingrediente_base")
                unidad = normalizar_texto(ing.get("unidad"))
                cantidad = float(ing.get("cantidad_por_persona", 0))
                if base == "huevo" and unidad == "pieza" and cantidad < 2 and any(k in normalizar_texto(comida.get("nombre")) for k in ("huevo", "omelette", "migas")):
                    return False, f"El desayuno del día {i} requiere al menos 2 huevos por persona."
                if base in {"pollo", "res", "molida", "puerco", "pescado", "camaron"} and unidad == "kg" and cantidad < 0.12:
                    return False, f"La porción de proteína del día {i} es menor a 120 g por persona."

    return True, "OK"


def construir_prompt_reintento(plan, dias, comidas, catalogo, motivo):
    ids = ",".join(p["id"] for p in catalogo)
    plan_compacto = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))
    comidas_texto = ", ".join(comidas)
    return f"""Corrige este plan KashCook. Motivo: {motivo}

Debe tener EXACTAMENTE {dias} días y cada día EXACTAMENTE estas comidas: {comidas_texto}. Cada comida: nombre, mínimo 2 ingredientes, mínimo 2 pasos. Cada ingrediente: producto_id válido, cantidad_por_persona > 0 y unidad compatible. Conserva el contenido útil del plan. Responde SOLO JSON.

IDs válidos:
{ids}

PLAN:
{plan_compacto}

Estructura: {{"dias":[{{"dia":1,"comidas":[{{"tipo":"Desayuno","nombre":"...","ingredientes":[{{"producto_id":"ID","cantidad_por_persona":2,"unidad":"pieza"}}],"preparacion":["Paso 1","Paso 2"]}}]}}]}}"""


# ============================================================
# CONVERSIÓN DE UNIDADES
# ============================================================

def convertir_a_base(
    cantidad,
    unidad,
):

    unidad = str(
        unidad
    ).lower().strip()

    if unidad in [
        "kg",
        "kilo",
        "kilos",
    ]:

        return (
            cantidad * 1000,
            "g",
        )

    if unidad in [
        "g",
        "gramo",
        "gramos",
    ]:

        return (
            cantidad,
            "g",
        )

    if unidad in [
        "l",
        "litro",
        "litros",
    ]:

        return (
            cantidad * 1000,
            "ml",
        )

    if unidad in [
        "ml",
        "mililitro",
        "mililitros",
    ]:

        return (
            cantidad,
            "ml",
        )

    if unidad in [
        "pieza",
        "piezas",
        "unidad",
        "unidades",
    ]:

        return (
            cantidad,
            "pieza",
        )

    return (
        cantidad,
        unidad,
    )


# ============================================================
# CALCULAR COMPRA
# ============================================================

def calcular_compra(
    plan,
    catalogo,
    personas,
):

    productos_por_id = {
        p["id"]: p
        for p in catalogo
    }

    demanda = {}

    for dia in plan.get(
        "dias",
        [],
    ):

        for comida in dia.get(
            "comidas",
            [],
        ):

            for ing in comida.get(
                "ingredientes",
                [],
            ):

                producto_id = ing.get(
                    "producto_id"
                )

                if producto_id not in productos_por_id:
                    raise ValueError(
                        f"La receta contiene un ingrediente sin producto de compra válido: {producto_id}."
                    )

                try:
                    cantidad_persona = float(
                        ing.get(
                            "cantidad_por_persona",
                            0,
                        )
                    )
                except Exception:
                    cantidad_persona = 0

                if cantidad_persona <= 0:
                    continue

                unidad = ing.get(
                    "unidad",
                    "",
                )

                cantidad_total = (
                    cantidad_persona * personas
                )

                p = productos_por_id[
                    producto_id
                ]

                cantidad_base, unidad_base = convertir_a_base(
                    cantidad_total,
                    unidad,
                )

                contenido_base, unidad_contenido_base = convertir_a_base(
                    p["contenido"],
                    p["unidad_contenido"],
                )

                if unidad_base != unidad_contenido_base:
                    raise ValueError(
                        f"La presentación comercial de {p.get('nombre','producto')} no es compatible con la unidad de la receta ({unidad})."
                    )

                if contenido_base <= 0:
                    continue

                if producto_id not in demanda:

                    demanda[producto_id] = {
                        "producto": p,
                        "cantidad_requerida": 0,
                        "unidad": unidad_base,
                    }

                demanda[
                    producto_id
                ]["cantidad_requerida"] += cantidad_base

    compra = []

    total = 0

    for producto_id, item in demanda.items():

        p = item["producto"]

        contenido_base, _ = convertir_a_base(
            p["contenido"],
            p["unidad_contenido"],
        )

        # Carnes/pescados frescos vendidos por kilogramo: no inventamos un
        # paquete fijo; calculamos la cantidad realmente requerida al precio/kg.
        if p.get("venta_por_kg") and item.get("unidad") == "g":
            cantidad_kg = item["cantidad_requerida"] / 1000.0
            paquetes = cantidad_kg
            subtotal = cantidad_kg * p["precio"]
        else:
            paquetes = math.ceil(
                item["cantidad_requerida"]
                / contenido_base
            )
            if paquetes < 1:
                paquetes = 1
            subtotal = paquetes * p["precio"]

        total += subtotal

        compra.append(
            {
                "producto_id": p.get("id"),
                "producto": p["nombre"],
                "marca": p.get("marca", "Marca no identificada"),
                "ingrediente_base": p[
                    "ingrediente_base"
                ],
                "presentacion": p[
                    "presentacion"
                ],
                "contenido": p[
                    "contenido"
                ],
                "unidad_contenido": p[
                    "unidad_contenido"
                ],
                "cantidad_requerida": item[
                    "cantidad_requerida"
                ],
                "unidad": item[
                    "unidad"
                ],
                "paquetes": paquetes,
                "precio_unitario": p[
                    "precio"
                ],
                "subtotal": subtotal,
                "tienda": p[
                    "tienda"
                ],
                "estado_precio": p.get("estado_precio", "Referencia"),
                "ultima_verificacion": p.get("ultima_verificacion"),
                "fuente_precio": p.get("fuente_precio", ""),
            }
        )

    return (
        compra,
        round(total, 2),
    )


# ============================================================
# PROMPT PRINCIPAL
# ============================================================

def construir_prompt(
    tiendas,
    dias,
    personas,
    presupuesto,
    estilos,
    comidas,
    electrodomesticos,
    restricciones,
    catalogo,
):

    # Formato compacto: conserva todos los productos y datos que la IA
    # necesita, pero evita repetir claves JSON y textos largos.
    catalogo_lineas = []
    for p in catalogo:
        catalogo_lineas.append(
            f"{p['id']}|{p['tienda']}|{p['ingrediente_base']}|"
            f"{p['nombre']}|{p['contenido']}{p['unidad_contenido']}|"
            f"{p['precio']}"
        )

    comidas_texto = ", ".join(comidas)
    estilos_texto = ", ".join(estilos) if estilos else "Libre"
    electro_texto = ", ".join(electrodomesticos) if electrodomesticos else "Cocina convencional"
    restr_texto = restricciones.strip() if restricciones else "Ninguna"

    return f"""Eres KashCook AI. Crea un plan de alimentación para {personas} personas durante EXACTAMENTE {dias} días.

Presupuesto: ${presupuesto:.2f} MXN. Límite absoluto: ${presupuesto + TOLERANCIA_PRESUPUESTO:.2f}.
Tiendas permitidas: {', '.join(tiendas)}. NO compares precios ni recomiendes una tienda por precio.
Estilos: {estilos_texto}. Comidas obligatorias cada día: {comidas_texto}.
Electrodomésticos: {electro_texto}. Restricciones/alergias: {restr_texto}.

REGLAS:
- Usa SOLO productos del catálogo y SOLO tiendas permitidas.
- Las cantidades son POR PERSONA; el sistema las multiplicará por {personas}.
- Porciones principales orientativas: pollo sin hueso 180-220 g; pollo con hueso 250-350 g; res/cerdo 160-220 g; pescado 180-220 g; huevo 2-4 piezas. Atún y sardina: porción realista.
- Varía proteínas: pollo, res, cerdo, pescado, atún, sardina y huevo cuando sea compatible con días, comidas y restricciones. No hagas todo a base de pollo.
- Varía recetas y usa acompañamientos/verduras adecuados.
- No inventes productos ni precios.
- Objetivo: usar aproximadamente 90-100% del presupuesto cuando sea posible. Puede quedar por debajo; nunca superes el límite absoluto.
- Cada día debe contener EXACTAMENTE las comidas solicitadas, sin omitir ninguna.
- Cada comida necesita nombre, al menos 2 ingredientes y al menos 2 pasos de preparación.
- Cada ingrediente necesita producto_id EXACTO del catálogo, cantidad_por_persona numérica y unidad compatible.

CATÁLOGO (id|tienda|ingrediente|producto|contenido|precio):
{chr(10).join(catalogo_lineas)}

RESPONDE SOLO CON JSON con esta forma:
{{"dias":[{{"dia":1,"comidas":[{{"tipo":"Desayuno","nombre":"...","ingredientes":[{{"producto_id":"ID","cantidad_por_persona":200,"unidad":"g"}}],"preparacion":["Paso 1","Paso 2"]}}]}}]}}

Debes entregar EXACTAMENTE {dias} días y en cada día EXACTAMENTE: {comidas_texto}. Verifica esto antes de responder."""


# ============================================================
# PROMPT DE AJUSTE
# ============================================================


def construir_prompt_ajuste(
    plan,
    compra,
    total,
    presupuesto,
    personas,
    catalogo,
    modo,
):

    catalogo_lineas = []
    for p in catalogo:
        catalogo_lineas.append(
            f"{p['id']}|{p['tienda']}|{p['ingrediente_base']}|"
            f"{p['nombre']}|{p['contenido']}{p['unidad_contenido']}|{p['precio']}"
        )

    plan_compacto = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))

    if modo == "subir":
        objetivo = (
            f"El total actual es ${total:.2f}. Está por debajo del objetivo. "
            f"Mejora cantidades/acompañamientos/variedad para acercarte a "
            f"${presupuesto:.2f}, sin superar ${presupuesto + TOLERANCIA_PRESUPUESTO:.2f}."
        )
    else:
        objetivo = (
            f"El total actual es ${total:.2f}. Debes reducirlo a máximo "
            f"${presupuesto + TOLERANCIA_PRESUPUESTO:.2f}, manteniendo porciones reales "
            f"para {personas} personas y sin eliminar proteínas de forma absurda."
        )

    return f"""Eres KashCook AI y debes AJUSTAR un plan existente.
{objetivo}

Conserva EXACTAMENTE la estructura actual de días y tipos de comida. No omitas ni agregues días o comidas. Las cantidades siguen siendo por persona. Usa SOLO IDs del catálogo. NO compares tiendas.

CATÁLOGO id|tienda|ingrediente|producto|contenido|precio:
{chr(10).join(catalogo_lineas)}

PLAN ACTUAL:
{plan_compacto}

COMPRA ACTUAL:
{json.dumps(compra, ensure_ascii=False, separators=(",", ":"))}

Devuelve SOLO JSON válido en la misma estructura del plan. Cada comida debe conservar nombre, al menos 2 ingredientes y al menos 2 pasos."""


# ============================================================
# GENERAR PDF

# ============================================================

def generar_pdf(
    plan,
    compra,
    total,
    presupuesto,
    personas,
    tiendas,
    total_verificado=False,
):

    buffer = io.BytesIO()

    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1.4 * cm,
        leftMargin=1.4 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
    )

    styles = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "TituloKash",
        parent=styles["Title"],
        fontSize=23,
        leading=27,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    subtitulo = ParagraphStyle(
        "SubtituloKash",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=16,
    )

    dia_style = ParagraphStyle(
        "DiaKash",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        spaceBefore=8,
        spaceAfter=10,
    )

    comida_style = ParagraphStyle(
        "ComidaKash",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=7,
        spaceAfter=5,
    )

    normal = ParagraphStyle(
        "NormalKash",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        spaceAfter=4,
    )

    pequeno = ParagraphStyle(
        "PequenoKash",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
    )

    story = []

    story.append(
        Paragraph(
            "KashCook AI",
            titulo,
        )
    )

    story.append(
        Paragraph(
            f"Plan alimenticio para {personas} persona(s)<br/>"
            f"{len(plan.get('dias', []))} día(s)<br/>"
            f"Tiendas seleccionadas: "
            f"{html.escape(', '.join(tiendas))}<br/>"
            f"Presupuesto: ${presupuesto:,.2f} MXN<br/>"
            + (f"Total de compra verificado: ${total:,.2f} MXN" if total_verificado and total is not None
               else "TOTAL DE COMPRA NO DISPONIBLE: faltan precios actuales verificados"),
            subtitulo,
        )
    )

    # ========================================================
    # RECETAS
    # ========================================================

    for indice, dia in enumerate(
        plan.get("dias", [])
    ):

        story.append(
            Paragraph(
                f"DÍA {dia.get('dia', indice + 1)}",
                dia_style,
            )
        )

        for comida in dia.get(
            "comidas",
            [],
        ):

            tipo = html.escape(
                str(
                    comida.get(
                        "tipo",
                        "Comida",
                    )
                )
            )

            nombre = html.escape(
                str(
                    comida.get(
                        "nombre",
                        "Receta",
                    )
                )
            )

            story.append(
                Paragraph(
                    f"{tipo}: {nombre}",
                    comida_style,
                )
            )

            story.append(
                Paragraph(
                    "<b>Ingredientes:</b>",
                    normal,
                )
            )

            for ing in comida.get(
                "ingredientes",
                [],
            ):

                producto_id = ing.get(
                    "producto_id"
                )

                cantidad = ing.get(
                    "cantidad_por_persona",
                    "",
                )

                unidad = ing.get(
                    "unidad",
                    "",
                )

                producto_encontrado = None

                for lista in CATALOGOS.values():

                    for p in lista:

                        if p["id"] == producto_id:

                            producto_encontrado = p
                            break

                    if producto_encontrado:
                        break

                if producto_encontrado:

                    nombre_producto = (
                        producto_encontrado[
                            "nombre"
                        ]
                    )

                else:

                    nombre_producto = (
                        str(producto_id)
                    )

                story.append(
                    Paragraph(
                        f"• "
                        f"{html.escape(nombre_producto)}: "
                        f"{cantidad} "
                        f"{html.escape(str(unidad))} "
                        f"por persona",
                        pequeno,
                    )
                )

            story.append(
                Spacer(
                    1,
                    4,
                )
            )

            story.append(
                Paragraph(
                    "<b>Preparación:</b>",
                    normal,
                )
            )

            pasos = comida.get(
                "preparacion",
                [],
            )

            if not pasos:

                pasos = [
                    "Preparar los ingredientes, "
                    "cocinar completamente y servir."
                ]

            for numero, paso in enumerate(
                pasos,
                1,
            ):

                story.append(
                    Paragraph(
                        f"{numero}. "
                        f"{html.escape(str(paso))}",
                        pequeno,
                    )
                )

            story.append(
                Spacer(
                    1,
                    8,
                )
            )

        if indice < len(
            plan.get("dias", [])
        ) - 1:

            story.append(
                PageBreak()
            )

    # ========================================================
    # LISTA DE COMPRA
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "LISTA DE COMPRA",
            dia_style,
        )
    )

    story.append(
        Paragraph(
            "Las cantidades se calcularon considerando "
            "el número de personas y las presentaciones "
            "de los productos.",
            normal,
        )
    )

    datos = [
        [
            Paragraph(
                "<b>Producto</b>",
                pequeno,
            ),
            Paragraph(
                "<b>Presentación</b>",
                pequeno,
            ),
            Paragraph(
                "<b>Cantidad</b>",
                pequeno,
            ),
            Paragraph(
                "<b>Precio</b>",
                pequeno,
            ),
            Paragraph(
                "<b>Total</b>",
                pequeno,
            ),
            Paragraph(
                "<b>Tienda</b>",
                pequeno,
            ),
        ]
    ]

    for item in compra:

        datos.append(
            [
                Paragraph(
                    html.escape(
                        item["producto"]
                    ),
                    pequeno,
                ),

                Paragraph(
                    html.escape(
                        item["presentacion"]
                    ),
                    pequeno,
                ),

                Paragraph(
                    str(
                        item["paquetes"]
                    ),
                    pequeno,
                ),

                Paragraph(
                    f"${item['precio_unitario']:,.2f}" if item.get("estado_precio") == "Verificado" else "Sin verificar",
                    pequeno,
                ),

                Paragraph(
                    f"${item['subtotal']:,.2f}" if item.get("estado_precio") == "Verificado" else "No calculable",
                    pequeno,
                ),

                Paragraph(
                    html.escape(
                        item["tienda"]
                    ),
                    pequeno,
                ),
            ]
        )

    tabla = Table(
        datos,
        colWidths=[
            4.0 * cm,
            4.0 * cm,
            1.1 * cm,
            1.7 * cm,
            1.7 * cm,
            2.6 * cm,
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
                    colors.HexColor("#222222"),
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),

                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),

                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),

                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
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

    story.append(
        Spacer(
            1,
            12,
        )
    )

    mensaje_total = (
        f"<b>TOTAL DE COMPRA VERIFICADO: ${total:,.2f} MXN</b>"
        if total_verificado and total is not None
        else "<b>TOTAL DE COMPRA NO DISPONIBLE</b><br/>Hay productos cuyo precio actual no se pudo verificar en la tienda seleccionada. No se calculó ni se presenta un total estimado como si fuera real."
    )
    story.append(Paragraph(
        mensaje_total,
        ParagraphStyle("TotalKash", parent=normal, fontSize=12, leading=16),
    ))

    story.append(
        Paragraph(
            f"Presupuesto original: "
            f"${presupuesto:,.2f} MXN",
            normal,
        )
    )

    if total_verificado and total is not None and total <= presupuesto:

        story.append(
            Paragraph(
                f"Disponible restante: "
                f"${presupuesto - total:,.2f} MXN",
                normal,
            )
        )

    elif total_verificado and total is not None:

        story.append(
            Paragraph(
                f"Excedente utilizado: "
                f"${total - presupuesto:,.2f} MXN",
                normal,
            )
        )

    documento.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()



# ============================================================
# MOTOR DE RECETAS REALES Y PLANIFICACIÓN LOCAL
# ============================================================
# KashCook NO inventa nombres de platillos. El catálogo siguiente contiene
# platillos tradicionales/documentados; la IA, si está disponible, solo puede
# escoger IDs de esta biblioteca. Ingredientes, cantidades y preparación son
# definidos localmente y después se enlazan con productos reales del catálogo.

RECETAS_REALES = {
    # ---------------- DESAYUNOS ----------------
    "huevos_mexicana": {"tipo":"Desayuno","nombre":"Huevos a la mexicana","fuente":"Recetas mexicanas tradicionales","ingredientes":[("huevo",2,"pieza"),("tomate",0.10,"kg"),("cebolla",0.03,"kg"),("tortilla",0.12,"kg"),("aceite",10,"ml")],"pasos":["Pica el tomate y la cebolla. Sofríe la cebolla en el aceite hasta que esté transparente.","Agrega el tomate y cocina hasta que se suavice y forme una salsa rústica.","Añade los huevos batidos, sazona y cocina moviendo hasta que queden cuajados pero jugosos.","Calienta las tortillas y sirve los huevos recién hechos."]},
    "huevos_rancheros": {"tipo":"Desayuno","nombre":"Huevos rancheros","fuente":"Recetas Nestlé México","ingredientes":[("huevo",2,"pieza"),("tomate",0.12,"kg"),("cebolla",0.03,"kg"),("tortilla",0.12,"kg"),("aceite",10,"ml")],"pasos":["Asa o sofríe ligeramente el tomate y la cebolla; licúa o machaca hasta obtener una salsa rústica.","Calienta la salsa unos minutos hasta que tome cuerpo y rectifica la sal.","Fríe o cocina los huevos al punto deseado.","Sirve los huevos bañados con salsa y acompaña con tortillas calientes."]},
    "papas_huevo": {"tipo":"Desayuno","nombre":"Papas con huevo a la mexicana","fuente":"Cocina mexicana tradicional","ingredientes":[("huevo",2,"pieza"),("papa",0.18,"kg"),("tomate",0.06,"kg"),("cebolla",0.03,"kg"),("tortilla",0.10,"kg"),("aceite",12,"ml")],"pasos":["Corta la papa en cubos pequeños y cocínala en sartén con aceite hasta que esté dorada y tierna.","Agrega cebolla y tomate picados y cocina hasta que las verduras estén suaves.","Incorpora los huevos batidos, sazona y remueve hasta que cuajen.","Sirve caliente con tortillas."]},
    "frijoles_huevo": {"tipo":"Desayuno","nombre":"Huevos con frijoles de la olla","fuente":"Cocina mexicana tradicional","ingredientes":[("huevo",2,"pieza"),("frijol",0.12,"kg"),("tomate",0.05,"kg"),("cebolla",0.02,"kg"),("tortilla",0.10,"kg"),("aceite",10,"ml")],"pasos":["Calienta los frijoles con un poco de su caldo hasta que estén bien calientes.","Sofríe cebolla y tomate picados y agrega los huevos batidos.","Cocina hasta que el huevo esté cuajado y sazona al gusto.","Sirve los huevos con frijoles y tortillas calientes."]},
    "quesadillas_calabacita": {"tipo":"Desayuno","nombre":"Quesadillas de calabacita y queso","fuente":"Cocina mexicana tradicional","ingredientes":[("tortilla",0.15,"kg"),("queso",0.06,"kg"),("calabaza",0.15,"kg"),("cebolla",0.02,"kg"),("tomate",0.05,"kg"),("aceite",8,"ml")],"pasos":["Saltea la calabacita y la cebolla picadas hasta que estén tiernas.","Calienta las tortillas y reparte calabacita y queso en cada una.","Dobla las tortillas y cocina por ambos lados hasta que el queso se funda y la tortilla quede ligeramente dorada.","Acompaña con tomate picado o una salsa de tomate casera."]},
    "enfrijoladas_queso": {"tipo":"Desayuno","nombre":"Enfrijoladas de queso fresco","fuente":"Cocina mexicana tradicional","ingredientes":[("tortilla",0.18,"kg"),("frijol",0.10,"kg"),("queso",0.05,"kg"),("cebolla",0.02,"kg"),("aceite",8,"ml")],"pasos":["Calienta los frijoles con un poco de agua y licúalos o machácalos hasta obtener una salsa espesa.","Calienta la salsa de frijol y ajusta su consistencia para que cubra las tortillas.","Pasa cada tortilla por la salsa caliente, dóblala y rellénala con queso fresco.","Sirve varias enfrijoladas juntas y termina con cebolla picada y queso."]},
    "arroz_huevo": {"tipo":"Desayuno","nombre":"Arroz con huevo a la mexicana","fuente":"Cocina mexicana casera","ingredientes":[("arroz",0.08,"kg"),("huevo",2,"pieza"),("tomate",0.08,"kg"),("cebolla",0.03,"kg"),("aceite",10,"ml")],"pasos":["Calienta el arroz cocido o prepáralo previamente hasta que quede suelto.","Sofríe cebolla y tomate picados en un poco de aceite.","Agrega el arroz y mezcla para que tome sabor.","Incorpora los huevos batidos y cocina hasta que estén completamente cuajados. Sirve caliente."]},
    "tortitas_papa": {"tipo":"Desayuno","nombre":"Tortitas de papa con queso","fuente":"Recetas mexicanas caseras","ingredientes":[("papa",0.22,"kg"),("queso",0.05,"kg"),("huevo",1,"pieza"),("cebolla",0.02,"kg"),("aceite",12,"ml"),("tortilla",0.08,"kg")],"pasos":["Cuece la papa hasta que esté suave, escúrrela y machácala.","Mezcla la papa con queso, cebolla picada y huevo hasta obtener una masa manejable.","Forma tortitas y dóralas en una sartén con poco aceite por ambos lados.","Sirve calientes con tortillas."]},

    # ---------------- COMIDAS / CENAS ----------------
    "picadillo": {"tipo":"Comida","nombre":"Picadillo de res a la mexicana","fuente":"Recetas Nestlé México / Kiwilimón","ingredientes":[("molida",0.16,"kg"),("papa",0.18,"kg"),("zanahoria",0.10,"kg"),("tomate",0.14,"kg"),("cebolla",0.04,"kg"),("aceite",12,"ml"),("arroz",0.08,"kg")],"pasos":["Sofríe la cebolla y agrega la carne molida; cocina hasta que cambie completamente de color.","Añade papa y zanahoria en cubos pequeños y cocina unos minutos.","Licúa o machaca el tomate con un poco de agua, incorpora la salsa y sazona.","Tapa y cocina hasta que las verduras estén tiernas y el guiso haya espesado.","Sirve con arroz blanco."]},
    "bistec_ranchero": {"tipo":"Comida","nombre":"Bistec ranchero","fuente":"Recetas Nestlé México","ingredientes":[("res",0.18,"kg"),("papa",0.15,"kg"),("tomate",0.14,"kg"),("cebolla",0.04,"kg"),("aceite",12,"ml"),("tortilla",0.10,"kg")],"pasos":["Corta el bistec en tiras o cubos y dóralo en una sartén caliente con un poco de aceite.","Agrega cebolla y papa en cubos y cocina hasta que comiencen a dorarse.","Incorpora el tomate picado y un poco de agua; cocina hasta formar una salsa ligera.","Rectifica la sazón y sirve caliente con tortillas."]},
    "bistec_cebollado": {"tipo":"Comida","nombre":"Bistec encebollado","fuente":"Kiwilimón","ingredientes":[("res",0.18,"kg"),("cebolla",0.10,"kg"),("tomate",0.06,"kg"),("aceite",12,"ml"),("tortilla",0.10,"kg"),("frijol",0.10,"kg")],"pasos":["Corta la carne en tiras y sazona.","Sella la carne en una sartén caliente con poco aceite.","Agrega abundante cebolla fileteada y tomate; cocina hasta que la cebolla quede suave y ligeramente dorada.","Sirve con frijoles y tortillas calientes."]},
    "carne_papas": {"tipo":"Comida","nombre":"Carne de res con papas en salsa de tomate","fuente":"Cocina mexicana casera","ingredientes":[("res",0.17,"kg"),("papa",0.20,"kg"),("tomate",0.15,"kg"),("cebolla",0.04,"kg"),("zanahoria",0.08,"kg"),("aceite",12,"ml"),("arroz",0.08,"kg")],"pasos":["Dora la carne en una olla con un poco de aceite.","Agrega cebolla, papa y zanahoria en cubos y sofríe unos minutos.","Incorpora el tomate licuado o machacado con agua y sazona.","Tapa y cocina hasta que la carne y las verduras estén tiernas.","Sirve con arroz blanco."]},
    "pollo_salsa_roja": {"tipo":"Comida","nombre":"Pollo en salsa de tomate","fuente":"Cocina mexicana casera","ingredientes":[("pollo",0.20,"kg"),("tomate",0.16,"kg"),("cebolla",0.04,"kg"),("papa",0.12,"kg"),("aceite",12,"ml"),("arroz",0.08,"kg")],"pasos":["Dora las piezas o trozos de pollo en una olla con poco aceite.","Agrega cebolla y papa en cubos y cocina unos minutos.","Licúa o machaca el tomate con agua, viértelo sobre el pollo y sazona.","Tapa y cocina hasta que el pollo esté bien cocido y la salsa espese.","Acompaña con arroz blanco."]},
    "pollo_mexicana": {"tipo":"Comida","nombre":"Pollo a la mexicana","fuente":"Cocina mexicana tradicional","ingredientes":[("pollo",0.20,"kg"),("tomate",0.14,"kg"),("cebolla",0.04,"kg"),("papa",0.10,"kg"),("zanahoria",0.08,"kg"),("aceite",12,"ml"),("tortilla",0.10,"kg")],"pasos":["Corta el pollo en trozos y dóralo en sartén.","Agrega cebolla, tomate, papa y zanahoria en cubos.","Cocina tapado con un poco de agua hasta que las verduras estén tiernas y el pollo completamente cocido.","Rectifica la sazón y sirve con tortillas calientes."]},
    "pollo_entomatado": {"tipo":"Cena","nombre":"Pollo entomatado con arroz","fuente":"Cocina mexicana casera","ingredientes":[("pollo",0.18,"kg"),("tomate",0.16,"kg"),("cebolla",0.04,"kg"),("arroz",0.08,"kg"),("aceite",10,"ml"),("zanahoria",0.08,"kg")],"pasos":["Dora el pollo con un poco de aceite.","Añade cebolla y tomate picados y cocina hasta que el tomate se deshaga.","Agrega un poco de agua, sazona y cocina tapado hasta que el pollo esté bien cocido.","Sirve con arroz blanco y zanahoria cocida o salteada."]},
    "cerdo_salsa_tomate": {"tipo":"Comida","nombre":"Cerdo en salsa de tomate","fuente":"Cocina mexicana casera","ingredientes":[("puerco",0.18,"kg"),("tomate",0.16,"kg"),("cebolla",0.04,"kg"),("papa",0.14,"kg"),("aceite",12,"ml"),("arroz",0.08,"kg")],"pasos":["Dora el cerdo en una olla con poco aceite.","Añade cebolla y papa en cubos y cocina unos minutos.","Agrega tomate licuado o machacado con agua y sazona.","Tapa y cocina hasta que el cerdo esté completamente cocido y la salsa espesa.","Sirve con arroz."]},
    "cerdo_papas": {"tipo":"Comida","nombre":"Cerdo con papas a la mexicana","fuente":"Cocina mexicana casera","ingredientes":[("puerco",0.18,"kg"),("papa",0.20,"kg"),("tomate",0.12,"kg"),("cebolla",0.04,"kg"),("zanahoria",0.08,"kg"),("aceite",12,"ml"),("tortilla",0.10,"kg")],"pasos":["Dora el cerdo en una sartén amplia.","Añade papa y zanahoria en cubos y cocina hasta que empiecen a dorar.","Incorpora cebolla y tomate picados y agrega un poco de agua.","Tapa y cocina hasta que la carne y las verduras estén tiernas.","Sirve con tortillas calientes."]},
    "pescado_mexicana": {"tipo":"Comida","nombre":"Pescado a la mexicana","fuente":"Cocina mexicana tradicional","ingredientes":[("pescado",0.20,"kg"),("tomate",0.14,"kg"),("cebolla",0.04,"kg"),("zanahoria",0.08,"kg"),("aceite",12,"ml"),("arroz",0.08,"kg")],"pasos":["Seca y sazona los filetes de pescado.","Sofríe cebolla y tomate picados hasta que estén suaves.","Agrega el pescado y cocina tapado hasta que esté opaco y completamente cocido.","Acompaña con zanahoria y arroz blanco."]},
    "pescado_tomate": {"tipo":"Cena","nombre":"Filete de pescado en salsa de tomate","fuente":"Cocina casera mexicana","ingredientes":[("pescado",0.20,"kg"),("tomate",0.16,"kg"),("cebolla",0.04,"kg"),("papa",0.12,"kg"),("aceite",12,"ml"),("tortilla",0.10,"kg")],"pasos":["Sella el pescado por ambos lados con poco aceite y retira temporalmente.","Sofríe cebolla y agrega tomate licuado o picado; cocina hasta obtener una salsa.","Incorpora papa previamente cocida en cubos y vuelve a colocar el pescado.","Tapa y cocina unos minutos hasta que el pescado esté completamente cocido. Sirve con tortillas."]},
    "atun_arroz": {"tipo":"Cena","nombre":"Atún a la mexicana con arroz","fuente":"Cocina mexicana casera","ingredientes":[("atun",0.5,"pieza"),("tomate",0.10,"kg"),("cebolla",0.03,"kg"),("papa",0.12,"kg"),("arroz",0.08,"kg"),("aceite",10,"ml")],"pasos":["Escurre el atún y reserva.","Sofríe cebolla y tomate picados; agrega papa cocida en cubos.","Incorpora el atún y cocina solo unos minutos para integrar sabores.","Sirve con arroz blanco."]},
    "ensalada_atun_papa": {"tipo":"Cena","nombre":"Ensalada de atún con papa a la mexicana","fuente":"Cocina mexicana casera","ingredientes":[("atun",0.5,"pieza"),("papa",0.16,"kg"),("lechuga",0.08,"pieza"),("tomate",0.08,"kg"),("cebolla",0.03,"kg")],"pasos":["Cuece la papa en cubos hasta que esté tierna y déjala enfriar.","Escurre el atún y mézclalo con tomate y cebolla picados.","Incorpora la papa con cuidado y sazona al gusto.","Sirve sobre lechuga fresca y acompaña con tortillas si se desea." ]},
    "sardinas_arroz": {"tipo":"Comida","nombre":"Sardinas en tomate con arroz","fuente":"Cocina mexicana casera","ingredientes":[("sardina",0.50,"kg"),("tomate",0.10,"kg"),("cebolla",0.03,"kg"),("arroz",0.08,"kg"),("papa",0.10,"kg")],"pasos":["Prepara arroz blanco y mantenlo caliente.","Sofríe cebolla y agrega tomate picado hasta que se forme una salsa ligera.","Incorpora las sardinas con cuidado para no deshacerlas demasiado y calienta suavemente.","Sirve las sardinas con arroz y papa cocida o dorada."]},
    "calabacitas_queso": {"tipo":"Cena","nombre":"Calabacitas con queso","fuente":"Recetas Nestlé México","ingredientes":[("calabaza",0.25,"kg"),("queso",0.06,"kg"),("tomate",0.10,"kg"),("cebolla",0.04,"kg"),("papa",0.12,"kg"),("aceite",10,"ml"),("frijol",0.10,"kg")],"pasos":["Sofríe cebolla y tomate picados.","Añade calabacita y papa en cubos; cocina tapado hasta que estén tiernas.","Agrega el queso desmoronado y deja que se caliente sin perder completamente su textura.","Sirve con frijoles calientes."]},
    "arroz_frijoles": {"tipo":"Cena","nombre":"Arroz con frijoles y queso fresco","fuente":"Cocina mexicana tradicional","ingredientes":[("arroz",0.09,"kg"),("frijol",0.10,"kg"),("queso",0.04,"kg"),("tomate",0.06,"kg"),("cebolla",0.02,"kg"),("aceite",8,"ml")],"pasos":["Prepara el arroz hasta que quede suelto.","Calienta los frijoles y sazónalos; pueden quedar enteros o ligeramente machacados.","Mezcla una parte del arroz con los frijoles o sírvelos por separado.","Termina con queso fresco y tomate y cebolla picados."]},
    "tacos_papa_queso": {"tipo":"Cena","nombre":"Tacos de papa con queso","fuente":"Cocina mexicana tradicional","ingredientes":[("tortilla",0.18,"kg"),("papa",0.22,"kg"),("queso",0.05,"kg"),("cebolla",0.02,"kg"),("aceite",12,"ml"),("frijol",0.10,"kg")],"pasos":["Cuece las papas y machácalas con cebolla picada.","Calienta las tortillas y rellénalas con papa y queso.","Dobla los tacos y dóralos en una sartén con poco aceite.","Sirve con frijoles calientes."]},
    "tortitas_papa_comida": {"tipo":"Comida","nombre":"Tortitas de papa con queso y frijoles","fuente":"Cocina mexicana tradicional","ingredientes":[("papa",0.25,"kg"),("queso",0.06,"kg"),("huevo",1,"pieza"),("cebolla",0.03,"kg"),("aceite",12,"ml"),("frijol",0.12,"kg"),("tomate",0.06,"kg")],"pasos":["Cuece y machaca las papas.","Mezcla con huevo, queso y cebolla; forma tortitas.","Dora las tortitas en poco aceite por ambos lados.","Sirve con frijoles y tomate picado."]},
    'chilaquiles_rojos': {"tipo":'Desayuno',"nombre":'Chilaquiles rojos con huevo y queso',"fuente":'Cocina mexicana casera',"ingredientes":[('tortilla', 0.18, 'kg'), ('tomate', 0.16, 'kg'), ('cebolla', 0.03, 'kg'), ('huevo', 2, 'pieza'), ('queso', 0.04, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de chilaquiles rojos con huevo y queso y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'omelette_calabacita': {"tipo":'Desayuno',"nombre":'Omelette de calabacita y queso',"fuente":'Cocina mexicana casera',"ingredientes":[('huevo', 2, 'pieza'), ('calabaza', 0.15, 'kg'), ('queso', 0.05, 'kg'), ('tomate', 0.05, 'kg'), ('cebolla', 0.02, 'kg'), ('aceite', 8, 'ml')],"pasos":['Prepara los ingredientes de omelette de calabacita y queso y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'huevos_arroz_frijol': {"tipo":'Desayuno',"nombre":'Huevos estrellados con arroz y frijoles',"fuente":'Cocina mexicana casera',"ingredientes":[('huevo', 2, 'pieza'), ('arroz', 0.1, 'kg'), ('frijol', 0.1, 'kg'), ('tomate', 0.06, 'kg'), ('cebolla', 0.02, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de huevos estrellados con arroz y frijoles y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'quesadillas_papa': {"tipo":'Desayuno',"nombre":'Quesadillas de papa con queso',"fuente":'Cocina mexicana casera',"ingredientes":[('tortilla', 0.16, 'kg'), ('papa', 0.18, 'kg'), ('queso', 0.06, 'kg'), ('cebolla', 0.02, 'kg'), ('tomate', 0.05, 'kg'), ('aceite', 8, 'ml')],"pasos":['Prepara los ingredientes de quesadillas de papa con queso y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'flautas_papa': {"tipo":'Desayuno',"nombre":'Flautas de papa con queso y lechuga',"fuente":'Cocina mexicana casera',"ingredientes":[('tortilla', 0.18, 'kg'), ('papa', 0.2, 'kg'), ('queso', 0.04, 'kg'), ('lechuga', 0.08, 'pieza'), ('tomate', 0.06, 'kg'), ('aceite', 14, 'ml')],"pasos":['Prepara los ingredientes de flautas de papa con queso y lechuga y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'huevos_tomate_papa': {"tipo":'Desayuno',"nombre":'Huevos con tomate, cebolla y papa',"fuente":'Cocina mexicana casera',"ingredientes":[('huevo', 2, 'pieza'), ('tomate', 0.14, 'kg'), ('cebolla', 0.05, 'kg'), ('papa', 0.1, 'kg'), ('tortilla', 0.1, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de huevos con tomate, cebolla y papa y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'tostadas_frijol_huevo': {"tipo":'Desayuno',"nombre":'Frijoles con huevo y queso sobre tortilla dorada',"fuente":'Cocina mexicana casera',"ingredientes":[('tortilla', 0.16, 'kg'), ('frijol', 0.12, 'kg'), ('huevo', 2, 'pieza'), ('queso', 0.04, 'kg'), ('tomate', 0.06, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de frijoles con huevo y queso sobre tortilla dorada y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'migas_mexicanas': {"tipo":'Desayuno',"nombre":'Migas mexicanas con huevo y queso',"fuente":'Cocina mexicana casera',"ingredientes":[('tortilla', 0.16, 'kg'), ('huevo', 2, 'pieza'), ('tomate', 0.08, 'kg'), ('cebolla', 0.03, 'kg'), ('queso', 0.04, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de migas mexicanas con huevo y queso y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'tinga_pollo': {"tipo":'Comida',"nombre":'Tinga de pollo casera',"fuente":'Cocina mexicana tradicional',"ingredientes":[('pollo', 0.2, 'kg'), ('tomate', 0.18, 'kg'), ('cebolla', 0.08, 'kg'), ('zanahoria', 0.06, 'kg'), ('aceite', 10, 'ml'), ('tortilla', 0.12, 'kg')],"pasos":['Prepara los ingredientes de tinga de pollo casera y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'albondigas': {"tipo":'Comida',"nombre":'Albóndigas de res en caldillo de tomate',"fuente":'Cocina mexicana tradicional',"ingredientes":[('molida', 0.18, 'kg'), ('arroz', 0.04, 'kg'), ('tomate', 0.18, 'kg'), ('cebolla', 0.05, 'kg'), ('zanahoria', 0.1, 'kg'), ('papa', 0.12, 'kg')],"pasos":['Prepara los ingredientes de albóndigas de res en caldillo de tomate y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'carne_molida_papas': {"tipo":'Comida',"nombre":'Carne molida con papas y zanahoria',"fuente":'Cocina mexicana tradicional',"ingredientes":[('molida', 0.18, 'kg'), ('papa', 0.2, 'kg'), ('zanahoria', 0.1, 'kg'), ('tomate', 0.14, 'kg'), ('cebolla', 0.04, 'kg'), ('aceite', 12, 'ml'), ('tortilla', 0.1, 'kg')],"pasos":['Prepara los ingredientes de carne molida con papas y zanahoria y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'pollo_papas': {"tipo":'Comida',"nombre":'Pollo con papas y zanahoria guisado',"fuente":'Cocina mexicana tradicional',"ingredientes":[('pollo', 0.2, 'kg'), ('papa', 0.2, 'kg'), ('zanahoria', 0.1, 'kg'), ('tomate', 0.14, 'kg'), ('cebolla', 0.04, 'kg'), ('aceite', 12, 'ml'), ('arroz', 0.08, 'kg')],"pasos":['Prepara los ingredientes de pollo con papas y zanahoria guisado y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'pollo_tomate_arroz': {"tipo":'Comida',"nombre":'Pollo guisado con tomate y arroz',"fuente":'Cocina mexicana tradicional',"ingredientes":[('pollo', 0.2, 'kg'), ('tomate', 0.18, 'kg'), ('cebolla', 0.04, 'kg'), ('zanahoria', 0.08, 'kg'), ('arroz', 0.09, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de pollo guisado con tomate y arroz y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'cerdo_papa_tomate': {"tipo":'Comida',"nombre":'Guisado de cerdo con tomate y papa',"fuente":'Cocina mexicana tradicional',"ingredientes":[('puerco', 0.18, 'kg'), ('papa', 0.2, 'kg'), ('tomate', 0.16, 'kg'), ('cebolla', 0.04, 'kg'), ('zanahoria', 0.08, 'kg'), ('aceite', 12, 'ml'), ('tortilla', 0.1, 'kg')],"pasos":['Prepara los ingredientes de guisado de cerdo con tomate y papa y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'pescado_papa_tomate': {"tipo":'Comida',"nombre":'Pescado guisado con papa y tomate',"fuente":'Cocina mexicana tradicional',"ingredientes":[('pescado', 0.2, 'kg'), ('papa', 0.18, 'kg'), ('tomate', 0.16, 'kg'), ('cebolla', 0.04, 'kg'), ('zanahoria', 0.08, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de pescado guisado con papa y tomate y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'atun_papa': {"tipo":'Comida',"nombre":'Atún guisado con papa y tomate',"fuente":'Cocina mexicana tradicional',"ingredientes":[('atun', 1, 'pieza'), ('papa', 0.18, 'kg'), ('tomate', 0.14, 'kg'), ('cebolla', 0.04, 'kg'), ('zanahoria', 0.08, 'kg'), ('tortilla', 0.1, 'kg')],"pasos":['Prepara los ingredientes de atún guisado con papa y tomate y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'sardinas_papa': {"tipo":'Cena',"nombre":'Sardinas guisadas con papa y tomate',"fuente":'Cocina mexicana tradicional',"ingredientes":[('sardina', 0.5, 'kg'), ('papa', 0.16, 'kg'), ('tomate', 0.14, 'kg'), ('cebolla', 0.04, 'kg'), ('zanahoria', 0.08, 'kg'), ('tortilla', 0.1, 'kg')],"pasos":['Prepara los ingredientes de sardinas guisadas con papa y tomate y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'calabacitas_arroz': {"tipo":'Cena',"nombre":'Calabacitas guisadas con queso y arroz',"fuente":'Cocina mexicana tradicional',"ingredientes":[('calabaza', 0.25, 'kg'), ('tomate', 0.12, 'kg'), ('cebolla', 0.04, 'kg'), ('queso', 0.06, 'kg'), ('arroz', 0.09, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de calabacitas guisadas con queso y arroz y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'frijoles_arroz_huevo': {"tipo":'Cena',"nombre":'Plato de frijoles, arroz y huevo',"fuente":'Cocina mexicana tradicional',"ingredientes":[('frijol', 0.14, 'kg'), ('arroz', 0.1, 'kg'), ('huevo', 2, 'pieza'), ('tomate', 0.06, 'kg'), ('cebolla', 0.03, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de plato de frijoles, arroz y huevo y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'enchiladas_queso': {"tipo":'Cena',"nombre":'Enchiladas rojas de queso fresco',"fuente":'Cocina mexicana tradicional',"ingredientes":[('tortilla', 0.2, 'kg'), ('tomate', 0.18, 'kg'), ('cebolla', 0.03, 'kg'), ('queso', 0.07, 'kg'), ('frijol', 0.1, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de enchiladas rojas de queso fresco y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},
    'tacos_atun': {"tipo":'Cena',"nombre":'Tacos de atún con papa y queso',"fuente":'Cocina mexicana tradicional',"ingredientes":[('tortilla', 0.18, 'kg'), ('atun', 1, 'pieza'), ('papa', 0.16, 'kg'), ('queso', 0.05, 'kg'), ('tomate', 0.06, 'kg'), ('cebolla', 0.03, 'kg'), ('aceite', 10, 'ml')],"pasos":['Prepara los ingredientes de tacos de atún con papa y queso y cocina cada componente hasta que quede bien cocido.', 'Integra los ingredientes principales y deja que se mezclen los sabores a fuego medio.', 'Ajusta la sazón y termina la preparación con la guarnición indicada.', 'Sirve caliente y aprovecha las porciones completas para evitar desperdicios.']},}


# Recetas verificadas en fuentes culinarias externas.
RECETAS_REALES.update({
    "camaron_mexicana": {"tipo":"Comida","nombre":"Camarón a la mexicana","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/camarones-a-la-mexicana","verificada":True,"cocina":"Mexicana","ingredientes":[("camaron",0.175,"kg"),("tomate",0.12,"kg"),("cebolla",0.04,"kg"),("aceite",8,"ml")],"pasos":["Sofríe la cebolla en aceite hasta que empiece a transparentar.","Agrega el camarón y cocina hasta que cambie de color y quede completamente cocido.","Incorpora el jitomate picado y cocina unos minutos para integrar la salsa.","Sazona y sirve inmediatamente; la receta original también contempla chile, ajo y condimentos."]},
    "camaron_oriental": {"tipo":"Cena","nombre":"Camarones orientales","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/camarones-orientales","verificada":True,"cocina":"Asiática","ingredientes":[("camaron",0.25,"kg"),("cebolla",0.03,"kg"),("aceite",10,"ml")],"pasos":["Marina los camarones con los condimentos de la receta original.","Sofríe la cebolla en aceite y agrega los camarones.","Cocina hasta que estén completamente cocidos y la salsa se integre.","Sirve caliente; la receta original incorpora salsa de soya y cátsup para el acabado oriental."]},
    "picadillo_verificado": {"tipo":"Comida","nombre":"Picadillo de carne molida estilo casero","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/picadillo-de-carne-molida-estilo-casero","verificada":True,"cocina":"Mexicana","ingredientes":[("molida",0.133,"kg"),("papa",0.17,"kg"),("zanahoria",0.10,"kg"),("tomate",0.18,"kg"),("cebolla",0.03,"kg"),("aceite",8,"ml")],"pasos":["Sofríe la cebolla y cocina la carne molida hasta que cambie completamente de color.","Agrega papa y zanahoria y cocina unos minutos.","Incorpora el jitomate licuado y cocina hasta que las verduras estén suaves y la salsa reduzca.","Sirve caliente con el acompañamiento elegido."]},
    "pescado_mexicana_verificado": {"tipo":"Comida","nombre":"Pescado a la mexicana","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/pescado-mexicana","verificada":True,"cocina":"Mexicana","ingredientes":[("pescado",0.12,"kg"),("cebolla",0.03,"kg"),("tomate",0.12,"kg"),("aceite",6,"ml")],"pasos":["Coloca el pescado con cebolla y jitomate y cocina con el sazonador de la receta original.","Cocina hasta que el filete esté completamente hecho.","Comprueba que la carne se desmenuce fácilmente y sirve caliente."]},
    "pollo_pimientos_verificado": {"tipo":"Comida","nombre":"Pollo con pimientos","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/pollo-pimientos","verificada":True,"cocina":"Mexicana","ingredientes":[("pollo",0.20,"kg"),("cebolla",0.04,"kg"),("aceite",10,"ml")],"pasos":["Saltea la cebolla y los pimientos de la receta original.","Agrega el pollo y dóralo por ambos lados.","Incorpora los condimentos de la receta y continúa la cocción hasta que el pollo esté completamente cocido.","Sirve caliente; la fuente recomienda acompañarlo con arroz blanco."]},
    "pollo_agridulce_verificado": {"tipo":"Comida","nombre":"Pollo agridulce","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/pollo-agridulce","verificada":True,"cocina":"Asiática","ingredientes":[("pollo",0.20,"kg"),("cebolla",0.04,"kg"),("calabaza",0.13,"kg"),("aceite",8,"ml")],"pasos":["Dora la cebolla y la calabacita en aceite.","Agrega el pollo y cocina hasta que tome color.","Incorpora la salsa y los condimentos de la receta original y deja reducir.","Sirve caliente; la fuente recomienda acompañar con arroz frito."]},
    "cerdo_crema_verificado": {"tipo":"Comida","nombre":"Cerdo a la crema","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/cerdo-a-la-crema","verificada":True,"cocina":"Mexicana","ingredientes":[("puerco",0.25,"kg"),("aceite",8,"ml")],"pasos":["Dora el cerdo con aceite.","Cocina el cerdo hasta que esté tierno.","Prepara la salsa cremosa con los ingredientes de la receta original y reincorpora la carne.","Cocina unos minutos más y sirve caliente."]},
    "res_pimienta_verificado": {"tipo":"Comida","nombre":"Puntas de res en salsa de pimienta","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/puntas-res-salsa-pimienta","verificada":True,"cocina":"Mexicana","ingredientes":[("res",0.15,"kg"),("cebolla",0.03,"kg"),("aceite",8,"ml")],"pasos":["Cocina las fajitas de res hasta que estén doradas.","Prepara la salsa de pimienta siguiendo la base de la receta original.","Cocina la salsa hasta que espese y báñala sobre la carne.","Sirve inmediatamente."]},
    "atun_bolitas_verificado": {"tipo":"Cena","nombre":"Bolitas de atún","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/bolitas-de-atun","verificada":True,"cocina":"Mexicana","ingredientes":[("atun",0.5,"pieza"),("huevo",0.5,"pieza"),("aceite",10,"ml"),("papa",0.08,"kg")],"pasos":["Mezcla el atún con huevo, papa y los condimentos de la receta original.","Forma las bolitas y rebózalas según la preparación original.","Fríe hasta que estén doradas y escurre el exceso de aceite.","Sirve calientes con ensalada o una guarnición ligera."]},
    "huevos_mexicana_verificados": {"tipo":"Desayuno","nombre":"Huevos a la mexicana","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/huevos-mexicana-desayuno","verificada":True,"cocina":"Mexicana","ingredientes":[("huevo",2,"pieza"),("tomate",0.10,"kg"),("cebolla",0.03,"kg"),("aceite",8,"ml")],"pasos":["Sofríe la cebolla y agrega el jitomate hasta que se suavice.","Bate los huevos y agrégalos al sartén.","Cocina moviendo hasta que el huevo quede cuajado y sirve caliente."]},
    "huevos_rancheros_verificados": {"tipo":"Desayuno","nombre":"Huevos rancheros","fuente":"Recetas Nestlé México","fuente_url":"https://www.recetasnestle.com.mx/recetas/huevos-rancheros","verificada":True,"cocina":"Mexicana","ingredientes":[("huevo",2,"pieza"),("tomate",0.15,"kg"),("cebolla",0.04,"kg"),("tortilla",0.10,"kg"),("aceite",8,"ml")],"pasos":["Prepara la salsa ranchera con jitomate, cebolla y los chiles de la receta original.","Cocina los huevos al punto deseado.","Sirve los huevos con la salsa caliente y tortillas."]},
})

# ---------------- AMPLIACIÓN DE PLATILLOS REALES ----------------
# Son preparaciones reconocibles de cocina mexicana/casera. Se mantienen dentro
# de los ingredientes que KashCook ya puede comprar para no crear ingredientes
# "fantasma" que luego desaparezcan de la lista de compras.
RECETAS_REALES.update({
    "enchiladas_rojas_pollo": {
        "tipo":"Comida","nombre":"Enchiladas rojas de pollo",
        "fuente":"Receta tradicional mexicana","verificada":False,"cocina":"Mexicana",
        "ingredientes":[("tortilla",0.15,"kg"),("pollo",0.18,"kg"),("tomate",0.16,"kg"),("cebolla",0.03,"kg"),("queso",0.04,"kg"),("aceite",8,"ml")],
        "pasos":["Cuece y deshebra el pollo.","Prepara una salsa de jitomate con cebolla y deja que reduzca.","Calienta las tortillas, rellénalas con pollo y báñalas con la salsa roja.","Termina con queso y cebolla y sirve calientes."],
    },
    "tostadas_tinga_pollo": {
        "tipo":"Comida","nombre":"Tostadas de tinga de pollo",
        "fuente":"Receta tradicional mexicana","verificada":False,"cocina":"Mexicana",
        "ingredientes":[("tortilla",0.15,"kg"),("pollo",0.18,"kg"),("tomate",0.14,"kg"),("cebolla",0.06,"kg"),("lechuga",0.10,"pieza"),("queso",0.04,"kg"),("aceite",8,"ml")],
        "pasos":["Cuece y deshebra el pollo.","Cocina cebolla y jitomate hasta formar la base de la tinga.","Incorpora el pollo y deja que absorba la salsa.","Dora las tortillas hasta obtener tostadas y sirve la tinga con lechuga y queso."],
    },
    "tacos_carne_asada": {
        "tipo":"Comida","nombre":"Tacos de carne asada",
        "fuente":"Receta tradicional mexicana","verificada":False,"cocina":"Mexicana",
        "ingredientes":[("res",0.18,"kg"),("tortilla",0.15,"kg"),("cebolla",0.04,"kg"),("tomate",0.10,"kg"),("aceite",6,"ml")],
        "pasos":["Corta la carne en tiras o trozos pequeños y sazona.","Sella la carne a fuego alto hasta el punto deseado.","Asa la cebolla y prepara tomate picado como acompañamiento.","Sirve la carne en tortillas calientes."],
    },
    "tacos_pollo_mexicana": {
        "tipo":"Comida","nombre":"Tacos de pollo a la mexicana",
        "fuente":"Receta tradicional mexicana","verificada":False,"cocina":"Mexicana",
        "ingredientes":[("pollo",0.18,"kg"),("tortilla",0.15,"kg"),("tomate",0.12,"kg"),("cebolla",0.04,"kg"),("aceite",8,"ml")],
        "pasos":["Cocina y deshebra el pollo.","Sofríe cebolla y jitomate hasta formar un guiso.","Agrega el pollo y cocina unos minutos para integrar los sabores.","Sirve en tortillas calientes."],
    },
    "tostadas_pollo": {
        "tipo":"Cena","nombre":"Tostadas de pollo",
        "fuente":"Receta tradicional mexicana","verificada":False,"cocina":"Mexicana",
        "ingredientes":[("tortilla",0.15,"kg"),("pollo",0.15,"kg"),("frijol",0.06,"kg"),("lechuga",0.10,"pieza"),("tomate",0.08,"kg"),("queso",0.04,"kg"),("aceite",8,"ml")],
        "pasos":["Cuece y deshebra el pollo.","Dora las tortillas hasta que estén crujientes.","Unta una capa de frijoles y agrega el pollo.","Termina con lechuga, tomate y queso."],
    },
    "carne_asada_cebolla": {
        "tipo":"Cena","nombre":"Carne asada con cebolla y tomate",
        "fuente":"Receta tradicional mexicana","verificada":False,"cocina":"Mexicana",
        "ingredientes":[("res",0.18,"kg"),("cebolla",0.06,"kg"),("tomate",0.10,"kg"),("aceite",6,"ml")],
        "pasos":["Sazona la carne y séllala en una sartén o parrilla.","Asa la cebolla hasta que esté dorada.","Agrega tomate fresco como acompañamiento.","Sirve la carne recién hecha con la cebolla asada."],
    },
    "shakshuka": {
        "tipo":"Cena","nombre":"Shakshuka de tomate y huevo",
        "fuente":"Cocina del Mediterráneo y Medio Oriente","verificada":False,"cocina":"Mediterránea",
        "ingredientes":[("huevo",2,"pieza"),("tomate",0.22,"kg"),("cebolla",0.05,"kg"),("aceite",8,"ml")],
        "pasos":["Sofríe la cebolla en aceite hasta suavizarla.","Agrega el tomate y cocina hasta obtener una salsa espesa.","Haz huecos en la salsa y añade los huevos.","Tapa y cocina hasta que las claras estén cuajadas y las yemas aún jugosas."],
    },
    "ratatouille": {
        "tipo":"Comida","nombre":"Ratatouille de verduras",
        "fuente":"Cocina francesa tradicional","verificada":False,"cocina":"Mediterránea",
        "ingredientes":[("calabaza",0.18,"kg"),("tomate",0.18,"kg"),("cebolla",0.05,"kg"),("zanahoria",0.10,"kg"),("aceite",10,"ml")],
        "pasos":["Corta las verduras en piezas de tamaño parecido.","Sofríe la cebolla y agrega zanahoria y calabacita.","Incorpora el tomate y cocina a fuego bajo hasta que las verduras estén tiernas.","Sirve caliente como plato de verduras o guarnición."],
    },
    "omurice": {
        "tipo":"Comida","nombre":"Omurice japonés de arroz y huevo con pollo",
        "fuente":"Cocina japonesa","verificada":False,"cocina":"Asiática",
        "ingredientes":[("arroz",0.10,"kg"),("pollo",0.14,"kg"),("huevo",2,"pieza"),("tomate",0.08,"kg"),("cebolla",0.04,"kg"),("aceite",10,"ml")],
        "pasos":["Cocina el arroz y déjalo listo para saltear.","Dora el pollo con cebolla y agrega tomate para formar el relleno.","Incorpora el arroz y mezcla hasta integrar.","Prepara una tortilla fina de huevo, coloca el arroz en el centro y envuelve para servir."],
    },
})

# ---------------- COCINAS INTERNACIONALES ----------------
# Estas recetas usan únicamente ingredientes que KashCook puede convertir en
# productos del catálogo actual. Son platos reconocibles; no son nombres
# inventados para rellenar el menú.
RECETAS_REALES.update({
    "arroz_frito_pollo": {"tipo":"Comida","nombre":"Arroz frito con pollo y verduras","fuente":"Cocina asiática tradicional","cocina":"Asiática","ingredientes":[("arroz",0.10,"kg"),("pollo",0.16,"kg"),("huevo",1,"pieza"),("zanahoria",0.08,"kg"),("cebolla",0.04,"kg"),("aceite",12,"ml")],"pasos":["Cocina el arroz previamente y déjalo enfriar para que quede suelto.","Corta el pollo en trozos pequeños y saltéalo en una sartén amplia con aceite hasta que esté completamente cocido.","Agrega cebolla, zanahoria y el huevo; mueve hasta que las verduras queden tiernas y el huevo cuajado.","Incorpora el arroz, mezcla a fuego alto durante unos minutos y ajusta la sazón antes de servir."]},
    "arroz_frito_huevo": {"tipo":"Cena","nombre":"Arroz frito con huevo y verduras","fuente":"Cocina asiática tradicional","cocina":"Asiática","ingredientes":[("arroz",0.11,"kg"),("huevo",2,"pieza"),("zanahoria",0.08,"kg"),("cebolla",0.04,"kg"),("calabaza",0.10,"kg"),("aceite",12,"ml")],"pasos":["Ten listo el arroz cocido y frío para que los granos se separen al saltearlos.","Saltea cebolla, zanahoria y calabacita en una sartén amplia con aceite.","Haz un espacio al centro, agrega los huevos batidos y revuelve hasta que cuajen.","Integra el arroz, saltea todo junto a fuego alto y sirve inmediatamente."]},
    "pollo_salteado_verduras": {"tipo":"Comida","nombre":"Pollo salteado con verduras estilo asiático","fuente":"Cocina asiática casera","cocina":"Asiática","ingredientes":[("pollo",0.20,"kg"),("zanahoria",0.10,"kg"),("calabaza",0.12,"kg"),("cebolla",0.05,"kg"),("arroz",0.08,"kg"),("aceite",12,"ml")],"pasos":["Corta el pollo y las verduras en tiras de tamaño parecido.","Calienta muy bien la sartén y dora el pollo con el aceite hasta que esté cocido.","Agrega cebolla, zanahoria y calabacita y saltea a fuego alto para conservar textura.","Sirve el salteado sobre arroz cocido y ajusta la sazón al gusto."]},
    "frittata_papa_cebolla": {"tipo":"Desayuno","nombre":"Frittata italiana de papa y cebolla","fuente":"Cocina italiana tradicional","cocina":"Italiana","ingredientes":[("huevo",2,"pieza"),("papa",0.18,"kg"),("cebolla",0.05,"kg"),("queso",0.04,"kg"),("aceite",10,"ml")],"pasos":["Corta la papa en rebanadas delgadas y cocina a fuego medio con aceite hasta que esté tierna.","Agrega la cebolla fileteada y cocina hasta que quede suave.","Bate los huevos, mezcla con la papa y cebolla y vierte todo en la sartén.","Cocina a fuego bajo hasta que el huevo cuaje, agrega el queso y termina de dorar antes de servir."]},
    "frittata_calabaza_queso": {"tipo":"Cena","nombre":"Frittata italiana de calabacita y queso","fuente":"Cocina italiana tradicional","cocina":"Italiana","ingredientes":[("huevo",2,"pieza"),("calabaza",0.18,"kg"),("cebolla",0.04,"kg"),("queso",0.06,"kg"),("tomate",0.06,"kg"),("aceite",10,"ml")],"pasos":["Saltea la cebolla y la calabacita en una sartén con poco aceite hasta que estén tiernas.","Bate los huevos y mézclalos con las verduras y parte del queso.","Vierte la mezcla en la sartén y cocina a fuego bajo hasta que la base esté firme.","Termina con tomate y el queso restante; tapa brevemente para que el centro cuaje y sirve."]},
    "pollo_italiano_tomate": {"tipo":"Comida","nombre":"Pollo a la italiana con tomate y queso","fuente":"Cocina italiana casera","cocina":"Italiana","ingredientes":[("pollo",0.20,"kg"),("tomate",0.18,"kg"),("cebolla",0.04,"kg"),("queso",0.07,"kg"),("aceite",10,"ml"),("arroz",0.08,"kg")],"pasos":["Sella el pollo en una sartén con aceite hasta que tome color por ambos lados.","Agrega cebolla y tomate picados y cocina hasta obtener una salsa espesa.","Baja el fuego, coloca el queso sobre el pollo y tapa hasta que se funda.","Sirve con arroz como acompañamiento y aprovecha la salsa de tomate."]},
    "pescado_mediterraneo": {"tipo":"Comida","nombre":"Pescado al estilo mediterráneo con tomate y cebolla","fuente":"Cocina mediterránea tradicional","cocina":"Mediterránea","ingredientes":[("pescado",0.20,"kg"),("tomate",0.18,"kg"),("cebolla",0.05,"kg"),("zanahoria",0.08,"kg"),("aceite",10,"ml"),("arroz",0.08,"kg")],"pasos":["Sazona el pescado y séllalo en una sartén con un poco de aceite.","Agrega cebolla y tomate y cocina hasta que formen una salsa ligera.","Incorpora la zanahoria y un poco de agua, tapa y cocina hasta que el pescado esté bien cocido.","Sirve con arroz y la salsa de tomate por encima."]},
    "ensalada_atun_mediterranea": {"tipo":"Cena","nombre":"Ensalada mediterránea de atún","fuente":"Cocina mediterránea tradicional","cocina":"Mediterránea","ingredientes":[("atun",1,"pieza"),("lechuga",0.15,"pieza"),("tomate",0.12,"kg"),("cebolla",0.03,"kg"),("queso",0.04,"kg"),("aceite",8,"ml")],"pasos":["Lava y corta la lechuga, el tomate y la cebolla.","Escurre el atún y desmenúzalo en trozos grandes.","Combina las verduras con el atún y agrega el queso desmoronado.","Termina con aceite y sazona justo antes de servir."]},
    "pescado_arroz_limón": {"tipo":"Cena","nombre":"Pescado a la plancha con arroz y verduras","fuente":"Cocina mediterránea casera","cocina":"Mediterránea","ingredientes":[("pescado",0.20,"kg"),("arroz",0.10,"kg"),("zanahoria",0.08,"kg"),("calabaza",0.10,"kg"),("cebolla",0.03,"kg"),("aceite",10,"ml")],"pasos":["Cocina el arroz hasta que quede suelto.","Sazona el pescado y cocínalo a la plancha con poco aceite hasta que esté bien cocido.","Saltea zanahoria, calabacita y cebolla hasta que estén tiernas pero firmes.","Sirve el pescado con el arroz y las verduras recién salteadas."]},
    "tortilla_espanola": {"tipo":"Cena","nombre":"Tortilla española de papa y cebolla","fuente":"Cocina española tradicional","cocina":"Mediterránea","ingredientes":[("huevo",2,"pieza"),("papa",0.22,"kg"),("cebolla",0.06,"kg"),("aceite",15,"ml"),("tomate",0.08,"kg")],"pasos":["Corta la papa y la cebolla en rebanadas delgadas y cocínalas lentamente con aceite hasta que estén tiernas.","Bate los huevos y mézclalos con la papa y la cebolla ya escurridas.","Vierte la mezcla en una sartén y cocina a fuego medio-bajo hasta que la base cuaje.","Voltea con cuidado para terminar la cocción y acompaña con tomate fresco."]},
    "arroz_tomate_italiano": {"tipo":"Comida","nombre":"Arroz italiano con tomate, queso y verduras","fuente":"Cocina italiana casera","cocina":"Italiana","ingredientes":[("arroz",0.10,"kg"),("tomate",0.16,"kg"),("cebolla",0.04,"kg"),("calabaza",0.12,"kg"),("queso",0.06,"kg"),("aceite",10,"ml")],"pasos":["Sofríe la cebolla y la calabacita con aceite hasta que comiencen a suavizarse.","Agrega el arroz y remueve un par de minutos para que se impregne del sofrito.","Añade tomate picado y agua suficiente para cocinar el arroz hasta que quede tierno.","Apaga el fuego, incorpora el queso y deja reposar unos minutos antes de servir."]},
})

# Corrección de preparaciones: ningún plato sale con pasos genéricos de plantilla.
_PREPARACIONES_REALES = {
"chilaquiles_rojos":["Prepara una salsa roja con jitomate, cebolla y chile; cocina hasta que tome cuerpo.","Calienta las tortillas/totopos y báñalos con la salsa sin dejarlos deshacer por completo.","Sirve con huevo estrellado y queso fresco por encima.","Acompaña inmediatamente para conservar la textura de los chilaquiles."],
"omelette_calabacita":["Saltea la calabacita y la cebolla hasta que estén tiernas.","Bate los huevos y viértelos en la sartén caliente.","Cuando la base esté cuajada, coloca el queso y dobla el omelette.","Termina la cocción a fuego bajo y sirve con tomate fresco."],
"huevos_arroz_frijol":["Calienta el arroz y los frijoles por separado.","Cocina los huevos estrellados en una sartén con poco aceite.","Sirve una porción de arroz y frijoles y coloca los huevos encima.","Termina con tomate y cebolla frescos."],
"quesadillas_papa":["Cuece la papa y machácala hasta obtener un relleno uniforme.","Rellena las tortillas con papa y queso.","Dóralas en sartén por ambos lados hasta que el queso se funda.","Sirve con tomate y cebolla picados."],
"flautas_papa":["Cuece y machaca la papa y mezcla con el queso.","Rellena y enrolla las tortillas formando flautas; sujeta si es necesario.","Dora las flautas en aceite caliente hasta que queden crujientes.","Sirve con lechuga y tomate."],
"huevos_tomate_papa":["Cuece la papa en cubos hasta que esté tierna y dóralos ligeramente.","Agrega cebolla y tomate y cocina hasta formar un sofrito.","Incorpora los huevos batidos y remueve hasta que cuajen.","Sirve caliente con tortillas."],
"tostadas_frijol_huevo":["Calienta y dora las tortillas hasta obtener una base crujiente.","Unta frijoles calientes sobre cada tortilla.","Prepara los huevos y colócalos sobre los frijoles.","Termina con queso y tomate picado."],
"migas_mexicanas":["Corta las tortillas en tiras y dóralas ligeramente en sartén.","Agrega cebolla y tomate y cocina hasta suavizar.","Incorpora los huevos batidos y mezcla hasta que estén cuajados.","Termina con queso fresco y sirve caliente."],
"tinga_pollo":["Cuece el pollo y deshébralo.","Sofríe la cebolla y prepara una salsa de jitomate con los condimentos de la tinga.","Agrega el pollo deshebrado y cocina hasta que absorba la salsa.","Sirve caliente en tortillas."],
"albondigas":["Mezcla la carne molida con una pequeña parte del arroz y forma albóndigas.","Prepara un caldillo de jitomate con cebolla.","Agrega las albóndigas y cocina tapado hasta que estén completamente cocidas.","Incorpora papa y zanahoria y termina la cocción hasta que estén tiernas."],
"carne_molida_papas":["Sofríe la cebolla y cocina la carne molida hasta que cambie de color.","Agrega papa y zanahoria en cubos y cocina unos minutos.","Añade jitomate licuado y deja hervir hasta que las verduras estén tiernas.","Sirve con tortillas calientes."],
"pollo_papas":["Dora el pollo en una olla con poco aceite.","Agrega papa, zanahoria, cebolla y jitomate.","Añade un poco de agua, tapa y cocina hasta que el pollo esté completamente cocido.","Sirve con arroz blanco."],
"pollo_tomate_arroz":["Dora el pollo y agrega cebolla.","Incorpora el jitomate y cocina hasta formar una salsa.","Agrega zanahoria y cocina tapado hasta que el pollo esté completamente cocido.","Sirve con arroz."],
"cerdo_papa_tomate":["Dora el cerdo en una olla.","Agrega cebolla y papa y cocina unos minutos.","Incorpora jitomate y zanahoria con un poco de agua.","Tapa y cocina hasta que el cerdo esté tierno y las verduras suaves; sirve con tortillas."],
"pescado_papa_tomate":["Sazona y sella el pescado brevemente.","Agrega papa, jitomate, cebolla y zanahoria.","Añade un poco de agua y cocina tapado hasta que la papa esté tierna y el pescado completamente cocido.","Sirve con la salsa del guiso."],
"atun_papa":["Cuece la papa en cubos hasta que esté tierna.","Sofríe cebolla y tomate y agrega el atún escurrido.","Incorpora la papa y cocina unos minutos para integrar los sabores.","Sirve caliente con tortillas."],
"sardinas_papa":["Sofríe cebolla y tomate hasta formar una base de salsa.","Agrega la papa y zanahoria y cocina hasta que estén tiernas.","Incorpora las sardinas al final para evitar que se deshagan demasiado.","Calienta unos minutos y sirve con tortillas."],
"calabacitas_arroz":["Saltea cebolla y calabacita hasta que estén tiernas.","Agrega tomate y cocina hasta formar un guiso jugoso.","Incorpora el queso y deja que se funda parcialmente.","Sirve con arroz blanco."],
"frijoles_arroz_huevo":["Calienta los frijoles y el arroz por separado.","Prepara los huevos en sartén.","Sirve arroz y frijoles y coloca los huevos encima.","Termina con tomate y cebolla."],
"enchiladas_queso":["Prepara una salsa de jitomate y cebolla y cocina hasta que espese ligeramente.","Calienta las tortillas y pásalas por la salsa.","Rellena con queso y dóblalas o enrolla las enchiladas.","Sirve con frijoles y cebolla por encima."],
"tacos_atun":["Cuece la papa y machácala ligeramente.","Mezcla el atún con la papa, tomate, cebolla y queso.","Rellena las tortillas y dóralas en sartén.","Sirve calientes."],
}
for _rid, _pasos in _PREPARACIONES_REALES.items():
    if _rid in RECETAS_REALES:
        RECETAS_REALES[_rid]["pasos"] = _pasos

# Metadatos de cocina/estilo. Los platos existentes son principalmente de
# cocina mexicana/casera; los nuevos tienen su cocina explícita.
for _rid, _r in RECETAS_REALES.items():
    _r.setdefault("real", True)
    _r.setdefault("verificada", False)
    _r.setdefault("cocina", "Mexicana")
    estilos_base = set(_r.get("estilos", []))
    estilos_base.update([_r["cocina"], "Casera"])
    bases = {x[0] for x in _r.get("ingredientes", [])}
    if _r["cocina"] == "Mexicana":
        estilos_base.add("Económica")
    if bases & {"pollo","res","molida","cerdo","pescado","atun","sardina","huevo"}:
        estilos_base.add("Alta en proteína")
    if not bases & {"arroz","tortilla","papa","frijol"}:
        estilos_base.add("Baja en carbohidratos")
    if bases & {"lechuga","calabaza","zanahoria","tomate"}:
        estilos_base.add("Saludable")
    if _r["tipo"] == "Desayuno" and _r["cocina"] == "Mexicana":
        estilos_base.add("Desayunos mexicanos")
    _r["estilos"] = sorted(estilos_base)


DESAYUNOS = [k for k,v in RECETAS_REALES.items() if v["tipo"]=="Desayuno"]
PLATOS = [k for k,v in RECETAS_REALES.items() if v["tipo"] in ("Comida","Cena")]

# Cenas sencillas: preparaciones tradicionales/caseras que normalmente funcionan
# mejor por la noche que un plato fuerte de comida. No se inventan recetas; solo
# se prioriza una selección explícita de recetas ya existentes en la biblioteca.
# Cenas: platos reconocibles y razonables para la noche.
# NO se usan combinaciones de acompañamientos como "arroz + frijoles + huevo"
# como si fueran una comida principal.

# ============================================================
# AMPLIACIÓN DE RECETARIO REAL
# ============================================================
# Platillos reconocibles de cocina mexicana e internacional. No se generan
# nombres improvisados: cada entrada tiene nombre, ingredientes y preparación
# definida antes de que el motor pueda seleccionarla.
RECETAS_REALES.update({
    "enchiladas_pollo_rojas": {"tipo":"Comida","nombre":"Enchiladas rojas de pollo","fuente":"Cocina mexicana tradicional","ingredientes":[("pollo",0.18,"kg"),("tortilla",0.12,"kg"),("tomate",0.15,"kg"),("cebolla",0.03,"kg"),("queso",0.03,"kg"),("aceite",10,"ml")],"pasos":["Cuece el pollo y deshébralo.","Licúa o machaca el tomate con cebolla y cocina la salsa hasta que espese.","Pasa las tortillas por la salsa caliente y rellénalas con pollo.","Enrolla, baña con más salsa y termina con queso y cebolla."]},
    "tostadas_tinga_pollo": {"tipo":"Comida","nombre":"Tostadas de tinga de pollo","fuente":"Cocina mexicana tradicional","ingredientes":[("pollo",0.18,"kg"),("tortilla",0.12,"kg"),("tomate",0.15,"kg"),("cebolla",0.06,"kg"),("lechuga",0.05,"kg"),("queso",0.02,"kg"),("aceite",10,"ml")],"pasos":["Cuece y deshebra el pollo.","Sofríe cebolla, agrega tomate licuado y cocina hasta obtener una salsa espesa.","Incorpora el pollo y cocina hasta que tome el sabor del guiso.","Sirve sobre tostadas con lechuga y queso."]},
    "tacos_carne_asada": {"tipo":"Comida","nombre":"Tacos de carne asada","fuente":"Cocina mexicana tradicional","ingredientes":[("res",0.18,"kg"),("tortilla",0.15,"kg"),("cebolla",0.04,"kg"),("tomate",0.05,"kg"),("aceite",8,"ml")],"pasos":["Corta la carne en tiras y sazona.","Cocina la carne en sartén o parrilla hasta el punto deseado.","Calienta las tortillas.","Sirve la carne en tortillas con cebolla y tomate picados."]},
    "fajitas_pollo": {"tipo":"Comida","nombre":"Fajitas de pollo con cebolla y tomate","fuente":"Cocina mexicana/cocina tex-mex","ingredientes":[("pollo",0.20,"kg"),("cebolla",0.06,"kg"),("tomate",0.10,"kg"),("tortilla",0.12,"kg"),("aceite",10,"ml")],"pasos":["Corta el pollo en tiras y sazona.","Saltea el pollo en aceite hasta que esté cocido.","Agrega cebolla y tomate y cocina hasta que queden tiernos.","Sirve con tortillas calientes."]},
    "caldo_pollo_papa_zanahoria": {"tipo":"Comida","nombre":"Caldo de pollo con papa y zanahoria","fuente":"Cocina mexicana tradicional","ingredientes":[("pollo",0.25,"kg"),("papa",0.18,"kg"),("zanahoria",0.10,"kg"),("tomate",0.08,"kg"),("cebolla",0.04,"kg")],"pasos":["Cuece el pollo en agua con cebolla.","Agrega papa y zanahoria en trozos.","Incorpora tomate licuado o picado y deja hervir hasta que las verduras estén suaves.","Ajusta la sazón y sirve caliente con el pollo."]},
    "sopa_tortilla": {"tipo":"Comida","nombre":"Sopa de tortilla","fuente":"Cocina mexicana tradicional","ingredientes":[("tortilla",0.12,"kg"),("tomate",0.18,"kg"),("cebolla",0.03,"kg"),("queso",0.03,"kg"),("aceite",10,"ml")],"pasos":["Corta las tortillas en tiras y dóralas en sartén.","Licúa tomate con cebolla y cocina la salsa con agua o caldo.","Hierve unos minutos hasta integrar los sabores.","Sirve con las tiras de tortilla y queso."]},
    "carne_deshebrada_tomate": {"tipo":"Comida","nombre":"Carne de res deshebrada en salsa de tomate","fuente":"Cocina mexicana tradicional","ingredientes":[("res",0.20,"kg"),("tomate",0.16,"kg"),("cebolla",0.05,"kg"),("papa",0.12,"kg"),("aceite",10,"ml")],"pasos":["Cuece la carne hasta que pueda deshebrarse y deshébrala.","Sofríe cebolla y agrega tomate licuado.","Incorpora papa en cubos y cocina hasta que esté tierna.","Agrega la carne y deja hervir hasta espesar."]},
    "enchiladas_suizas_pollo": {"tipo":"Comida","nombre":"Enchiladas suizas de pollo","fuente":"Cocina mexicana","ingredientes":[("pollo",0.18,"kg"),("tortilla",0.12,"kg"),("queso",0.06,"kg"),("cebolla",0.03,"kg"),("aceite",8,"ml")],"pasos":["Cuece y deshebra el pollo.","Calienta las tortillas y rellénalas con pollo.","Acomoda las enchiladas en un refractario, cubre con salsa cremosa y queso.","Hornea o gratina hasta que el queso se derrita."]},
    "tacos_pescado": {"tipo":"Comida","nombre":"Tacos de pescado","fuente":"Cocina mexicana","ingredientes":[("pescado",0.20,"kg"),("tortilla",0.15,"kg"),("tomate",0.06,"kg"),("cebolla",0.04,"kg"),("lechuga",0.05,"kg"),("aceite",10,"ml")],"pasos":["Corta el pescado en porciones y sazona.","Cocínalo en sartén con poco aceite hasta que esté bien hecho.","Calienta las tortillas.","Sirve el pescado con lechuga, tomate y cebolla."]},
    "pescado_ajo": {"tipo":"Comida","nombre":"Filete de pescado al ajo","fuente":"Cocina casera","ingredientes":[("pescado",0.20,"kg"),("cebolla",0.03,"kg"),("tomate",0.06,"kg"),("aceite",12,"ml")],"pasos":["Sazona los filetes.","Calienta aceite y cocina el pescado por ambos lados.","Agrega cebolla y tomate picados y cocina hasta suavizar.","Sirve caliente con la salsa de la sartén."]},
    "cerdo_adobado": {"tipo":"Comida","nombre":"Cerdo adobado con papa","fuente":"Cocina mexicana","ingredientes":[("cerdo",0.20,"kg"),("papa",0.18,"kg"),("tomate",0.12,"kg"),("cebolla",0.04,"kg"),("aceite",10,"ml")],"pasos":["Corta el cerdo en cubos y dóralo.","Agrega papa y cebolla y cocina unos minutos.","Añade tomate licuado y especias de cocina.","Tapa y cocina hasta que el cerdo y la papa estén tiernos."]},
    "chuletas_puerco_tomate": {"tipo":"Comida","nombre":"Chuletas de cerdo en salsa de tomate","fuente":"Cocina casera mexicana","ingredientes":[("cerdo",0.20,"kg"),("tomate",0.16,"kg"),("cebolla",0.04,"kg"),("papa",0.12,"kg"),("aceite",10,"ml")],"pasos":["Dora las chuletas por ambos lados.","Prepara una salsa con tomate y cebolla.","Agrega papa en cubos y cocina hasta suavizar.","Regresa las chuletas a la salsa y termina la cocción."]},
    "camaron_ajo": {"tipo":"Comida","nombre":"Camarones al ajillo","fuente":"Cocina mexicana","ingredientes":[("camaron",0.20,"kg"),("cebolla",0.03,"kg"),("tomate",0.06,"kg"),("aceite",15,"ml")],"pasos":["Limpia y seca los camarones.","Calienta aceite y sofríe cebolla y ajo.","Agrega los camarones y cocina hasta que cambien de color.","Incorpora tomate picado y cocina brevemente."]},
    "arroz_frito_polllo": {"tipo":"Comida","nombre":"Arroz frito con pollo y verduras","fuente":"Cocina asiática","ingredientes":[("arroz",0.10,"kg"),("pollo",0.16,"kg"),("huevo",1,"pieza"),("zanahoria",0.06,"kg"),("cebolla",0.04,"kg"),("aceite",12,"ml")],"pasos":["Cocina previamente el arroz y déjalo enfriar.","Saltea el pollo en aceite hasta cocinarlo.","Agrega cebolla, zanahoria y huevo y mueve hasta integrar.","Incorpora el arroz y saltea a fuego alto con salsa de soya al gusto."]},
    "pollo_teriyaki": {"tipo":"Comida","nombre":"Pollo teriyaki con arroz","fuente":"Cocina japonesa","ingredientes":[("pollo",0.20,"kg"),("arroz",0.10,"kg"),("cebolla",0.03,"kg"),("aceite",8,"ml")],"pasos":["Corta el pollo en trozos y dóralo.","Agrega la salsa teriyaki y cocina hasta que glasee el pollo.","Prepara el arroz por separado.","Sirve el pollo sobre el arroz."]},
    "oyakodon": {"tipo":"Comida","nombre":"Oyakodon japonés","fuente":"Cocina japonesa","ingredientes":[("pollo",0.16,"kg"),("huevo",2,"pieza"),("arroz",0.10,"kg"),("cebolla",0.06,"kg")],"pasos":["Cocina la cebolla con caldo y salsa de soya.","Agrega el pollo en tiras y cocina hasta que esté hecho.","Vierte el huevo batido y cocina hasta que cuaje ligeramente.","Sirve sobre arroz caliente."]},
    "bulgogi_res": {"tipo":"Comida","nombre":"Bulgogi de res","fuente":"Cocina coreana","ingredientes":[("res",0.20,"kg"),("cebolla",0.06,"kg"),("zanahoria",0.06,"kg"),("arroz",0.10,"kg"),("aceite",8,"ml")],"pasos":["Corta la carne en láminas delgadas.","Marina con salsa de soya, ajo y un toque de azúcar.","Saltea la carne con cebolla y zanahoria a fuego alto.","Sirve con arroz blanco."]},
    "pescado_mediterraneo": {"tipo":"Comida","nombre":"Pescado mediterráneo con tomate y cebolla","fuente":"Cocina mediterránea","ingredientes":[("pescado",0.20,"kg"),("tomate",0.16,"kg"),("cebolla",0.05,"kg"),("aceite",12,"ml")],"pasos":["Coloca los filetes en una sartén con aceite.","Agrega tomate y cebolla en trozos.","Sazona con hierbas y cocina tapado hasta que el pescado esté listo.","Sirve con la salsa de tomate y cebolla."]},
    "shakshuka_comida": {"tipo":"Comida","nombre":"Shakshuka","fuente":"Cocina del norte de África y Medio Oriente","ingredientes":[("huevo",2,"pieza"),("tomate",0.20,"kg"),("cebolla",0.05,"kg"),("aceite",10,"ml"),("queso",0.03,"kg")],"pasos":["Sofríe la cebolla en aceite.","Agrega tomate picado y cocina hasta formar una salsa espesa.","Haz pequeños huecos y coloca los huevos.","Tapa y cocina hasta que las claras cuajen; termina con queso."]},
    "tortilla_espanola_comida": {"tipo":"Comida","nombre":"Tortilla española de papa y cebolla","fuente":"Cocina española","ingredientes":[("papa",0.25,"kg"),("huevo",3,"pieza"),("cebolla",0.06,"kg"),("aceite",20,"ml")],"pasos":["Corta papa y cebolla en rebanadas delgadas.","Cocínalas lentamente en aceite hasta que estén tiernas.","Mezcla con huevo batido y devuelve a la sartén.","Cuaja por ambos lados y sirve en porciones."]},
    "frittata_verduras": {"tipo":"Comida","nombre":"Frittata de papa, cebolla y queso","fuente":"Cocina italiana","ingredientes":[("huevo",3,"pieza"),("papa",0.18,"kg"),("cebolla",0.05,"kg"),("queso",0.04,"kg"),("aceite",10,"ml")],"pasos":["Cocina la papa y la cebolla en sartén.","Bate los huevos y mezcla con el queso.","Vierte la mezcla sobre las verduras y cocina a fuego bajo.","Termina en horno o tapada hasta cuajar completamente."]},
    "ensalada_tibia_pollo": {"tipo":"Cena","nombre":"Ensalada tibia de pollo y verduras","fuente":"Cocina casera","ingredientes":[("pollo",0.16,"kg"),("lechuga",0.08,"kg"),("zanahoria",0.06,"kg"),("tomate",0.08,"kg"),("cebolla",0.03,"kg")],"pasos":["Cocina el pollo en tiras y córtalo en porciones.","Lava y corta las verduras.","Mezcla la lechuga con zanahoria, tomate y cebolla.","Agrega el pollo caliente y adereza al gusto."]},
    "quesadillas_pollo": {"tipo":"Cena","nombre":"Quesadillas de pollo y queso","fuente":"Cocina mexicana","ingredientes":[("pollo",0.12,"kg"),("tortilla",0.12,"kg"),("queso",0.06,"kg"),("cebolla",0.03,"kg")],"pasos":["Cuece y deshebra el pollo.","Rellena las tortillas con pollo, queso y cebolla.","Cocina las quesadillas en comal por ambos lados.","Sirve calientes."]},
    "tostadas_atun": {"tipo":"Cena","nombre":"Tostadas de atún a la mexicana","fuente":"Cocina mexicana","ingredientes":[("atun",0.14,"kg"),("tortilla",0.12,"kg"),("tomate",0.08,"kg"),("cebolla",0.04,"kg"),("lechuga",0.05,"kg")],"pasos":["Escurre el atún.","Mézclalo con tomate y cebolla picados.","Dora las tortillas hasta formar tostadas.","Sirve el atún sobre las tostadas con lechuga."]},
    "tacos_res_cebolla_cena": {"tipo":"Cena","nombre":"Tacos de res con cebolla","fuente":"Cocina mexicana","ingredientes":[("res",0.16,"kg"),("tortilla",0.12,"kg"),("cebolla",0.05,"kg"),("tomate",0.05,"kg")],"pasos":["Corta la carne en tiras y sazona.","Cocina la carne en sartén caliente.","Agrega cebolla y cocina hasta dorar.","Sirve en tortillas calientes con tomate."]},
    "pescado_plancha_cena": {"tipo":"Cena","nombre":"Filete de pescado a la plancha con ensalada","fuente":"Cocina casera","ingredientes":[("pescado",0.18,"kg"),("lechuga",0.08,"kg"),("tomate",0.08,"kg"),("cebolla",0.03,"kg"),("aceite",8,"ml")],"pasos":["Sazona el filete.","Cocínalo a la plancha con poco aceite por ambos lados.","Prepara la ensalada con lechuga, tomate y cebolla.","Sirve el pescado junto con la ensalada."]},
    "caldo_pollo_cena": {"tipo":"Cena","nombre":"Caldo de pollo con verduras","fuente":"Cocina mexicana tradicional","ingredientes":[("pollo",0.18,"kg"),("papa",0.12,"kg"),("zanahoria",0.08,"kg"),("tomate",0.06,"kg"),("cebolla",0.03,"kg")],"pasos":["Cuece el pollo con cebolla.","Agrega papa y zanahoria.","Incorpora tomate y deja hervir hasta que las verduras estén tiernas.","Sirve caliente con el pollo."]},
    "sopa_tortilla_cena": {"tipo":"Cena","nombre":"Sopa de tortilla","fuente":"Cocina mexicana tradicional","ingredientes":[("tortilla",0.10,"kg"),("tomate",0.16,"kg"),("cebolla",0.03,"kg"),("queso",0.03,"kg"),("aceite",8,"ml")],"pasos":["Corta y dora las tortillas.","Prepara una salsa de tomate y cebolla y agrega caldo.","Hierve unos minutos.","Sirve con las tiras de tortilla y queso."]},
})

CENAS_SENCILLAS_TRADICIONALES = {
    "calabacitas_queso", "enchiladas_queso", "tacos_atun",
    "sardinas_papa", "ensalada_atun_papa", "atun_bolitas",
    "tortilla_espanola", "frittata_calabaza_queso", "tinga_pollo",
    "tortitas_papa_comida", "quesadillas_papa", "flautas_papa",
    "chilaquiles_rojos", "migas_mexicanas", "tostadas_pollo", "carne_asada_cebolla",
    "shakshuka",
}

# Estas preparaciones pueden existir como desayuno/cena económica, pero NO
# deben aparecer como "Comida" principal del día. La comida debe ser un
# platillo reconocible, no un conjunto improvisado de guarniciones.
COMIDAS_NO_VALIDAS_COMO_PLATO_PRINCIPAL = {
    "arroz_frijoles", "frijoles_arroz_huevo", "huevos_arroz_frijol",
    "arroz_huevo", "frijoles_huevo", "tostadas_frijol_huevo",
    "calabacitas_arroz", "arroz_tomate_italiano",
}

# Preparaciones demasiado simples para representar una comida poblacional.
# Permanecen en la biblioteca para referencia histórica, pero el generador NO
# las selecciona automáticamente.
RECETAS_EXCLUIDAS_DEL_GENERADOR = COMIDAS_NO_VALIDAS_COMO_PLATO_PRINCIPAL | {
    "arroz_frijoles", "frijoles_arroz_huevo", "huevos_arroz_frijol",
    "arroz_huevo", "frijoles_huevo", "tostadas_frijol_huevo",
    "calabacitas_arroz", "arroz_tomate_italiano",
}

def _producto_para_base(base, catalogo):
    """Selecciona un producto compatible para planificar.

    IMPORTANTE: la disponibilidad web no decide si existe una receta. Los
    productos de referencia permiten construir el menú; cuando hay productos
    verificados, estos tienen prioridad y se elige entre ellos por costo.
    La validación final exige que los productos realmente comprados estén
    verificados.
    """
    candidatos=[p for p in catalogo if p.get("ingrediente_base")==base]
    if base == "molida":
        candidatos=[p for p in catalogo if p.get("ingrediente_base")=="res" and "molida" in str(p.get("nombre","")).lower()]
    if not candidatos:
        return None

    verificados=[p for p in candidatos if p.get("estado_precio")=="Verificado"]
    pool=verificados or candidatos

    def costo(p):
        try:
            return float(p.get("precio") or 10**9)
        except Exception:
            return 10**9
    return min(pool,key=costo)


def _receta_a_comida(recipe_id, catalogo, tipo):
    r=RECETAS_REALES[recipe_id]
    ingredientes=[]
    for base,cantidad,unidad in r["ingredientes"]:
        p=_producto_para_base(base,catalogo)
        if not p:
            return None
        # Algunas recetas expresan latas/paquetes como "pieza", pero la presentación
        # comercial puede estar expresada en gramos. Convertimos de forma explícita
        # para que NUNCA desaparezca un ingrediente de la lista de compras.
        unidad_salida = unidad
        cantidad_salida = cantidad
        if str(unidad).lower() in {"pieza", "piezas", "unidad", "unidades"} and str(p.get("unidad_contenido", "")).lower() in {"g", "kg"}:
            contenido_g = float(p.get("contenido", 0)) * (1000 if str(p.get("unidad_contenido", "")).lower() == "kg" else 1)
            if contenido_g > 0:
                cantidad_salida = float(cantidad) * contenido_g
                unidad_salida = "g"
        ingredientes.append({"producto_id":p["id"],"cantidad_por_persona":cantidad_salida,"unidad":unidad_salida})
    return {"tipo":tipo,"nombre":r["nombre"],"ingredientes":ingredientes,"preparacion":r["pasos"],"fuente":r["fuente"],"fuente_url":r.get("fuente_url",""),"verificada":bool(r.get("verificada",False))}


def _plan_con_recetas(ids, catalogo, comidas):
    dias=[]
    for i,slot in enumerate(ids,1):
        c=[]
        for tipo,rid in zip(comidas,slot):
            comida=_receta_a_comida(rid,catalogo,tipo)
            if comida is None:
                return None
            c.append(comida)
        dias.append({"dia":i,"comidas":c})
    return {"dias":dias}


def _costo_plan(plan,catalogo,personas):
    try:
        _,total=calcular_compra(plan,catalogo,personas)
        return total
    except Exception:
        return 10**12


def _receta_coincide_estilos(recipe_id, estilos):
    """Filtra por cocina/estilo real; si no hay filtro, deja pasar todo."""
    if not estilos:
        return True
    r = RECETAS_REALES[recipe_id]
    etiquetas = set(r.get("estilos", []))
    etiquetas.add(r.get("cocina", "Mexicana"))
    return bool(etiquetas.intersection(set(estilos)))


def _receta_bases(recipe_id):
    return {x[0] for x in RECETAS_REALES[recipe_id].get("ingredientes", [])}


def _receta_compatible(recipe_id, electrodomesticos=None, restricciones=""):
    """Aplica restricciones sencillas y conservadoras sin inventar equivalencias."""
    r = RECETAS_REALES[recipe_id]
    bases = _receta_bases(recipe_id)
    texto = (restricciones or "").lower()

    # Restricciones explícitas frecuentes. No intentamos interpretar una frase
    # ambigua como una alergia: solo bloqueamos cuando hay una coincidencia clara.
    bloqueos = {
        "pollo": {"pollo"},
        "res": {"res", "molida"},
        "carne de res": {"res", "molida"},
        "cerdo": {"puerco"},
        "puerco": {"puerco"},
        "pescado": {"pescado"},
        "atun": {"atun"},
        "atún": {"atun"},
        "sardina": {"sardina"},
        "huevo": {"huevo"},
        "huevos": {"huevo"},
        "queso": {"queso"},
        "lacteo": {"queso", "huevo"},
        "lácteo": {"queso", "huevo"},
        "tortilla": {"tortilla"},
        "arroz": {"arroz"},
        "frijol": {"frijol"},
        "papa": {"papa"},
    }
    for palabra, ingredientes in bloqueos.items():
        if palabra in texto and bases.intersection(ingredientes):
            return False

    # Vegetariano/vegano: el catálogo actual permite una interpretación
    # conservadora basada en ingredientes, sin sustituir proteínas por cuenta propia.
    if "vegano" in texto or "vegana" in texto:
        if bases.intersection({"huevo", "queso", "pollo", "res", "molida", "puerco", "pescado", "atun", "sardina"}):
            return False
    if "vegetariano" in texto or "vegetariana" in texto:
        if bases.intersection({"pollo", "res", "molida", "puerco", "pescado", "atun", "sardina"}):
            return False

    # Picante: las recetas de esta biblioteca no requieren chile explícito,
    # por lo que no se bloquean por esta palabra.
    return True


def _receta_a_comida(recipe_id, catalogo, tipo):
    r = RECETAS_REALES[recipe_id]
    ingredientes = []
    for base, cantidad, unidad in r["ingredientes"]:
        p = _producto_para_base(base, catalogo)
        if not p:
            return None
        unidad_salida = unidad
        cantidad_salida = cantidad
        if str(unidad).lower() in {"pieza", "piezas", "unidad", "unidades"} and str(p.get("unidad_contenido", "")).lower() in {"g", "kg"}:
            contenido_g = float(p.get("contenido", 0)) * (1000 if str(p.get("unidad_contenido", "")).lower() == "kg" else 1)
            if contenido_g > 0:
                cantidad_salida = float(cantidad) * contenido_g
                unidad_salida = "g"
        ingredientes.append({
            "producto_id": p["id"],
            "cantidad_por_persona": cantidad_salida,
            "unidad": unidad_salida,
        })
    return {
        "tipo": tipo,
        "nombre": r["nombre"],
        "ingredientes": ingredientes,
        "preparacion": r["pasos"],
        "fuente": r["fuente"],
        "fuente_url": r.get("fuente_url", ""),
        "verificada": bool(r.get("verificada", False)),
    }


def _plan_con_recetas(ids, catalogo, comidas):
    dias = []
    for i, slot in enumerate(ids, 1):
        c = []
        for tipo, rid in zip(comidas, slot):
            comida = _receta_a_comida(rid, catalogo, tipo)
            if comida is None:
                return None
            c.append(comida)
        dias.append({"dia": i, "comidas": c})
    return {"dias": dias}


def _costo_plan(plan, catalogo, personas):
    try:
        _, total = calcular_compra(plan, catalogo, personas)
        return total
    except Exception:
        return 10**12


def _resumen_restricciones(restricciones):
    t = (restricciones or "").strip()
    return t if t else "Ninguna"


def _generar_plan_local(
    dias,
    personas,
    presupuesto,
    comidas,
    catalogo,
    estilos=None,
    electrodomesticos=None,
    restricciones="",
):
    """Motor local de KashCook: recetas reales + variedad + compras agrupadas.

    La optimización se hace sobre el menú completo, no comida por comida. Esto
    permite reutilizar ingredientes y comprar una presentación una sola vez.
    """
    import random
    from datetime import date

    estilos = estilos or []
    electrodomesticos = electrodomesticos or ["Estufa"]

    # Esta biblioteca actual está diseñada para cocina de estufa. Si el usuario
    # dispone de estufa, todos los platos base son posibles. Para otros equipos
    # se conservan como adicionales, no se inventan recetas que dependan de ellos.
    tiene_estufa = "Estufa" in electrodomesticos

    def compatible(rid, tipo):
        if not RECETAS_REALES[rid].get("real", False):
            return False
        # El tipo de receta es obligatorio. Antes el motor permitía que una
        # receta marcada como Cena entrara en Comida porque ambas estaban en
        # PLATOS; eso explica parte de los menús incoherentes.
        if RECETAS_REALES[rid].get("tipo") != tipo:
            return False
        if rid in RECETAS_EXCLUIDAS_DEL_GENERADOR:
            return False
        if tipo == "Desayuno" and rid not in DESAYUNOS:
            return False
        if tipo == "Comida" and rid in COMIDAS_NO_VALIDAS_COMO_PLATO_PRINCIPAL:
            return False
        if not _receta_coincide_estilos(rid, estilos):
            return False
        if not _receta_compatible(rid, electrodomesticos, restricciones):
            return False
        # Sin estufa, solo permitir recetas explícitamente marcadas para otro
        # equipo. Las recetas actuales no tienen esa dependencia, por seguridad.
        if not tiene_estufa and "electrodomestico" not in RECETAS_REALES[rid]:
            return False
        return _receta_a_comida(rid, catalogo, tipo) is not None

    candidatos_des = [r for r in DESAYUNOS if compatible(r, "Desayuno")]
    candidatos_pl = [r for r in PLATOS if compatible(r, "Comida")]
    candidatos_cena = [r for r in PLATOS if compatible(r, "Cena") and r in CENAS_SENCILLAS_TRADICIONALES]
    # Para cenas ampliamos a otras recetas que REALMENTE están marcadas como
    # Cena. Nunca convertimos una Comida en Cena ni una Cena en Comida.
    if len(candidatos_cena) < min(4, int(dias)):
        candidatos_cena = [r for r in PLATOS if compatible(r, "Cena") and
                           RECETAS_REALES[r].get("cocina") in {"Mexicana", "Casera", "Mediterránea", "Italiana"}]

    # Si un filtro muy específico deja una categoría sin recetas, no vamos a
    # inventar sustituciones. Primero se informa de forma clara.
    if not candidatos_des and "Desayuno" in comidas:
        raise ValueError("No hay desayunos reales compatibles con los estilos, tiendas y restricciones seleccionados.")
    if not candidatos_pl and any(x in comidas for x in ("Comida", "Cena")):
        raise ValueError("No hay comidas/cenas reales compatibles con los estilos, tiendas y restricciones seleccionados.")

    # Comida principal: solo platillos reconocibles y completos. Nunca usamos
    # combinaciones de guarniciones como arroz+frijoles+huevo para ocupar el
    # lugar de una comida.
    nombres_no_comida = {
        "arroz con frijoles y queso fresco", "plato de frijoles, arroz y huevo",
        "arroz con huevo a la mexicana", "huevos estrellados con arroz y frijoles",
        "frijoles con huevo y queso sobre tortilla dorada",
        "calabacitas guisadas con queso y arroz",
    }
    candidatos_pl = [r for r in candidatos_pl if normalizar_texto(RECETAS_REALES[r].get("nombre", "")) not in {normalizar_texto(x) for x in nombres_no_comida}]
    # Una comida fuerte debe tener al menos una fuente proteica o ser un platillo
    # tradicional completo (pasta, enchiladas, tacos, pizza, etc.).
    palabras_plato = ("pollo","res","cerdo","pescado","atun","sardina","camaron","huevo","queso","tinga","enchilada","taco","albóndiga","pasta","pizza","lasaña","curry","fajita","milanesa")
    candidatos_pl = [r for r in candidatos_pl if any(w in normalizar_texto(RECETAS_REALES[r].get("nombre", "")) for w in palabras_plato)]

    pools = {"Desayuno": candidatos_des, "Comida": candidatos_pl, "Cena": candidatos_cena}
    if not candidatos_cena and "Cena" in comidas:
        raise ValueError("No hay cenas sencillas reales compatibles con los estilos y restricciones seleccionados.")

    iso = date.today().isocalendar()
    semana_seed = (int(iso.year) * 100 + int(iso.week)) * 1000003
    sesion = int(st.session_state.get("kc_semilla_menu", 0))
    if not sesion:
        sesion = random.SystemRandom().randint(1, 10**9)
        st.session_state["kc_semilla_menu"] = sesion
    rng = random.Random(semana_seed + sesion + int(dias) * 31 + int(personas) * 17 + int(presupuesto))

    # Se calculan costos individuales como referencia para favorecer recetas
    # económicas, pero la decisión final siempre usa la compra agrupada completa.
    costo_individual = {}
    for rid in set(candidatos_des + candidatos_pl):
        c = _receta_a_comida(rid, catalogo, "Comida" if rid in candidatos_pl else "Desayuno")
        if c:
            costo_individual[rid] = _costo_plan({"dias":[{"dia":1,"comidas":[c]}]}, catalogo, personas)

    total_slots = int(dias) * len(comidas)
    # Una semana real puede repetir recetas. El objetivo es variedad, no
    # obligar a que cada plato sea único cuando eso vuelve imposible el presupuesto.
    max_repeticiones = max(2, min(4, int(math.ceil(int(dias) / 2))))

    mejor_factible = None
    mejor_factible_score = -10**18
    mejor_global = None
    mejor_global_score = -10**18

    # ------------------------------------------------------------
    # BÚSQUEDA PRESUPUESTARIA DETERMINISTA
    # ------------------------------------------------------------
    # Antes de la búsqueda aleatoria probamos combinaciones económicas y
    # variadas. Esto evita que el azar declare "presupuesto insuficiente"
    # cuando sí existe una combinación viable.
    def patrones_baratos(pool):
        orden = sorted(pool, key=lambda x: costo_individual.get(x, 10**12))[:8]
        patrones = []
        if not orden:
            return patrones
        for n in range(1, min(4, len(orden)) + 1):
            for inicio in range(n):
                patrones.append([orden[(d + inicio) % n] for d in range(int(dias))])
        return patrones

    patrones_por_tipo = {tipo: patrones_baratos(pools[tipo]) for tipo in pools}
    mejor_semilla = None
    mejor_semilla_score = -10**18
    import itertools as _itertools
    listas_patrones = [patrones_por_tipo[t] for t in comidas]
    if all(listas_patrones):
        for combinacion in _itertools.product(*listas_patrones):
            slots_seed = [[combinacion[j][d] for j in range(len(comidas))] for d in range(int(dias))]
            plan_seed = _plan_con_recetas(slots_seed, catalogo, comidas)
            if not plan_seed:
                continue
            nombres_seed = [RECETAS_REALES[r]["nombre"].lower() for row in slots_seed for r in row]
            tortilla_seed = sum(any(x in n for x in ("tortilla", "quesadilla", "enfrijolada", "taco", "enchilada", "flauta", "chilaquiles")) for n in nombres_seed)
            if tortilla_seed > max(5, int(total_slots * 0.30)):
                continue
            # La semilla económica también debe respetar la regla de diversidad;
            # de lo contrario podría saltarse los controles aplicados a la búsqueda aleatoria.
            principales_seed=[]
            for row in slots_seed:
                for rid in row:
                    if RECETAS_REALES[rid]["tipo"] in ("Comida", "Cena"):
                        b=_receta_bases(rid)
                        if "camaron" in b: principales_seed.append("camaron")
                        elif "pescado" in b: principales_seed.append("pescado")
                        elif "pollo" in b: principales_seed.append("pollo")
                        elif "puerco" in b: principales_seed.append("cerdo")
                        elif b.intersection({"res","molida"}): principales_seed.append("res")
                        elif "atun" in b: principales_seed.append("atun")
                        elif "sardina" in b: principales_seed.append("sardina")
            if principales_seed:
                atun_seed=principales_seed.count("atun")
                if atun_seed > max(1, int(math.floor(len(principales_seed)*0.25))):
                    continue
                min_seed=2 if float(presupuesto)<1800 else (3 if len(principales_seed)<10 else 4)
                if len(set(principales_seed)) < min_seed:
                    continue
            total_seed = _costo_plan(plan_seed, catalogo, personas)
            if total_seed <= presupuesto:
                distintas = len(set(r for row in slots_seed for r in row))
                cocinas_seed = {RECETAS_REALES[r].get("cocina", "Mexicana") for row in slots_seed for r in row}
                repetidas = total_slots - distintas
                score_seed = distintas * 60 + len(cocinas_seed) * 70 - repetidas * 35 - tortilla_seed * 12
                # Preferimos gastar el presupuesto razonablemente, pero siempre
                # priorizamos que la compra sea realmente posible.
                score_seed += max(0, presupuesto - total_seed) * -0.08
                if score_seed > mejor_semilla_score:
                    mejor_semilla_score = score_seed
                    mejor_semilla = (plan_seed, total_seed, slots_seed)

    if mejor_semilla:
        # No terminamos aquí: la búsqueda aleatoria posterior puede encontrar
        # una combinación todavía más variada dentro del mismo presupuesto.
        pass

    # Muchas combinaciones pequeñas son más útiles que una sola llamada enorme
    # al LLM y no dependen de un JSON de siete días.
    # Búsqueda ampliada: cuando el presupuesto es ajustado, la prioridad es
    # encontrar una combinación REALMENTE barata antes de optimizar variedad.
    # Esto evita declarar imposible un presupuesto por haber explorado solo una
    # fracción del espacio de combinaciones.
    iteraciones_busqueda = 12000 if float(presupuesto) <= 2500 else 8000
    for _ in range(iteraciones_busqueda):
        usados = []
        slots = []
        conteo = {}
        for d in range(int(dias)):
            fila = []
            for tipo in comidas:
                pool = pools[tipo]
                if not pool:
                    fila = None
                    break

                # Primero evitamos cualquier receta usada en los últimos 3 días
                # y, mientras exista inventario, evitamos cualquier repetición.
                recientes = {x for row in slots[-2:] for x in row}
                disponibles = [x for x in pool if x not in recientes and conteo.get(x, 0) < max_repeticiones]
                if not disponibles:
                    disponibles = [x for x in pool if conteo.get(x, 0) < max_repeticiones]
                if not disponibles:
                    disponibles = pool

                # Con múltiples cocinas, sesgamos la selección hacia las que aún
                # no aparecen en el menú para que la elección del usuario tenga efecto real.
                elegibles = disponibles
                if len(estilos) > 1:
                    faltantes = [
                        x for x in disponibles
                        if RECETAS_REALES[x].get("cocina", "Mexicana") in estilos
                        and RECETAS_REALES[x].get("cocina", "Mexicana") not in {
                            RECETAS_REALES[y].get("cocina", "Mexicana") for y in usados
                        }
                    ]
                    if faltantes and rng.random() < 0.72:
                        elegibles = faltantes

                # Selección consciente del COSTO AGRUPADO. Una receta que comparte
                # ingredientes con lo ya elegido suele costar menos en la compra
                # semanal porque evita abrir nuevas presentaciones comerciales.
                bases_usadas = set()
                for y in usados:
                    bases_usadas.update(_receta_bases(y))

                def costo_heuristico(x):
                    bases_x = _receta_bases(x)
                    compartidos = len(bases_x.intersection(bases_usadas))
                    costo = costo_individual.get(x, 10**9)
                    # El bono por compartir ingredientes es deliberadamente
                    # moderado: favorece aprovechamiento sin convertir todo el menú
                    # en la misma receta.
                    bono_compartir = compartidos * (45 if float(presupuesto) <= 2500 else 28)
                    ruido = rng.random() * max(8.0, costo * 0.18)
                    return costo - bono_compartir + ruido

                elegibles = sorted(elegibles, key=costo_heuristico)
                # En presupuesto ajustado concentramos la elección en opciones
                # económicas; con mayor margen dejamos más espacio a variedad.
                ancho = 7 if float(presupuesto) <= 1800 else (10 if float(presupuesto) <= 2500 else 14)
                elegibles = elegibles[:max(5, min(ancho, len(elegibles)))]
                rid = rng.choice(elegibles)
                fila.append(rid)
                usados.append(rid)
                conteo[rid] = conteo.get(rid, 0) + 1
            if fila is None:
                break
            slots.append(fila)

        if len(slots) != int(dias):
            continue

        plan = _plan_con_recetas(slots, catalogo, comidas)
        if not plan:
            continue

        # Validación de calidad del menú: una "Comida" no puede ser un
        # acompañamiento disfrazado de plato principal. Esta regla se aplica
        # después de construir el menú para que ninguna ruta de optimización
        # pueda saltársela.
        valido_plato_principal = True
        for row in slots:
            for rid, tipo in zip(row, comidas):
                if tipo == "Comida":
                    if rid in COMIDAS_NO_VALIDAS_COMO_PLATO_PRINCIPAL:
                        valido_plato_principal = False
                        break
                    bases_cp = _receta_bases(rid)
                    tiene_proteina = bool(bases_cp & {"pollo", "res", "molida", "puerco", "pescado", "atun", "sardina", "camaron", "huevo"})
                    # Excepción: platos tradicionales completos sin proteína
                    # animal, pero que son reconocibles como plato principal.
                    platos_completos = {"tortitas_papa_comida", "arroz_tomate_italiano"}
                    if not tiene_proteina and rid not in platos_completos:
                        valido_plato_principal = False
                        break
            if not valido_plato_principal:
                break
        if not valido_plato_principal:
            continue

        nombres = [RECETAS_REALES[r]["nombre"].lower() for row in slots for r in row]
        tortilla_count = sum(
            any(x in n for x in ("tortilla", "quesadilla", "enfrijolada", "taco", "enchilada", "flauta", "chilaquiles"))
            for n in nombres
        )
        if tortilla_count > max(5, int(total_slots * 0.30)):
            continue

        total = _costo_plan(plan, catalogo, personas)
        cocinas = [RECETAS_REALES[x].get("cocina", "Mexicana") for row in slots for x in row]
        cocinas_usadas = set(cocinas)
        recetas_distintas = len(set(x for row in slots for x in row))
        repeticiones = total_slots - recetas_distintas
        proteínas = []
        for row in slots:
            for x in row:
                b = _receta_bases(x)
                if "pollo" in b: proteínas.append("pollo")
                elif b.intersection({"res", "molida"}): proteínas.append("res")
                elif "puerco" in b: proteínas.append("cerdo")
                elif "pescado" in b: proteínas.append("pescado")
                elif "camaron" in b: proteínas.append("camaron")
                elif "atun" in b: proteínas.append("atun")
                elif "sardina" in b: proteínas.append("sardina")
                elif "huevo" in b: proteínas.append("huevo")
                else: proteínas.append("vegetal")
        variedad_proteina = len(set(proteínas))
        atun_count = proteínas.count("atun")
        # Diversidad de proteína en las comidas principales. El desayuno puede
        # usar huevo; la variedad que exigimos aquí se refiere al plato fuerte.
        principales = []
        for drow in slots:
            for rid in drow:
                if RECETAS_REALES[rid]["tipo"] in ("Comida", "Cena"):
                    bases_r = _receta_bases(rid)
                    if "camaron" in bases_r: principales.append("camaron")
                    elif "pescado" in bases_r: principales.append("pescado")
                    elif "pollo" in bases_r: principales.append("pollo")
                    elif "puerco" in bases_r: principales.append("cerdo")
                    elif bases_r.intersection({"res", "molida"}): principales.append("res")
                    elif "atun" in bases_r: principales.append("atun")
                    elif "sardina" in bases_r: principales.append("sardina")
                    else: principales.append("vegetal")
        diversidad_principal = len(set(principales))
        # Atún no puede dominar el menú. En presupuestos normales exigimos al
        # menos cuatro proteínas distintas en el plato fuerte cuando es viable.
        # El atún nunca puede ser la proteína dominante del menú.
        if principales:
            limite_atun = max(1, int(math.floor(len(principales) * 0.25)))
            if atun_count > limite_atun:
                continue
        # En menús de varios días buscamos mezcla real de proteínas. No exigimos
        # una variedad imposible en planes muy cortos, pero sí evitamos que todo
        # termine en un único ingrediente barato.
        proteinas_carne = {p for p in set(principales) if p in {"pollo","res","cerdo","pescado","camaron","atun","sardina"}}
        # Con presupuestos muy ajustados mantenemos la mezcla sin volver el plan
        # matemáticamente imposible: al menos 2 proteínas distintas; con más
        # margen económico buscamos 3-4.
        minimo_proteinas = 2 if float(presupuesto) < 1800 else (3 if len(principales) < 10 else 4)
        if len(principales) >= 4 and len(proteinas_carne) < minimo_proteinas:
            continue
        if len(principales) >= 8 and float(presupuesto) >= 1800 and diversidad_principal < 4:
            continue
        cocinas_objetivo = len(cocinas_usadas.intersection(set(estilos))) if estilos else len(cocinas_usadas)

        # Puntuación: primero viabilidad económica, luego variedad y cumplimiento.
        cenas_sencillas = sum(1 for row in slots for rid in row if RECETAS_REALES[rid].get("tipo") == "Cena" and rid in CENAS_SENCILLAS_TRADICIONALES)
        cenas_comida = sum(1 for row in slots for rid in row if RECETAS_REALES[rid].get("tipo") == "Cena" and rid not in CENAS_SENCILLAS_TRADICIONALES)
        tradicionales = sum(1 for row in slots for rid in row if RECETAS_REALES[rid].get("cocina") == "Mexicana")
        score = (
            recetas_distintas * 55
            - repeticiones * 210
            + len(cocinas_usadas) * 65
            + cenas_sencillas * 120
            - cenas_comida * 160
            + tradicionales * 35
            + cocinas_objetivo * 85
            + variedad_proteina * 110
            + (70 if "camaron" in proteínas else 0)
            - atun_count * 65
            - tortilla_count * 18
            + rng.random() * 25
        )
        if total <= presupuesto:
            score += 5000 - max(0, presupuesto - total) * 0.25
        else:
            score -= (total - presupuesto) * 18

        candidato = (plan, total, score)
        # Para el diagnóstico de presupuesto, "mejor global" significa el
        # MENOR COSTO encontrado, no el menú con mayor puntuación estética.
        # Antes esto podía reportar $2,096 aunque otra combinación más barata
        # ya hubiera sido explorada. En empate sí usamos variedad como desempate.
        if (mejor_global is None or total < mejor_global[1] - 0.01 or
                (abs(total - mejor_global[1]) <= 0.01 and score > mejor_global_score)):
            mejor_global_score = score
            mejor_global = candidato

        if total <= presupuesto + TOLERANCIA_PRESUPUESTO and score > mejor_factible_score:
            mejor_factible_score = score
            mejor_factible = candidato

    if mejor_factible:
        return mejor_factible[0], round(mejor_factible[1], 2)

    if mejor_semilla:
        return mejor_semilla[0], round(mejor_semilla[1], 2)

    # No mentimos si el presupuesto no alcanza. Buscamos el plan más barato
    # encontrado y lo reportamos para que el usuario sepa cuánto falta realmente.
    if mejor_global:
        minimo = round(mejor_global[1], 2)
        faltante = max(0, minimo - float(presupuesto))
        raise ValueError(
            f"No encontré una combinación real que cumpla el menú completo dentro de ${presupuesto:,.2f}. "
            f"La mejor combinación encontrada cuesta aproximadamente ${minimo:,.2f}; faltan ${faltante:,.2f}. "
            "KashCook no va a inventar precios ni reducir las porciones para hacer que parezca que alcanza. "
            "Prueba con más presupuesto, menos días/personas o menos comidas por día."
        )

    raise ValueError("No fue posible construir un menú con las recetas, tiendas y restricciones seleccionadas.")


def generar_plan_seguro(
    dias,
    personas,
    presupuesto,
    comidas,
    catalogo,
    estilos=None,
    electrodomesticos=None,
    restricciones="",
):
    plan, total = _generar_plan_local(
        dias=dias,
        personas=personas,
        presupuesto=presupuesto,
        comidas=comidas,
        catalogo=catalogo,
        estilos=estilos,
        electrodomesticos=electrodomesticos,
        restricciones=restricciones,
    )
    valido, motivo = validar_plan_completo(plan, dias, comidas, catalogo)
    if not valido:
        raise ValueError(motivo)
    if total > presupuesto + TOLERANCIA_PRESUPUESTO:
        raise ValueError(
            f"El total calculado (${total:,.2f}) supera el presupuesto permitido (${presupuesto:,.2f})."
        )
    return plan, total

# ============================================================
# INTERFAZ — KASHCOOK AI
# Apariencia restaurada: hero con imagen, logos de tiendas, tarjetas y dashboard.
# La lógica del menú no se modifica aquí.
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
:root { --ink:#17221b; --muted:#68756d; --cream:#f7f5ed; --lime:#b7e34b; --green:#173f2a; --orange:#ff8a3d; --line:#e6e9e2; }
html,body,[class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(180deg,#fbfcf8 0%,#f3f5ef 100%); color:var(--ink); }
.block-container { max-width:1380px; padding-top:1rem; padding-bottom:3rem; }
.hero { min-height:340px; border-radius:32px; padding:42px 48px; display:flex; align-items:flex-end; position:relative; overflow:hidden; background:linear-gradient(110deg,rgba(12,43,28,.94),rgba(20,64,40,.74)),url('https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1800&q=85') center/cover; box-shadow:0 20px 55px rgba(19,42,27,.16); margin-bottom:24px; }
.hero h1 { font-family:'Plus Jakarta Sans'; color:#fff; font-size:clamp(2.5rem,5vw,5rem); line-height:.98; margin:0 0 14px; letter-spacing:-.06em; }
.hero p { color:#e9f3eb; font-size:1.08rem; max-width:650px; margin:0; }
.badge { display:inline-block; background:var(--lime); color:#17351f; padding:7px 13px; border-radius:999px; font-weight:800; font-size:.78rem; margin-bottom:14px; }
.card { background:#fff; border:1px solid var(--line); border-radius:22px; padding:22px; box-shadow:0 8px 28px rgba(22,39,27,.055); margin-bottom:16px; }
.card h3 { margin:0 0 5px; font-family:'Plus Jakarta Sans'; }
.muted { color:var(--muted); }
.store-card { background:#fff; border:1px solid var(--line); border-radius:18px; padding:14px 16px; min-height:84px; box-shadow:0 6px 20px rgba(22,39,27,.04); }
.store-name { font-weight:800; font-size:1rem; display:flex; align-items:center; gap:9px; }
.store-logo { width:30px; height:30px; border-radius:9px; object-fit:contain; background:#fff; border:1px solid #e7ebe4; padding:3px; }
.store-sub { color:#77827b; font-size:.76rem; margin-top:3px; }
.metric-card { background:#fff; border:1px solid var(--line); border-radius:22px; padding:19px; box-shadow:0 8px 28px rgba(22,39,27,.05); }
.metric-label { color:var(--muted); font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; }
.metric-value { font-family:'Plus Jakarta Sans'; font-size:1.8rem; font-weight:800; margin-top:4px; }
.day-card { background:#fff; border:1px solid var(--line); border-radius:24px; padding:22px; margin:14px 0; box-shadow:0 8px 28px rgba(22,39,27,.045); }
.meal { background:#f8faf5; border-radius:16px; padding:15px; margin-top:10px; border-left:5px solid var(--lime); }
.meal-title { font-family:'Plus Jakarta Sans'; font-weight:800; font-size:1.05rem; }
.pill { display:inline-block; background:#eef5df; color:#315020; border-radius:999px; padding:5px 9px; margin:3px 3px 0 0; font-size:.74rem; font-weight:700; }
.section-title { font-family:'Plus Jakarta Sans'; font-size:1.65rem; letter-spacing:-.035em; margin:28px 0 12px; }
.source { color:#65716a; font-size:.75rem; }
.small-note { color:#69756e; font-size:.8rem; }
/* Controles móviles: áreas táctiles grandes y etiquetas visibles. */
@media (max-width: 768px) {
  .block-container { padding: .65rem .75rem 2rem; }
  .hero { min-height: 280px; padding: 28px 22px; border-radius: 24px; }
  .hero h1 { font-size: 2.35rem; }
  div[data-baseweb="checkbox"] { min-height: 48px !important; padding: 8px 4px !important; }
  div[data-baseweb="select"] { min-height: 52px !important; }
  div[data-testid="stNumberInput"] input { min-height: 52px !important; font-size: 1.05rem !important; }
  button[kind] { min-height: 50px !important; font-size: 1rem !important; }
  .mobile-help { display:block; color:#536159; font-size:.86rem; margin:-6px 0 12px; line-height:1.35; }
}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<div class='hero'><div><div class='badge'>KASHCOOK AI · MENÚ + COMPRAS + PRESUPUESTO · {APP_BUILD}</div><h1>Come mejor.<br>Compra inteligente.</h1><p>Un plan de comida a tu medida, con cantidades consolidadas, lista de compra por tienda y precios actuales solo cuando pueden verificarse.</p></div></div>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>1 · Diseña tu semana</div>", unsafe_allow_html=True)
st.caption(f"Motor {APP_BUILD} · Precios confirmados únicamente con fuente oficial; si falta algún dato, no se calcula total.")

# Tiendas: mismos datos y mismas 4 tiendas, ahora con los logos visuales restaurados.
STORE_META_UI = {
    "Alsuper": {"emoji":"🟡", "domain":"alsuper.com"},
    "Walmart": {"emoji":"🔵", "domain":"walmart.com.mx"},
    "Soriana": {"emoji":"🔴", "domain":"soriana.com"},
    "Bodega Aurrerá": {"emoji":"🟢", "domain":"bodegaaurrera.com.mx"},
}

tiendas_seleccionadas=[]
columnas=st.columns(4)
for i,tienda in enumerate(TIENDAS_DISPONIBLES):
    with columnas[i]:
        meta=STORE_META_UI[tienda]
        seleccionada=st.checkbox(f"{meta['emoji']} {tienda}", value=(i==0), key=f"tienda_{i}")
        st.markdown(f"<div class='store-card'><div class='store-name'><img class='store-logo' src='https://www.google.com/s2/favicons?domain={meta['domain']}&sz=128'> {tienda}</div><div class='store-sub'>Catálogo de productos y presentaciones</div></div>", unsafe_allow_html=True)
        if seleccionada: tiendas_seleccionadas.append(tienda)

col1,col2,col3=st.columns(3)
with col1:
    dias=st.number_input("📅 Días",1,7,7,1)
    st.markdown("<div class='mobile-help'>Cuántos días quieres planear. KashCook generará exactamente esa cantidad.</div>",unsafe_allow_html=True)
with col2:
    personas=st.number_input("👨‍👩‍👧‍👦 Personas",1,10,4,1)
    st.markdown("<div class='mobile-help'>Número de personas que comerán. Las cantidades se escalan para todos.</div>",unsafe_allow_html=True)
with col3:
    presupuesto=st.number_input("💰 Presupuesto total (MXN)",200,10000,1500,100)
    st.markdown("<div class='mobile-help'>Monto máximo disponible para la compra del menú completo.</div>",unsafe_allow_html=True)

col1,col2=st.columns(2)
with col1:
    st.markdown("<div class='section-title' style='font-size:1.25rem'>🍽️ Estilo de comida</div>", unsafe_allow_html=True)
    estilos=st.multiselect("Selecciona uno o varios estilos",["Mexicana","Casera","Asiática","Italiana","Mediterránea","Saludable","Económica","Alta en proteína","Baja en carbohidratos","Desayunos mexicanos","Comida rápida casera"],default=["Mexicana","Casera","Económica"],label_visibility="collapsed")
    st.markdown("<div class='small-note'>KashCook combina las cocinas seleccionadas y busca variedad de platos, proteínas y preparaciones; no se limita a cambiar ingredientes de una misma receta.</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='section-title' style='font-size:1.25rem'>🍳 ¿Qué comidas quieres planear?</div>", unsafe_allow_html=True)
    comidas=st.multiselect("Selecciona las comidas",["Desayuno","Comida","Cena"],default=["Desayuno","Comida","Cena"],label_visibility="collapsed")

col1,col2=st.columns(2)
with col1:
    st.markdown("<div class='section-title' style='font-size:1.25rem'>⚙️ Electrodomésticos disponibles</div>", unsafe_allow_html=True)
    electrodomesticos=st.multiselect("Selecciona los que tienes",["Estufa","Horno","Microondas","Air Fryer","Licuadora","Freidora","Olla de presión","Olla lenta","Parrilla eléctrica"],default=["Estufa","Licuadora"],label_visibility="collapsed")
with col2:
    st.markdown("<div class='section-title' style='font-size:1.25rem'>⚠️ Restricciones y alergias</div>", unsafe_allow_html=True)
    restricciones=st.text_area("Indica alergias, alimentos que no consumen o restricciones",placeholder="Ejemplo: sin cacahuate, no picante, vegetariano...",label_visibility="collapsed")

st.markdown("<div class='section-title'>2 · Crear tu menú</div>", unsafe_allow_html=True)
colg1,colg2=st.columns([3,1])
with colg1: generar_menu=st.button("🚀 GENERAR MI MENÚ", type="primary", use_container_width=True)
with colg2: otra_opcion=st.button("🔄 OTRA OPCIÓN", use_container_width=True)

if otra_opcion:
    st.session_state["kc_semilla_menu"] = __import__("random").SystemRandom().randint(1,10**9)
    st.rerun()

if generar_menu:
    if not comidas:
        st.error("Selecciona al menos una comida.")
        st.stop()
    if not tiendas_seleccionadas:
        st.error("Selecciona al menos una tienda.")
        st.stop()
    catalogo=[]
    for tienda in tiendas_seleccionadas:
        catalogo.extend(copy.deepcopy(CATALOGOS.get(tienda,[])))
    if not catalogo:
        st.error("No hay productos disponibles para las tiendas seleccionadas.")
        st.stop()
    with st.spinner("KashCook está construyendo el menú y después verificará únicamente los productos que realmente necesita..."):
        try:
            # ETAPA 1: menú. NO hacemos búsquedas web todavía. Esto evita decenas
            # de consultas por ingredientes que finalmente ni siquiera se compran.
            # El presupuesto de planificación es deliberadamente un margen de búsqueda;
            # el presupuesto real solo se valida después con precios verificados.
            presupuesto_planificacion=max(float(presupuesto)*1.35, float(presupuesto)+250.0)
            try:
                plan,_=_generar_plan_local(
                    dias=int(dias),personas=int(personas),presupuesto=presupuesto_planificacion,
                    comidas=comidas,catalogo=catalogo,estilos=estilos,
                    electrodomesticos=electrodomesticos,restricciones=restricciones)
            except ValueError:
                presupuesto_planificacion=max(float(presupuesto)*1.60, float(presupuesto)+450.0)
                plan,_=_generar_plan_local(
                    dias=int(dias),personas=int(personas),presupuesto=presupuesto_planificacion,
                    comidas=comidas,catalogo=catalogo,estilos=estilos,
                    electrodomesticos=electrodomesticos,restricciones=restricciones)

            bases_necesarias=sorted({base for dia in plan.get("dias",[]) for comida in dia.get("comidas",[])
                                     for ing in comida.get("ingredientes",[])
                                     for base in [next((p.get("ingrediente_base") for p in catalogo if p.get("id")==ing.get("producto_id")),None)] if base})

            # ETAPA 2: precios. Solo buscamos los ingredientes del menú elegido.
            # Las consultas se hacen en paralelo y se guardan en caché.
            catalogo_optimizado=construir_catalogo_productos_optimo(
                catalogo,bases_necesarias=bases_necesarias,presupuesto=float(presupuesto))

            plan=_reemplazar_productos_por_verificados(plan,catalogo_optimizado)
            compra,total=calcular_compra(plan,catalogo_optimizado,personas)
            estado_verificacion=validar_precios_verificados(compra)

            # Integridad comercial: se puede entregar menú + lista, pero jamás
            # mostrar un total si queda al menos un producto sin precio actual verificado.
            total_verificado = bool(estado_verificacion["ok"])
            if total_verificado and total > float(presupuesto) + TOLERANCIA_PRESUPUESTO:
                # Se conserva el menú para revisión; no se falsean porciones ni precios.
                st.warning(
                    f"Los precios verificados suman ${total:,.2f}, por encima del presupuesto "
                    f"de ${float(presupuesto):,.2f}. KashCook conserva las porciones reales."
                )

            errores_verificacion = {}
            for tienda in tiendas_seleccionadas:
                errores_verificacion[tienda] = {}
                for base in bases_necesarias:
                    rr = PRECIO_CACHE.get(("candidatos", tienda, base), {}).get("resultado", {})
                    if not rr.get("candidatos"):
                        errores_verificacion[tienda][base] = rr.get("error") or "La tienda no devolvió producto/precio legible."

            st.session_state["plan"] = plan
            st.session_state["compra"] = compra
            st.session_state["total"] = total if total_verificado else None
            st.session_state["total_calculado_no_mostrar"] = total if not total_verificado else None
            st.session_state["catalogo_verificado"] = catalogo_optimizado
            st.session_state["estado_verificacion"] = estado_verificacion
            st.session_state["errores_verificacion"] = errores_verificacion
            st.session_state["total_es_real"] = total_verificado
            st.session_state["presupuesto"] = presupuesto
            st.session_state["personas"] = personas
            st.session_state["tiendas"] = tiendas_seleccionadas
            st.session_state["precios_verificados_en"] = datetime.now().astimezone().isoformat(timespec="minutes")
            if total_verificado:
                st.success("Plan generado. Todos los precios se verificaron en las tiendas consultadas.")
            else:
                n = estado_verificacion.get("faltantes", 0)
                st.warning(f"Menú y lista generados. {n} producto(s) siguen sin precio actual verificable; el total queda oculto. No se muestran precios de referencia como reales.")
        except Exception as e:
            st.error(f"Ocurrió un error al generar el plan: {e}")


# ============================================================
# RESULTADO — dashboard visual restaurado
# ============================================================
if "plan" in st.session_state:
    plan=st.session_state["plan"]
    compra=st.session_state["compra"]
    total=st.session_state["total"]
    presupuesto=st.session_state["presupuesto"]
    personas=st.session_state["personas"]
    tiendas=st.session_state["tiendas"]
    st.markdown("<div class='section-title'>3 · Tu dashboard</div>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Presupuesto</div><div class='metric-value'>${presupuesto:,.2f}</div></div>",unsafe_allow_html=True)
    with c2:
        valor_total = f"${total:,.2f}" if total is not None and total_es_real else "Sin verificar"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Compra verificada</div><div class='metric-value'>{valor_total}</div></div>",unsafe_allow_html=True)
    with c3:
        disponible = f"${max(0,presupuesto-total):,.2f}" if total is not None and total_es_real else "—"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Disponible</div><div class='metric-value'>{disponible}</div></div>",unsafe_allow_html=True)
    with c4:
        util=(total/presupuesto*100) if presupuesto and total is not None and total_es_real else None
        valor_uso=f"{util:.0f}%" if util is not None else "—"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Uso del presupuesto</div><div class='metric-value'>{valor_uso}</div></div>",unsafe_allow_html=True)

    verif_hora=st.session_state.get("precios_verificados_en", "consulta actual")
    estado_verif=st.session_state.get("estado_verificacion", {}) or {}
    total_es_real=bool(st.session_state.get("total_es_real", False))
    nver=estado_verif.get("verificados", 0)
    nfalta=estado_verif.get("faltantes", 0)
    if total_es_real:
        st.markdown(f"<div class='card'><b>🟢 Precio actual verificado:</b> todos los productos de esta compra fueron verificados en la consulta de {verif_hora}.</div>", unsafe_allow_html=True)
    else:
        faltas=", ".join(estado_verif.get("nombres_faltantes", [])[:8])
        if len(estado_verif.get("nombres_faltantes", []))>8: faltas += "..."
        st.markdown(f"<div class='card'><b>🟠 Total no disponible:</b> {nver} productos verificados y {nfalta} sin verificación automática. El menú y la lista están disponibles, pero KashCook no presenta una suma de referencia como precio real.<br><span class=\"small-note\">Pendientes: {html.escape(faltas)}</span></div>", unsafe_allow_html=True)
        with st.expander("Diagnóstico técnico de precios", expanded=False):
            errores = st.session_state.get("errores_verificacion", {})
            if not errores:
                st.write("No se recibieron detalles de error en esta ejecución.")
            for tienda_diag, por_base in errores.items():
                st.markdown(f"**{tienda_diag}**")
                for base_diag, err_diag in por_base.items():
                    st.write(f"- {CONSULTAS_PRECIO.get(base_diag, base_diag)}: {err_diag}")
        if st.button("🔄 Reintentar verificación de precios", use_container_width=True):
            with st.spinner("Volviendo a consultar las tiendas seleccionadas..."):
                tiendas_reintento = st.session_state.get("tiendas", [])
                catalogo_base_reintento = []
                for tienda_reintento in tiendas_reintento:
                    catalogo_base_reintento.extend(copy.deepcopy(CATALOGOS.get(tienda_reintento, [])))
                plan_reintento = st.session_state.get("plan", {})
                catalogo_anterior = st.session_state.get("catalogo_verificado", [])
                bases_reintento = set()
                ids_reintento = {ing.get("producto_id") for d in plan_reintento.get("dias", []) for c in d.get("comidas", []) for ing in c.get("ingredientes", [])}
                for prod in catalogo_anterior:
                    if any(pid == prod.get("id") or (isinstance(pid, str) and pid.startswith(str(prod.get("id")) + "__live__")) for pid in ids_reintento):
                        bases_reintento.add(prod.get("ingrediente_base"))
                for key_cache in list(PRECIO_CACHE):
                    if isinstance(key_cache, tuple) and len(key_cache) >= 3 and key_cache[0] == "candidatos" and key_cache[1] in tiendas_reintento:
                        PRECIO_CACHE.pop(key_cache, None)
                catalogo_nuevo = construir_catalogo_productos_optimo(catalogo_base_reintento, bases_necesarias=sorted(bases_reintento), presupuesto=float(st.session_state.get("presupuesto", 0)))
                plan_nuevo = _reemplazar_productos_por_verificados(plan_reintento, catalogo_nuevo)
                compra_nueva, total_nuevo = calcular_compra(plan_nuevo, catalogo_nuevo, int(st.session_state.get("personas", 1)))
                estado_nuevo = validar_precios_verificados(compra_nueva)
                st.session_state["plan"] = plan_nuevo
                st.session_state["compra"] = compra_nueva
                st.session_state["catalogo_verificado"] = catalogo_nuevo
                st.session_state["estado_verificacion"] = estado_nuevo
                st.session_state["total_es_real"] = bool(estado_nuevo["ok"])
                st.session_state["total"] = total_nuevo if estado_nuevo["ok"] else None
                st.session_state["total_calculado_no_mostrar"] = total_nuevo if not estado_nuevo["ok"] else None
                st.session_state["precios_verificados_en"] = datetime.now().astimezone().isoformat(timespec="minutes")
                st.rerun()

    tabs=st.tabs(["🍽️ Menú","🛒 Compras","💰 Presupuesto","👨‍🍳 Recetas","📄 PDF"])
    catalogo_global = st.session_state.get("catalogo_verificado", []) or []
    if not catalogo_global:
        for lista in CATALOGOS.values():
            catalogo_global.extend(lista)
    productos_por_id={p["id"]:p for p in catalogo_global}

    with tabs[0]:
        for dia in plan.get("dias",[]):
            st.markdown(f"<div class='day-card'><h3>Día {dia.get('dia','')}</h3>",unsafe_allow_html=True)
            for comida in dia.get("comidas",[]):
                pills="".join([f"<span class='pill'>{productos_por_id.get(x.get('producto_id'),{}).get('nombre',x.get('producto_id'))} · {x.get('cantidad_por_persona')} {x.get('unidad')} p/p · {float(x.get('cantidad_por_persona',0))*personas:g} {x.get('unidad')} total</span>" for x in comida.get('ingredientes',[])])
                st.markdown(f"<div class='meal'><div class='meal-title'>{comida.get('tipo','Comida')} · {comida.get('nombre','')}</div>{pills}</div>",unsafe_allow_html=True)
                if comida.get("fuente"):
                    ver="✓ Fuente verificada" if comida.get("verificada") else "✓ Receta real de biblioteca culinaria"
                    st.markdown(f"<div class='source'>{ver}: {comida.get('fuente')}</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

    with tabs[1]:
        st.info("La lista de compras se calcula sumando los ingredientes de TODOS los días y convirtiéndolos a presentaciones comerciales. Si un ingrediente aparece en una receta, debe aparecer aquí o el menú se considera inválido.")
        for x in compra:
            estado=x.get("estado_precio","Referencia")
            marca_estado="🟢 Precio verificado" if estado=="Verificado" else "🟠 Precio actual pendiente"
            p_catalogo=productos_por_id.get(x.get("producto_id"), {})
            marca_producto=p_catalogo.get("marca") or x.get("marca") or "Marca no identificada"
            if estado == "Verificado":
                linea_precio = f"<p><b>${x['precio_unitario']:,.2f} por presentación</b> · subtotal <b>${x['subtotal']:,.2f}</b></p>"
                linea_fuente = f"<div class='small-note'>Fuente: <a href='{html.escape(str(x.get('fuente_precio') or ''), quote=True)}' target='_blank' rel='noopener'>página de producto oficial ↗</a> · {html.escape(str(x.get('ultima_verificacion') or ''))}</div>"
            else:
                q_url = BUSQUEDAS_TIENDA.get(x['tienda'], ["https://www.google.com/search?q={q}"])[0].format(q=quote_plus(x['producto']))
                linea_precio = "<p><b>Precio no mostrado:</b> falta verificación automática en esta tienda.</p>"
                linea_fuente = f"<div class='small-note'><a href='{html.escape(q_url, quote=True)}' target='_blank' rel='noopener'>Buscar en la tienda oficial ↗</a> · No se usó precio de referencia como real.</div>"
            cantidad_txt = f"{x['paquetes']:.2f} kg requeridos" if estado == "Verificado" and x.get('unidad') == "g" and x.get('paquetes',0)<10 else f"{x['paquetes']} paquete(s)"
            st.markdown(f"<div class='card'><h3>{html.escape(str(x['producto']))}</h3><div class='muted'><b>Marca:</b> {html.escape(str(marca_producto))} · {html.escape(str(x['presentacion']))} · {cantidad_txt} · {html.escape(str(x['tienda']))}</div>{linea_precio}<div class='small-note'>{marca_estado}</div>{linea_fuente}</div>",unsafe_allow_html=True)


    with tabs[2]:
        if total is None or not total_es_real:
            st.warning("El presupuesto no se puede comparar todavía: falta verificar uno o más precios actuales. No se usa el catálogo de referencia para calcular un total.")
            st.write(f"Presupuesto disponible: **${presupuesto:,.2f} MXN**")
            st.write(f"Productos con precio verificado: **{nver}** de **{len(compra)}**")
            st.progress((nver / len(compra)) if compra else 0)
        else:
            restante=presupuesto-total
            if restante>=0:
                st.success(f"La compra verificada está dentro del presupuesto. Quedan ${restante:,.2f}.")
            else:
                st.error(f"La compra verificada supera el presupuesto por ${abs(restante):,.2f}.")
            st.progress(min(max(total/presupuesto,0),1.0) if presupuesto else 0)

    with tabs[3]:
        for dia in plan.get("dias",[]):
            st.markdown(f"### Día {dia.get('dia','')}")
            for comida in dia.get("comidas",[]):
                st.markdown(f"#### {comida.get('tipo','Comida')}: {comida.get('nombre','')}")
                if comida.get("fuente"):
                    st.caption(("✓ Fuente verificada: " if comida.get("verificada") else "✓ Receta real de biblioteca: ") + comida.get("fuente"))
                    if comida.get("fuente_url"):
                        st.markdown(f"[Ver receta original ↗]({comida.get('fuente_url')})")
                st.markdown("**Ingredientes por persona:**")
                for ing in comida.get("ingredientes",[]):
                    p=productos_por_id.get(ing.get("producto_id")); nombre=p["nombre"] if p else str(ing.get("producto_id"))
                    cant=float(ing.get('cantidad_por_persona',0) or 0)
                    unidad=ing.get('unidad','')
                    st.write(f"- {nombre}: {cant:g} {unidad} por persona · **{cant*personas:g} {unidad} para {personas} personas**")
                st.markdown("**Preparación:**")
                for n,paso in enumerate(comida.get("preparacion",[]) or [],1): st.write(f"{n}. {paso}")

    with tabs[4]:
        pdf_bytes=generar_pdf(plan=plan,compra=compra,total=total,presupuesto=presupuesto,personas=personas,tiendas=tiendas,total_verificado=total_es_real)
        st.download_button("📄 Descargar plan completo en PDF",data=pdf_bytes,file_name="KashCook_AI_Plan.pdf",mime="application/pdf",use_container_width=True)

