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
