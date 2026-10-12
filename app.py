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

APP_BUILD = "2026.10.09-futurista-v5"

TIENDAS_DISPONIBLES = [
    "Alsuper",
    "Smart",
    "Soriana",
    "Walmart",
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

# S-Mart no expone aquí un catálogo transaccional de productos/precios que podamos
# certificar. Se genera un catálogo técnico de referencia solo para permitir la
# planificación del menú; jamás se marca como precio de S-Mart verificado.
_smart_refs = {}
for _lista_ref in CATALOGOS.values():
    for _prod_ref in _lista_ref:
        _base_ref = _prod_ref.get("ingrediente_base")
        if _base_ref and _base_ref not in _smart_refs:
            _smart_refs[_base_ref] = _prod_ref
CATALOGOS["Smart"] = []
for _base_ref, _prod_ref in _smart_refs.items():
    _smart_item = copy.deepcopy(_prod_ref)
    _smart_item["id"] = f"smart_ref_{_base_ref}"
    _smart_item["tienda"] = "Smart"
    _smart_item["nombre"] = _prod_ref.get("nombre", _base_ref)
    _smart_item["estado_precio"] = "Referencia"
    _smart_item["ultima_verificacion"] = None
    _smart_item["fuente_precio"] = "Referencia técnica para planificar; no es precio confirmado de S-Mart"
    CATALOGOS["Smart"].append(_smart_item)

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
    # Página oficial de ofertas de S-Mart; no equivale a un buscador de catálogo.
    # Solo se aceptará un producto si la página expone nombre, precio y presentación.
    "Smart": [
        "https://www.supermercadossmart.com/ofertas",
    ],
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
    "Smart": "supermercadossmart.com",
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
    """Llamada de compatibilidad a Groq con un límite de salida conservador.

    El planificador principal es local; si esta función se utiliza en un flujo
    auxiliar, evita pedir 8.000 tokens de salida de golpe. Cuando el proveedor
    devuelve un error de TPM/413, reintenta una sola vez con una respuesta más
    corta en vez de repetir indefinidamente la misma petición.
    """
    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres KashCook AI. Diseñas menús familiares, recetas, cantidades "
                "y compras. Responde solo JSON válido cuando se solicite un plan. "
                "Sé conciso y no repitas instrucciones."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    try:
        respuesta = cliente.chat.completions.create(
            model="openai/gpt-oss-120b", messages=mensajes,
            temperature=temperatura, max_tokens=2048,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        detalle = str(exc).lower()
        es_limite_tokens = any(x in detalle for x in ("413", "tokens per minute", "tpm", "request too large", "rate_limit_exceeded"))
        if not es_limite_tokens:
            raise
        respuesta = cliente.chat.completions.create(
            model="openai/gpt-oss-120b", messages=mensajes,
            temperature=temperatura, max_tokens=768,
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
                "venta_por_kg": bool(p.get("venta_por_kg", False)),
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
- Cada comida necesita nombre, al menos 2 ingredientes y al menos 2 pasos de 
