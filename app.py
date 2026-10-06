import io
import re
import json
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
# ALSUPER
# ============================================================

ALSUPER_URL = "https://alsuper.com"

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


# ============================================================
# CATÁLOGO INTERNO ALSUPER
#
# Estos productos se consultan internamente.
# NO se muestran como catálogo al usuario.
# ============================================================

PRODUCTOS_ALSUPER = [

    # --------------------------------------------------------
    # POLLO
    # --------------------------------------------------------

    {
        "categoria": "Pollo",
        "url": "https://alsuper.com/producto/caderita-de-pollo-44400",
    },

    {
        "categoria": "Pollo",
        "url": "https://alsuper.com/producto/ala-de-pollo-premium-352077",
    },


    # --------------------------------------------------------
    # RES
    # --------------------------------------------------------

    {
        "categoria": "Res",
        "url": "https://alsuper.com/producto/pata-de-res-9216",
    },

    {
        "categoria": "Res",
        "url": "https://alsuper.com/producto/puchero-de-res-14038",
    },

    {
        "categoria": "Res",
        "url": "https://alsuper.com/producto/carne-para-jugo-421810",
    },

    {
        "categoria": "Res",
        "url": "https://alsuper.com/producto/sabana-de-res-497606",
    },


    # --------------------------------------------------------
    # PUERCO
    # --------------------------------------------------------

    {
        "categoria": "Puerco",
        "url": "https://alsuper.com/producto/filete-de-cerdo-371873",
    },

    {
        "categoria": "Puerco",
        "url": "https://alsuper.com/producto/molida-de-puerco-13817",
    },

    {
        "categoria": "Puerco",
        "url": "https://alsuper.com/producto/milanesa-de-puerco-3405",
    },

    {
        "categoria": "Puerco",
        "url": "https://alsuper.com/producto/carne-de-cerdo-para-disco-406195",
    },


    # --------------------------------------------------------
    # PESCADO
    # --------------------------------------------------------

    {
        "categoria": "Pescado",
        "url": "https://alsuper.com/producto/pescado-rodajeado-391892",
    },

    {
        "categoria": "Pescado",
        "url": "https://alsuper.com/producto/filete-de-bagre-basa-3834",
    },

    {
        "categoria": "Pescado",
        "url": "https://alsuper.com/producto/filete-de-pescado-finas-hierbas-369673",
    },

    {
        "categoria": "Pescado",
        "url": "https://alsuper.com/producto/filete-de-pescado-pimienta-limon-352746",
    },


    # --------------------------------------------------------
    # HUEVO
    # --------------------------------------------------------

    {
        "categoria": "Huevo",
        "url": "https://alsuper.com/producto/huevo-blanco-12-piezas-655",
    },
]


# ============================================================
# PRODUCTOS DE DESPENSA
#
# Se mantienen como términos de apoyo para Groq.
# No se presentan como catálogo.
# ============================================================

PRODUCTOS_DESPENSA = [
    "arroz",
    "frijol",
    "tortilla",
    "papa",
    "tomate",
    "jitomate",
    "cebolla",
    "zanahoria",
    "calabaza",
    "chile",
    "aguacate",
    "limon",
    "ajo",
    "leche",
    "queso",
    "crema",
    "pan",
    "avena",
    "platano",
    "manzana",
]


# ============================================================
# DESCARGAR PÁGINA
# ============================================================

@st.cache_data(ttl=900, show_spinner=False)
def obtener_pagina(url):

    try:

        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=25,
        )

        respuesta.raise_for_status()

        return respuesta.text

    except Exception:

        return None


# ============================================================
# CONVERTIR PRECIO
# ============================================================

def convertir_precio(valor):

    if valor is None:
        return None

    valor = str(valor)

    valor = (
        valor
        .replace("$", "")
        .replace(",", "")
        .replace("MXN", "")
        .replace("mxn", "")
        .strip()
    )

    match = re.search(
        r"(\d+(?:\.\d{1,2})?)",
        valor,
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


# ============================================================
# EXTRAER PRODUCTO ALSUPER
# ============================================================

def extraer_producto_alsuper(
    url,
    categoria,
):

    html_pagina = obtener_pagina(url)

    if not html_pagina:
        return None

    soup = BeautifulSoup(
        html_pagina,
        "html.parser",
    )

    producto = {
        "nombre": None,
        "descripcion": "",
        "precio": None,
        "categoria": categoria,
        "url": url,
    }


    # --------------------------------------------------------
    # NOMBRE
    # --------------------------------------------------------

    h1 = soup.find("h1")

    if h1:

        producto["nombre"] = h1.get_text(
            " ",
            strip=True,
        )


    if not producto["nombre"]:

        meta = soup.find(
            "meta",
            property="og:title",
        )

        if meta:

            producto["nombre"] = meta.get(
                "content",
                "",
            )


    # --------------------------------------------------------
    # DESCRIPCIÓN
    # --------------------------------------------------------

    meta_description = soup.find(
        "meta",
        attrs={
            "name": "description"
        },
    )

    if meta_description:

        producto["descripcion"] = (
            meta_description.get(
                "content",
                "",
            )
        )


    if not producto["descripcion"]:

        texto = soup.get_text(
            " ",
            strip=True,
        )

        producto["descripcion"] = texto[:300]


    # --------------------------------------------------------
    # PRECIOS
    # --------------------------------------------------------

    precios = []


    # JSON-LD

    scripts = soup.find_all(
        "script",
        type="application/ld+json",
    )

    for script in scripts:

        try:

            contenido = script.string

            if not contenido:
                continue

            encontrados = re.findall(
                r'"price"\s*:\s*"?(?:MXN\s*)?'
                r'([0-9]+(?:\.[0-9]{1,2})?)',
                contenido,
                flags=re.IGNORECASE,
            )

            for valor in encontrados:

                precio = convertir_precio(valor)

                if precio:
                    precios.append(precio)

        except Exception:
            pass


    # Meta product price

    meta_precio = soup.find(
        "meta",
        property="product:price:amount",
    )

    if meta_precio:

        precio = convertir_precio(
            meta_precio.get("content")
        )

        if precio:
            precios.append(precio)


    # --------------------------------------------------------
    # TEXTO VISIBLE
    # --------------------------------------------------------

    texto = soup.get_text(
        " ",
        strip=True,
    )

    encontrados = re.findall(
        r"\$\s*([0-9]{1,5}(?:\.[0-9]{1,2})?)",
        texto,
    )

    for valor in encontrados:

        precio = convertir_precio(valor)

        if precio:
            precios.append(precio)


    precios_validos = [
        p
        for p in precios
        if 0 < p < 10000
    ]


    if precios_validos:

        producto["precio"] = precios_validos[0]


    # --------------------------------------------------------
    # LIMPIEZA
    # --------------------------------------------------------

    if producto["nombre"]:

        producto["nombre"] = re.sub(
            r"\s+",
            " ",
            producto["nombre"],
        ).strip()


    if producto["descripcion"]:

        producto["descripcion"] = re.sub(
            r"\s+",
            " ",
            producto["descripcion"],
        ).strip()


    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------

    if not producto["nombre"]:
        return None

    if producto["precio"] is None:
        return None

    return producto


# ============================================================
# CREAR CATÁLOGO
# ============================================================

def crear_catalogo_alsuper():

    catalogo = []

    progreso = st.progress(
        0,
        text="Consultando productos de Alsuper...",
    )

    total = len(PRODUCTOS_ALSUPER)

    for i, item in enumerate(PRODUCTOS_ALSUPER):

        producto = extraer_producto_alsuper(
            item["url"],
            item["categoria"],
        )

        if producto:

            catalogo.append(producto)

        progreso.progress(
            int(
                ((i + 1) / total) * 100
            ),
            text=(
                f"Consultando producto "
                f"{i + 1} de {total}"
            ),
        )

    progreso.empty()


    # --------------------------------------------------------
    # ELIMINAR DUPLICADOS
    # --------------------------------------------------------

    resultado = []

    vistos = set()

    for producto in catalogo:

        clave = (
            producto["nombre"]
            .strip()
            .lower()
        )

        if clave in vistos:
            continue

        vistos.add(clave)

        resultado.append(producto)

    return resultado


# ============================================================
# GROQ
# ============================================================

groq_key = st.secrets.get(
    "GROQ_API_KEY",
    "",
)

if not groq_key:

    groq_key = st.text_input(
        "🔑 Ingresa tu Groq API Key (gsk_...):",
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

    smart = st.checkbox(
        "Smart",
        value=False,
    )

    soriana = st.checkbox(
        "Soriana",
        value=False,
    )

    walmart = st.checkbox(
        "Walmart",
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
        "💰 Presupuesto máximo (MXN):",
        min_value=200,
        max_value=10000,
        value=600,
        step=50,
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
    t
    for t, sel in [
        ("Alsuper", alsuper),
        ("Smart", smart),
        ("Soriana", soriana),
        ("Walmart", walmart),
        ("Bodega Aurrerá", aurrera),
    ]
    if sel
]


estilos_seleccionados = [
    e
    for e, sel in [
        ("Mexicana Tradicional", est_mex),
        ("Regional Norteña", est_nor),
        ("Asiática", est_asi),
        ("Italiana", est_ita),
        ("Saludable / Fitness", est_fit),
    ]
    if sel
]


tiempos = [
    t
    for t, sel in [
        ("Desayuno", c_des),
        ("Comida", c_com),
        ("Cena", c_cen),
    ]
    if sel
]


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def limpiar_json_de_groq(texto):

    """
    Extrae un objeto JSON aunque Groq lo envuelva
    accidentalmente en markdown.
    """

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

    inicio = texto.find("{")
    final = texto.rfind("}")

    if inicio == -1 or final == -1:
        return None

    texto = texto[inicio:final + 1]

    try:
        return json.loads(texto)

    except Exception:

        # Segundo intento:
        # quitar caracteres de control

        texto_limpio = re.sub(
            r"[\x00-\x08\x0B\x0C\x0E-\x1F]",
            " ",
            texto,
        )

        try:
            return json.loads(texto_limpio)

        except Exception:
            return None


def numero_seguro(valor, default=0):

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

        return float(default)


def escapar_pdf(texto):

    if texto is None:
        return ""

    texto = str(texto)

    texto = html.escape(
        texto,
        quote=False,
    )

    texto = texto.replace(
        "\n",
        "<br/>",
    )

    return texto


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
    # OBTENER PRODUCTOS
    # --------------------------------------------------------

    catalogo = []

    if alsuper:

        with st.spinner(
            "🛒 Consultando productos de Alsuper..."
        ):

            catalogo = crear_catalogo_alsuper()


    if not catalogo:

        st.error(
            "❌ No fue posible obtener productos "
            "con precio desde Alsuper."
        )

        st.info(
            "KashCook no generará precios inventados."
        )

        st.stop()


    # --------------------------------------------------------
    # CATÁLOGO INTERNO
    # --------------------------------------------------------

    catalogo_texto = "\n".join(
        [
            (
                f"PRODUCTO: {p['nombre']}\n"
                f"CATEGORÍA: {p['categoria']}\n"
                f"DESCRIPCIÓN: {p['descripcion']}\n"
                f"PRECIO REAL CONSULTADO: ${p['precio']:.2f} MXN\n"
                f"URL: {p['url']}"
            )
            for p in catalogo
        ]
    )


    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt_text = f"""
Eres KashCook AI.

Eres chef profesional especializado en:
- planeación de menús familiares;
- cocina mexicana;
- cocina norteña;
- aprovechamiento de ingredientes;
- alimentación económica;
- control de presupuesto.

Tu trabajo es crear un PLAN COMPLETO DE COMIDAS
y una LISTA DE COMPRAS.

========================================================
DATOS DEL USUARIO
========================================================

Personas: {personas}

Días: {dias}

Presupuesto máximo:
${presupuesto:.2f} MXN

Tiempos seleccionados:
{', '.join(tiempos)}

Estilos culinarios:
{', '.join(estilos_seleccionados)}

Utensilios disponibles:
{', '.join(utensilios)}

Restricciones / alergias:
{restringidos if restringidos else 'Ninguna'}


========================================================
PRODUCTOS Y PRECIOS REALES CONSULTADOS
========================================================

Los siguientes productos fueron consultados
directamente desde páginas públicas de Alsuper.

SOLO puedes utilizar estos productos cuando
necesites asignar un precio.

NO inventes precios.

NO cambies precios.

NO redondees precios.

NO estimes precios.

NO inventes presentaciones.

CATÁLOGO INTERNO:

{catalogo_texto}


========================================================
REGLAS DEL MENÚ
========================================================

Debes crear exactamente {dias} días.

Cada día debe contener EXACTAMENTE estos tiempos:

{', '.join(tiempos)}

NO utilices "Almuerzo".

Utiliza "Desayuno", "Comida" y "Cena".

========================================================
VARIEDAD DE PROTEÍNAS
========================================================

ES MUY IMPORTANTE:

No hagas un menú basado principalmente en pollo.

Debes buscar variedad real.

Cuando la cantidad de días y presupuesto lo permitan,
alterna entre:

- Pollo
- Res
- Puerco
- Pescado
- Atún
- Sardinas
- Huevo
- Frijoles
- Queso
- Otras proteínas económicas

Si no existe un producto específico de atún o sardina
con precio en el catálogo, puedes utilizarlos en recetas,
PERO NO debes inventarles un precio.

No repitas el mismo platillo innecesariamente.

No hagas pollo todos los días.

========================================================
APROVECHAMIENTO
========================================================

Diseña el menú para reutilizar ingredientes.

Ejemplo:

Si se compra cebolla para una comida,
puede utilizarse posteriormente.

Evita comprar ingredientes que solamente
se utilizan una vez cuando exista una alternativa.

========================================================
RECETAS
========================================================

Cada receta debe estar COMPLETA.

Para cada platillo incluye:

- nombre;
- ingredientes;
- cantidades;
- preparación paso a paso.

La preparación debe ser suficientemente detallada
para que una persona pueda cocinarla sin tener
que preguntarte qué hacer después.

NO resumas.

NO pongas "preparar como de costumbre".

NO pongas "cocinar hasta que esté listo".

Explica el proceso.

========================================================
LISTA DE COMPRAS
========================================================

La lista de compras debe incluir ÚNICAMENTE
los ingredientes realmente necesarios para
todo el menú.

NO generes un catálogo.

NO muestres productos que no se utilicen.

Para cada producto indica:

- producto;
- descripción / presentación;
- cantidad;
- precio unitario;
- total.

MUY IMPORTANTE:

Si un producto tiene precio real en el catálogo,
utiliza exactamente ese precio.

Si no tiene precio real disponible,
escribe:

"PRECIO NO DISPONIBLE"

No inventes el precio.

========================================================
PRESUPUESTO
========================================================

Calcula:

- presupuesto máximo;
- total de compras con precios disponibles;
- dinero restante;
- costo por día;
- costo por persona.

Si existen productos sin precio,
indica claramente que el total es parcial.

========================================================
FORMATO DE RESPUESTA
========================================================

RESPONDE EXCLUSIVAMENTE CON JSON VÁLIDO.

NO uses Markdown.

NO uses ```.

NO agregues texto antes o después del JSON.

Usa exactamente esta estructura:

{{
  "dias": [
    {{
      "dia": 1,
      "comidas": [
        {{
          "tipo": "Desayuno",
          "nombre": "Nombre del platillo",
          "ingredientes": [
            "cantidad ingrediente",
            "cantidad ingrediente"
          ],
          "preparacion": [
            "Paso 1 completo.",
            "Paso 2 completo.",
            "Paso 3 completo."
          ]
        }}
      ]
    }}
  ],
  "lista_compras": [
    {{
      "producto": "Nombre",
      "descripcion": "Presentación real",
      "cantidad": 1,
      "unidad": "kg",
      "precio_unitario": 100.00,
      "total": 100.00,
      "precio_disponible": true
    }}
  ],
  "presupuesto": {{
    "maximo": {presupuesto:.2f},
    "total_compras": 0.00,
    "dinero_restante": 0.00,
    "costo_por_dia": 0.00,
    "costo_por_persona": 0.00,
    "total_parcial": false
  }},
  "aprovechamiento": [
    "Consejo de aprovechamiento 1.",
    "Consejo de aprovechamiento 2."
  ]
}}

========================================================
REGLAS JSON
========================================================

Debes generar exactamente {dias} objetos dentro de
"dias".

Cada día debe contener exactamente los tiempos:

{', '.join(tiempos)}

Cada comida debe tener:

- nombre;
- ingredientes;
- preparación.

"ingredientes" debe ser una lista.

"preparacion" debe ser una lista de pasos completos.

NO pongas la receta completa en una sola cadena.

La lista de compras debe contener los productos
realmente utilizados en las recetas.

La cantidad debe ser numérica.

Ejemplos:

1 kg:
cantidad = 1
unidad = "kg"

2 paquetes:
cantidad = 2
unidad = "paquetes"

12 piezas:
cantidad = 12
unidad = "piezas"

Cuando no exista precio real:

precio_unitario = null
total = null
precio_disponible = false

Cuando exista precio real:

precio_unitario debe coincidir EXACTAMENTE
con el precio del catálogo.

El total de una línea debe ser:

cantidad × precio_unitario

No inventes precios.

No inventes presentaciones.

========================================================
RESTRICCIONES
========================================================

Nunca utilices alimentos prohibidos por el usuario:

{restringidos if restringidos else 'NINGUNO'}

Utiliza únicamente los utensilios disponibles:

{', '.join(utensilios)}

========================================================
OBJETIVO
========================================================

Quiero un menú práctico, variado, económico,
realista y cocinable.

Quiero variedad de proteínas.

Quiero recetas completas.

Quiero una lista de compras clara.

Quiero precios reales cuando estén disponibles.

No quiero un catálogo visible.

No inventes precios.
"""


    # --------------------------------------------------------
    # GROQ
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
                            "Responde exclusivamente con JSON válido. "
                            "No utilices Markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt_text,
                    },
                ],
                temperature=0.15,
                max_tokens=16000,
            )

            content = (
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
    # PARSEAR JSON
    # --------------------------------------------------------

    datos = limpiar_json_de_groq(
        content
    )


    if not datos:

        st.error(
            "❌ Groq no devolvió un JSON válido."
        )

        st.code(
            content,
            language="text",
        )

        st.stop()


    # --------------------------------------------------------
    # VALIDAR DÍAS
    # --------------------------------------------------------

    dias_generados = datos.get(
        "dias",
        [],
    )

    if len(dias_generados) != dias:

        st.error(
            f"❌ Se solicitaron {dias} días, "
            f"pero Groq generó {len(dias_generados)}."
        )

        st.stop()


    # --------------------------------------------------------
    # VALIDAR COMIDAS
    # --------------------------------------------------------

    for dia_info in dias_generados:

        comidas = dia_info.get(
            "comidas",
            [],
        )

        tipos = [
            str(
                comida.get(
                    "tipo",
                    ""
                )
            ).strip().lower()
            for comida in comidas
        ]

        esperadas = [
            x.lower()
            for x in tiempos
        ]

        faltantes = [
            x
            for x in esperadas
            if x not in tipos
        ]

        if faltantes:

            st.error(
                f"❌ El día {dia_info.get('dia')} "
                f"no contiene todos los tiempos "
                f"solicitados: {', '.join(faltantes)}."
            )

            st.stop()


    # --------------------------------------------------------
    # VALIDAR Y RECALCULAR COMPRAS
    # --------------------------------------------------------

    lista_compras = datos.get(
        "lista_compras",
        [],
    )

    total_calculado = 0.0
    hay_precios_faltantes = False

    for item in lista_compras:

        precio = item.get(
            "precio_unitario"
        )

        cantidad = numero_seguro(
            item.get(
                "cantidad",
                0,
            ),
            0,
        )

        if precio is None:

            item["precio_disponible"] = False
            item["total"] = None
            hay_precios_faltantes = True

        else:

            precio = numero_seguro(
                precio,
                0,
            )

            item["precio_unitario"] = round(
                precio,
                2,
            )

            total_linea = round(
                cantidad * precio,
                2,
            )

            item["total"] = total_linea

            total_calculado += total_linea


    total_calculado = round(
        total_calculado,
        2,
    )


    dinero_restante = round(
        presupuesto - total_calculado,
        2,
    )


    costo_por_dia = round(
        total_calculado / dias,
        2,
    ) if dias else 0


    costo_por_persona = round(
        total_calculado / personas,
        2,
    ) if personas else 0


    datos["presupuesto"] = {
        "maximo": round(
            float(presupuesto),
            2,
        ),
        "total_compras": total_calculado,
        "dinero_restante": dinero_restante,
        "costo_por_dia": costo_por_dia,
        "costo_por_persona": costo_por_persona,
        "total_parcial": hay_precios_faltantes,
    }


    # ========================================================
    # MOSTRAR PLAN
    # ========================================================

    st.success(
        "🎉 Plan generado correctamente."
    )

    st.markdown("---")


    # --------------------------------------------------------
    # MOSTRAR CADA DÍA
    # --------------------------------------------------------

    for dia_info in dias_generados:

        numero_dia = dia_info.get(
            "dia",
            "",
        )

        st.markdown(
            f"## 📅 DÍA {numero_dia}"
        )

        st.markdown("---")

        for comida in dia_info.get(
            "comidas",
            [],
        ):

            tipo = comida.get(
                "tipo",
                "",
            )

            nombre = comida.get(
                "nombre",
                "Platillo",
            )

            st.markdown(
                f"### {tipo.upper()}"
            )

            st.markdown(
                f"**{nombre}**"
            )

            st.markdown(
                "**Ingredientes:**"
            )

            for ingrediente in comida.get(
                "ingredientes",
                [],
            ):

                st.markdown(
                    f"- {ingrediente}"
                )

            st.markdown(
                "**Preparación:**"
            )

            pasos = comida.get(
                "preparacion",
                [],
            )

            for i, paso in enumerate(
                pasos,
                start=1,
            ):

                st.markdown(
                    f"{i}. {paso}"
                )

            st.markdown("---")


    # ========================================================
    # LISTA DE COMPRAS
    # ========================================================

    st.markdown(
        "## 🛒 Lista de compras"
    )

    st.caption(
        "Esta lista contiene únicamente los productos "
        "que KashCook determinó necesarios para el menú."
    )


    filas_compras = []

    for item in lista_compras:

        producto = item.get(
            "producto",
            "",
        )

        descripcion = item.get(
            "descripcion",
            "",
        )

        cantidad = item.get(
            "cantidad",
            "",
        )

        unidad = item.get(
            "unidad",
            "",
        )

        precio = item.get(
            "precio_unitario"
        )

        total = item.get(
            "total"
        )

        if precio is None:

            precio_texto = "Precio no disponible"

        else:

            precio_texto = (
                f"${float(precio):,.2f}"
            )

        if total is None:

            total_texto = "No disponible"

        else:

            total_texto = (
                f"${float(total):,.2f}"
            )

        filas_compras.append(
            [
                producto,
                descripcion,
                f"{cantidad} {unidad}",
                precio_texto,
                total_texto,
            ]
        )


    if filas_compras:

        st.dataframe(
            filas_compras,
            column_config={
                0: "Producto",
                1: "Descripción / Presentación",
                2: "Cantidad",
                3: "Precio unitario",
                4: "Total",
            },
            hide_index=True,
            use_container_width=True,
        )

    else:

        st.warning(
            "No se generó una lista de compras."
        )


    # ========================================================
    # RESUMEN
    # ========================================================

    st.markdown(
        "## 💰 Resumen del presupuesto"
    )

    presupuesto_info = datos["presupuesto"]

    r1, r2, r3, r4 = st.columns(4)

    with r1:

        st.metric(
            "Presupuesto",
            f"${presupuesto_info['maximo']:,.2f}",
        )

    with r2:

        st.metric(
            "Compras",
            f"${presupuesto_info['total_compras']:,.2f}",
        )

    with r3:

        st.metric(
            "Restante",
            f"${presupuesto_info['dinero_restante']:,.2f}",
        )

    with r4:

        st.metric(
            "Costo por día",
            f"${presupuesto_info['costo_por_dia']:,.2f}",
        )


    if hay_precios_faltantes:

        st.warning(
            "⚠️ El total mostrado es PARCIAL porque "
            "uno o más productos no tienen un precio "
            "real disponible en el catálogo consultado."
        )


    # ========================================================
    # APROVECHAMIENTO
    # ========================================================

    st.markdown(
        "## ♻️ Aprovechamiento"
    )

    for consejo in datos.get(
        "aprovechamiento",
        [],
    ):

        st.markdown(
            f"- {consejo}"
        )


    st.markdown("---")

    st.caption(
        "Los precios corresponden a productos "
        "consultados en el catálogo público de Alsuper "
        "y pueden cambiar por promociones, existencias, "
        "zona y fecha de compra."
    )


    # ========================================================
    # PDF
    # ========================================================

    pdf_buffer = io.BytesIO()


    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=38,
        leftMargin=38,
        topMargin=42,
        bottomMargin=42,
        title="KashCook AI - Plan",
        author="KashCook AI",
        allowSplitting=1,
    )


    styles = getSampleStyleSheet()


    # ========================================================
    # ESTILOS PDF
    # ========================================================

    title_style = ParagraphStyle(
        "KashTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
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
        spaceAfter=0,
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
        spaceBefore=10,
        spaceAfter=6,
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
        spaceAfter=7,
    )


    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor(
            "#333333"
        ),
        spaceBefore=5,
        spaceAfter=3,
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
        spaceAfter=5,
        splitLongWords=True,
    )


    ingredient_style = ParagraphStyle(
        "Ingredient",
        parent=body_style,
        leftIndent=10,
        firstLineIndent=-8,
        spaceAfter=3,
    )


    step_style = ParagraphStyle(
        "Step",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-12,
        spaceAfter=5,
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
        spaceBefore=14,
        spaceAfter=8,
    )


    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.white,
        alignment=TA_CENTER,
    )


    table_body_style = ParagraphStyle(
        "TableBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor(
            "#222222"
        ),
    )


    # ========================================================
    # STORY
    # ========================================================

    story = []


    # --------------------------------------------------------
    # PORTADA / ENCABEZADO
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
                f"Plan alimenticio y lista de compras | "
                f"{dias} días | "
                f"{personas} persona(s) | "
                f"Presupuesto máximo "
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
            spaceAfter=12,
        )
    )


    # ========================================================
    # DÍAS
    # ========================================================

    for indice_dia, dia_info in enumerate(
        dias_generados
    ):

        # Cada día empieza en página nueva,
        # excepto el primero.

        if indice_dia > 0:

            story.append(
                PageBreak()
            )


        numero_dia = dia_info.get(
            "dia",
            indice_dia + 1,
        )


        # ----------------------------------------------------
        # ENCABEZADO DEL DÍA
        # ----------------------------------------------------

        tabla_dia = Table(
            [
                [
                    Paragraph(
                        f"DÍA {numero_dia}",
                        day_style,
                    )
                ]
            ],
            colWidths=[
                536
            ],
        )


        tabla_dia.setStyle(
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
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        9,
                    ),
                ]
            )
        )


        story.append(
            tabla_dia
        )

        story.append(
            Spacer(
                1,
                8,
            )
        )


        # ----------------------------------------------------
        # COMIDAS
        # ----------------------------------------------------

        for comida in dia_info.get(
            "comidas",
            [],
        ):

            tipo = comida.get(
                "tipo",
                "",
            )

            nombre = comida.get(
                "nombre",
                "Platillo",
            )


            story.append(
                Paragraph(
                    escapar_pdf(
                        str(tipo).upper()
                    ),
                    meal_style,
                )
            )


            story.append(
                Paragraph(
                    escapar_pdf(nombre),
                    dish_style,
                )
            )


            story.append(
                Paragraph(
                    "INGREDIENTES",
                    label_style,
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
                        + escapar_pdf(
                            ingrediente
                        ),
                        ingredient_style,
                    )
                )


            story.append(
                Paragraph(
                    "PREPARACIÓN",
                    label_style,
                )
            )


            preparacion = comida.get(
                "preparacion",
                [],
            )


            for numero_paso, paso in enumerate(
                preparacion,
                start=1,
            ):

                story.append(
                    Paragraph(
                        (
                            f"{numero_paso}. "
                            f"{escapar_pdf(paso)}"
                        ),
                        step_style,
                    )
                )


            story.append(
                Spacer(
                    1,
                    7,
                )
            )

            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=colors.HexColor(
                        "#D5D5D5"
                    ),
                    spaceBefore=2,
                    spaceAfter=5,
                )
            )


    # ========================================================
    # LISTA DE COMPRAS PDF
    # ========================================================

    story.append(
        PageBreak()
    )


    story.append(
        Paragraph(
            "LISTA DE COMPRAS",
            section_style,
        )
    )


    story.append(
        Paragraph(
            (
                "Productos necesarios para preparar "
                "el menú completo."
            ),
            body_style,
        )
    )


    encabezado = [
        Paragraph(
            "Producto",
            table_header_style,
        ),
        Paragraph(
            "Descripción / Presentación",
            table_header_style,
        ),
        Paragraph(
            "Cantidad",
            table_header_style,
        ),
        Paragraph(
            "Precio unitario",
            table_header_style,
        ),
        Paragraph(
            "Total",
            table_header_style,
        ),
    ]


    tabla_compras = [
        encabezado
    ]


    for item in lista_compras:

        producto = escapar_pdf(
            item.get(
                "producto",
                "",
            )
        )

        descripcion = escapar_pdf(
            item.get(
                "descripcion",
                "",
            )
        )

        cantidad = item.get(
            "cantidad",
            "",
        )

        unidad = escapar_pdf(
            item.get(
                "unidad",
                "",
            )
        )

        precio = item.get(
            "precio_unitario"
        )

        total = item.get(
            "total"
        )


        if precio is None:

            precio_texto = (
                "No disponible"
            )

        else:

            precio_texto = (
                f"${float(precio):,.2f}"
            )


        if total is None:

            total_texto = (
                "No disponible"
            )

        else:

            total_texto = (
                f"${float(total):,.2f}"
            )


        tabla_compras.append(
            [
                Paragraph(
                    producto,
                    table_body_style,
                ),
                Paragraph(
                    descripcion,
                    table_body_style,
                ),
                Paragraph(
                    f"{cantidad} {unidad}",
                    table_body_style,
                ),
                Paragraph(
                    precio_texto,
                    table_body_style,
                ),
                Paragraph(
                    total_texto,
                    table_body_style,
                ),
            ]
        )


    if len(tabla_compras) > 1:

        tabla = Table(
            tabla_compras,
            colWidths=[
                105,
                170,
                70,
                90,
                80,
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
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )


        story.append(
            tabla
        )


    else:

        story.append(
            Paragraph(
                "No se generaron productos.",
                body_style,
            )
        )


    # ========================================================
    # RESUMEN PDF
    # ========================================================

    story.append(
        Spacer(
            1,
            12,
        )
    )


    story.append(
        Paragraph(
            "RESUMEN DEL PRESUPUESTO",
            section_style,
        )
    )


    resumen = datos["presupuesto"]


    resumen_data = [
        [
            Paragraph(
                "Presupuesto máximo",
                table_body_style,
            ),
            Paragraph(
                f"${resumen['maximo']:,.2f} MXN",
                table_body_style,
            ),
        ],
        [
            Paragraph(
                "Total de compras",
                table_body_style,
            ),
            Paragraph(
                f"${resumen['total_compras']:,.2f} MXN",
                table_body_style,
            ),
        ],
        [
            Paragraph(
                "Dinero restante",
                table_body_style,
            ),
            Paragraph(
                f"${resumen['dinero_restante']:,.2f} MXN",
                table_body_style,
            ),
        ],
        [
            Paragraph(
                "Costo por día",
                table_body_style,
            ),
            Paragraph(
                f"${resumen['costo_por_dia']:,.2f} MXN",
                table_body_style,
            ),
        ],
        [
            Paragraph(
                "Costo por persona",
                table_body_style,
            ),
            Paragraph(
                f"${resumen['costo_por_persona']:,.2f} MXN",
                table_body_style,
            ),
        ],
    ]


    tabla_resumen = Table(
        resumen_data,
        colWidths=[
            250,
            266,
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
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#F2F5F8"
                    ),
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
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


    # ========================================================
    # APROVECHAMIENTO PDF
    # ========================================================

    story.append(
        Spacer(
            1,
            12,
        )
    )


    story.append(
        Paragraph(
            "APROVECHAMIENTO",
            section_style,
        )
    )


    for consejo in datos.get(
        "aprovechamiento",
        [],
    ):

        story.append(
            Paragraph(
                "• "
                + escapar_pdf(
                    consejo
                ),
                body_style,
            )
        )


    # ========================================================
    # NOTA DE PRECIOS
    # ========================================================

    story.append(
        Spacer(
            1,
            10,
        )
    )


    story.append(
        HRFlowable(
            width="100%",
            thickness=0.5,
            color=colors.HexColor(
                "#CCCCCC"
            ),
            spaceBefore=3,
            spaceAfter=7,
        )
    )


    story.append(
        Paragraph(
            (
                "NOTA: Los precios corresponden a productos "
                "consultados en el catálogo público de Alsuper "
                "y pueden cambiar por promociones, existencias, "
                "zona y fecha de compra."
            ),
            small_style,
        )
    )


    if hay_precios_faltantes:

        story.append(
            Spacer(
                1,
                5,
            )
        )

        story.append(
            Paragraph(
                (
                    "ADVERTENCIA: El total de compras es "
                    "parcial debido a productos cuyo precio "
                    "real no estuvo disponible durante "
                    "la consulta."
                ),
                small_style,
            )
        )


    # ========================================================
    # PIE DE PÁGINA
    # ========================================================

    def agregar_pie_pagina(
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


    # ========================================================
    # CREAR PDF
    # ========================================================

    try:

        doc.build(
            story,
            onFirstPage=agregar_pie_pagina,
            onLaterPages=agregar_pie_pagina,
        )


        pdf_bytes = pdf_buffer.getvalue()


        st.download_button(
            label=(
                "📄 Descargar "
                "Plan KashCook en PDF"
            ),
            data=pdf_bytes,
            file_name=(
                "KashCook_Plan.pdf"
            ),
            mime="application/pdf",
            use_container_width=True,
        )


    except Exception as e:

        st.error(
            f"Error al generar PDF: {e}"
        )

else:

    st.info(
        "👋 KashCook."
    )
