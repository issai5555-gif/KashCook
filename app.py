import io
import json
import math
import re
import html

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
                    continue

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
                    continue

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

        paquetes = math.ceil(
            item["cantidad_requerida"]
            / contenido_base
        )

        if paquetes < 1:
            paquetes = 1

        subtotal = (
            paquetes * p["precio"]
        )

        total += subtotal

        compra.append(
            {
                "producto": p["nombre"],
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
            f"Compra estimada: ${total:,.2f} MXN",
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
                    f"${item['precio_unitario']:,.2f}",
                    pequeno,
                ),

                Paragraph(
                    f"${item['subtotal']:,.2f}",
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

    story.append(
        Paragraph(
            f"<b>TOTAL DE COMPRA: "
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
}

DESAYUNOS = [k for k,v in RECETAS_REALES.items() if v["tipo"]=="Desayuno"]
PLATOS = [k for k,v in RECETAS_REALES.items() if v["tipo"] in ("Comida","Cena")]

def _producto_para_base(base, catalogo):
    """Selecciona el producto más barato de la tienda seleccionada para un ingrediente."""
    candidatos=[p for p in catalogo if p.get("ingrediente_base")==base]
    if base == "molida":
        candidatos=[p for p in catalogo if p.get("ingrediente_base")=="res" and "molida" in str(p.get("nombre","")).lower()]
    if not candidatos:
        return None
    return min(candidatos,key=lambda p: float(p.get("precio") or 10**9))


def _receta_a_comida(recipe_id, catalogo, tipo):
    r=RECETAS_REALES[recipe_id]
    ingredientes=[]
    for base,cantidad,unidad in r["ingredientes"]:
        p=_producto_para_base(base,catalogo)
        if not p:
            return None
        ingredientes.append({"producto_id":p["id"],"cantidad_por_persona":cantidad,"unidad":unidad})
    return {"tipo":tipo,"nombre":r["nombre"],"ingredientes":ingredientes,"preparacion":r["pasos"],"fuente":r["fuente"]}


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


def _generar_plan_local(dias, personas, presupuesto, comidas, catalogo, estilos=None):
    """Optimización local: no permite que la IA invente platos ni cantidades."""
    import random
    candidatos_des=[r for r in DESAYUNOS if _receta_a_comida(r,catalogo,"Desayuno")]
    candidatos_pl=[r for r in PLATOS if _receta_a_comida(r,"".join([]) if False else catalogo,"Comida")]
    if not candidatos_des or not candidatos_pl:
        raise ValueError("No hay suficientes recetas compatibles con los productos de las tiendas seleccionadas.")
    # Generar candidatos compactos y evaluar el costo real de paquetes.
    rng=random.Random(20261007 + int(dias)*31 + int(personas)*17 + int(presupuesto))
    mejor=None
    mejor_score=-10**18
    for _ in range(2500):
        historial=[]; slots=[]
        for d in range(dias):
            fila=[]
            recientes={x for row in historial[-2:] for x in row}
            for tipo in comidas:
                pool=candidatos_des if tipo=="Desayuno" else candidatos_pl
                disponibles=[x for x in pool if x not in recientes]
                if len(disponibles)<2: disponibles=pool
                rid=rng.choice(disponibles)
                fila.append(rid)
            slots.append(fila); historial.append(fila)
        plan=_plan_con_recetas(slots,catalogo,comidas)
        if not plan: continue
        nombres=[RECETAS_REALES[r]["nombre"].lower() for row in slots for r in row]
        tortilla_count=sum(1 for n in nombres if any(x in n for x in ("tortilla","quesadilla","enfrijolada","taco","enchilada")))
        if tortilla_count > max(5, int(dias*3*0.30)):
            continue
        total=_costo_plan(plan,catalogo,personas)
        limite=presupuesto+TOLERANCIA_PRESUPUESTO
        if total>limite: continue
        # Acercarse al presupuesto sin excederlo, penalizando repetición.
        if total <= presupuesto:
            score=-(presupuesto-total)
        else:
            # Nunca preferir un plan que se pase si existe uno dentro del presupuesto.
            score=-10000-(total-presupuesto)
        score += len(set(x for row in slots for x in row))*4
        if total>=presupuesto*MIN_UTILIZACION_PRESUPUESTO and total<=presupuesto: score+=40
        if score>mejor_score:
            mejor_score=score; mejor=(plan,total)
    if mejor:
        return mejor
    # No se permite devolver un plan que exceda el presupuesto.
    # Si el presupuesto es matemáticamente insuficiente para la combinación
    # de días/personas y las presentaciones disponibles, se informa en lugar
    # de falsear el resultado.
    raise ValueError(
        f"El presupuesto de ${presupuesto:,.2f} no alcanza para {dias} días y {personas} persona(s) con las presentaciones disponibles. "
        "KashCook no va a inventar precios ni reducir las porciones a niveles irreales. "
        "Aumenta el presupuesto, reduce días/personas o cambia la selección de tiendas."
    )
    return mejor


def generar_plan_seguro(dias,personas,presupuesto,comidas,catalogo,estilos=None):
    plan,total=_generar_plan_local(dias,personas,presupuesto,comidas,catalogo,estilos)
    valido,motivo=validar_plan_completo(plan,dias,comidas,catalogo)
    if not valido:
        raise ValueError(motivo)
    return plan,total

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
