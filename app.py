import io
import json
import math
import re
import html
import requests
import streamlit as st

from bs4 import BeautifulSoup
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
    KeepTogether,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="KashCook AI",
    page_icon="🍳",
    layout="wide"
)

TIENDAS_DISPONIBLES = [
    "Alsuper",
    "Walmart",
    "Soriana",
    "Bodega Aurrerá"
]

TOLERANCIA_PRESUPUESTO = 100.00

# El sistema intentará utilizar al menos este porcentaje
# del presupuesto cuando sea razonablemente posible.
MIN_UTILIZACION_PRESUPUESTO = 0.90


# ============================================================
# CATÁLOGOS
#
# IMPORTANTE:
# precio = precio de UNA presentación
# contenido = cantidad contenida en esa presentación
# unidad_contenido = g, kg, ml, pieza, lata, etc.
# ============================================================

PRODUCTOS_ALSUPER = [

    # ---------------- PROTEÍNAS ----------------

    {
        "id": "alsuper_pollo_caderita",
        "tienda": "Alsuper",
        "nombre": "Caderita de pollo",
        "categoria": "pollo",
        "ingrediente_base": "pollo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 44.90,
        "url": "https://alsuper.com/producto/caderita-de-pollo-44400"
    },

    {
        "id": "alsuper_pollo_alas",
        "tienda": "Alsuper",
        "nombre": "Alas de pollo",
        "categoria": "pollo",
        "ingrediente_base": "pollo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 114.90,
        "url": "https://alsuper.com/producto/ala-pollo-352077"
    },

    {
        "id": "alsuper_res_puchero",
        "tienda": "Alsuper",
        "nombre": "Carne de res para puchero",
        "categoria": "res",
        "ingrediente_base": "res",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 259.90,
        "url": "https://alsuper.com/producto/puchero-res-14038"
    },

    {
        "id": "alsuper_res_jugo",
        "tienda": "Alsuper",
        "nombre": "Carne de res para jugo",
        "categoria": "res",
        "ingrediente_base": "res",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 319.90,
        "url": "https://alsuper.com/producto/carne-para-jugo-421810"
    },

    {
        "id": "alsuper_res_sabana",
        "tienda": "Alsuper",
        "nombre": "Sábana de res",
        "categoria": "res",
        "ingrediente_base": "res",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 169.90,
        "url": "https://alsuper.com/producto/sabana-497606"
    },

    {
        "id": "alsuper_cerdo_filete",
        "tienda": "Alsuper",
        "nombre": "Filete de cerdo",
        "categoria": "cerdo",
        "ingrediente_base": "cerdo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 154.90,
        "url": "https://alsuper.com/producto/filete-cerdo-371873"
    },

    {
        "id": "alsuper_cerdo_molida",
        "tienda": "Alsuper",
        "nombre": "Carne molida de puerco",
        "categoria": "cerdo",
        "ingrediente_base": "cerdo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 114.90,
        "url": "https://alsuper.com/producto/molida-puerco-13817"
    },

    {
        "id": "alsuper_cerdo_milanesa",
        "tienda": "Alsuper",
        "nombre": "Milanesa de puerco",
        "categoria": "cerdo",
        "ingrediente_base": "cerdo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 114.90,
        "url": "https://alsuper.com/producto/milanesa-puerco-3405"
    },

    {
        "id": "alsuper_pescado",
        "tienda": "Alsuper",
        "nombre": "Pescado rodajeado",
        "categoria": "pescado",
        "ingrediente_base": "pescado",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 84.90,
        "url": "https://alsuper.com/producto/pescado-rodajeado-391892"
    },

    {
        "id": "alsuper_basa",
        "tienda": "Alsuper",
        "nombre": "Bagre basa",
        "categoria": "pescado",
        "ingrediente_base": "pescado",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 84.90,
        "url": "https://alsuper.com/producto/bagre-basa-3834"
    },

    {
        "id": "alsuper_atun_eldorado",
        "tienda": "Alsuper",
        "nombre": "Atún El Dorado en agua",
        "categoria": "atun",
        "ingrediente_base": "atun",
        "presentacion": "lata",
        "contenido": 130,
        "unidad_contenido": "g",
        "precio": 12.90,
        "url": "https://alsuper.com/producto/atun-449782"
    },

    {
        "id": "alsuper_atun_mazatun",
        "tienda": "Alsuper",
        "nombre": "Atún Mazatún en agua",
        "categoria": "atun",
        "ingrediente_base": "atun",
        "presentacion": "lata",
        "contenido": 130,
        "unidad_contenido": "g",
        "precio": 18.90,
        "url": "https://alsuper.com/producto/atun-446574"
    },

    # ---------------- HUEVO ----------------

    {
        "id": "alsuper_huevo_30_huizache",
        "tienda": "Alsuper",
        "nombre": "Huevo Huizache",
        "categoria": "huevo",
        "ingrediente_base": "huevo",
        "presentacion": "charola",
        "contenido": 30,
        "unidad_contenido": "pieza",
        "precio": 66.90,
        "url": "https://alsuper.com/producto/huevo-huizache-30-394553"
    },

    {
        "id": "alsuper_huevo_30_sanjuan",
        "tienda": "Alsuper",
        "nombre": "Huevo San Juan",
        "categoria": "huevo",
        "ingrediente_base": "huevo",
        "presentacion": "charola",
        "contenido": 30,
        "unidad_contenido": "pieza",
        "precio": 74.90,
        "url": "https://alsuper.com/producto/huevo-san-juan-30-323673"
    },

    {
        "id": "alsuper_huevo_12",
        "tienda": "Alsuper",
        "nombre": "Huevo Huizache",
        "categoria": "huevo",
        "ingrediente_base": "huevo",
        "presentacion": "cartón",
        "contenido": 12,
        "unidad_contenido": "pieza",
        "precio": 29.90,
        "url": "https://alsuper.com/producto/huevo-12-399988"
    },

    # ---------------- BÁSICOS ----------------

    {
        "id": "alsuper_arroz_907",
        "tienda": "Alsuper",
        "nombre": "Arroz Cazerola",
        "categoria": "arroz",
        "ingrediente_base": "arroz",
        "presentacion": "bolsa",
        "contenido": 907,
        "unidad_contenido": "g",
        "precio": 22.90,
        "url": "https://alsuper.com/producto/arroz-379848"
    },

    {
        "id": "alsuper_frijol_1kg",
        "tienda": "Alsuper",
        "nombre": "Frijol Pinto Alsuper",
        "categoria": "frijol",
        "ingrediente_base": "frijol",
        "presentacion": "bolsa",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 24.90,
        "url": "https://alsuper.com/producto/frijol-pinto-409"
    },

    {
        "id": "alsuper_tortilla_1kg",
        "tienda": "Alsuper",
        "nombre": "Tortilla de maíz",
        "categoria": "tortilla",
        "ingrediente_base": "tortilla",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 25.90,
        "url": "https://alsuper.com/producto/tortilla-380477"
    },

    # ---------------- VERDURAS ----------------

    {
        "id": "alsuper_papa",
        "tienda": "Alsuper",
        "nombre": "Papa morena",
        "categoria": "verdura",
        "ingrediente_base": "papa",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 13.90,
        "url": "https://alsuper.com/producto/papa-morena-6"
    },

    {
        "id": "alsuper_tomate",
        "tienda": "Alsuper",
        "nombre": "Tomate saladet",
        "categoria": "verdura",
        "ingrediente_base": "tomate",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 29.90,
        "url": "https://alsuper.com/producto/tomate-saladet-98"
    },

    {
        "id": "alsuper_cebolla",
        "tienda": "Alsuper",
        "nombre": "Cebolla",
        "categoria": "verdura",
        "ingrediente_base": "cebolla",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 49.90,
        "url": "https://alsuper.com/producto/cebolla-924"
    },

    {
        "id": "alsuper_tomatillo",
        "tienda": "Alsuper",
        "nombre": "Tomatillo",
        "categoria": "verdura",
        "ingrediente_base": "tomatillo",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 39.90,
        "url": "https://alsuper.com/producto/tomatillo-65"
    },

    {
        "id": "alsuper_brocoli",
        "tienda": "Alsuper",
        "nombre": "Brócoli",
        "categoria": "verdura",
        "ingrediente_base": "brocoli",
        "presentacion": "pieza",
        "contenido": 1,
        "unidad_contenido": "pieza",
        "precio": 44.90,
        "url": "https://alsuper.com/producto/brocoli-71"
    },

    # ---------------- QUESO ----------------

    {
        "id": "alsuper_queso_panela",
        "tienda": "Alsuper",
        "nombre": "Queso panela",
        "categoria": "queso",
        "ingrediente_base": "queso",
        "presentacion": "pieza",
        "contenido": 400,
        "unidad_contenido": "g",
        "precio": 124.90,
        "url": "https://alsuper.com/producto/queso-panela-402102"
    },
]


PRODUCTOS_WALMART = [

    {
        "id": "walmart_pollo",
        "tienda": "Walmart",
        "nombre": "Pollo",
        "categoria": "pollo",
        "ingrediente_base": "pollo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 67.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_res",
        "tienda": "Walmart",
        "nombre": "Carne de res",
        "categoria": "res",
        "ingrediente_base": "res",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 180.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_cerdo",
        "tienda": "Walmart",
        "nombre": "Carne de cerdo",
        "categoria": "cerdo",
        "ingrediente_base": "cerdo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 130.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_pescado",
        "tienda": "Walmart",
        "nombre": "Filete de pescado",
        "categoria": "pescado",
        "ingrediente_base": "pescado",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 120.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_huevo",
        "tienda": "Walmart",
        "nombre": "Huevo",
        "categoria": "huevo",
        "ingrediente_base": "huevo",
        "presentacion": "cartón",
        "contenido": 30,
        "unidad_contenido": "pieza",
        "precio": 75.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_arroz",
        "tienda": "Walmart",
        "nombre": "Arroz Great Value",
        "categoria": "arroz",
        "ingrediente_base": "arroz",
        "presentacion": "bolsa",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 15.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_frijol",
        "tienda": "Walmart",
        "nombre": "Frijol Pinto Great Value",
        "categoria": "frijol",
        "ingrediente_base": "frijol",
        "presentacion": "bolsa",
        "contenido": 900,
        "unidad_contenido": "g",
        "precio": 25.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_atun",
        "tienda": "Walmart",
        "nombre": "Atún Great Value en agua",
        "categoria": "atun",
        "ingrediente_base": "atun",
        "presentacion": "lata",
        "contenido": 140,
        "unidad_contenido": "g",
        "precio": 17.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_tortilla",
        "tienda": "Walmart",
        "nombre": "Tortilla de maíz",
        "categoria": "tortilla",
        "ingrediente_base": "tortilla",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 25.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_papa",
        "tienda": "Walmart",
        "nombre": "Papa",
        "categoria": "verdura",
        "ingrediente_base": "papa",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 25.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_tomate",
        "tienda": "Walmart",
        "nombre": "Tomate",
        "categoria": "verdura",
        "ingrediente_base": "tomate",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 35.00,
        "url": "https://www.walmart.com.mx/"
    },

    {
        "id": "walmart_cebolla",
        "tienda": "Walmart",
        "nombre": "Cebolla",
        "categoria": "verdura",
        "ingrediente_base": "cebolla",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 35.00,
        "url": "https://www.walmart.com.mx/"
    },
]


PRODUCTOS_SORIANA = [

    {
        "id": "soriana_pollo",
        "tienda": "Soriana",
        "nombre": "Pollo",
        "categoria": "pollo",
        "ingrediente_base": "pollo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 70.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_res",
        "tienda": "Soriana",
        "nombre": "Carne de res",
        "categoria": "res",
        "ingrediente_base": "res",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 190.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_cerdo",
        "tienda": "Soriana",
        "nombre": "Carne de cerdo",
        "categoria": "cerdo",
        "ingrediente_base": "cerdo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 135.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_pescado",
        "tienda": "Soriana",
        "nombre": "Filete de pescado",
        "categoria": "pescado",
        "ingrediente_base": "pescado",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 125.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_huevo",
        "tienda": "Soriana",
        "nombre": "Huevo",
        "categoria": "huevo",
        "ingrediente_base": "huevo",
        "presentacion": "cartón",
        "contenido": 30,
        "unidad_contenido": "pieza",
        "precio": 78.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_arroz",
        "tienda": "Soriana",
        "nombre": "Arroz",
        "categoria": "arroz",
        "ingrediente_base": "arroz",
        "presentacion": "bolsa",
        "contenido": 900,
        "unidad_contenido": "g",
        "precio": 12.90,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_frijol",
        "tienda": "Soriana",
        "nombre": "Frijol",
        "categoria": "frijol",
        "ingrediente_base": "frijol",
        "presentacion": "bolsa",
        "contenido": 900,
        "unidad_contenido": "g",
        "precio": 25.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_atun",
        "tienda": "Soriana",
        "nombre": "Atún Dolores en agua",
        "categoria": "atun",
        "ingrediente_base": "atun",
        "presentacion": "lata",
        "contenido": 140,
        "unidad_contenido": "g",
        "precio": 21.50,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_tortilla",
        "tienda": "Soriana",
        "nombre": "Tortilla de maíz",
        "categoria": "tortilla",
        "ingrediente_base": "tortilla",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 26.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_papa",
        "tienda": "Soriana",
        "nombre": "Papa",
        "categoria": "verdura",
        "ingrediente_base": "papa",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 25.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_tomate",
        "tienda": "Soriana",
        "nombre": "Tomate",
        "categoria": "verdura",
        "ingrediente_base": "tomate",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 35.00,
        "url": "https://www.soriana.com/"
    },

    {
        "id": "soriana_cebolla",
        "tienda": "Soriana",
        "nombre": "Cebolla",
        "categoria": "verdura",
        "ingrediente_base": "cebolla",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 35.00,
        "url": "https://www.soriana.com/"
    },
]


PRODUCTOS_AURRERA = [

    {
        "id": "aurrera_pollo",
        "tienda": "Bodega Aurrerá",
        "nombre": "Pollo",
        "categoria": "pollo",
        "ingrediente_base": "pollo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 67.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_res",
        "tienda": "Bodega Aurrerá",
        "nombre": "Carne de res",
        "categoria": "res",
        "ingrediente_base": "res",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 180.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_cerdo",
        "tienda": "Bodega Aurrerá",
        "nombre": "Carne de cerdo",
        "categoria": "cerdo",
        "ingrediente_base": "cerdo",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 130.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_pescado",
        "tienda": "Bodega Aurrerá",
        "nombre": "Filete de pescado",
        "categoria": "pescado",
        "ingrediente_base": "pescado",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 120.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_huevo",
        "tienda": "Bodega Aurrerá",
        "nombre": "Huevo Aurrera",
        "categoria": "huevo",
        "ingrediente_base": "huevo",
        "presentacion": "charola",
        "contenido": 30,
        "unidad_contenido": "pieza",
        "precio": 70.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_arroz",
        "tienda": "Bodega Aurrerá",
        "nombre": "Arroz Aurrera",
        "categoria": "arroz",
        "ingrediente_base": "arroz",
        "presentacion": "bolsa",
        "contenido": 900,
        "unidad_contenido": "g",
        "precio": 14.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_frijol",
        "tienda": "Bodega Aurrerá",
        "nombre": "Frijol",
        "categoria": "frijol",
        "ingrediente_base": "frijol",
        "presentacion": "bolsa",
        "contenido": 900,
        "unidad_contenido": "g",
        "precio": 25.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_atun",
        "tienda": "Bodega Aurrerá",
        "nombre": "Atún Aurrera en agua",
        "categoria": "atun",
        "ingrediente_base": "atun",
        "presentacion": "lata",
        "contenido": 130,
        "unidad_contenido": "g",
        "precio": 10.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_sardinas",
        "tienda": "Bodega Aurrerá",
        "nombre": "Sardinas Guaymex",
        "categoria": "sardinas",
        "ingrediente_base": "sardinas",
        "presentacion": "lata",
        "contenido": 425,
        "unidad_contenido": "g",
        "precio": 47.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_tortilla",
        "tienda": "Bodega Aurrerá",
        "nombre": "Tortilla de maíz",
        "categoria": "tortilla",
        "ingrediente_base": "tortilla",
        "presentacion": "paquete",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 25.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_papa",
        "tienda": "Bodega Aurrerá",
        "nombre": "Papa",
        "categoria": "verdura",
        "ingrediente_base": "papa",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 25.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_tomate",
        "tienda": "Bodega Aurrerá",
        "nombre": "Tomate",
        "categoria": "verdura",
        "ingrediente_base": "tomate",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 35.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },

    {
        "id": "aurrera_cebolla",
        "tienda": "Bodega Aurrerá",
        "nombre": "Cebolla",
        "categoria": "verdura",
        "ingrediente_base": "cebolla",
        "presentacion": "kilogramo",
        "contenido": 1000,
        "unidad_contenido": "g",
        "precio": 35.00,
        "url": "https://www.bodegaaurrera.com.mx/"
    },
]


# ============================================================
# CATÁLOGO
# ============================================================

CATALOGOS = {
    "Alsuper": PRODUCTOS_ALSUPER,
    "Walmart": PRODUCTOS_WALMART,
    "Soriana": PRODUCTOS_SORIANA,
    "Bodega Aurrerá": PRODUCTOS_AURRERA,
}


def crear_catalogo_tienda(tiendas):
    catalogo = []

    for tienda in tiendas:
        catalogo.extend(CATALOGOS.get(tienda, []))

    # Eliminar duplicados
    resultado = {}
    for producto in catalogo:
        resultado[producto["id"]] = producto

    return list(resultado.values())


# ============================================================
# UTILIDADES
# ============================================================

def numero_seguro(valor, default=0.0):
    try:
        if valor is None:
            return default

        if isinstance(valor, str):
            valor = valor.replace("$", "").replace(",", "").strip()

        return float(valor)
    except Exception:
        return default


def entero_seguro(valor, default=0):
    try:
        return int(float(valor))
    except Exception:
        return default


def limpiar_texto(valor):
    if valor is None:
        return ""

    return str(valor).strip()


def escapar_pdf(texto):
    return html.escape(str(texto))


# ============================================================
# GROQ
# ============================================================

def obtener_cliente_groq():
    api_key = None

    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        pass

    if not api_key:
        api_key = st.session_state.get("groq_api_key")

    if not api_key:
        api_key = st.text_input(
            "🔑 Ingresa tu GROQ API Key",
            type="password"
        )

        if api_key:
            st.session_state["groq_api_key"] = api_key

    if not api_key:
        return None

    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"No se pudo inicializar Groq: {e}")
        return None


def llamar_groq(cliente, prompt, temperatura=0.4):
    respuesta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres KashCook AI, un planificador experto de alimentación "
                    "familiar, compras y presupuesto. "
                    "Debes responder exclusivamente con JSON válido cuando se solicite."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperatura,
        max_tokens=16000
    )

    return respuesta.choices[0].message.content


def extraer_json(texto):
    if not texto:
        raise ValueError("Groq no devolvió contenido.")

    texto = texto.strip()

    texto = re.sub(
        r"^```(?:json)?",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = re.sub(
        r"```$",
        "",
        texto
    )

    texto = texto.strip()

    # Intento directo
    try:
        return json.loads(texto)
    except Exception:
        pass

    # Buscar objeto JSON
    inicio = texto.find("{")
    fin = texto.rfind("}")

    if inicio != -1 and fin != -1 and fin > inicio:
        bloque = texto[inicio:fin + 1]

        try:
            return json.loads(bloque)
        except Exception:
            pass

    raise ValueError("No se pudo interpretar el JSON generado por Groq.")


# ============================================================
# VALIDACIÓN DEL CATÁLOGO
# ============================================================

def producto_por_id(catalogo):
    return {
        producto["id"]: producto
        for producto in catalogo
    }


# ============================================================
# CÁLCULO REAL DE COMPRAS
#
# Groq indica:
#
# cantidad_por_persona
# unidad
#
# Python:
#
# cantidad_total = cantidad_por_persona * personas
#
# y después:
#
# paquetes = ceil(cantidad_total / contenido_presentacion)
# ============================================================

def normalizar_unidad(unidad):
    unidad = limpiar_texto(unidad).lower()

    equivalencias = {
        "gramos": "g",
        "gramo": "g",
        "gr": "g",
        "kgs": "kg",
        "kilogramos": "kg",
        "kilogramo": "kg",
        "litros": "l",
        "litro": "l",
        "mililitros": "ml",
        "mililitro": "ml",
        "piezas": "pieza",
        "unidad": "pieza",
        "unidades": "pieza",
        "latas": "lata",
        "lata": "lata",
    }

    return equivalencias.get(unidad, unidad)


def convertir_a_gramos(cantidad, unidad):
    unidad = normalizar_unidad(unidad)

    if unidad == "kg":
        return cantidad * 1000

    if unidad == "g":
        return cantidad

    return None


def calcular_compra(plan, catalogo, personas):
    mapa_productos = producto_por_id(catalogo)

    demanda = {}

    for dia in plan.get("dias", []):
        for comida in dia.get("comidas", []):

            ingredientes = comida.get("ingredientes", [])

            for ingrediente in ingredientes:

                producto_id = limpiar_texto(
                    ingrediente.get("producto_id")
                )

                if not producto_id:
                    continue

                if producto_id not in mapa_productos:
                    continue

                producto = mapa_productos[producto_id]

                cantidad_por_persona = numero_seguro(
                    ingrediente.get("cantidad_por_persona"),
                    0
                )

                unidad = normalizar_unidad(
                    ingrediente.get("unidad", "")
                )

                if cantidad_por_persona <= 0:
                    continue

                cantidad_total = cantidad_por_persona * personas

                # -----------------------------------------
                # Caso gramos / kg
                # -----------------------------------------

                cantidad_g = convertir_a_gramos(
                    cantidad_total,
                    unidad
                )

                contenido_g = convertir_a_gramos(
                    numero_seguro(producto["contenido"]),
                    producto["unidad_contenido"]
                )

                if cantidad_g is not None and contenido_g is not None:

                    if contenido_g <= 0:
                        continue

                    cantidad_presentaciones = math.ceil(
                        cantidad_g / contenido_g
                    )

                    comprado_g = (
                        cantidad_presentaciones *
                        contenido_g
                    )

                    sobrante_g = max(
                        0,
                        comprado_g - cantidad_g
                    )

                    clave = producto_id

                    if clave not in demanda:
                        demanda[clave] = {
                            "producto_id": producto_id,
                            "producto": producto["nombre"],
                            "tienda": producto["tienda"],
                            "presentacion": producto["presentacion"],
                            "contenido": producto["contenido"],
                            "unidad_contenido": producto["unidad_contenido"],
                            "precio_unitario": producto["precio"],
                            "cantidad_necesaria": 0,
                            "unidad_necesaria": "g",
                            "cantidad_comprar": 0,
                            "sobrante": 0,
                            "total": 0,
                        }

                    # Acumulamos demanda, pero las presentaciones
                    # se redondean AL FINAL.
                    demanda[clave]["cantidad_necesaria"] += cantidad_g

                # -----------------------------------------
                # Caso piezas
                # -----------------------------------------

                elif unidad == "pieza":

                    contenido = numero_seguro(
                        producto["contenido"]
                    )

                    if contenido <= 0:
                        continue

                    cantidad_presentaciones = math.ceil(
                        cantidad_total / contenido
                    )

                    clave = producto_id

                    if clave not in demanda:
                        demanda[clave] = {
                            "producto_id": producto_id,
                            "producto": producto["nombre"],
                            "tienda": producto["tienda"],
                            "presentacion": producto["presentacion"],
                            "contenido": producto["contenido"],
                            "unidad_contenido": producto["unidad_contenido"],
                            "precio_unitario": producto["precio"],
                            "cantidad_necesaria": 0,
                            "unidad_necesaria": "pieza",
                            "cantidad_comprar": 0,
                            "sobrante": 0,
                            "total": 0,
                        }

                    demanda[clave]["cantidad_necesaria"] += cantidad_total

    # ========================================================
    # Redondeo FINAL de presentaciones
    # ========================================================

    compra = []

    for producto_id, item in demanda.items():

        producto = mapa_productos[producto_id]

        contenido = numero_seguro(
            producto["contenido"]
        )

        unidad_producto = normalizar_unidad(
            producto["unidad_contenido"]
        )

        if item["unidad_necesaria"] == "g":

            contenido_g = convertir_a_gramos(
                contenido,
                unidad_producto
            )

            if not contenido_g:
                continue

            cantidad_comprar = math.ceil(
                item["cantidad_necesaria"] / contenido_g
            )

            comprado = cantidad_comprar * contenido_g

            item["cantidad_comprar"] = cantidad_comprar
            item["sobrante"] = max(
                0,
                comprado - item["cantidad_necesaria"]
            )

        else:

            cantidad_comprar = math.ceil(
                item["cantidad_necesaria"] / contenido
            )

            comprado = cantidad_comprar * contenido

            item["cantidad_comprar"] = cantidad_comprar
            item["sobrante"] = max(
                0,
                comprado - item["cantidad_necesaria"]
            )

        item["total"] = (
            item["cantidad_comprar"] *
            item["precio_unitario"]
        )

        compra.append(item)

    total = sum(
        item["total"]
        for item in compra
    )

    return compra, round(total, 2)


# ============================================================
# VALIDACIÓN DE CANTIDADES
# ============================================================

def validar_proteinas(plan, personas):
    proteinas = []

    for dia in plan.get("dias", []):
        for comida in dia.get("comidas", []):

            categoria = limpiar_texto(
                comida.get("categoria_proteina", "")
            ).lower()

            if categoria:
                proteinas.append(categoria)

    return proteinas


def contar_comidas(plan):
    total = 0

    for dia in plan.get("dias", []):
        total += len(dia.get("comidas", []))

    return total


# ============================================================
# PROMPT PRINCIPAL
# ============================================================

def construir_prompt(
    personas,
    dias,
    presupuesto,
    estilos,
    comidas,
    restricciones,
    electrodomesticos,
    catalogo
):

    catalogo_resumido = []

    for p in catalogo:
        catalogo_resumido.append({
            "id": p["id"],
            "producto": p["nombre"],
            "tienda": p["tienda"],
            "categoria": p["categoria"],
            "ingrediente_base": p["ingrediente_base"],
            "presentacion": p["presentacion"],
            "contenido": p["contenido"],
            "unidad_contenido": p["unidad_contenido"],
            "precio": p["precio"]
        })

    catalogo_json = json.dumps(
        catalogo_resumido,
        ensure_ascii=False,
        indent=2
    )

    return f"""
Eres el cerebro culinario de KashCook AI.

Necesito crear un plan de alimentación para:

PERSONAS: {personas}
DÍAS: {dias}
PRESUPUESTO OBJETIVO: ${presupuesto:.2f} MXN
PRESUPUESTO MÁXIMO ABSOLUTO: ${presupuesto + TOLERANCIA_PRESUPUESTO:.2f} MXN

ESTILOS:
{json.dumps(estilos, ensure_ascii=False)}

COMIDAS:
{json.dumps(comidas, ensure_ascii=False)}

RESTRICCIONES / ALERGIAS:
{restricciones}

ELECTRODOMÉSTICOS:
{json.dumps(electrodomesticos, ensure_ascii=False)}

============================================================
REGLAS CRÍTICAS
============================================================

1. El plan es para TODAS las personas indicadas.

2. No hagas recetas para 1 persona y después pretendas
   que alcance para todos.

3. Las cantidades de ingredientes deben ser POR PERSONA.

4. KashCook multiplicará automáticamente esas cantidades
   por el número real de personas.

5. NO determines cuántos paquetes comprar.
   Python hará ese cálculo usando la presentación real.

6. Para proteínas principales utiliza normalmente entre
   150 y 220 g crudos por persona por comida, dependiendo
   del plato.

7. Para pescado utiliza aproximadamente 160-220 g por persona.

8. Para carne molida utiliza aproximadamente 150-200 g
   por persona.

9. Para pollo con hueso puedes utilizar aproximadamente
   250-350 g por persona debido al hueso.

10. Para atún considera aproximadamente 1 lata de 130-140 g
    por persona cuando sea plato principal.

11. Para sardinas considera aproximadamente 180-250 g
    por persona cuando sea plato principal.

12. Para huevo:
    - desayuno normal: 2-3 piezas por persona
    - plato principal: 2-3 piezas por persona

13. Arroz seco:
    aproximadamente 70-100 g por persona como guarnición.
    Si es plato principal puede llegar a 100-120 g.

14. Frijol seco:
    aproximadamente 60-90 g por persona como guarnición.

15. Tortillas:
    aproximadamente 3-5 piezas por persona dependiendo
    del platillo. Como el catálogo trabaja por gramos,
    estima aproximadamente 25 g por tortilla.

16. Verduras:
    utiliza cantidades suficientes para que las comidas
    sean completas. No pongas cantidades ridículamente bajas.

17. NO diseñes un menú cuyo costo sea artificialmente bajo
    solamente para ahorrar presupuesto.

18. El presupuesto es un objetivo de alimentación, no una
    excusa para comprar cantidades insuficientes.

19. Intenta que el costo final calculado por Python quede
    aproximadamente entre 90% y 100% del presupuesto.

20. Si el presupuesto es alto para la cantidad de personas
    y días, mejora la calidad, variedad y cantidad razonable
    de alimentos en lugar de inventar gastos.

21. Si el presupuesto es bajo, prioriza alimentos nutritivos,
    económicos y rendidores.

22. NUNCA excedas el presupuesto máximo absoluto:
    ${presupuesto + TOLERANCIA_PRESUPUESTO:.2f}

23. Debes utilizar ÚNICAMENTE productos del catálogo
    proporcionado.

24. El usuario ya eligió las tiendas.
    NO compares precios entre tiendas.

25. Si hay varias tiendas seleccionadas, puedes utilizar
    productos de cualquiera de ellas.

26. NO digas "cómpralo donde sea más barato".

27. Debes utilizar variedad de proteínas:
    pollo, res, cerdo, pescado, atún, sardinas, huevo,
    etc., siempre que el número de días lo permita.

28. Evita que todas las comidas tengan pollo.

29. No repitas exactamente el mismo platillo.

30. Respeta estrictamente alergias y restricciones.

31. Las recetas deben ser realistas y las cantidades deben
    corresponder al número de personas.

============================================================
CATÁLOGO DISPONIBLE
============================================================

{catalogo_json}

============================================================
FORMATO JSON OBLIGATORIO
============================================================

Devuelve EXCLUSIVAMENTE este formato:

{{
  "resumen": "breve explicación del plan",
  "dias": [
    {{
      "dia": 1,
      "comidas": [
        {{
          "tipo": "Desayuno",
          "nombre": "Nombre del platillo",
          "categoria_proteina": "huevo",
          "ingredientes": [
            {{
              "producto_id": "ID_EXACTO_DEL_CATALOGO",
              "cantidad_por_persona": 2,
              "unidad": "pieza",
              "uso": "huevos"
            }}
          ],
          "preparacion": [
            "Paso 1",
            "Paso 2",
            "Paso 3"
          ],
          "tiempo_minutos": 20
        }}
      ]
    }}
  ]
}}

IMPORTANTE:

- Cada comida debe tener ingredientes.
- Cada ingrediente debe usar un producto_id REAL del catálogo.
- cantidad_por_persona SIEMPRE es para UNA sola persona.
- No pongas cantidades de compra.
- No pongas precios.
- No pongas totales.
- No inventes productos.
- No inventes IDs.
- No agregues productos que no estén en el catálogo.

El JSON debe ser válido.
"""


# ============================================================
# AJUSTE POR PRESUPUESTO
# ============================================================

def construir_prompt_ajuste(
    plan,
    compra,
    total,
    personas,
    dias,
    presupuesto,
    catalogo,
    motivo
):

    objetivo_minimo = presupuesto * MIN_UTILIZACION_PRESUPUESTO
    maximo = presupuesto + TOLERANCIA_PRESUPUESTO

    if motivo == "BAJO":
        instruccion = f"""
El plan está dejando demasiado presupuesto sin utilizar.

Costo actual: ${total:.2f}
Presupuesto: ${presupuesto:.2f}
Objetivo mínimo aproximado: ${objetivo_minimo:.2f}

Debes mejorar el plan para aprovechar mejor el presupuesto,
SIN desperdiciar dinero y SIN agregar comidas innecesarias.

Puedes:
- aumentar razonablemente las porciones,
- mejorar variedad de proteínas,
- agregar verduras suficientes,
- mejorar desayunos,
- incluir fruta cuando exista en catálogo,
- utilizar mejores ingredientes disponibles,
- sustituir algunos platillos por opciones más completas.

NO puedes:
- agregar productos innecesarios,
- inventar productos,
- cambiar número de personas,
- cambiar número de días,
- exceder ${maximo:.2f}.

Las cantidades siguen siendo POR PERSONA.
"""

    else:

        instruccion = f"""
El plan excede el límite permitido.

Costo actual: ${total:.2f}
Presupuesto: ${presupuesto:.2f}
Máximo permitido: ${maximo:.2f}

Debes reducir el costo manteniendo:
- número de personas,
- número de días,
- número de comidas,
- cantidades nutricionalmente razonables.

Puedes cambiar productos por alternativas económicas
del catálogo y ajustar recetas.

NO reduzcas las porciones a cantidades absurdamente pequeñas.
"""

    catalogo_json = json.dumps(
        catalogo,
        ensure_ascii=False
    )

    plan_json = json.dumps(
        plan,
        ensure_ascii=False
    )

    return f"""
Eres KashCook AI y estás corrigiendo un plan de alimentación.

PERSONAS: {personas}
DÍAS: {dias}

{instruccion}

CATÁLOGO:
{catalogo_json}

PLAN ACTUAL:
{plan_json}

Devuelve exclusivamente el JSON completo del plan corregido,
usando exactamente la misma estructura:

{{
  "resumen": "...",
  "dias": [
    {{
      "dia": 1,
      "comidas": [
        {{
          "tipo": "Desayuno",
          "nombre": "...",
          "categoria_proteina": "...",
          "ingredientes": [
            {{
              "producto_id": "...",
              "cantidad_por_persona": 0,
              "unidad": "...",
              "uso": "..."
            }}
          ],
          "preparacion": [],
          "tiempo_minutos": 20
        }}
      ]
    }}
  ]
}}

No escribas explicaciones fuera del JSON.
"""


# ============================================================
# PDF
# ============================================================

def generar_pdf(
    plan,
    compra,
    total,
    presupuesto,
    personas,
    dias,
    tiendas
):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=1.3 * cm,
        leftMargin=1.3 * cm,
        topMargin=1.3 * cm,
        bottomMargin=1.3 * cm
    )

    styles = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=12
    )

    subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=8
    )

    normal = ParagraphStyle(
        "NormalKash",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        spaceAfter=5
    )

    pequeno = ParagraphStyle(
        "Pequeno",
        parent=styles["BodyText"],
        fontSize=7.5,
        leading=9.5
    )

    story = []

    story.append(
        Paragraph(
            "🍳 KASHCOOK AI",
            titulo
        )
    )

    story.append(
        Paragraph(
            "Plan de alimentación y compras",
            subtitulo
        )
    )

    story.append(
        Paragraph(
            f"<b>Personas:</b> {personas} &nbsp;&nbsp; "
            f"<b>Días:</b> {dias} &nbsp;&nbsp; "
            f"<b>Presupuesto:</b> ${presupuesto:,.2f}",
            normal
        )
    )

    story.append(
        Paragraph(
            f"<b>Tiendas seleccionadas:</b> "
            f"{', '.join(tiendas)}",
            normal
        )
    )

    story.append(Spacer(1, 8))

    # ========================================================
    # MENÚ
    # ========================================================

    story.append(
        Paragraph(
            "MENÚ",
            subtitulo
        )
    )

    for dia in plan.get("dias", []):

        story.append(
            Paragraph(
                f"DÍA {dia.get('dia', '')}",
                subtitulo
            )
        )

        for comida in dia.get("comidas", []):

            story.append(
                Paragraph(
                    f"<b>{escapar_pdf(comida.get('tipo', ''))}: "
                    f"{escapar_pdf(comida.get('nombre', ''))}</b>",
                    normal
                )
            )

            categoria = comida.get(
                "categoria_proteina",
                ""
            )

            if categoria:
                story.append(
                    Paragraph(
                        f"Proteína: {escapar_pdf(categoria)}",
                        pequeno
                    )
                )

            story.append(
                Paragraph(
                    "<b>Ingredientes por persona:</b>",
                    pequeno
                )
            )

            ingredientes_texto = []

            for ing in comida.get("ingredientes", []):

                cantidad = numero_seguro(
                    ing.get("cantidad_por_persona"),
                    0
                )

                unidad = ing.get("unidad", "")

                uso = ing.get("uso", "")

                ingredientes_texto.append(
                    f"• {escapar_pdf(uso)}: "
                    f"{cantidad:g} {escapar_pdf(unidad)}"
                )

            for texto in ingredientes_texto:
                story.append(
                    Paragraph(
                        texto,
                        pequeno
                    )
                )

            story.append(
                Paragraph(
                    "<b>Preparación:</b>",
                    pequeno
                )
            )

            for i, paso in enumerate(
                comida.get("preparacion", []),
                1
            ):
                story.append(
                    Paragraph(
                        f"{i}. {escapar_pdf(paso)}",
                        pequeno
                    )
                )

            tiempo = comida.get(
                "tiempo_minutos",
                ""
            )

            if tiempo:
                story.append(
                    Paragraph(
                        f"Tiempo aproximado: {tiempo} minutos",
                        pequeno
                    )
                )

            story.append(Spacer(1, 7))

    story.append(PageBreak())

    # ========================================================
    # LISTA DE COMPRAS
    # ========================================================

    story.append(
        Paragraph(
            "LISTA DE COMPRAS",
            subtitulo
        )
    )

    datos = [
        [
            "Producto",
            "Presentación",
            "Cantidad",
            "Precio",
            "Total",
            "Tienda"
        ]
    ]

    for item in compra:

        cantidad = item["cantidad_comprar"]

        datos.append([
            Paragraph(
                escapar_pdf(item["producto"]),
                pequeno
            ),
            Paragraph(
                f"{cantidad} × "
                f"{escapar_pdf(str(item['contenido']))} "
                f"{escapar_pdf(item['unidad_contenido'])}",
                pequeno
            ),
            Paragraph(
                f"{cantidad}",
                pequeno
            ),
            Paragraph(
                f"${item['precio_unitario']:,.2f}",
                pequeno
            ),
            Paragraph(
                f"${item['total']:,.2f}",
                pequeno
            ),
            Paragraph(
                escapar_pdf(item["tienda"]),
                pequeno
            )
        ])

    tabla = Table(
        datos,
        repeatRows=1,
        colWidths=[
            4.0 * cm,
            3.2 * cm,
            1.6 * cm,
            2.0 * cm,
            2.0 * cm,
            3.0 * cm
        ]
    )

    tabla.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#222222")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )

    story.append(tabla)

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            f"<b>TOTAL ESTIMADO DE COMPRA: "
            f"${total:,.2f}</b>",
            subtitulo
        )
    )

    porcentaje = (
        (total / presupuesto) * 100
        if presupuesto > 0
        else 0
    )

    story.append(
        Paragraph(
            f"Utilización del presupuesto: "
            f"{porcentaje:.1f}%",
            normal
        )
    )

    story.append(
        Paragraph(
            f"Límite máximo permitido: "
            f"${presupuesto + TOLERANCIA_PRESUPUESTO:,.2f}",
            normal
        )
    )

    story.append(
        Spacer(1, 8)
    )

    story.append(
        Paragraph(
            "Las cantidades de compra se calcularon "
            "automáticamente a partir de las porciones "
            "por persona y las presentaciones disponibles.",
            pequeno
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# MOSTRAR PLAN
# ============================================================

def mostrar_plan(
    plan,
    compra,
    total,
    presupuesto,
    personas
):

    st.success(
        f"Plan generado para {personas} persona(s). "
        f"Compra estimada: ${total:,.2f}"
    )

    porcentaje = (
        total / presupuesto * 100
        if presupuesto > 0
        else 0
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Presupuesto",
            f"${presupuesto:,.2f}"
        )

    with col2:
        st.metric(
            "Compra estimada",
            f"${total:,.2f}"
        )

    with col3:
        st.metric(
            "Utilización",
            f"{porcentaje:.1f}%"
        )

    st.divider()

    # ========================================================
    # MENÚ
    # ========================================================

    st.header("🍽️ Menú")

    for dia in plan.get("dias", []):

        st.subheader(
            f"Día {dia.get('dia', '')}"
        )

        for comida in dia.get("comidas", []):

            with st.expander(
                f"{comida.get('tipo', '')} — "
                f"{comida.get('nombre', '')}",
                expanded=False
            ):

                categoria = comida.get(
                    "categoria_proteina",
                    ""
                )

                if categoria:
                    st.caption(
                        f"Proteína: {categoria}"
                    )

                st.markdown(
                    "**Ingredientes por persona:**"
                )

                for ing in comida.get(
                    "ingredientes",
                    []
                ):

                    st.write(
                        f"- {ing.get('uso', 'Ingrediente')}: "
                        f"{ing.get('cantidad_por_persona')} "
                        f"{ing.get('unidad', '')}"
                    )

                st.markdown(
                    "**Preparación:**"
                )

                for i, paso in enumerate(
                    comida.get("preparacion", []),
                    1
                ):
                    st.write(
                        f"{i}. {paso}"
                    )

                if comida.get("tiempo_minutos"):
                    st.caption(
                        f"⏱️ {comida.get('tiempo_minutos')} minutos"
                    )

    st.divider()

    # ========================================================
    # COMPRAS
    # ========================================================

    st.header("🛒 Lista de compras")

    filas = []

    for item in compra:

        filas.append({
            "Producto": item["producto"],
            "Presentación": (
                f"{item['contenido']} "
                f"{item['unidad_contenido']}"
            ),
            "Cantidad": item["cantidad_comprar"],
            "Precio unitario": (
                f"${item['precio_unitario']:,.2f}"
            ),
            "Total": (
                f"${item['total']:,.2f}"
            ),
            "Tienda": item["tienda"]
        })

    st.dataframe(
        filas,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# INTERFAZ
# ============================================================

st.title("🍳 KashCook AI")

st.write(
    "Planea tus comidas, calcula las cantidades reales "
    "y genera tu lista de compras."
)

st.divider()

cliente = obtener_cliente_groq()

if cliente is None:

    st.warning(
        "Ingresa tu GROQ API Key o configúrala en "
        "Streamlit Secrets como GROQ_API_KEY."
    )

    st.stop()


# ============================================================
# FORMULARIO
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🛒 Tiendas")

    tiendas_seleccionadas = []

    for tienda in TIENDAS_DISPONIBLES:

        if st.checkbox(
            tienda,
            value=(tienda == "Alsuper"),
            key=f"tienda_{tienda}"
        ):
            tiendas_seleccionadas.append(tienda)

    dias = st.number_input(
        "📅 Días",
        min_value=1,
        max_value=7,
        value=3,
        step=1
    )

    personas = st.number_input(
        "👨‍👩‍👧‍👦 Personas",
        min_value=1,
        max_value=10,
        value=4,
        step=1
    )

    presupuesto = st.number_input(
        "💰 Presupuesto total",
        min_value=200.0,
        max_value=10000.0,
        value=1500.0,
        step=50.0
    )


with col2:

    st.subheader("🍽️ Preferencias")

    estilos = st.multiselect(
        "Estilos de cocina",
        [
            "Mexicana",
            "Casera",
            "Saludable",
            "Económica",
            "Italiana",
            "Mediterránea",
            "Alta en proteína",
            "Rápida"
        ],
        default=["Mexicana", "Casera"]
    )

    comidas = st.multiselect(
        "Comidas a planear",
        [
            "Desayuno",
            "Comida",
            "Cena"
        ],
        default=[
            "Desayuno",
            "Comida",
            "Cena"
        ]
    )

    electrodomesticos = st.multiselect(
        "Electrodomésticos disponibles",
        [
            "Estufa",
            "Horno",
            "Microondas",
            "Freidora de aire",
            "Licuadora",
            "Olla de presión",
            "Parrilla eléctrica"
        ],
        default=[
            "Estufa",
            "Licuadora"
        ]
    )

    restricciones = st.text_area(
        "🚫 Alergias / restricciones",
        placeholder=(
            "Ejemplo: sin cerdo, sin lactosa, "
            "alergia a cacahuate..."
        )
    )


# ============================================================
# VALIDACIONES
# ============================================================

if not tiendas_seleccionadas:

    st.error(
        "Selecciona al menos una tienda."
    )

    st.stop()

if not comidas:

    st.error(
        "Selecciona al menos una comida."
    )

    st.stop()


catalogo = crear_catalogo_tienda(
    tiendas_seleccionadas
)

if not catalogo:

    st.error(
        "No hay productos disponibles para "
        "las tiendas seleccionadas."
    )

    st.stop()


# ============================================================
# GENERAR
# ============================================================

if st.button(
    "🚀 Generar plan",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Diseñando el menú y calculando cantidades reales..."
    ):

        try:

            prompt = construir_prompt(
                personas=personas,
                dias=dias,
                presupuesto=presupuesto,
                estilos=estilos,
                comidas=comidas,
                restricciones=restricciones,
                electrodomesticos=electrodomesticos,
                catalogo=catalogo
            )

            respuesta = llamar_groq(
                cliente,
                prompt,
                temperatura=0.45
            )

            plan = extraer_json(respuesta)

            compra, total = calcular_compra(
                plan,
                catalogo,
                personas
            )

            # =================================================
            # AJUSTE 1:
            # PRESUPUESTO DEMASIADO BAJO
            # =================================================

            if (
                total < presupuesto * MIN_UTILIZACION_PRESUPUESTO
                and presupuesto >= 500
            ):

                st.info(
                    "El primer cálculo dejó demasiado "
                    "presupuesto disponible. Ajustando "
                    "el plan para aprovecharlo mejor..."
                )

                prompt_ajuste = construir_prompt_ajuste(
                    plan=plan,
                    compra=compra,
                    total=total,
                    personas=personas,
                    dias=dias,
                    presupuesto=presupuesto,
                    catalogo=catalogo,
                    motivo="BAJO"
                )

                respuesta_ajuste = llamar_groq(
                    cliente,
                    prompt_ajuste,
                    temperatura=0.35
                )

                plan_ajustado = extraer_json(
                    respuesta_ajuste
                )

                compra_ajustada, total_ajustado = calcular_compra(
                    plan_ajustado,
                    catalogo,
                    personas
                )

                # Solo aceptamos el ajuste si realmente
                # mejoró la utilización sin exceder el límite.
                if (
                    total_ajustado > total
                    and
                    total_ajustado <= (
                        presupuesto +
                        TOLERANCIA_PRESUPUESTO
                    )
                ):

                    plan = plan_ajustado
                    compra = compra_ajustada
                    total = total_ajustado

            # =================================================
            # AJUSTE 2:
            # PRESUPUESTO EXCEDIDO
            # =================================================

            if total > (
                presupuesto +
                TOLERANCIA_PRESUPUESTO
            ):

                st.warning(
                    "El primer menú excedió el límite. "
                    "KashCook está ajustándolo..."
                )

                prompt_ajuste = construir_prompt_ajuste(
                    plan=plan,
                    compra=compra,
                    total=total,
                    personas=personas,
                    dias=dias,
                    presupuesto=presupuesto,
                    catalogo=catalogo,
                    motivo="ALTO"
                )

                respuesta_ajuste = llamar_groq(
                    cliente,
                    prompt_ajuste,
                    temperatura=0.25
                )

                plan_ajustado = extraer_json(
                    respuesta_ajuste
                )

                compra_ajustada, total_ajustado = calcular_compra(
                    plan_ajustado,
                    catalogo,
                    personas
                )

                if total_ajustado <= (
                    presupuesto +
                    TOLERANCIA_PRESUPUESTO
                ):

                    plan = plan_ajustado
                    compra = compra_ajustada
                    total = total_ajustado

            # =================================================
            # VALIDACIÓN FINAL ABSOLUTA
            # =================================================

            if total > (
                presupuesto +
                TOLERANCIA_PRESUPUESTO
            ):

                st.error(
                    "No fue posible generar un plan válido "
                    "dentro del presupuesto permitido."
                )

                st.stop()

            # =================================================
            # VALIDACIÓN DE COMIDAS
            # =================================================

            comidas_generadas = contar_comidas(
                plan
            )

            comidas_esperadas = (
                dias *
                len(comidas)
            )

            if comidas_generadas < comidas_esperadas:

                st.warning(
                    f"El modelo generó {comidas_generadas} "
                    f"comidas de {comidas_esperadas} esperadas."
                )

            # =================================================
            # GUARDAR EN SESSION
            # =================================================

            st.session_state["plan"] = plan
            st.session_state["compra"] = compra
            st.session_state["total"] = total
            st.session_state["presupuesto"] = presupuesto
            st.session_state["personas"] = personas
            st.session_state["dias"] = dias
            st.session_state["tiendas"] = tiendas_seleccionadas

            st.success(
                "Plan generado correctamente."
            )

        except Exception as e:

            st.error(
                f"Ocurrió un error al generar el plan: {e}"
            )


# ============================================================
# MOSTRAR RESULTADO
# ============================================================

if "plan" in st.session_state:

    mostrar_plan(
        plan=st.session_state["plan"],
        compra=st.session_state["compra"],
        total=st.session_state["total"],
        presupuesto=st.session_state["presupuesto"],
        personas=st.session_state["personas"]
    )

    st.divider()

    # ========================================================
    # PDF
    # ========================================================

    pdf_bytes = generar_pdf(
        plan=st.session_state["plan"],
        compra=st.session_state["compra"],
        total=st.session_state["total"],
        presupuesto=st.session_state["presupuesto"],
        personas=st.session_state["personas"],
        dias=st.session_state["dias"],
        tiendas=st.session_state["tiendas"]
    )

    st.download_button(
        "📄 Descargar plan completo en PDF",
        data=pdf_bytes,
        file_name="KashCook_AI_plan.pdf",
        mime="application/pdf",
        use_container_width=True
    )
