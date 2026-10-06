import io
import re
import requests
from bs4 import BeautifulSoup

from groq import Groq

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
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
# KashCook usa estos productos como referencia interna.
# NO se muestran como catálogo al usuario.
#
# Las páginas son productos reales publicados por Alsuper.
# ============================================================

PRODUCTOS_ALSUPER = [

    # -------------------------
    # POLLO
    # -------------------------

    {
        "categoria": "Pollo",
        "url": (
            "https://alsuper.com/producto/"
            "caderita-de-pollo-44400"
        ),
    },

    {
        "categoria": "Pollo",
        "url": (
            "https://alsuper.com/producto/"
            "ala-de-pollo-premium-352077"
        ),
    },


    # -------------------------
    # RES
    # -------------------------

    {
        "categoria": "Res",
        "url": (
            "https://alsuper.com/producto/"
            "pata-de-res-9216"
        ),
    },

    {
        "categoria": "Res",
        "url": (
            "https://alsuper.com/producto/"
            "puchero-de-res-14038"
        ),
    },

    {
        "categoria": "Res",
        "url": (
            "https://alsuper.com/producto/"
            "carne-para-jugo-421810"
        ),
    },

    {
        "categoria": "Res",
        "url": (
            "https://alsuper.com/producto/"
            "sabana-de-res-497606"
        ),
    },


    # -------------------------
    # PUERCO
    # -------------------------

    {
        "categoria": "Puerco",
        "url": (
            "https://alsuper.com/producto/"
            "filete-de-cerdo-371873"
        ),
    },

    {
        "categoria": "Puerco",
        "url": (
            "https://alsuper.com/producto/"
            "molida-de-puerco-13817"
        ),
    },

    {
        "categoria": "Puerco",
        "url": (
            "https://alsuper.com/producto/"
            "milanesa-de-puerco-3405"
        ),
    },

    {
        "categoria": "Puerco",
        "url": (
            "https://alsuper.com/producto/"
            "carne-de-cerdo-para-disco-406195"
        ),
    },


    # -------------------------
    # PESCADO
    # -------------------------

    {
        "categoria": "Pescado",
        "url": (
            "https://alsuper.com/producto/"
            "pescado-rodajeado-391892"
        ),
    },

    {
        "categoria": "Pescado",
        "url": (
            "https://alsuper.com/producto/"
            "filete-de-bagre-basa-3834"
        ),
    },

    {
        "categoria": "Pescado",
        "url": (
            "https://alsuper.com/producto/"
            "filete-de-pescado-finas-hierbas-369673"
        ),
    },

    {
        "categoria": "Pescado",
        "url": (
            "https://alsuper.com/producto/"
            "filete-de-pescado-pimienta-limon-352746"
        ),
    },


    # -------------------------
    # HUEVO
    # -------------------------

    {
        "categoria": "Huevo",
        "url": (
            "https://alsuper.com/producto/"
            "huevo-blanco-12-piezas-655"
        ),
    },


    # -------------------------
    # ATÚN
    # -------------------------

    {
        "categoria": "Atún",
        "url": (
            "https://alsuper.com/producto/"
            "atun"
        ),
    },
]


# ============================================================
# DESPENSA Y VEGETALES
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
# EXTRAER PRECIO
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
        .strip()
    )

    match = re.search(
        r"(\d+(?:\.\d{1,2})?)",
        valor,
    )

    if not match:
        return None

    try:

        precio = float(
            match.group(1)
        )

        if 0 < precio < 10000:
            return precio

    except Exception:
        pass

    return None


# ============================================================
# EXTRAER PRODUCTO
# ============================================================

def extraer_producto_alsuper(
    url,
    categoria,
):

    html = obtener_pagina(
        url
    )

    if not html:
        return None

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    producto = {
        "nombre": None,
        "descripcion": "",
        "precio": None,
        "categoria": categoria,
        "url": url,
    }


    # ========================================================
    # NOMBRE
    # ========================================================

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


    # ========================================================
    # DESCRIPCIÓN
    # ========================================================

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


    # ========================================================
    # PRECIOS
    # ========================================================

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

                precio = convertir_precio(
                    valor
                )

                if precio:
                    precios.append(
                        precio
                    )

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

            precios.append(
                precio
            )


    # Texto

    texto = soup.get_text(
        " ",
        strip=True,
    )

    encontrados = re.findall(
        r"\$\s*([0-9]{1,5}(?:\.[0-9]{1,2})?)",
        texto,
    )

    for valor in encontrados:

        precio = convertir_precio(
            valor
        )

        if precio:

            precios.append(
                precio
            )


    precios_validos = [
        p
        for p in precios
        if 0 < p < 10000
    ]


    if precios_validos:

        producto["precio"] = (
            precios_validos[0]
        )


    # ========================================================
    # VALIDACIÓN
    # ========================================================

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

    total = len(
        PRODUCTOS_ALSUPER
    )

    for i, item in enumerate(
        PRODUCTOS_ALSUPER
    ):

        producto = extraer_producto_alsuper(
            item["url"],
            item["categoria"],
        )

        if producto:

            catalogo.append(
                producto
            )

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


    # Eliminar duplicados

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

        vistos.add(
            clave
        )

        resultado.append(
            producto
        )

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
# GENERACIÓN
# ============================================================

if st.button(
    "🚀 Generar Plan Inteligente",
    use_container_width=True,
):

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


    # ========================================================
    # OBTENER PRODUCTOS
    # ========================================================

    catalogo = []

    if alsuper:

        with st.spinner(
            "🛒 Consultando productos de Alsuper..."
        ):

            catalogo = (
                crear_catalogo_alsuper()
            )


    if not catalogo:

        st.error(
            "❌ No fue posible obtener productos "
            "con precio desde Alsuper."
        )

        st.info(
            "KashCook no generará precios inventados."
        )

        st.stop()


    # ========================================================
    # NO MOSTRAR CATÁLOGO
    #
    # Los datos se utilizan internamente.
    # ========================================================

    catalogo_texto = "\n".join(
        [
            (
                f"- Categoría: {p['categoria']} | "
                f"Producto: {p['nombre']} | "
                f"Descripción: {p['descripcion']} | "
                f"Precio: ${p['precio']:.2f} MXN | "
                f"URL: {p['url']}"
            )
            for p in catalogo
        ]
    )


    # ========================================================
    # PROMPT
    # ========================================================

    prompt_text = f"""
Eres KashCook AI.

Eres chef profesional y especialista en
planeación de comidas económicas.

Tu misión es crear un plan completo de alimentación
y una lista REALISTA de compras.

========================================================
DATOS DEL USUARIO
========================================================

Personas: {personas}

Días: {dias}

Presupuesto máximo:
${presupuesto:.2f} MXN

Tiempos:
{', '.join(tiempos)}

Estilos:
{', '.join(estilos_seleccionados)}

Utensilios:
{', '.join(utensilios)}

Restricciones:
{restringidos if restringidos else 'Ninguna'}


========================================================
CATÁLOGO INTERNO DE PRODUCTOS
========================================================

Utiliza estos productos y precios como referencia.

NO inventes productos.

NO inventes precios.

NO cambies precios.

NO estimes precios.

CATÁLOGO:

{catalogo_texto}


========================================================
REGLAS DE MENÚ
========================================================

Planea exactamente {dias} días.

Cada día debe tener los tiempos seleccionados:

{', '.join(tiempos)}

NO utilices la palabra "Almuerzo".

VARÍA LAS PROTEÍNAS.

En comidas principales procura alternar:

- Pollo
- Res
- Puerco
- Pescado
- Atún
- Huevo
- Otras proteínas económicas

NO hagas todos los días pollo.

No repitas el mismo platillo más de una vez
salvo que sea necesario por presupuesto.

Reutiliza ingredientes para disminuir desperdicio.

Las recetas deben ser realistas para una familia.

Utiliza solamente los utensilios disponibles.


========================================================
LISTA DE COMPRAS
========================================================

La lista debe contener ÚNICAMENTE los productos
que realmente se necesitan comprar para preparar
todo el menú.

NO pongas una lista genérica.

Para cada producto indica:

Producto
Descripción / presentación
Cantidad
Precio unitario
Total

Ejemplo:

| Producto | Descripción | Cantidad | Precio unitario | Total |
| Pollo | Caderita 1 kg | 1 kg | $44.90 | $44.90 |

La descripción debe corresponder al producto
del catálogo.

No inventes presentaciones.

Si un producto no está disponible en el catálogo:

PRECIO NO DISPONIBLE


========================================================
PRESUPUESTO
========================================================

Calcula:

Presupuesto máximo
Total de compras
Dinero restante
Costo por día
Costo por persona


========================================================
FORMATO OBLIGATORIO
========================================================

# DÍA 1

## DESAYUNO
Nombre del platillo

Ingredientes:
- ingrediente
- ingrediente

Preparación:
Explicación completa paso a paso.


## COMIDA
Nombre del platillo

Ingredientes:
- ingrediente
- ingrediente

Preparación:
Explicación completa.


## CENA
Nombre del platillo

Ingredientes:
- ingrediente
- ingrediente

Preparación:
Explicación completa.


# DÍA 2

Mismo formato.


Continúa hasta el DÍA {dias}.


# LISTA DE COMPRAS

| Producto | Descripción / Presentación | Cantidad | Precio unitario | Total |


# RESUMEN DEL PRESUPUESTO

Presupuesto máximo:
Total de compras:
Dinero restante:
Costo por día:
Costo por persona:


# APROVECHAMIENTO

Explica cómo aprovechar los ingredientes
sobrantes para evitar desperdicio.


# NOTA SOBRE PRECIOS

Indica que los precios corresponden a productos
consultados en el catálogo público de Alsuper
y pueden cambiar por promociones, existencias,
zona y fecha de compra.


========================================================
IMPORTANTE
========================================================

Las recetas deben estar COMPLETAS.

No reduzcas las instrucciones.

No resumas las preparaciones.

No omitas ingredientes importantes.

Cada día debe estar claramente separado.
"""


    # ========================================================
    # GROQ
    # ========================================================

    with st.spinner(
        "🤖 KashCook está diseñando tu plan..."
    ):

        try:

            completion = (
                client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt_text,
                        }
                    ],
                    temperature=0.15,
                    max_tokens=12000,
                )
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


    # ========================================================
    # MOSTRAR RESULTADO
    # ========================================================

    st.success(
        "🎉 Plan generado correctamente."
    )

    st.markdown("---")

    st.markdown(
        content
    )


    # ========================================================
    # PDF
    # ========================================================

    pdf_buffer = io.BytesIO()


    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=40,
        bottomMargin=40,
        title="KashCook AI",
        author="KashCook AI",
    )


    styles = getSampleStyleSheet()


    # ========================================================
    # ESTILOS PDF
    # ========================================================

    title_style = ParagraphStyle(
        "KashTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
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
        spaceBefore=10,
        spaceAfter=12,
        alignment=TA_CENTER,
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
        spaceBefore=12,
        spaceAfter=4,
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
        spaceAfter=5,
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
    )


    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor(
            "#444444"
        ),
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
    # LIMPIAR TEXTO
    # ========================================================

    def limpiar_texto(texto):

        if not isinstance(
            texto,
            str,
        ):

            texto = str(
                texto
            )

        texto = texto.replace(
            "```markdown",
            "",
        )

        texto = texto.replace(
            "```",
            "",
        )

        texto = texto.replace(
            "**",
            "",
        )

        texto = texto.replace(
            "__",
            "",
        )

        texto = texto.replace(
            "•",
            "-",
        )

        # ReportLab interpreta & como entidad HTML.
        texto = texto.replace(
            "&",
            "&amp;",
        )

        return texto.strip()


    # ========================================================
    # STORY PDF
    # ========================================================

    story = []


    story.append(
        Paragraph(
            "🍳 KASHCOOK AI",
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
            spaceAfter=15,
        )
    )


    # ========================================================
    # PARSEAR RESPUESTA PARA PDF
    # ========================================================

    lineas = content.split(
        "\n"
    )

    dia_actual = None
    comida_actual = None
    receta_buffer = []


    def agregar_receta_buffer():

        nonlocal receta_buffer

        if not receta_buffer:
            return

        for texto in receta_buffer:

            texto = texto.strip()

            if not texto:
                continue

            story.append(
                Paragraph(
                    limpiar_texto(
                        texto
                    ),
                    body_style,
                )
            )

        receta_buffer = []


    for linea in lineas:

        linea = linea.strip()

        if not linea:
            continue


        # Quitar markdown de código

        if linea.startswith(
            "```"
        ):
            continue


        # ====================================================
        # DÍA
        # ====================================================

        match_dia = re.match(
            r"^#+\s*D[ÍI]A\s+(\d+)",
            linea,
            flags=re.IGNORECASE,
        )

        if match_dia:

            agregar_receta_buffer()

            dia_numero = match_dia.group(
                1
            )

            # Separación entre días
            if dia_actual is not None:

                story.append(
                    PageBreak()
                )

            dia_actual = dia_numero
            comida_actual = None


            # Bloque visual del día

            tabla_dia = Table(
                [
                    [
                        Paragraph(
                            f"DÍA {dia_numero}",
                            day_style,
                        )
                    ]
                ],
                colWidths=[
                    540
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
                            8,
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
                tabla_dia
            )

            continue


        # ====================================================
        # TIEMPO DE COMIDA
        # ====================================================

        match_comida = re.match(
            r"^#+\s*(DESAYUNO|COMIDA|CENA)",
            linea,
            flags=re.IGNORECASE,
        )

        if match_comida:

            agregar_receta_buffer()

            comida_actual = (
                match_comida
                .group(1)
                .upper()
            )

            story.append(
                Paragraph(
                    comida_actual,
                    meal_style,
                )
            )

            continue


        # ====================================================
        # LISTA DE COMPRAS
        # ====================================================

        if re.match(
            r"^#+\s*LISTA DE COMPRAS",
            linea,
            flags=re.IGNORECASE,
        ):

            agregar_receta_buffer()

            story.append(
                Spacer(
                    1,
                    12,
                )
            )

            story.append(
                Paragraph(
                    "LISTA DE COMPRAS",
                    section_style,
                )
            )

            continue


        # ====================================================
        # RESUMEN
        # ====================================================

        if re.match(
            r"^#+\s*RESUMEN DEL PRESUPUESTO",
            linea,
            flags=re.IGNORECASE,
        ):

            agregar_receta_buffer()

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

            continue


        # ====================================================
        # APROVECHAMIENTO
        # ====================================================

        if re.match(
            r"^#+\s*APROVECHAMIENTO",
            linea,
            flags=re.IGNORECASE,
        ):

            agregar_receta_buffer()

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

            continue


        # ====================================================
        # TÍTULOS INTERNOS
        # ====================================================

        if linea.startswith(
            "###"
        ):

            agregar_receta_buffer()

            texto = re.sub(
                r"^#+\s*",
                "",
                linea,
            )

            story.append(
                Paragraph(
                    limpiar_texto(
                        texto
                    ),
                    dish_style,
                )
            )

            continue


        # ====================================================
        # TABLA
        # ====================================================

        if "|" in linea:

            agregar_receta_buffer()

            partes = [
                x.strip()
                for x in linea.split("|")
            ]

            partes = [
                x
                for x in partes
                if x
            ]

            if not partes:
                continue


            # Separador Markdown

            if all(
                set(
                    x.replace(
                        " ",
                        "",
                    )
                ) <= {
                    "-",
                    ":",
                }
                for x in partes
            ):
                continue


            # Crear tabla de compras

            if len(partes) >= 4:

                fila = [
                    Paragraph(
                        limpiar_texto(x),
                        table_body_style,
                    )
                    for x in partes[:5]
                ]

                if len(fila) == 5:

                    # Guardamos temporalmente
                    # como tabla individual.
                    tabla = Table(
                        [fila],
                        colWidths=[
                            90,
                            170,
                            75,
                            85,
                            80,
                        ],
                    )

                    tabla.setStyle(
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
                                    "TOP",
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

                continue


        # ====================================================
        # NEGRITAS / LABELS
        # ====================================================

        if (
            linea.startswith(
                "Ingredientes:"
            )
            or linea.startswith(
                "Preparación:"
            )
        ):

            agregar_receta_buffer()

            story.append(
                Paragraph(
                    limpiar_texto(
                        linea
                    ),
                    dish_style,
                )
            )

            continue


        # ====================================================
        # TEXTO NORMAL
        # ====================================================

        receta_buffer.append(
            linea
        )


    agregar_receta_buffer()


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

        pdf_bytes = (
            pdf_buffer
            .getvalue()
        )


        st.download_button(
            label=(
                "📄 Descargar "
                "Plan KashCook en PDF"
            ),
            data=pdf_bytes,
            file_name=(
                "KashCook_"
                "Plan.pdf"
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
        "👋 Configura tu Groq API Key "
        "para comenzar."
    )
