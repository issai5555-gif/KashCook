import re, json, math, html
from io import BytesIO
from datetime import datetime
from urllib.parse import quote_plus, urljoin

import requests
import streamlit as st
from bs4 import BeautifulSoup

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

APP_NAME = "KashCook AI"
DEFAULT_POSTAL_CODE = "31000"
TIMEOUT = 15
CACHE_SECONDS = 900
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept-Language": "es-MX,es;q=0.9,en;q=0.7",
}

STORE_SEARCH_URLS = {
    "Alsuper": ["https://www.alsuper.com.mx/buscar?q={q}", "https://www.alsuper.com.mx/search?q={q}"],
    "Walmart": ["https://www.walmart.com.mx/search?q={q}", "https://www.walmart.com.mx/search?query={q}"],
    "Soriana": ["https://www.soriana.com/search?q={q}", "https://www.soriana.com/search?text={q}"],
    "Bodega Aurrerá": ["https://www.bodegaaurrera.com.mx/search?q={q}", "https://www.bodegaaurrera.com.mx/search?query={q}"],
}

# Cantidades de referencia para recetas; no son precios ni equivalencias de empaque.
INGREDIENTS = {
    "huevo": {"unit":"pieza", "query":"huevo", "qty":1.0},
    "tortillas": {"unit":"kg", "query":"tortillas de maíz", "qty":0.10},
    "arroz": {"unit":"kg", "query":"arroz 1 kg", "qty":0.07},
    "frijol": {"unit":"kg", "query":"frijol 1 kg", "qty":0.07},
    "pollo": {"unit":"kg", "query":"pollo", "qty":0.18},
    "carne de res": {"unit":"kg", "query":"carne de res", "qty":0.12},
    "carne de cerdo": {"unit":"kg", "query":"carne de cerdo", "qty":0.12},
    "atún": {"unit":"lata", "query":"atún en agua lata", "qty":0.15},
    "sardina": {"unit":"lata", "query":"sardina en tomate lata", "qty":0.08},
    "leche": {"unit":"litro", "query":"leche 1 litro", "qty":0.10},
    "avena": {"unit":"kg", "query":"avena", "qty":0.04},
    "pasta": {"unit":"paquete", "query":"pasta para sopa", "qty":0.10},
    "jitomate": {"unit":"kg", "query":"jitomate", "qty":0.08},
    "cebolla": {"unit":"kg", "query":"cebolla", "qty":0.03},
    "papa": {"unit":"kg", "query":"papa", "qty":0.08},
    "zanahoria": {"unit":"kg", "query":"zanahoria", "qty":0.04},
    "calabacita": {"unit":"kg", "query":"calabacita", "qty":0.05},
    "plátano": {"unit":"kg", "query":"plátano", "qty":0.07},
    "manzana": {"unit":"kg", "query":"manzana", "qty":0.05},
    "aceite": {"unit":"litro", "query":"aceite vegetal 1 litro", "qty":0.015},
    "queso": {"unit":"kg", "query":"queso", "qty":0.03},
}

RECIPES = {
    "Mexicana tradicional": [
        ("Desayuno","Huevos a la mexicana con tortillas",["huevo","jitomate","cebolla","tortillas"],"Pica jitomate y cebolla. Sofríe, agrega el huevo batido y cocina bien. Sirve con tortillas."),
        ("Comida","Pollo guisado con arroz y calabacita",["pollo","arroz","calabacita","jitomate","cebolla"],"Dora el pollo, agrega jitomate y cebolla. Cocina tapado hasta que esté completamente cocido. Acompaña con arroz y calabacita."),
        ("Cena","Tacos de frijol con queso",["frijol","tortillas","queso"],"Calienta los frijoles, machácalos ligeramente y sirve en tortillas con queso."),
        ("Desayuno","Avena con plátano",["avena","leche","plátano"],"Cuece la avena con leche y agua al gusto. Sirve con plátano rebanado."),
        ("Comida","Picadillo de res con papa y zanahoria",["carne de res","papa","zanahoria","jitomate","cebolla"],"Sofríe la carne, añade verduras picadas, jitomate y un poco de agua. Cocina hasta que todo esté suave."),
        ("Cena","Tacos de atún",["atún","tortillas","jitomate","cebolla"],"Escurre el atún, mezcla con jitomate y cebolla picados y sirve en tortillas."),
        ("Desayuno","Quesadillas con manzana",["tortillas","queso","manzana"],"Derrite el queso dentro de las tortillas en un sartén. Acompaña con manzana."),
        ("Comida","Cerdo guisado con arroz",["carne de cerdo","arroz","jitomate","cebolla"],"Dora el cerdo, añade jitomate y cebolla y cocina completamente. Sirve con arroz."),
        ("Cena","Sopa de pasta con huevo",["pasta","huevo","jitomate","cebolla"],"Dora ligeramente la pasta, agrega jitomate licuado con cebolla y agua. Cuece y añade huevo bien cocido."),
    ],
    "Regional norteña": [
        ("Desayuno","Huevos con papa y tortillas",["huevo","papa","tortillas","cebolla"],"Dora papa y cebolla en cubos hasta suavizar. Agrega huevo batido y cocina por completo."),
        ("Comida","Pollo a la mexicana con arroz",["pollo","jitomate","cebolla","arroz"],"Cocina el pollo con jitomate y cebolla hasta que esté bien cocido. Acompaña con arroz."),
        ("Cena","Frijoles con queso y tortillas",["frijol","queso","tortillas"],"Calienta los frijoles y acompaña con queso y tortillas calientes."),
        ("Desayuno","Avena con manzana",["avena","leche","manzana"],"Cuece la avena con leche y sirve con manzana picada."),
        ("Comida","Picadillo norteño",["carne de res","papa","jitomate","cebolla"],"Dora la carne molida, agrega papa en cubos, jitomate, cebolla y agua. Cocina hasta que la papa esté suave."),
        ("Cena","Ensalada de atún con tortillas",["atún","jitomate","cebolla","tortillas"],"Mezcla atún escurrido con jitomate y cebolla picados. Sirve con tortillas tostadas en sartén."),
        ("Desayuno","Quesadillas y plátano",["tortillas","queso","plátano"],"Calienta las tortillas con queso hasta derretir. Acompaña con plátano."),
        ("Comida","Cerdo con verduras",["carne de cerdo","zanahoria","calabacita","arroz"],"Cocina el cerdo completamente, añade verduras y sirve con arroz."),
        ("Cena","Sardinas guisadas",["sardina","jitomate","cebolla","tortillas"],"Calienta las sardinas con jitomate y cebolla picados. Sirve con tortillas."),
    ],
    "Asiática sencilla": [
        ("Desayuno","Huevo revuelto con arroz",["huevo","arroz","cebolla"],"Prepara arroz cocido y saltéalo con cebolla y huevo hasta que esté completamente cocido."),
        ("Comida","Pollo salteado con verduras y arroz",["pollo","zanahoria","calabacita","arroz"],"Corta el pollo y las verduras en tiras. Saltea hasta cocinar por completo y acompaña con arroz."),
        ("Cena","Sopa de pasta con verduras",["pasta","zanahoria","cebolla"],"Cuece la pasta en caldo o agua con zanahoria y cebolla picadas."),
        ("Desayuno","Avena con plátano",["avena","leche","plátano"],"Cuece la avena y sirve con leche y plátano."),
        ("Comida","Cerdo salteado con verduras",["carne de cerdo","papa","zanahoria","arroz"],"Cocina el cerdo en trozos finos hasta que esté bien cocido; añade verduras y sirve con arroz."),
        ("Cena","Arroz con huevo y verduras",["arroz","huevo","zanahoria","cebolla"],"Saltea verduras, agrega arroz cocido y huevo. Cocina hasta que el huevo esté listo."),
    ],
    "Italiana económica": [
        ("Desayuno","Huevo con jitomate",["huevo","jitomate","tortillas"],"Sofríe jitomate y agrega huevo batido. Cocina por completo y acompaña con tortillas."),
        ("Comida","Pasta con carne y jitomate",["pasta","carne de res","jitomate","cebolla"],"Cuece la pasta. Prepara una salsa de carne molida, jitomate y cebolla y mezcla."),
        ("Cena","Quesadillas con verduras",["tortillas","queso","calabacita"],"Cocina la calabacita en tiras, rellena tortillas con queso y verdura y calienta."),
        ("Desayuno","Avena con manzana",["avena","leche","manzana"],"Cuece la avena con leche y acompaña con manzana."),
