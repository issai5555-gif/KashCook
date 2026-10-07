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
    """Llamada compacta y tolerante a Groq.

    No usa response_format=json_object porque gpt-oss puede rechazar una
    generación parcialmente válida con json_validate_failed. La validación
    del JSON se hace localmente en extraer_json(), donde podemos reparar
    Markdown, comillas y truncamientos sin perder el control de la app.
    """
    respuesta = cliente.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres KashCook AI. Genera planes de comida. "
                    "Cuando se solicite JSON, responde EXCLUSIVAMENTE un objeto JSON válido, "
                    "sin Markdown, sin comentarios y sin texto adicional. "
                    "Usa respuestas compactas."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperatura,
        max_tokens=6000,
    )

    contenido = respuesta.choices[0].message.content
    if not contenido:
        raise ValueError("Groq no devolvió contenido.")
    return contenido


# ============================================================
# EXTRAER JSON
# ============================================================

def extraer_json(texto):
    """Extrae JSON incluso si el modelo añadió Markdown o texto alrededor."""
    if not texto:
        raise ValueError("La IA no devolvió contenido.")

    texto = str(texto).strip()
    candidatos = [texto]
    limpio = re.sub(r"```(?:json)?", "", texto, flags=re.IGNORECASE).replace("```", "").strip()
    if limpio not in candidatos:
        candidatos.append(limpio)

    # Extrae desde la primera llave hasta la última, ignorando texto exterior.
    ini = limpio.find("{")
    fin = limpio.rfind("}")
    if ini >= 0 and fin > ini:
        candidatos.append(limpio[ini:fin + 1])

    # Quita trailing commas, un error frecuente de modelos generativos.
    for candidato in list(candidatos):
        reparado = re.sub(r",\s*([}\]])", r"\1", candidato)
        if reparado not in candidatos:
            candidatos.append(reparado)

    errores = []
    for candidato in candidatos:
        try:
            obj = json.loads(candidato)
            if isinstance(obj, dict):
                return obj
        except Exception as exc:
            errores.append(str(exc))

    raise ValueError(
        "No fue posible interpretar la respuesta de la IA como JSON. "
        "La respuesta pudo haber quedado truncada; se solicitará una corrección compacta."
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

                # Compatibilidad: algunos modelos devuelven el nombre del
                # ingrediente en lugar del ID. Lo resolvemos contra el catálogo.
                if not producto_id:
                    nombre_ing = ing.get("ingrediente") or ing.get("nombre") or ing.get("ingredient")
                    if nombre_ing:
                        objetivo = normalizar_texto(nombre_ing)
                        for lista in CATALOGOS.values():
                            for producto_cat in lista:
                                if normalizar_texto(producto_cat.get("ingrediente_base")) == objetivo:
                                    producto_id = producto_cat.get("id")
                                    break
                            if producto_id:
                                break

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
            # No existe máximo de ingredientes ni pasos: la calidad de la receta
            # manda. Solo verificamos que exista una preparación utilizable.
            if len(comida.get("preparacion", [])) < 2:
                return False, f"Una comida del día {i} tiene una preparación insuficiente."
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
    # La corrección nunca debe empobrecer las recetas. No imponemos límite de
    # ingredientes ni de pasos: solo exigimos que sean válidos y completos.
    ids = ",".join(p["id"] for p in catalogo)
    plan_compacto = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))
    comidas_texto = ",".join(comidas)
    return f"""Corrige el plan de KashCook. Motivo de validación: {motivo}

Conserva EXACTAMENTE {dias} días y las comidas {comidas_texto}. Mantén o mejora la calidad culinaria. NO reduzcas artificialmente ingredientes ni pasos. Cada platillo puede tener tantos ingredientes y pasos como necesite una receta completa. Usa solo estos IDs cuando puedas: {ids}
Si recibes ingredientes por nombre, usa nombres claros y reales del catálogo.
Devuelve SOLO JSON válido, sin Markdown.
PLAN:{plan_compacto}"""


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

        precio = p.get("precio")
        if precio is None:
            subtotal = None
        else:
            subtotal = paquetes * float(precio)
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
                "precio_unitario": precio,
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
    tiendas, dias, personas, presupuesto, estilos, comidas,
    electrodomesticos, restricciones, catalogo,
):
    """Construye un prompt culinario rico pero compacto.

    La IA diseña recetas; el motor local calcula cantidades, presentaciones
    y costos. No se limita artificialmente el número de ingredientes.
    """
    # Para reducir TPM, enviamos un índice de ingredientes/IDs en vez de
    # descripciones largas y repetitivas de cada producto.
    indice = {}
    for p in catalogo:
        base = str(p.get("ingrediente_base", "")).strip()
        if base:
            indice.setdefault(base, []).append(p["id"])

    catalogo_lineas = [
        f"{base}:{'/'.join(ids[:4])}"
        for base, ids in sorted(indice.items())
    ]

    comidas_texto = ",".join(comidas)
    estilos_texto = ",".join(estilos) if estilos else "Libre"
    electro_texto = ",".join(electrodomesticos) if electrodomesticos else "Cocina convencional"
    restr_texto = (restricciones or "Ninguna").strip()[:900]

    return f"""Eres KashCook AI, chef y planificador culinario profesional.
Crea EXACTAMENTE {dias} días para {personas} personas.

COMIDAS: {comidas_texto}
ESTILOS: {estilos_texto}
EQUIPO DISPONIBLE: {electro_texto}
RESTRICCIONES/ALERGIAS: {restr_texto}
PRESUPUESTO: ${presupuesto:.0f} MXN. No inventes precios ni hagas cálculos de costo.

CALIDAD CULINARIA OBLIGATORIA:
- Los platillos deben ser completos, apetitosos y variados; evita recetas pobres o de 2-3 ingredientes salvo que el platillo realmente lo justifique.
- NO existe límite de ingredientes. Usa todos los ingredientes necesarios para una receta bien hecha: proteína, verduras, base, guarnición, salsa/adobo, especias, aromáticos y complementos cuando correspondan.
- NO existe límite artificial de pasos. Explica la preparación completa, normalmente en 4-10 pasos cuando el platillo lo requiera.
- Incluye guarniciones y componentes que formen parte natural del platillo.
- Alterna pollo, res, cerdo, pescado, atún, sardina, huevo y opciones económicas según estilos y disponibilidad. No repitas la misma proteína de forma monótona.
- Respeta los electrodomésticos disponibles y las restricciones.
- Usa cantidades por persona y unidades culinarias claras: g, ml, pieza, diente, etc.
- Nunca uses la palabra "Almuerzo".
- No agregues ni elimines días o comidas.

ÍNDICE DE INGREDIENTES DISPONIBLES (ingrediente_base: IDs de producto):
{chr(10).join(catalogo_lineas)}

Para cada ingrediente, intenta usar un ID del índice. Si no es posible, usa el nombre exacto del ingrediente_base y KashCook lo resolverá localmente.

FORMATO JSON ÚNICO:
{{"dias":[{{"dia":1,"comidas":[{{"tipo":"Comida","nombre":"Platillo completo","ingredientes":[{{"ingrediente":"pollo","cantidad_por_persona":180,"unidad":"g"}},{{"ingrediente":"tomate","cantidad_por_persona":0.5,"unidad":"pieza"}}],"preparacion":["Paso 1","Paso 2","Paso 3"]}}]}}]}}

Devuelve SOLO el objeto JSON. Exactamente {dias} días y exactamente estas comidas: {comidas_texto}."""


# ============================================================
# PROMPT DE AJUSTE
# ============================================================


def construir_prompt_ajuste(plan, compra, total, presupuesto, personas, catalogo, modo):
    ids = ",".join(p["id"] for p in catalogo)
    plan_compacto = json.dumps(plan, ensure_ascii=False, separators=(",", ":"))
    if modo == "subir":
        objetivo = f"Sube moderadamente el costo hacia ${presupuesto:.0f}, sin superar ${presupuesto + TOLERANCIA_PRESUPUESTO:.0f}."
    else:
        objetivo = f"Baja el costo a máximo ${presupuesto + TOLERANCIA_PRESUPUESTO:.0f}, conservando comidas y porciones razonables."
    return f"""Ajusta este plan. {objetivo}
Conserva EXACTAMENTE días, comidas, calidad culinaria y porciones razonables. NO reduzcas artificialmente ingredientes ni pasos. Puedes sustituir ingredientes/platillos cuando sea necesario para el presupuesto. Usa SOLO IDs válidos cuando los uses. No escribas explicaciones.
IDs:{ids}
PLAN:{plan_compacto}
Devuelve SOLO JSON válido con la misma estructura."""


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
                        texto_pequeno,
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
                        texto_pequeno,
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
# GENERACIÓN POR BLOQUES — EVITA RESPUESTAS JSON TRUNCADAS
# ============================================================

def _indice_ingredientes(catalogo):
    indice = {}
    for p in catalogo:
        base = normalizar_texto(p.get("ingrediente_base", ""))
        if base:
            indice.setdefault(base, []).append(p["id"])
    return indice


def _resolver_producto_por_nombre(valor, catalogo):
    objetivo = normalizar_texto(valor or "")
    if not objetivo:
        return None

    # Coincidencia exacta con ingrediente_base.
    for p in catalogo:
        if normalizar_texto(p.get("ingrediente_base")) == objetivo:
            return p["id"]

    # Coincidencia por inclusión controlada.
    for p in catalogo:
        base = normalizar_texto(p.get("ingrediente_base"))
        nombre = normalizar_texto(p.get("nombre"))
        if objetivo == base or objetivo in base or base in objetivo:
            return p["id"]
        if objetivo and objetivo in nombre:
            return p["id"]
    return None


def _prompt_bloque(tienda_texto, dias_bloque, personas, estilos, comidas,
                   electrodomesticos, restricciones, catalogo):
    indice = _indice_ingredientes(catalogo)
    indice_texto = "\n".join(
        f"{k}:{'/'.join(v[:3])}" for k, v in sorted(indice.items())
    )
    estilos_texto = ",".join(estilos) if estilos else "Libre"
    equipo = ",".join(electrodomesticos) if electrodomesticos else "Cocina convencional"
    restricciones = (restricciones or "Ninguna").strip()[:700]
    comidas_texto = ",".join(comidas)
    dias_texto = ",".join(str(x) for x in dias_bloque)

    return f"""KashCook AI — bloque de días {dias_texto}.\n\nGenera SOLO los días {dias_texto}, para {personas} personas. Cada día debe contener EXACTAMENTE estas comidas: {comidas_texto}.\nEstilos: {estilos_texto}. Equipo: {equipo}. Restricciones: {restricciones}. Tiendas: {tienda_texto}.\n\nCALIDAD: crea platillos completos y sustanciosos, no recetas básicas. No hay límite de ingredientes ni de pasos. Usa los ingredientes necesarios para que cada receta sea realmente buena: proteína, verduras, aromáticos, salsa/adobo, guarnición y complementos cuando correspondan. Normalmente 6-12 ingredientes y 4-10 pasos son perfectamente válidos, pero no fuerces esos números. Varía proteínas y evita repetir preparaciones.\n\nNunca uses la palabra Almuerzo. Cantidades por persona. Unidades claras. Usa ingredientes del índice cuando existan.\nÍNDICE:\n{indice_texto}\n\nJSON: {{"dias":[{{"dia":{dias_bloque[0]},"comidas":[{{"tipo":"Comida","nombre":"...","ingredientes":[{{"ingrediente":"pollo","cantidad_por_persona":180,"unidad":"g"}}],"preparacion":["...","..."]}}]}}]}}\nDevuelve SOLO JSON válido. No Markdown. No explicaciones."""


def generar_plan_por_bloques(cliente, dias, personas, estilos, comidas,
                              electrodomesticos, restricciones, catalogo,
                              tiendas):
    """Genera el menú en bloques para evitar el JSON gigante/truncado."""
    resultado = {"dias": []}
    # 2 días por llamada: suficiente detalle culinario sin disparar TPM.
    bloques = []
    inicio = 1
    while inicio <= int(dias):
        fin = min(inicio + 1, int(dias))
        bloques.append(list(range(inicio, fin + 1)))
        inicio = fin + 1

    tienda_texto = ", ".join(tiendas)

    for bloque in bloques:
        prompt = _prompt_bloque(
            tienda_texto, bloque, personas, estilos, comidas,
            electrodomesticos, restricciones, catalogo
        )
        respuesta = llamar_groq(cliente, prompt, temperatura=0.55)
        try:
            parcial = normalizar_plan(extraer_json(respuesta))
        except Exception:
            # Regeneración del mismo bloque, sin reenviar la respuesta rota.
            prompt += "\nLa respuesta anterior se perdió o quedó truncada. Regenera COMPLETO este mismo bloque."
            respuesta = llamar_groq(cliente, prompt, temperatura=0.25)
            parcial = normalizar_plan(extraer_json(respuesta))

        if not parcial.get("dias"):
            raise ValueError(f"Groq no devolvió los días {bloque}.")
        resultado["dias"].extend(parcial["dias"])

    # Orden y normalización final.
    resultado["dias"] = sorted(resultado["dias"], key=lambda d: int(d.get("dia", 999)))
    return normalizar_plan(resultado)


def toggle_seleccion(clave, valor):
    actual = st.session_state.get(clave, [])
    actual = list(actual)
    if valor in actual:
        actual.remove(valor)
    else:
        actual.append(valor)
    st.session_state[clave] = actual


# ============================================================
# INTERFAZ — KASHCOOK AI MOBILE FIRST
# ============================================================

st.markdown("""
<style>
:root { --kc-lime:#B7E532; --kc-dark:#171A17; --kc-cream:#FFF9ED; --kc-coral:#FF7043; --kc-muted:#69706A; }
.block-container { max-width: 1180px; padding: 1rem 1rem 4rem 1rem; }
html, body, [class*="stApp"] { font-size: 17px !important; }
.stApp { background: linear-gradient(180deg,#fffdf8 0%,#f5f8f0 100%); color:#171A17; }
.kc-hero { border-radius:28px; padding:30px 26px; margin-bottom:22px; background:linear-gradient(135deg,#171A17 0%,#263026 55%,#64751e 100%); color:white; box-shadow:0 12px 35px rgba(23,26,23,.16); }
.kc-hero h1 { font-size:clamp(2rem,6vw,3.5rem); line-height:1; margin:0 0 10px 0; letter-spacing:-1.5px; }
.kc-hero p { font-size:1.05rem; margin:0; color:#f3f7eb; }
.kc-section { font-size:1.35rem; font-weight:800; margin:25px 0 12px 0; }
.kc-card { background:white; border:1px solid #e4e8df; border-radius:20px; padding:18px; box-shadow:0 7px 22px rgba(23,26,23,.07); margin-bottom:14px; }
.kc-store { min-height:100px; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; border-radius:20px; }
.kc-logo { font-size:2rem; font-weight:900; letter-spacing:-1px; }
.kc-muted { color:#69706A; font-size:.92rem; }
.kc-price { font-size:1.55rem; font-weight:900; }
.kc-recipe { border-left:7px solid var(--kc-lime); background:white; border-radius:18px; padding:20px; margin:12px 0; box-shadow:0 7px 20px rgba(23,26,23,.07); }
.kc-day { background:#171A17; color:white; border-radius:16px; padding:12px 16px; margin-top:22px; font-size:1.2rem; font-weight:800; }
.kc-pill { display:inline-block; background:#eef6d3; color:#34410c; border-radius:999px; padding:6px 11px; margin:3px; font-weight:700; font-size:.9rem; }
.kc-note { background:#fff5e6; border:1px solid #ffd9a8; border-radius:16px; padding:14px 16px; }
div.stButton > button { min-height:50px !important; border-radius:16px !important; font-size:16px !important; font-weight:800 !important; border:1px solid #dce2d5 !important; box-shadow:0 3px 10px rgba(0,0,0,.05) !important; white-space:normal !important; }
div.stButton > button[kind="primary"] { background:#B7E532 !important; color:#171A17 !important; border-color:#9ecb18 !important; }
div.stButton > button:hover { transform:translateY(-1px); border-color:#9ecb18 !important; }
[data-testid="stMetric"] { background:white; border:1px solid #e4e8df; padding:15px; border-radius:18px; }
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea { font-size:17px !important; }
@media (max-width: 700px) {
  .block-container { padding: .65rem .7rem 3rem .7rem; }
  .kc-hero { padding:24px 19px; border-radius:22px; }
  .kc-hero p { font-size:.98rem; }
  .kc-card { padding:14px; border-radius:17px; }
  div.stButton > button { min-height:54px !important; font-size:16px !important; }
  [data-testid="stMetric"] { padding:11px; }
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="kc-hero">
  <h1>🍳 KashCook AI</h1>
  <p>Tu sistema inteligente de planificación culinaria y financiera.</p>
  <p style="margin-top:8px;opacity:.9">Recetas completas · compras reales · presupuesto · PDF</p>
</div>
""", unsafe_allow_html=True)

# Estado persistente para botones de selección.
st.session_state.setdefault("kc_tiendas", ["Alsuper"])
st.session_state.setdefault("kc_estilos", ["Mexicana", "Casera", "Económica"])
st.session_state.setdefault("kc_comidas", ["Desayuno", "Comida", "Cena"])
st.session_state.setdefault("kc_electro", ["Estufa", "Licuadora"])


def selector_botones(titulo, opciones, clave, iconos=None, columnas=2):
    st.markdown(f'<div class="kc-section">{titulo}</div>', unsafe_allow_html=True)
    cols = st.columns(columnas)
    seleccion = st.session_state.get(clave, [])
    for i, opcion in enumerate(opciones):
        with cols[i % columnas]:
            pref = (iconos or {}).get(opcion, "")
            texto = f"{pref} {opcion}".strip()
            st.button(
                ("✓  " if opcion in seleccion else "") + texto,
                key=f"sel_{clave}_{i}",
                use_container_width=True,
                type="primary" if opcion in seleccion else "secondary",
                on_click=toggle_seleccion,
                args=(clave, opcion),
            )


selector_botones(
    "🛒 ¿Dónde vas a comprar?",
    ["Alsuper", "Walmart", "Soriana", "Bodega Aurrerá", "Smart"],
    "kc_tiendas",
    {"Alsuper":"🟢", "Walmart":"🔵", "Soriana":"🔴", "Bodega Aurrerá":"🟠", "Smart":"🟣"},
    columnas=2,
)

tienda_info = st.session_state["kc_tiendas"]
if "Smart" in tienda_info:
    st.markdown('<div class="kc-note">Smart está disponible como tienda de selección, pero KashCook no inventará precios si no existe una fuente pública verificable.</div>', unsafe_allow_html=True)
if not tienda_info:
    st.error("Selecciona al menos una tienda.")

st.markdown('<div class="kc-section">⚙️ Configura tu plan</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    dias = st.number_input("📅 Días", min_value=1, max_value=7, value=7, step=1, key="kc_dias")
with c2:
    personas = st.number_input("👨‍👩‍👧‍👦 Personas", min_value=1, max_value=10, value=4, step=1, key="kc_personas")
with c3:
    presupuesto = st.number_input("💰 Presupuesto (MXN)", min_value=200, max_value=10000, value=1500, step=100, key="kc_presupuesto")

selector_botones(
    "🍽️ Estilo de comida",
    ["Mexicana", "Casera", "Saludable", "Económica", "Alta en proteína", "Baja en carbohidratos", "Italiana", "Mediterránea", "Desayunos mexicanos", "Comida rápida casera", "Regional Norteña", "Asiática", "Fitness"],
    "kc_estilos",
    columnas=2,
)

selector_botones(
    "🍳 ¿Qué comidas quieres planear?",
    ["Desayuno", "Comida", "Cena"],
    "kc_comidas",
    columnas=3,
)

selector_botones(
    "🔌 Electrodomésticos disponibles",
    ["Estufa", "Horno", "Microondas", "Air Fryer", "Licuadora", "Freidora", "Olla de presión", "Olla lenta", "Parrilla eléctrica"],
    "kc_electro",
    columnas=2,
)

st.markdown('<div class="kc-section">⚠️ Restricciones y alergias</div>', unsafe_allow_html=True)
restricciones = st.text_area(
    "",
    placeholder="Ejemplo: sin camarón, sin cacahuate, no picante, vegetariano...",
    key="kc_restricciones",
    label_visibility="collapsed",
)

st.markdown('<div class="kc-card"><b>🍴 Importante:</b> KashCook no limita artificialmente tus recetas. Un platillo puede tener 5, 8, 12 o más ingredientes y todos los pasos necesarios para que sea realmente completo.</div>', unsafe_allow_html=True)

if not st.session_state["kc_comidas"]:
    st.warning("Selecciona al menos una comida.")
if not st.session_state["kc_tiendas"]:
    st.warning("Selecciona al menos una tienda.")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

if st.button("🚀 GENERAR MI PLAN", type="primary", use_container_width=True, key="generar_plan_kc"):
    comidas = st.session_state["kc_comidas"]
    tiendas_seleccionadas = st.session_state["kc_tiendas"]
    estilos = st.session_state["kc_estilos"]
    electrodomesticos = st.session_state["kc_electro"]

    if not comidas or not tiendas_seleccionadas:
        st.error("Selecciona al menos una comida y una tienda.")
        st.stop()

    cliente = obtener_cliente_groq()
    if not cliente:
        st.error("Configura GROQ_API_KEY para continuar.")
        st.stop()

    catalogo = []
    for tienda in tiendas_seleccionadas:
        catalogo.extend(CATALOGOS.get(tienda, []))
    if not catalogo:
        st.error("No hay productos disponibles para las tiendas seleccionadas. Si elegiste Smart, agrega también Alsuper, Walmart o Soriana.")
        st.stop()

    with st.spinner("👨‍🍳 KashCook está preparando recetas completas..."):
        try:
            plan = generar_plan_por_bloques(
                cliente, dias, personas, estilos, comidas,
                electrodomesticos, restricciones, catalogo, tiendas_seleccionadas
            )

            valido, motivo = validar_plan_completo(plan, dias, comidas, catalogo)
            if not valido:
                respuesta = llamar_groq(
                    cliente,
                    construir_prompt_reintento(plan, dias, comidas, catalogo, motivo),
                    temperatura=0.25,
                )
                plan = normalizar_plan(extraer_json(respuesta))
                valido, motivo = validar_plan_completo(plan, dias, comidas, catalogo)
                if not valido:
                    raise ValueError(f"La IA devolvió un plan incompleto: {motivo}")

            compra, total = calcular_compra(plan, catalogo, personas)

            # Conservamos la lógica original de ajuste de presupuesto, pero
            # sin exigir que las recetas sean pequeñas.
            if total < presupuesto * MIN_UTILIZACION_PRESUPUESTO and presupuesto >= 500:
                try:
                    respuesta_ajuste = llamar_groq(
                        cliente,
                        construir_prompt_ajuste(plan, compra, total, presupuesto, personas, catalogo, "subir"),
                        temperatura=0.35,
                    )
                    plan_ajustado = normalizar_plan(extraer_json(respuesta_ajuste))
                    ok, _ = validar_plan_completo(plan_ajustado, dias, comidas, catalogo)
                    if ok:
                        compra2, total2 = calcular_compra(plan_ajustado, catalogo, personas)
                        if total2 <= presupuesto + TOLERANCIA_PRESUPUESTO:
                            plan, compra, total = plan_ajustado, compra2, total2
                except Exception:
                    pass

            if total > presupuesto + TOLERANCIA_PRESUPUESTO:
                try:
                    respuesta_ajuste = llamar_groq(
                        cliente,
                        construir_prompt_ajuste(plan, compra, total, presupuesto, personas, catalogo, "bajar"),
                        temperatura=0.25,
                    )
                    plan_ajustado = normalizar_plan(extraer_json(respuesta_ajuste))
                    ok, _ = validar_plan_completo(plan_ajustado, dias, comidas, catalogo)
                    if ok:
                        compra2, total2 = calcular_compra(plan_ajustado, catalogo, personas)
                        if total2 <= presupuesto + TOLERANCIA_PRESUPUESTO:
                            plan, compra, total = plan_ajustado, compra2, total2
                except Exception:
                    pass

            st.session_state.update({
                "plan": plan,
                "compra": compra,
                "total": total,
                "presupuesto": presupuesto,
                "personas": personas,
                "tiendas": tiendas_seleccionadas,
            })
            st.success("✅ Plan generado correctamente.")
        except Exception as e:
            st.error(f"No se pudo generar el plan: {e}")


# ============================================================
# RESULTADOS
# ============================================================
if "plan" in st.session_state:
    plan = st.session_state["plan"]
    compra = st.session_state["compra"]
    total = st.session_state["total"]
    presupuesto_resultado = st.session_state["presupuesto"]
    personas_resultado = st.session_state["personas"]
    tiendas_resultado = st.session_state["tiendas"]

    st.markdown('<div class="kc-section">📊 Resumen del plan</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a: st.metric("💰 Presupuesto", f"${presupuesto_resultado:,.0f}")
    with b: st.metric("🛒 Compra", f"${total:,.2f}")
    with c: st.metric("💵 Disponible", f"${presupuesto_resultado-total:,.2f}" if presupuesto_resultado >= total else f"-${total-presupuesto_resultado:,.2f}")

    if total <= presupuesto_resultado:
        st.success(f"Compra dentro del presupuesto. Te quedan ${presupuesto_resultado-total:,.2f} MXN.")
    else:
        st.warning(f"La compra excede el presupuesto por ${total-presupuesto_resultado:,.2f} MXN.")

    st.markdown('<div class="kc-section">🍽️ Menú completo</div>', unsafe_allow_html=True)
    productos_por_id = {p["id"]: p for lista in CATALOGOS.values() for p in lista}

    for dia in plan.get("dias", []):
        st.markdown(f'<div class="kc-day">Día {dia.get("dia", "")}</div>', unsafe_allow_html=True)
        for comida in dia.get("comidas", []):
            tipo = html.escape(str(comida.get("tipo", "Comida")))
            nombre = html.escape(str(comida.get("nombre", "Receta")))
            st.markdown(f'<div class="kc-recipe"><div class="kc-pill">{tipo}</div><h2 style="margin:9px 0 12px 0;font-size:1.35rem">{nombre}</h2>', unsafe_allow_html=True)
            st.markdown("**Ingredientes:**")
            ingredientes_html = []
            for ing in comida.get("ingredientes", []):
                pid = ing.get("producto_id")
                p = productos_por_id.get(pid, {})
                nombre_ing = p.get("nombre") or ing.get("ingrediente") or pid or "Ingrediente"
                ingredientes_html.append(f'<span class="kc-pill">{html.escape(str(nombre_ing))}: {ing.get("cantidad_por_persona")} {html.escape(str(ing.get("unidad", "")))}/persona</span>')
            st.markdown(" ".join(ingredientes_html), unsafe_allow_html=True)
            st.markdown("**Preparación:**")
            for n, paso in enumerate(comida.get("preparacion", []), 1):
                st.markdown(f"**{n}.** {paso}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="kc-section">🛒 Lista de compra</div>', unsafe_allow_html=True)
    for item in compra:
        precio = item.get("precio_unitario")
        subtotal = item.get("subtotal")
        precio_txt = f"${precio:,.2f}" if precio is not None else "PRECIO NO DISPONIBLE"
        subtotal_txt = f"${subtotal:,.2f}" if subtotal is not None else "—"
        st.markdown(f"""<div class="kc-card"><div style="font-size:1.08rem;font-weight:850">{html.escape(str(item.get("producto","Producto")))}</div><div class="kc-muted">{html.escape(str(item.get("presentacion","")))} · {html.escape(str(item.get("tienda","")))}</div><div style="margin-top:8px"><b>{item.get("paquetes",1)} paquete(s)</b> · {precio_txt} c/u · <b>{subtotal_txt}</b></div></div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="kc-card"><div class="kc-muted">TOTAL CALCULADO</div><div class="kc-price">${total:,.2f} MXN</div></div>', unsafe_allow_html=True)

    pdf_bytes = generar_pdf(
        plan=plan, compra=compra, total=total,
        presupuesto=presupuesto_resultado, personas=personas_resultado,
        tiendas=tiendas_resultado,
    )
    st.download_button(
        "📄 DESCARGAR PLAN COMPLETO EN PDF",
        data=pdf_bytes,
        file_name="KashCook_AI_Plan.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
