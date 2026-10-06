import io
import json
import re
import math
import html
import requests
import streamlit as st

from bs4 import BeautifulSoup
from groq import Groq

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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
    layout="wide",
)

TIENDAS_DISPONIBLES = [
    "Alsuper",
    "Walmart",
    "Soriana",
    "Bodega Aurrerá",
]

TOLERANCIA_PRESUPUESTO = 100.00
MIN_UTILIZACION_PRESUPUESTO = 0.90


# ============================================================
# CATÁLOGOS DE PRODUCTOS
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
    url="",
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
        "url": url,
    }


def crear_catalogos():
    catalogos = {}

    # --------------------------------------------------------
    # ALSUPER
    # --------------------------------------------------------

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
            "alsuper_pollo_muslo",
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
            "1 kg",
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
            "1 kg",
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
            "1 kg",
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
            "1 kg",
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

    # --------------------------------------------------------
    # WALMART
    # --------------------------------------------------------

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
            "1 kg",
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
            "1 kg",
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
            "1 kg",
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

    # --------------------------------------------------------
    # SORIANA
    # --------------------------------------------------------

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
            "1 kg",
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
            "1 kg",
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
            "1 kg",
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

    # --------------------------------------------------------
    # BODEGA AURRERÁ
    # --------------------------------------------------------

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
            "1 kg",
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
            "1 kg",
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
            "1 kg",
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
# GROQ
# ============================================================

def obtener_cliente_groq():
    api_key = None

    try:
        api_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        api_key = st.text_input(
            "Introduce tu GROQ_API_KEY",
            type="password",
        )

    if not api_key:
        return None

    return Groq(api_key=api_key)


def llamar_groq(cliente, prompt, temperatura=0.4):
    respuesta = cliente.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres KashCook AI, un planificador experto de "
                    "alimentación familiar, compras y presupuesto. "
                    "Cuando se solicite un plan debes devolver "
                    "exclusivamente JSON válido."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=temperatura,
        max_tokens=16000,
        response_format={"type": "json_object"},
    )

    return respuesta.choices[0].message.content


# ============================================================
# JSON
# ============================================================

def extraer_json(texto):
    if not texto:
        raise ValueError("La IA no devolvió contenido.")

    texto = texto.strip()

    # Intento directo
    try:
        return json.loads(texto)
    except Exception:
        pass

    # Quitar bloques markdown
    texto_limpio = re.sub(
        r"```json\s*",
        "",
        texto,
        flags=re.IGNORECASE,
    )

    texto_limpio = re.sub(
        r"```\s*",
        "",
        texto_limpio,
    )

    texto_limpio = texto_limpio.strip()

    try:
        return json.loads(texto_limpio)
    except Exception:
        pass

    # Buscar primer objeto JSON
    inicio = texto_limpio.find("{")
    fin = texto_limpio.rfind("}")

    if inicio != -1 and fin != -1 and fin > inicio:
        posible = texto_limpio[inicio : fin + 1]

        try:
            return json.loads(posible)
        except Exception:
            pass

    raise ValueError(
        "No fue posible interpretar la respuesta de la IA como JSON."
    )


# ============================================================
# CONVERSIÓN DE UNIDADES
# ============================================================

def convertir_a_base(cantidad, unidad):
    unidad = unidad.lower().strip()

    if unidad in ["kg", "kilo", "kilos"]:
        return cantidad * 1000, "g"

    if unidad in ["g", "gramo", "gramos"]:
        return cantidad, "g"

    if unidad in ["l", "litro", "litros"]:
        return cantidad * 1000, "ml"

    if unidad in ["ml", "mililitro", "mililitros"]:
        return cantidad, "ml"

    if unidad in ["pieza", "piezas", "unidad", "unidades"]:
        return cantidad, "pieza"

    return cantidad, unidad


# ============================================================
# CÁLCULO REAL DE COMPRA
# ============================================================

def calcular_compra(plan, catalogo, personas):
    productos_por_id = {
        p["id"]: p for p in catalogo
    }

    demanda = {}

    for dia in plan.get("dias", []):
        for comida in dia.get("comidas", []):
            ingredientes = comida.get("ingredientes", [])

            for ing in ingredientes:
                producto_id = ing.get("producto_id")

                if not producto_id:
                    continue

                if producto_id not in productos_por_id:
                    continue

                cantidad_persona = float(
                    ing.get("cantidad_por_persona", 0)
                    or 0
                )

                unidad = str(
                    ing.get("unidad", "")
                ).lower().strip()

                if cantidad_persona <= 0:
                    continue

                cantidad_total = cantidad_persona * personas

                producto_info = productos_por_id[producto_id]

                contenido = producto_info["contenido"]
                unidad_contenido = producto_info["unidad_contenido"]

                cantidad_base, unidad_base = convertir_a_base(
                    cantidad_total,
                    unidad,
                )

                contenido_base, contenido_unidad_base = convertir_a_base(
                    contenido,
                    unidad_contenido,
                )

                if unidad_base != contenido_unidad_base:
                    continue

                if contenido_base <= 0:
                    continue

                paquetes = math.ceil(
                    cantidad_base / contenido_base
                )

                if paquetes < 1:
                    paquetes = 1

                if producto_id not in demanda:
                    demanda[producto_id] = {
                        "producto": producto_info,
                        "cantidad_requerida": 0,
                        "unidad": unidad_base,
                        "paquetes": 0,
                    }

                demanda[producto_id]["cantidad_requerida"] += cantidad_base

    # Recalcular paquetes después de juntar todos los usos
    compra = []

    total = 0

    for producto_id, item in demanda.items():
        p = item["producto"]

        contenido_base, _ = convertir_a_base(
            p["contenido"],
            p["unidad_contenido"],
        )

        paquetes = math.ceil(
            item["cantidad_requerida"] / contenido_base
        )

        subtotal = paquetes * p["precio"]

        item["paquetes"] = paquetes
        item["subtotal"] = subtotal

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
            "precio_unitario": p["precio"],
            "subtotal": subtotal,
            "tienda": p["tienda"],
            "url": p.get("url", ""),
        })

    return compra, round(total, 2)


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
    catalogo_texto = []

    for p in catalogo:
        catalogo_texto.append(
            {
                "id": p["id"],
                "tienda": p["tienda"],
                "producto": p["nombre"],
                "categoria": p["categoria"],
                "ingrediente_base": p["ingrediente_base"],
                "presentacion": p["presentacion"],
                "contenido": p["contenido"],
                "unidad_contenido": p["unidad_contenido"],
                "precio": p["precio"],
            }
        )

    return f"""
Eres KashCook AI.

Debes crear un plan de alimentación familiar realista,
variado y económicamente eficiente.

DATOS DEL USUARIO:

Tiendas seleccionadas:
{", ".join(tiendas)}

Días:
{dias}

Personas:
{personas}

Presupuesto:
${presupuesto:.2f} MXN

Estilos de cocina:
{", ".join(estilos) if estilos else "Libre"}

Comidas:
{", ".join(comidas)}

Electrodomésticos disponibles:
{", ".join(electrodomesticos) if electrodomesticos else "Cocina convencional"}

Restricciones/alergias:
{restricciones if restricciones else "Ninguna"}

REGLAS IMPORTANTES:

1. SOLO puedes utilizar productos del catálogo proporcionado.

2. Las tiendas seleccionadas por el usuario son las únicas
   tiendas permitidas.

3. NO hagas comparación de precios entre tiendas.

4. NO digas que un producto debe comprarse en una tienda
   porque ahí está más barato.

5. Si hay varias tiendas seleccionadas, simplemente puedes
   utilizar productos de cualquiera de ellas.

6. Las cantidades de ingredientes deben calcularse POR PERSONA.

7. Después KashCook multiplicará esas cantidades por el número
   real de personas y calculará los paquetes necesarios según
   la presentación real del producto.

8. No pongas cantidades absurdamente pequeñas.

9. Las proteínas principales deben tener por persona,
   aproximadamente:

   - Pechuga de pollo sin hueso: 180-220 g
   - Pollo con hueso: 250-350 g
   - Carne de res: 160-220 g
   - Carne de cerdo: 160-220 g
   - Pescado: 180-220 g
   - Atún: suficiente para una porción real de comida
   - Sardina: suficiente para una porción real
   - Huevo: normalmente 2-4 piezas por persona según receta

10. NO hagas un menú compuesto principalmente por pollo.

11. Procura utilizar diferentes fuentes de proteína:
    pollo, res, cerdo, pescado, atún, sardina y huevo.

12. Evita repetir exactamente la misma preparación.

13. Los acompañamientos deben ser suficientes para el número
    de personas.

14. Utiliza arroz, frijol, tortillas, papa y verduras cuando
    tenga sentido.

15. Respeta las alergias y restricciones.

16. El objetivo es que el costo final calculado por KashCook
    utilice aproximadamente entre 90% y 100% del presupuesto.

17. NO necesitas gastar exactamente el presupuesto.

18. JAMÁS debes superar el presupuesto + $100 MXN.

19. El precio de cada producto ya viene indicado en el catálogo.
    No inventes precios.

20. No muestres análisis técnico al usuario.

21. Cada comida debe tener ingredientes y preparación.

22. Las recetas deben ser realmente cocinables.

CATÁLOGO:

{json.dumps(catalogo_texto, ensure_ascii=False, indent=2)}

FORMATO OBLIGATORIO:

Devuelve exclusivamente JSON válido con esta estructura:

{{
  "dias": [
    {{
      "dia": 1,
      "comidas": [
        {{
          "tipo": "Desayuno",
          "nombre": "Nombre de la receta",
          "ingredientes": [
            {{
              "producto_id": "ID_EXACTO",
              "cantidad_por_persona": 2,
              "unidad": "pieza"
            }}
          ],
          "preparacion": [
            "Paso 1",
            "Paso 2",
            "Paso 3"
          ]
        }}
      ]
    }}
  ]
}}

IMPORTANTE:

- cantidad_por_persona debe ser numérica.
- producto_id debe coincidir EXACTAMENTE con el catálogo.
- unidad debe coincidir con la unidad del producto.
- No agregues productos fuera del catálogo.
- No agregues texto fuera del JSON.
"""


# ============================================================
# PROMPT PARA AJUSTAR PRESUPUESTO
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
    catalogo_texto = []

    for p in catalogo:
        catalogo_texto.append(
            {
                "id": p["id"],
                "producto": p["nombre"],
                "ingrediente_base": p["ingrediente_base"],
                "presentacion": p["presentacion"],
                "contenido": p["contenido"],
                "unidad_contenido": p["unidad_contenido"],
                "precio": p["precio"],
            }
        )

    compra_texto = []

    for item in compra:
        compra_texto.append(
            {
                "producto": item["producto"],
                "presentacion": item["presentacion"],
                "paquetes": item["paquetes"],
                "precio_unitario": item["precio_unitario"],
                "subtotal": item["subtotal"],
            }
        )

    if modo == "subir":
        instruccion = f"""
El costo actual es ${total:.2f} y el presupuesto es ${presupuesto:.2f}.

El costo está demasiado por debajo del presupuesto.

Debes mejorar el plan para que la compra utilice aproximadamente
entre 90% y 100% del presupuesto.

NO agregues comida innecesaria solamente para gastar.

Aumenta cantidades razonables, mejora variedad de proteínas,
verduras y acompañamientos y crea porciones familiares correctas.

El nuevo costo NO debe superar ${presupuesto + TOLERANCIA_PRESUPUESTO:.2f}.
"""
    else:
        instruccion = f"""
El costo actual es ${total:.2f}.

El presupuesto máximo permitido es:
${presupuesto + TOLERANCIA_PRESUPUESTO:.2f}

Debes reducir el costo sin destruir la calidad del menú.

Mantén porciones adecuadas para {personas} personas.

El nuevo costo debe ser como máximo:
${presupuesto + TOLERANCIA_PRESUPUESTO:.2f}
"""

    return f"""
Eres KashCook AI y estás corrigiendo un plan de alimentación.

{instruccion}

CATÁLOGO:

{json.dumps(catalogo_texto, ensure_ascii=False, indent=2)}

COMPRA ACTUAL:

{json.dumps(compra_texto, ensure_ascii=False, indent=2)}

PLAN ACTUAL:

{json.dumps(plan, ensure_ascii=False, indent=2)}

Devuelve exclusivamente JSON válido.

Conserva esta estructura:

{{
  "dias": [
    {{
      "dia": 1,
      "comidas": [
        {{
          "tipo": "Desayuno",
          "nombre": "Nombre",
          "ingredientes": [
            {{
              "producto_id": "ID_EXACTO",
              "cantidad_por_persona": 2,
              "unidad": "pieza"
            }}
          ],
          "preparacion": [
            "Paso 1"
          ]
        }}
      ]
    }}
  ]
}}

No agregues texto fuera del JSON.
"""


# ============================================================
# PDF
# ============================================================

def generar_pdf(plan, compra, total, presupuesto, personas, tiendas):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
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
        "Dia",
        parent=styles["Heading1"],
        fontSize=17,
        leading=20,
        spaceBefore=10,
        spaceAfter=10,
    )

    comida_style = ParagraphStyle(
        "Comida",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=5,
    )

    normal = ParagraphStyle(
        "NormalKash",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=13,
        spaceAfter=4,
    )

    pequeño = ParagraphStyle(
        "Pequeno",
        parent=styles["BodyText"],
        fontSize=8,
        leading=10,
    )

    story = []

    story.append(
        Paragraph(
            "🍳 KashCook AI",
            titulo,
        )
    )

    story.append(
        Paragraph(
            f"Plan para {personas} persona(s) · "
            f"{len(plan.get('dias', []))} día(s)<br/>"
            f"Tiendas: {html.escape(', '.join(tiendas))}<br/>"
            f"Presupuesto: ${presupuesto:,.2f} MXN · "
            f"Compra calculada: ${total:,.2f} MXN",
            subtitulo,
        )
    )

    # --------------------------------------------------------
    # MENÚ
    # --------------------------------------------------------

    for indice, dia in enumerate(plan.get("dias", [])):
        story.append(
            Paragraph(
                f"DÍA {dia.get('dia', indice + 1)}",
                dia_style,
            )
        )

        for comida in dia.get("comidas", []):
            nombre = html.escape(
                str(comida.get("nombre", "Receta"))
            )

            tipo = html.escape(
                str(comida.get("tipo", "Comida"))
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

            ingredientes = comida.get("ingredientes", [])

            for ing in ingredientes:
                producto_id = ing.get("producto_id", "")
                cantidad = ing.get(
                    "cantidad_por_persona",
                    "",
                )
                unidad = ing.get("unidad", "")

                catalogo_global = []

                for lista in CATALOGOS.values():
                    catalogo_global.extend(lista)

                p = next(
                    (
                        x for x in catalogo_global
                        if x["id"] == producto_id
                    ),
                    None,
                )

                if p:
                    nombre_producto = p["nombre"]
                else:
                    nombre_producto = producto_id

                texto = (
                    f"• {html.escape(str(nombre_producto))}: "
                    f"{cantidad} {html.escape(str(unidad))} "
                    f"por persona"
                )

                story.append(
                    Paragraph(
                        texto,
                        pequeño,
                    )
                )

            story.append(
                Spacer(1, 4)
            )

            story.append(
                Paragraph(
                    "<b>Preparación:</b>",
                    normal,
                )
            )

            preparacion = comida.get(
                "preparacion",
                [],
            )

            for numero, paso in enumerate(preparacion, 1):
                story.append(
                    Paragraph(
                        f"{numero}. {html.escape(str(paso))}",
                        pequeño,
                    )
                )

            story.append(
                Spacer(1, 8)
            )

        if indice < len(plan.get("dias", [])) - 1:
            story.append(PageBreak())

    # --------------------------------------------------------
    # LISTA DE COMPRA
    # --------------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "LISTA DE COMPRA",
            dia_style,
        )
    )

    story.append(
        Paragraph(
            "Productos calculados considerando las presentaciones "
            "reales y el número de personas.",
            normal,
        )
    )

    datos = [
        [
            Paragraph("<b>Producto</b>", pequeño),
            Paragraph("<b>Presentación</b>", pequeño),
            Paragraph("<b>Cant.</b>", pequeño),
            Paragraph("<b>Precio</b>", pequeño),
            Paragraph("<b>Total</b>", pequeño),
            Paragraph("<b>Tienda</b>", pequeño),
        ]
    ]

    for item in compra:
        datos.append(
            [
                Paragraph(
                    html.escape(item["producto"]),
                    pequeño,
                ),
                Paragraph(
                    html.escape(item["presentacion"]),
                    pequeño,
                ),
                Paragraph(
                    str(item["paquetes"]),
                    pequeño,
                ),
                Paragraph(
                    f"${item['precio_unitario']:,.2f}",
                    pequeño,
                ),
                Paragraph(
                    f"${item['subtotal']:,.2f}",
                    pequeño,
                ),
                Paragraph(
                    html.escape(item["tienda"]),
                    pequeño,
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

    story.append(tabla)

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            f"<b>TOTAL DE COMPRA: ${total:,.2f} MXN</b>",
            ParagraphStyle(
                "Total",
                parent=normal,
                fontSize=14,
                leading=17,
            ),
        )
    )

    story.append(
        Paragraph(
            f"Presupuesto original: ${presupuesto:,.2f} MXN",
            normal,
        )
    )

    if total <= presupuesto:
        diferencia = presupuesto - total

        story.append(
            Paragraph(
                f"Disponible restante: ${diferencia:,.2f} MXN",
                normal,
            )
        )
    else:
        excedente = total - presupuesto

        story.append(
            Paragraph(
                f"Excedente utilizado: ${excedente:,.2f} MXN",
                normal,
            )
        )

    doc.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ============================================================
# VALIDACIONES
# ============================================================

def validar_plan(plan):
    if not isinstance(plan, dict):
        return False

    if "dias" not in plan:
        return False

    if not isinstance(plan["dias"], list):
        return False

    if not plan["dias"]:
        return False

    for dia in plan["dias"]:
        if "comidas" not in dia:
            return False

        if not isinstance(dia["comidas"], list):
            return False

        for comida in dia["comidas"]:
            if "ingredientes" not in comida:
                return False

            if "preparacion" not in comida:
                return False

    return True


# ============================================================
# INTERFAZ
# ============================================================

st.title("🍳 KashCook AI")

st.markdown(
    """
### Tu menú, tus compras y tu presupuesto en un solo lugar

KashCook genera un menú familiar y calcula la compra real
considerando las presentaciones de los productos.
"""
)

st.divider()

# ------------------------------------------------------------
# TIENDAS
# ------------------------------------------------------------

st.subheader("🛒 ¿Dónde vas a comprar?")

tiendas_seleccionadas = []

cols = st.columns(4)

for i, tienda in enumerate(TIENDAS_DISPONIBLES):
    with cols[i]:
        if st.checkbox(
            tienda,
            value=(i == 0),
            key=f"tienda_{i}",
        ):
            tiendas_seleccionadas.append(tienda)

if not tiendas_seleccionadas:
    st.warning(
        "Selecciona al menos una tienda."
    )
    st.stop()

# ------------------------------------------------------------
# DATOS PRINCIPALES
# ------------------------------------------------------------

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

# ------------------------------------------------------------
# ESTILOS
# ------------------------------------------------------------

st.subheader("🍽️ Estilo de comida")

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

# ------------------------------------------------------------
# COMIDAS
# ------------------------------------------------------------

st.subheader("🍳 ¿Qué comidas quieres planear?")

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

# ------------------------------------------------------------
# ELECTRODOMÉSTICOS
# ------------------------------------------------------------

st.subheader("🔌 Electrodomésticos disponibles")

electrodomesticos = st.multiselect(
    "Selecciona los que tienes disponibles",
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

# ------------------------------------------------------------
# RESTRICCIONES
# ------------------------------------------------------------

st.subheader("⚠️ Restricciones y alergias")

restricciones = st.text_area(
    "Indica alergias, alimentos que no consumen o restricciones",
    placeholder=(
        "Ejemplo: sin camarón, sin cacahuate, "
        "no picante, vegetariano..."
    ),
)

st.divider()

# ------------------------------------------------------------
# GENERACIÓN
# ------------------------------------------------------------

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
            "Necesitas configurar GROQ_API_KEY."
        )
        st.stop()

    catalogo = []

    for tienda in tiendas_seleccionadas:
        catalogo.extend(
            CATALOGOS.get(tienda, [])
        )

    if not catalogo:
        st.error(
            "No hay productos disponibles "
            "para las tiendas seleccionadas."
        )
        st.stop()

    with st.spinner(
        "KashCook está diseñando tu menú..."
    ):

        try:

            # ------------------------------------------------
            # 1. CREAR PLAN INICIAL
            # ------------------------------------------------

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

            plan = extraer_json(respuesta)

            if not validar_plan(plan):
                raise ValueError(
                    "La IA devolvió un plan incompleto."
                )

            # ------------------------------------------------
            # 2. CALCULAR COMPRA REAL
            # ------------------------------------------------

            compra, total = calcular_compra(
                plan,
                catalogo,
                personas,
            )

            # ------------------------------------------------
            # 3. SI QUEDA DEMASIADO PRESUPUESTO LIBRE
            # ------------------------------------------------

            if (
                total < presupuesto * MIN_UTILIZACION_PRESUPUESTO
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

                plan_ajustado = extraer_json(
                    respuesta_ajuste
                )

                if validar_plan(plan_ajustado):

                    compra_ajustada, total_ajustado = calcular_compra(
                        plan_ajustado,
                        catalogo,
                        personas,
                    )

                    if (
                        total_ajustado
                        <= presupuesto + TOLERANCIA_PRESUPUESTO
                    ):
                        plan = plan_ajustado
                        compra = compra_ajustada
                        total = total_ajustado

            # ------------------------------------------------
            # 4. SI SE PASA DEL PRESUPUESTO + $100
            # ------------------------------------------------

            if total > presupuesto + TOLERANCIA_PRESUPUESTO:

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

                plan_ajustado = extraer_json(
                    respuesta_ajuste
                )

                if validar_plan(plan_ajustado):

                    compra_ajustada, total_ajustado = calcular_compra(
                        plan_ajustado,
                        catalogo,
                        personas,
                    )

                    plan = plan_ajustado
                    compra = compra_ajustada
                    total = total_ajustado

            # ------------------------------------------------
            # 5. VALIDACIÓN FINAL
            # ------------------------------------------------

            if total > presupuesto + TOLERANCIA_PRESUPUESTO:

                st.error(
                    f"KashCook no pudo ajustar la compra "
                    f"al límite permitido. "
                    f"Total: ${total:,.2f} | "
                    f"Límite: "
                    f"${presupuesto + TOLERANCIA_PRESUPUESTO:,.2f}"
                )

                st.stop()

            # ------------------------------------------------
            # GUARDAR
            # ------------------------------------------------

            st.session_state["plan"] = plan
            st.session_state["compra"] = compra
            st.session_state["total"] = total
            st.session_state["presupuesto"] = presupuesto
            st.session_state["personas"] = personas
            st.session_state["tiendas"] = tiendas_seleccionadas

        except Exception as e:

            st.error(
                f"Ocurrió un error al generar el plan: {e}"
            )

            st.stop()


# ============================================================
# MOSTRAR PLAN
# ============================================================

if "plan" in st.session_state:

    plan = st.session_state["plan"]
    compra = st.session_state["compra"]
    total = st.session_state["total"]
    presupuesto = st.session_state["presupuesto"]
    personas = st.session_state["personas"]
    tiendas = st.session_state["tiendas"]

    st.divider()

    st.header("📋 Tu plan")

    # --------------------------------------------------------
    # RESUMEN DE PRESUPUESTO
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Presupuesto",
            f"${presupuesto:,.2f}",
        )

    with col2:
        st.metric(
            "Compra calculada",
            f"${total:,.2f}",
        )

    with col3:

        diferencia = presupuesto - total

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

    # --------------------------------------------------------
    # ALERTA DE PRESUPUESTO
    # --------------------------------------------------------

    if total <= presupuesto:
        st.success(
            f"La compra está dentro del presupuesto. "
            f"Quedan ${presupuesto - total:,.2f}."
        )

    elif total <= presupuesto + TOLERANCIA_PRESUPUESTO:
        st.warning(
            f"Se utilizó la tolerancia permitida de "
            f"${total - presupuesto:,.2f}."
        )

    # --------------------------------------------------------
    # MENÚ POR DÍA
    # --------------------------------------------------------

    st.header("🍽️ Menú semanal")

    catalogo_global = []

    for lista in CATALOGOS.values():
        catalogo_global.extend(lista)

    productos_por_id = {
        p["id"]: p
        for p in catalogo_global
    }

    for dia in plan.get("dias", []):

        st.subheader(
            f"Día {dia.get('dia', '')}"
        )

        for comida in dia.get("comidas", []):

            st.markdown(
                f"### {comida.get('tipo', 'Comida')}: "
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
                    nombre = p["nombre"]
                else:
                    nombre = producto_id

                st.write(
                    f"- {nombre}: "
                    f"{cantidad} {unidad} "
                    f"por persona"
                )

            st.markdown(
                "**Preparación:**"
            )

            for i, paso in enumerate(
                comida.get(
                    "preparacion",
                    [],
                ),
                1,
            ):
                st.write(
                    f"{i}. {paso}"
                )

            st.divider()

    # --------------------------------------------------------
    # LISTA DE COMPRA
    # --------------------------------------------------------

    st.header("🛒 Lista de compra")

    datos_tabla = []

    for item in compra:
        datos_tabla.append(
            {
                "Producto": item["producto"],
                "Presentación": item["presentacion"],
                "Cantidad": item["paquetes"],
                "Precio unitario": (
                    f"${item['precio_unitario']:,.2f}"
                ),
                "Total": (
                    f"${item['subtotal']:,.2f}"
                ),
                "Tienda": item["tienda"],
            }
        )

    if datos_tabla:
        st.dataframe(
            datos_tabla,
            use_container_width=True,
            hide_index=True,
        )

    st.subheader(
        f"💰 Total: ${total:,.2f} MXN"
    )

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

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
    )
