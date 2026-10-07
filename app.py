import io
import json
import math
import re
import html
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote_plus

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
        # IMPORTANTE: el valor numérico recibido en "precio" se conserva
        # únicamente por compatibilidad con el catálogo heredado.
        # NUNCA se utiliza como precio de compra. Los precios válidos son
        # únicamente los obtenidos públicamente durante la actualización.
        "precio": None,
        "precio_verificado": False,
        "fuente_precio": None,
        "url_precio": None,
        "precio_actualizado": None,
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


# ============================================================
# PRECIOS PÚBLICOS / ACTUALES
# ============================================================

# No se usan precios escritos a mano para calcular la compra.
# KashCook intenta obtener el precio publicado por cada tienda.
# Si no puede verificarlo, el producto queda como:
# "PRECIO NO DISPONIBLE".

FUENTES_TIENDAS = {
    "Alsuper": "https://alsuper.com/buscar?q={q}",
    "Walmart": "https://www.walmart.com.mx/search?q={q}",
    "Soriana": "https://www.soriana.com/buscar?q={q}",
    "Bodega Aurrerá": "https://www.bodegaaurrera.com.mx/search?q={q}",
}

PRECIO_NO_DISPONIBLE = "PRECIO NO DISPONIBLE"


def _precio_desde_texto(texto):
    if not texto:
        return None
    patrones = [
        r"\$\s*([0-9]{1,4}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)",
        r"([0-9]{1,4}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)\s*MXN",
    ]
    candidatos = []
    for patron in patrones:
        for m in re.finditer(patron, texto, flags=re.I):
            try:
                valor = float(m.group(1).replace(",", ""))
            except Exception:
                continue
            if 1 <= valor <= 10000:
                candidatos.append(valor)
    if not candidatos:
        return None
    return candidatos[0]


def _normalizar_para_busqueda(texto):
    texto = normalizar_texto(texto)
    texto = re.sub(r"[^a-z0-9]+", " ", texto.lower())
    return re.sub(r"\s+", " ", texto).strip()


def _puntaje_nombre(nombre, consulta):
    n = _normalizar_para_busqueda(nombre)
    q = _normalizar_para_busqueda(consulta)
    tokens = [t for t in q.split() if len(t) >= 4]
    if not tokens:
        return 0
    aciertos = sum(1 for t in tokens if t in n)
    return aciertos / len(tokens)


def _extraer_productos_jsonld(soup):
    encontrados = []

    def recorrer(obj):
        if isinstance(obj, dict):
            tipo = obj.get("@type")
            if tipo == "Product" or (isinstance(tipo, list) and "Product" in tipo):
                nombre = obj.get("name")
                ofertas = obj.get("offers")
                precio = None
                moneda = None
                url = obj.get("url")
                if isinstance(ofertas, dict):
                    precio = ofertas.get("price") or ofertas.get("lowPrice")
                    moneda = ofertas.get("priceCurrency")
                    url = ofertas.get("url") or url
                elif isinstance(ofertas, list):
                    for oferta in ofertas:
                        if isinstance(oferta, dict):
                            precio = oferta.get("price") or oferta.get("lowPrice")
                            moneda = oferta.get("priceCurrency")
                            url = oferta.get("url") or url
                            if precio is not None:
                                break
                if nombre:
                    try:
                        precio_num = float(str(precio).replace(",", "")) if precio is not None else None
                    except Exception:
                        precio_num = None
                    encontrados.append({
                        "nombre": str(nombre),
                        "precio": precio_num if moneda in (None, "MXN", "mxn") else None,
                        "url": url,
                    })
            for v in obj.values():
                recorrer(v)
        elif isinstance(obj, list):
            for v in obj:
                recorrer(v)

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or script.get_text())
            recorrer(data)
        except Exception:
            continue
    return encontrados


def _extraer_candidatos_html(soup, consulta):
    candidatos = []
    palabras = [p for p in _normalizar_para_busqueda(consulta).split() if len(p) >= 4]

    for nodo in soup.find_all(["article", "li", "div"]):
        texto = " ".join(nodo.stripped_strings)
        if len(texto) < 10 or len(texto) > 2500:
            continue
        normal = _normalizar_para_busqueda(texto)
        if not any(p in normal for p in palabras[:2]):
            continue
        precio = _precio_desde_texto(texto)
        if precio is None:
            continue
        enlace = nodo.find("a", href=True)
        url = enlace.get("href") if enlace else None
        if url and url.startswith("/"):
            url = None
        candidatos.append({"nombre": texto[:300], "precio": precio, "url": url})
        if len(candidatos) >= 20:
            break
    return candidatos


def obtener_precio_publico(producto_obj, session=None):
    tienda = producto_obj["tienda"]
    plantilla = FUENTES_TIENDAS.get(tienda)
    if not plantilla:
        return None

    consulta = producto_obj["nombre"]
    url_busqueda = plantilla.format(q=quote_plus(consulta))
    ses = session or requests.Session()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/154.0 Safari/537.36"
        ),
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.7",
    }

    try:
        respuesta = ses.get(url_busqueda, headers=headers, timeout=12, allow_redirects=True)
        if respuesta.status_code != 200:
            return None
        soup = BeautifulSoup(respuesta.text, "html.parser")

        candidatos = _extraer_productos_jsonld(soup)
        candidatos.extend(_extraer_candidatos_html(soup, consulta))

        mejores = []
        for c in candidatos:
            precio = c.get("precio")
            if precio is None or precio <= 0:
                continue
            score = _puntaje_nombre(c.get("nombre", ""), consulta)
            if score >= 0.35:
                mejores.append((score, precio, c))

        if not mejores:
            return None

        mejores.sort(key=lambda x: (-x[0], x[1]))
        _, precio, candidato = mejores[0]
        return {
            "precio": round(float(precio), 2),
            "url": candidato.get("url") or url_busqueda,
            "fuente": tienda,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except Exception:
        return None


def actualizar_precios_publicos(tiendas_seleccionadas):
    catalogo = []
    for tienda in tiendas_seleccionadas:
        catalogo.extend(CATALOGOS.get(tienda, []))

    # Evita volver a consultar innecesariamente en cada rerun de Streamlit.
    firma = tuple(sorted((p["id"], p["tienda"], p["nombre"]) for p in catalogo))
    cache_key = "precios_publicos_cache"
    cache = st.session_state.get(cache_key)
    ahora = time.time()
    if cache and cache.get("firma") == firma and ahora - cache.get("timestamp", 0) < 3600:
        return cache["catalogo"], cache.get("errores", [])

    errores = []
    resultados = {}
    tareas = {}

    with ThreadPoolExecutor(max_workers=min(8, max(1, len(catalogo)))) as executor:
        for p in catalogo:
            tareas[executor.submit(obtener_precio_publico, p)] = p

        for futuro in as_completed(tareas):
            p = tareas[futuro]
            try:
                resultado = futuro.result()
            except Exception:
                resultado = None
            if resultado:
                resultados[p["id"]] = resultado

    catalogo_actualizado = []
    for p in catalogo:
        copia = dict(p)
        dato = resultados.get(p["id"])
        if dato:
            copia["precio"] = dato["precio"]
            copia["precio_verificado"] = True
            copia["fuente_precio"] = dato["fuente"]
            copia["url_precio"] = dato["url"]
            copia["precio_actualizado"] = dato["fecha"]
        else:
            copia["precio"] = None
            copia["precio_verificado"] = False
            copia["fuente_precio"] = None
            copia["url_precio"] = None
            copia["precio_actualizado"] = None
            errores.append(f"{p['tienda']}: {p['nombre']}")
        catalogo_actualizado.append(copia)

    st.session_state[cache_key] = {
        "firma": firma,
        "timestamp": ahora,
        "catalogo": catalogo_actualizado,
        "errores": errores,
    }
    return catalogo_actualizado, errores


def catalogo_por_tiendas(tiendas, catalogo_actualizado):
    permitidas = set(tiendas)
    return [p for p in catalogo_actualizado if p["tienda"] in permitidas]


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

    mensajes = [
        {
            "role": "system",
            "content": (
                "Eres KashCook AI. Diseñas menús familiares, "
                "recetas, cantidades y compras. Responde solo "
                "JSON válido cuando se solicite un plan."
            ),
        },
        {"role": "user", "content": prompt},
    ]

    try:
        respuesta = cliente.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=mensajes,
            temperature=temperatura,
            max_tokens=4500,
            response_format={"type": "json_object"},
        )
    except Exception as error:
        mensaje_error = str(error).lower()
        if not any(x in mensaje_error for x in ("413", "too large", "tokens per minute")):
            raise
        respuesta = cliente.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=mensajes,
            temperature=min(temperatura, 0.25),
            max_tokens=3000,
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
                    if float(ing.get("cantidad_por_persona", 0)) <= 0:
                        return False, f"Hay una cantidad inválida en el día {i}."
                except Exception:
                    return False, f"Hay una cantidad inválida en el día {i}."

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
    productos_por_id = {p["id"]: p for p in catalogo}
    demanda = {}
    faltantes_precio = []

    for dia in plan.get("dias", []):
        for comida in dia.get("comidas", []):
            for ing in comida.get("ingredientes", []):
                producto_id = ing.get("producto_id")
                if producto_id not in productos_por_id:
                    continue
                try:
                    cantidad_persona = float(ing.get("cantidad_por_persona", 0))
                except Exception:
                    cantidad_persona = 0
                if cantidad_persona <= 0:
                    continue

                unidad = ing.get("unidad", "")
                cantidad_total = cantidad_persona * personas
                p = productos_por_id[producto_id]
                cantidad_base, unidad_base = convertir_a_base(cantidad_total, unidad)
                contenido_base, unidad_contenido_base = convertir_a_base(
                    p["contenido"], p["unidad_contenido"]
                )
                if unidad_base != unidad_contenido_base or contenido_base <= 0:
                    continue

                if producto_id not in demanda:
                    demanda[producto_id] = {
                        "producto": p,
                        "cantidad_requerida": 0,
                        "unidad": unidad_base,
                    }
                demanda[producto_id]["cantidad_requerida"] += cantidad_base

    compra = []
    total = 0.0
    presupuesto_verificable = True

    for producto_id, item in demanda.items():
        p = item["producto"]
        contenido_base, _ = convertir_a_base(p["contenido"], p["unidad_contenido"])
        paquetes = max(1, math.ceil(item["cantidad_requerida"] / contenido_base))
        precio = p.get("precio")
        precio_disponible = bool(p.get("precio_verificado") and precio is not None and precio > 0)

        if not precio_disponible:
            presupuesto_verificable = False
            faltantes_precio.append(p["nombre"])
            subtotal = None
        else:
            subtotal = round(paquetes * float(precio), 2)
            total += subtotal

        compra.append({
            "producto": p["nombre"],
            "ingrediente_base": p["ingrediente_base"],
            "presentacion": p["presentacion"],
            "contenido": p["contenido"],
            "unidad_contenido": p["unidad_contenido"],
            "cantidad_requerida": item["cantidad_requerida"],
            "unidad": item["unidad"],
            "paquetes": paquetes,
            "precio_unitario": float(precio) if precio_disponible else None,
            "precio_texto": f"${float(precio):,.2f}" if precio_disponible else PRECIO_NO_DISPONIBLE,
            "subtotal": subtotal,
            "subtotal_texto": f"${subtotal:,.2f}" if subtotal is not None else PRECIO_NO_DISPONIBLE,
            "tienda": p["tienda"],
            "precio_verificado": precio_disponible,
            "fuente_precio": p.get("fuente_precio"),
            "url_precio": p.get("url_precio"),
        })

    return compra, round(total, 2), presupuesto_verificable, faltantes_precio


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
            f"{p['precio'] if p.get('precio_verificado') else PRECIO_NO_DISPONIBLE}"
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
- Prioriza productos con precio verificado. Nunca conviertas PRECIO NO DISPONIBLE en un número.
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
            f"{p['nombre']}|{p['contenido']}{p['unidad_contenido']}|{p['precio'] if p.get('precio_verificado') else PRECIO_NO_DISPONIBLE}"
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
# APROVECHAMIENTO Y AVISO DE PRECIOS
# ============================================================

def generar_aprovechamiento(compra):
    recomendaciones = []
    categorias = {str(item.get("ingrediente_base", "")).lower() for item in compra}
    if any(x in categorias for x in {"pollo", "res", "cerdo", "pescado"}):
        recomendaciones.append("Divide las proteínas en porciones antes de congelarlas para evitar descongelar de más.")
    if any(x in categorias for x in {"cebolla", "tomate", "zanahoria", "papa", "lechuga", "calabaza"}):
        recomendaciones.append("Organiza las verduras al recibirlas y utiliza primero las más perecederas.")
    if "tortilla" in categorias:
        recomendaciones.append("Separa las tortillas en porciones y congela las que no vayas a consumir pronto.")
    if any(x in categorias for x in {"arroz", "frijol"}):
        recomendaciones.append("Refrigera o congela porciones de arroz y frijol sobrantes para reutilizarlas en otra comida.")
    if not recomendaciones:
        recomendaciones.append("Conserva los sobrantes en recipientes cerrados, etiquétalos y utiliza primero los alimentos más perecederos.")
    return recomendaciones


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

    compra_verificada = bool(compra) and all(
        item.get("precio_verificado", False) for item in compra
    )
    estado_compra = "Compra verificada" if compra_verificada else "Compra parcial: hay precios no disponibles"

    story.append(
        Paragraph(
            f"Plan alimenticio para {personas} persona(s)<br/>"
            f"{len(plan.get('dias', []))} día(s)<br/>"
            f"Tiendas seleccionadas: "
            f"{html.escape(', '.join(tiendas))}<br/>"
            f"Presupuesto: ${presupuesto:,.2f} MXN<br/>"
            f"{estado_compra}: ${total:,.2f} MXN",
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
                    html.escape(item.get("precio_texto", PRECIO_NO_DISPONIBLE)),
                    pequeno,
                ),

                Paragraph(
                    html.escape(item.get("subtotal_texto", PRECIO_NO_DISPONIBLE)),
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
            10,
        )
    )

    story.append(Paragraph("APROVECHAMIENTO", dia_style))
    for recomendacion in generar_aprovechamiento(compra):
        story.append(Paragraph("• " + html.escape(recomendacion), normal))

    story.append(
        Paragraph(
            "<b>Aviso de precios:</b> los precios públicos consultados pueden cambiar por promociones, disponibilidad, peso real o actualización de la tienda. Verifica el precio final antes de pagar.",
            pequeno,
        )
    )

    story.append(
        Spacer(
            1,
            12,
        )
    )

    story.append(
        Paragraph(
            f"<b>{'TOTAL DE COMPRA VERIFICADO' if compra_verificada else 'TOTAL PARCIAL (HAY PRECIOS NO DISPONIBLES)'}: "
            f"${total:,.2f} MXN</b>",
            ParagraphStyle(
                "TotalKash",
                parent=normal,
                fontSize=14,
                leading=18,
            ),
        )
    )

    story.append(
        Paragraph(
            f"Presupuesto original: "
            f"${presupuesto:,.2f} MXN",
            normal,
        )
    )

    if total <= presupuesto:

        story.append(
            Paragraph(
                f"Disponible restante: "
                f"${presupuesto - total:,.2f} MXN",
                normal,
            )
        )

    else:

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
# INTERFAZ
# ============================================================

st.title(
    "🍳 KashCook AI"
)

st.markdown(
    """
### Tu menú, tus compras y tu presupuesto en un solo lugar

KashCook crea el menú, calcula las cantidades para el número
de personas y transforma esas cantidades en productos reales
según la presentación disponible.
"""
)

st.divider()


# ============================================================
# TIENDAS
# ============================================================

st.subheader(
    "🛒 ¿Dónde vas a comprar?"
)

tiendas_seleccionadas = []

columnas = st.columns(4)

for i, tienda in enumerate(
    TIENDAS_DISPONIBLES
):

    with columnas[i]:

        seleccionada = st.checkbox(
            tienda,
            value=(i == 0),
            key=f"tienda_{i}",
        )

        if seleccionada:
            tiendas_seleccionadas.append(
                tienda
            )

if not tiendas_seleccionadas:

    st.warning(
        "Selecciona al menos una tienda."
    )

    st.stop()

if st.button("🔄 Actualizar precios públicos ahora"):
    st.session_state.pop("precios_publicos_cache", None)
    st.success("Cache de precios eliminado. La próxima generación consultará nuevamente las tiendas.")


# ============================================================
# DATOS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    dias = st.number_input(
        "📅 Días",
        min_value=1,
        max_value=7,
        value=7,
        step=1,
    )

with col2:

    personas = st.number_input(
        "👨‍👩‍👧‍👦 Personas",
        min_value=1,
        max_value=10,
        value=4,
        step=1,
    )

with col3:

    presupuesto = st.number_input(
        "💰 Presupuesto total",
        min_value=200,
        max_value=10000,
        value=1500,
        step=100,
    )


# ============================================================
# ESTILOS
# ============================================================

st.subheader(
    "🍽️ Estilo de comida"
)

estilos = st.multiselect(
    "Selecciona uno o varios estilos",
    [
        "Mexicana",
        "Casera",
        "Saludable",
        "Económica",
        "Alta en proteína",
        "Baja en carbohidratos",
        "Italiana",
        "Mediterránea",
        "Desayunos mexicanos",
        "Comida rápida casera",
    ],
    default=[
        "Mexicana",
        "Casera",
        "Económica",
    ],
)


# ============================================================
# COMIDAS
# ============================================================

st.subheader(
    "🍳 ¿Qué comidas quieres planear?"
)

comidas = st.multiselect(
    "Selecciona las comidas",
    [
        "Desayuno",
        "Comida",
        "Cena",
    ],
    default=[
        "Desayuno",
        "Comida",
        "Cena",
    ],
)


# ============================================================
# ELECTRODOMÉSTICOS
# ============================================================

st.subheader(
    "🔌 Electrodomésticos disponibles"
)

electrodomesticos = st.multiselect(
    "Selecciona los que tienes",
    [
        "Estufa",
        "Horno",
        "Microondas",
        "Air Fryer",
        "Licuadora",
        "Freidora",
        "Olla de presión",
        "Olla lenta",
        "Parrilla eléctrica",
    ],
    default=[
        "Estufa",
        "Licuadora",
    ],
)


# ============================================================
# RESTRICCIONES
# ============================================================

st.subheader(
    "⚠️ Restricciones y alergias"
)

restricciones = st.text_area(
    "Indica alergias, alimentos que no consumen "
    "o restricciones",
    placeholder=(
        "Ejemplo: sin camarón, sin cacahuate, "
        "no picante, vegetariano..."
    ),
)


st.divider()


# ============================================================
# BOTÓN GENERAR
# ============================================================

if st.button(
    "🚀 Generar mi plan",
    type="primary",
    use_container_width=True,
):

    if not comidas:

        st.error(
            "Selecciona al menos una comida."
        )

        st.stop()

    cliente = obtener_cliente_groq()

    if not cliente:

        st.error(
            "Configura GROQ_API_KEY para continuar."
        )

        st.stop()

    catalogo_base = []

    for tienda in tiendas_seleccionadas:
        catalogo_base.extend(CATALOGOS.get(tienda, []))

    if not catalogo_base:

        st.error(
            "No hay productos disponibles "
            "para las tiendas seleccionadas."
        )

        st.stop()

    with st.spinner(
        "Actualizando precios públicos y diseñando tu menú..."
    ):

        try:

            # =================================================
            # PRECIOS REALES / PÚBLICOS
            # =================================================
            catalogo, errores_precio = actualizar_precios_publicos(
                tiendas_seleccionadas
            )

            precios_ok = sum(1 for p in catalogo if p.get("precio_verificado"))
            precios_total = len(catalogo)

            if precios_ok == 0:
                st.warning(
                    "No se pudo verificar ningún precio público en este momento. "
                    "KashCook no usará precios inventados; los productos aparecerán "
                    "como PRECIO NO DISPONIBLE y el total de compra no se considerará verificable."
                )
            elif precios_ok < precios_total:
                st.info(
                    f"Precios públicos verificados: {precios_ok}/{precios_total}. "
                    "Los productos sin precio quedan como PRECIO NO DISPONIBLE y no se inventará ningún importe."
                )

            # =================================================
            # PLAN INICIAL
            # =================================================

            prompt = construir_prompt(
                tiendas=tiendas_seleccionadas,
                dias=dias,
                personas=personas,
                presupuesto=presupuesto,
                estilos=estilos,
                comidas=comidas,
                electrodomesticos=electrodomesticos,
                restricciones=restricciones,
                catalogo=catalogo,
            )

            respuesta = llamar_groq(
                cliente,
                prompt,
                temperatura=0.45,
            )

            plan_raw = extraer_json(
                respuesta
            )

            plan = normalizar_plan(
                plan_raw
            )

            valido, motivo = validar_plan_completo(
                plan, dias, comidas, catalogo
            )

            if not valido:
                # Una segunda llamada pequeña corrige omisiones sin reenviar
                # todo el catálogo descriptivo.
                prompt_reintento = construir_prompt_reintento(
                    plan, dias, comidas, catalogo, motivo
                )
                respuesta_reintento = llamar_groq(
                    cliente, prompt_reintento, temperatura=0.20
                )
                plan = normalizar_plan(extraer_json(respuesta_reintento))
                valido, motivo = validar_plan_completo(
                    plan, dias, comidas, catalogo
                )
                if not valido:
                    raise ValueError(
                        f"La IA devolvió un plan incompleto: {motivo}"
                    )

            # =================================================
            # CALCULAR COMPRA REAL
            # =================================================

            compra, total, presupuesto_verificable, faltantes_precio = calcular_compra(
                plan,
                catalogo,
                personas,
            )

            # Los ajustes económicos solo son válidos cuando TODOS los
            # productos necesarios tienen precio público verificado.
            # Nunca se ajusta un presupuesto usando precios inventados.
            if not presupuesto_verificable:
                st.warning(
                    "El menú se generó, pero el presupuesto no puede considerarse "
                    "real/verificado porque faltan precios públicos de: "
                    + ", ".join(faltantes_precio)
                )

            # =================================================
            # SI EL COSTO ES DEMASIADO BAJO
            # =================================================

            if (
                presupuesto_verificable
                and total
                < presupuesto
                * MIN_UTILIZACION_PRESUPUESTO
                and presupuesto >= 500
            ):

                prompt_ajuste = construir_prompt_ajuste(
                    plan=plan,
                    compra=compra,
                    total=total,
                    presupuesto=presupuesto,
                    personas=personas,
                    catalogo=catalogo,
                    modo="subir",
                )

                respuesta_ajuste = llamar_groq(
                    cliente,
                    prompt_ajuste,
                    temperatura=0.35,
                )

                try:

                    plan_ajustado_raw = extraer_json(
                        respuesta_ajuste
                    )

                    plan_ajustado = normalizar_plan(
                        plan_ajustado_raw
                    )

                    valido_ajuste, _ = validar_plan_completo(
                        plan_ajustado, dias, comidas, catalogo
                    )

                    if valido_ajuste:

                        compra_ajustada, total_ajustado, verificable_ajustado, _ = calcular_compra(
                            plan_ajustado,
                            catalogo,
                            personas,
                        )

                        if (
                            verificable_ajustado
                            and total_ajustado
                            <= presupuesto
                            + TOLERANCIA_PRESUPUESTO
                        ):

                            plan = plan_ajustado

                            compra = compra_ajustada

                            total = total_ajustado

                except Exception:
                    pass

            # =================================================
            # SI SE PASA DEL LÍMITE
            # =================================================

            if (
                presupuesto_verificable
                and total
                > presupuesto
                + TOLERANCIA_PRESUPUESTO
            ):

                prompt_ajuste = construir_prompt_ajuste(
                    plan=plan,
                    compra=compra,
                    total=total,
                    presupuesto=presupuesto,
                    personas=personas,
                    catalogo=catalogo,
                    modo="bajar",
                )

                respuesta_ajuste = llamar_groq(
                    cliente,
                    prompt_ajuste,
                    temperatura=0.25,
                )

                try:

                    plan_ajustado_raw = extraer_json(
                        respuesta_ajuste
                    )

                    plan_ajustado = normalizar_plan(
                        plan_ajustado_raw
                    )

                    valido_ajuste, _ = validar_plan_completo(
                        plan_ajustado, dias, comidas, catalogo
                    )

                    if valido_ajuste:

                        compra_ajustada, total_ajustado, verificable_ajustado, _ = calcular_compra(
                            plan_ajustado,
                            catalogo,
                            personas,
                        )

                        if (
                            verificable_ajustado
                            and total_ajustado
                            <= presupuesto
                            + TOLERANCIA_PRESUPUESTO
                        ):

                            plan = plan_ajustado

                            compra = compra_ajustada

                            total = total_ajustado

                except Exception:
                    pass

            # =================================================
            # VALIDACIÓN FINAL
            # =================================================

            if (
                presupuesto_verificable
                and total
                > presupuesto
                + TOLERANCIA_PRESUPUESTO
            ):

                st.error(
                    "No fue posible ajustar el plan "
                    "al presupuesto permitido."
                )

                st.write(
                    f"Total calculado: "
                    f"${total:,.2f}"
                )

                st.write(
                    f"Límite permitido: "
                    f"${presupuesto + TOLERANCIA_PRESUPUESTO:,.2f}"
                )

                st.stop()

            # =================================================
            # GUARDAR EN SESIÓN
            # =================================================

            st.session_state["plan"] = plan

            st.session_state["compra"] = compra

            st.session_state["total"] = total

            st.session_state[
                "presupuesto"
            ] = presupuesto

            st.session_state[
                "personas"
            ] = personas

            st.session_state[
                "tiendas"
            ] = tiendas_seleccionadas

            st.session_state[
                "presupuesto_verificable"
            ] = presupuesto_verificable

            st.session_state[
                "precios_verificados"
            ] = precios_ok

            st.success(
                "Plan generado correctamente."
            )

        except Exception as e:

            st.error(
                f"Ocurrió un error al generar el plan: {e}"
            )

            st.stop()


# ============================================================
# MOSTRAR RESULTADO
# ============================================================

if "plan" in st.session_state:

    plan = st.session_state[
        "plan"
    ]

    compra = st.session_state[
        "compra"
    ]

    total = st.session_state[
        "total"
    ]

    presupuesto = st.session_state[
        "presupuesto"
    ]

    personas = st.session_state[
        "personas"
    ]

    tiendas = st.session_state[
        "tiendas"
    ]

    presupuesto_verificable = st.session_state.get(
        "presupuesto_verificable", True
    )

    precios_verificados = st.session_state.get(
        "precios_verificados", 0
    )

    st.divider()

    st.header(
        "📋 Tu plan"
    )

    # ========================================================
    # RESUMEN
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Presupuesto",
            f"${presupuesto:,.2f}",
        )

    with col2:

        st.metric(
            "Compra verificada" if presupuesto_verificable else "Total parcial",
            f"${total:,.2f}",
        )

    with col3:

        diferencia = (
            presupuesto - total
        )

        if diferencia >= 0:

            st.metric(
                "Disponible",
                f"${diferencia:,.2f}",
            )

        else:

            st.metric(
                "Excedente",
                f"${abs(diferencia):,.2f}",
            )

    # ========================================================
    # MENSAJE PRESUPUESTO
    # ========================================================

    if not presupuesto_verificable:
        st.warning(
            f"El total mostrado (${total:,.2f}) es PARCIAL. "
            "No se muestran precios inventados: los productos sin precio público "
            "verificado aparecen como PRECIO NO DISPONIBLE."
        )
    elif total <= presupuesto:

        st.success(
            f"La compra está dentro del presupuesto. "
            f"Quedan ${presupuesto - total:,.2f}."
        )

    elif (
        total
        <= presupuesto
        + TOLERANCIA_PRESUPUESTO
    ):

        st.warning(
            f"Se utilizaron "
            f"${total - presupuesto:,.2f} "
            f"de la tolerancia permitida."
        )

    # ========================================================
    # MENÚ
    # ========================================================

    st.header(
        "🍽️ Menú"
    )

    catalogo_global = []

    for lista in CATALOGOS.values():

        catalogo_global.extend(
            lista
        )

    productos_por_id = {
        p["id"]: p
        for p in catalogo_global
    }

    for dia in plan.get(
        "dias",
        [],
    ):

        st.subheader(
            f"Día {dia.get('dia', '')}"
        )

        for comida in dia.get(
            "comidas",
            [],
        ):

            st.markdown(
                f"### "
                f"{comida.get('tipo', 'Comida')}: "
                f"{comida.get('nombre', '')}"
            )

            st.markdown(
                "**Ingredientes:**"
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

                p = productos_por_id.get(
                    producto_id
                )

                if p:

                    nombre = p[
                        "nombre"
                    ]

                else:

                    nombre = str(
                        producto_id
                    )

                st.write(
                    f"- {nombre}: "
                    f"{cantidad} "
                    f"{unidad} "
                    f"por persona"
                )

            st.markdown(
                "**Preparación:**"
            )

            pasos = comida.get(
                "preparacion",
                [],
            )

            if not pasos:

                pasos = [
                    "Preparar los ingredientes "
                    "y cocinar completamente."
                ]

            for numero, paso in enumerate(
                pasos,
                1,
            ):

                st.write(
                    f"{numero}. {paso}"
                )

            st.divider()

    # ========================================================
    # LISTA DE COMPRA
    # ========================================================

    st.header(
        "🛒 Lista de compra"
    )

    datos_tabla = []

    for item in compra:

        datos_tabla.append(
            {
                "Producto": item[
                    "producto"
                ],
                "Presentación": item[
                    "presentacion"
                ],
                "Cantidad": item[
                    "paquetes"
                ],
                "Precio unitario": item.get(
                    "precio_texto", PRECIO_NO_DISPONIBLE
                ),
                "Total": item.get(
                    "subtotal_texto", PRECIO_NO_DISPONIBLE
                ),
                "Tienda": item[
                    "tienda"
                ],
            }
        )

    if datos_tabla:

        st.dataframe(
            datos_tabla,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader(
        f"💰 {'Total verificado' if presupuesto_verificable else 'Total parcial'}: ${total:,.2f} MXN"
    )

    # ========================================================
    # PDF
    # ========================================================

    pdf_bytes = generar_pdf(
        plan=plan,
        compra=compra,
        total=total,
        presupuesto=presupuesto,
        personas=personas,
        tiendas=tiendas,
    )

    st.download_button(
        label="📄 Descargar plan completo en PDF",
        data=pdf_bytes,
        file_name="KashCook_AI_Plan.pdf",
        mime="application/pdf",
        use_container_width=True,
