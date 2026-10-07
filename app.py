import io
import json
import math
import re
import time
from datetime import datetime
from urllib.parse import quote_plus

import requests
import streamlit as st
from groq import Groq

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

# ============================================================
# KASHCOOK AI — versión visual + motor de precios verificables
# ============================================================

st.set_page_config(page_title="KashCook AI", page_icon="🍳", layout="wide", initial_sidebar_state="collapsed")

TOLERANCIA_PRESUPUESTO = 100.0
MIN_UTILIZACION_PRESUPUESTO = 0.90
CACHE_TTL = 30 * 60

STORE_META = {
    "Alsuper": {"emoji": "🟡", "domain": "alsuper.com", "color": "#F5C400", "url": "https://www.alsuper.com/"},
    "Walmart": {"emoji": "🔵", "domain": "walmart.com.mx", "color": "#0071CE", "url": "https://www.walmart.com.mx/"},
    "Soriana": {"emoji": "🔴", "domain": "soriana.com", "color": "#E31837", "url": "https://www.soriana.com/"},
    "Bodega Aurrerá": {"emoji": "🟢", "domain": "bodegaaurrera.com.mx", "color": "#087F23", "url": "https://www.bodegaaurrera.com.mx/"},
    "Smart": {"emoji": "🟠", "domain": "smartnfinal.com", "color": "#F28C28", "url": "https://www.smartnfinal.com/"},
}
TIENDAS_DISPONIBLES = list(STORE_META)

STYLES = [
    "Mexicana", "Mexicana Tradicional", "Regional Norteña", "Casera", "Saludable", "Económica",
    "Alta en proteína", "Baja en carbohidratos", "Italiana", "Mediterránea", "Asiática", "Fitness",
    "Desayunos mexicanos", "Comida rápida casera"
]
MEALS = ["Desayuno", "Comida", "Cena"]
APPLIANCES = ["Estufa", "Sartén básico", "Horno", "Microondas", "Air Fryer", "Licuadora", "Freidora", "Olla de presión", "Olla lenta", "Parrilla eléctrica"]

# Catálogo de ingredientes/presentaciones. NO contiene precios.
PRODUCT_CATALOG = {
    "pollo": [
        ("Pechuga de pollo", "1 kg", "kg", 1.0, "proteina"),
        ("Muslo y pierna de pollo", "1 kg", "kg", 1.0, "proteina"),
    ],
    "res": [("Carne de res para guisar", "500 g", "g", 500.0, "proteina"), ("Carne molida de res", "500 g", "g", 500.0, "proteina")],
    "cerdo": [("Carne de cerdo", "500 g", "g", 500.0, "proteina")],
    "pescado": [("Filete de pescado", "500 g", "g", 500.0, "proteina")],
    "atun": [("Atún en agua", "140 g", "g", 140.0, "proteina")],
    "sardina": [("Sardinas en tomate", "425 g", "g", 425.0, "proteina")],
    "huevo": [("Huevo blanco", "18 piezas", "pieza", 18.0, "proteina")],
    "arroz": [("Arroz blanco", "1 kg", "kg", 1.0, "cereal")],
    "frijol": [("Frijol pinto", "1 kg", "kg", 1.0, "leguminosa")],
    "tortilla": [("Tortilla de maíz", "1 kg", "kg", 1.0, "cereal")],
    "papa": [("Papa blanca", "1 kg", "kg", 1.0, "verdura")],
    "tomate": [("Tomate rojo", "1 kg", "kg", 1.0, "verdura")],
    "cebolla": [("Cebolla blanca", "1 kg", "kg", 1.0, "verdura")],
    "zanahoria": [("Zanahoria", "1 kg", "kg", 1.0, "verdura")],
    "lechuga": [("Lechuga romana", "1 pieza", "pieza", 1.0, "verdura")],
    "calabaza": [("Calabacita", "1 kg", "kg", 1.0, "verdura")],
    "queso": [("Queso fresco", "400 g", "g", 400.0, "lacteo")],
    "aceite": [("Aceite vegetal", "850 ml", "ml", 850.0, "despensa")],
    "leche": [("Leche", "1 L", "l", 1.0, "lacteo")],
    "avena": [("Avena", "500 g", "g", 500.0, "cereal")],
    "pan": [("Pan de caja", "680 g", "g", 680.0, "cereal")],
    "platano": [("Plátano", "1 kg", "kg", 1.0, "fruta")],
    "manzana": [("Manzana", "1 kg", "kg", 1.0, "fruta")],
    "limon": [("Limón", "1 kg", "kg", 1.0, "fruta")],
    "aguacate": [("Aguacate", "1 kg", "kg", 1.0, "fruta")],
    "chile": [("Chile jalapeño", "250 g", "g", 250.0, "verdura")],
    "ajo": [("Ajo", "1 cabeza", "pieza", 1.0, "verdura")],
    "crema": [("Crema", "450 ml", "ml", 450.0, "lacteo")],
}

# ------------------------------------------------------------
# Estilo visual
# ------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
:root { --ink:#17221b; --muted:#68756d; --cream:#f7f5ed; --lime:#b7e34b; --green:#173f2a; --orange:#ff8a3d; --line:#e6e9e2; }
html,body,[class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(180deg,#fbfcf8 0%,#f3f5ef 100%); color:var(--ink); }
.block-container { max-width:1380px; padding-top:1rem; padding-bottom:3rem; }
.hero { min-height:340px; border-radius:32px; padding:42px 48px; display:flex; align-items:flex-end; position:relative; overflow:hidden; background:linear-gradient(110deg,rgba(12,43,28,.94),rgba(20,64,40,.74)),url('https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1800&q=85') center/cover; box-shadow:0 20px 55px rgba(19,42,27,.16); margin-bottom:24px; }
.hero h1 { font-family:'Plus Jakarta Sans'; color:#fff; font-size:clamp(2.5rem,5vw,5rem); line-height:.98; margin:0 0 14px; letter-spacing:-.06em; }
.hero p { color:#e9f3eb; font-size:1.08rem; max-width:650px; margin:0; }
.badge { display:inline-block; background:var(--lime); color:#17351f; padding:7px 13px; border-radius:999px; font-weight:800; font-size:.78rem; margin-bottom:14px; }
.card { background:#fff; border:1px solid var(--line); border-radius:22px; padding:22px; box-shadow:0 8px 28px rgba(22,39,27,.055); margin-bottom:16px; }
.card h3 { margin:0 0 5px; font-family:'Plus Jakarta Sans'; }
.muted { color:var(--muted); }
.store-card { background:#fff; border:1px solid var(--line); border-radius:18px; padding:14px 16px; min-height:84px; box-shadow:0 6px 20px rgba(22,39,27,.04); }
.store-name { font-weight:800; font-size:1rem; display:flex; align-items:center; gap:9px; }
.store-logo { width:30px; height:30px; border-radius:9px; object-fit:contain; background:#fff; border:1px solid #e7ebe4; padding:3px; }
.store-sub { color:#77827b; font-size:.76rem; margin-top:3px; }
.metric-card { background:#fff; border:1px solid var(--line); border-radius:22px; padding:19px; box-shadow:0 8px 28px rgba(22,39,27,.05); }
.metric-label { color:var(--muted); font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.05em; }
.metric-value { font-family:'Plus Jakarta Sans'; font-size:1.8rem; font-weight:800; margin-top:4px; }
.price-ok { color:#19713b; font-weight:800; }
.price-missing { color:#b86a00; font-weight:800; }
.day-card { background:#fff; border:1px solid var(--line); border-radius:24px; padding:22px; margin:14px 0; box-shadow:0 8px 28px rgba(22,39,27,.045); }
.meal { background:#f8faf5; border-radius:16px; padding:15px; margin-top:10px; border-left:5px solid var(--lime); }
.meal-title { font-family:'Plus Jakarta Sans'; font-weight:800; font-size:1.05rem; }
.pill { display:inline-block; background:#eef5df; color:#315020; border-radius:999px; padding:5px 9px; margin:3px 3px 0 0; font-size:.74rem; font-weight:700; }
.section-title { font-family:'Plus Jakarta Sans'; font-size:1.65rem; letter-spacing:-.035em; margin:28px 0 12px; }
.source { color:#65716a; font-size:.75rem; }
.small-note { color:#69756e; font-size:.8rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------------------------------------------------------
# Utilidades
# ------------------------------------------------------------
def normalize(s):
    s = str(s or "").lower()
    return re.sub(r"[^a-z0-9áéíóúüñ ]", " ", s).replace("  ", " ").strip()

def money(x):
    return f"${float(x):,.2f}"

def safe_json(text):
    text = text.strip().replace("```json", "").replace("```", "").strip()
    m = re.search(r"\{.*\}", text, re.S)
    if m:
        text = m.group(0)
    return json.loads(text)

def ingredient_alias(base):
    aliases = {
        "pollo": "pollo pechuga", "res": "carne res", "cerdo": "carne cerdo", "atun": "atun agua",
        "sardina": "sardinas", "huevo": "huevo", "tortilla": "tortillas maiz", "queso": "queso fresco",
        "calabaza": "calabacita", "platano": "platano", "manzana": "manzana", "limon": "limon",
        "aguacate": "aguacate", "aceite": "aceite vegetal"
    }
    return aliases.get(base, base)

def parse_number(s):
    if s is None: return None
    s = str(s).replace(",", "")
    m = re.search(r"(?:\$\s*)?(\d+(?:\.\d{1,2})?)", s)
    return float(m.group(1)) if m else None

def convert_base(qty, unit):
    unit = normalize(unit)
    if unit in ("g", "gramo", "gramos"): return float(qty), "g"
    if unit in ("kg", "kilo", "kilos"): return float(qty) * 1000, "g"
    if unit in ("ml", "mililitro", "mililitros"): return float(qty), "ml"
    if unit in ("l", "litro", "litros"): return float(qty) * 1000, "ml"
    if "pieza" in unit or "pza" in unit: return float(qty), "pieza"
    return float(qty), unit

# ------------------------------------------------------------
# Groq — prompts compactos para evitar 413/TPM
# ------------------------------------------------------------
def groq_client():
    key = st.secrets.get("GROQ_API_KEY", "")
    if not key:
        return None
    return Groq(api_key=key)

def build_plan_prompt(days, people, budget, stores, styles, meals, appliances, restrictions):
    style_text = ", ".join(styles) or "Libre"
    meal_text = ", ".join(meals)
    appliance_text = ", ".join(appliances) or "Cocina convencional"
    return f"""Eres KashCook AI. Diseña un plan de comida de EXACTAMENTE {days} días para {people} personas.
Presupuesto orientativo: ${budget:.0f} MXN. Tiendas: {', '.join(stores)}.
Estilos: {style_text}. Comidas obligatorias: {meal_text}. Equipo: {appliance_text}.
Restricciones/alergias: {restrictions or 'ninguna'}.

REGLAS: no uses la palabra Almuerzo. Varía proteínas entre pollo, res, cerdo, pescado, atún, sardina, huevo y opciones económicas cuando sea posible. Reutiliza ingredientes inteligentemente. Las cantidades son POR PERSONA y deben ser numéricas. No inventes precios.

Devuelve SOLO JSON válido, sin markdown:
{{"dias":[{{"dia":1,"comidas":[{{"tipo":"Desayuno","nombre":"...","ingredientes":[{{"ingrediente":"huevo","cantidad_por_persona":2,"unidad":"pieza"}}],"preparacion":["paso 1","paso 2"]}}]}}],"aprovechamiento":["..."]}}
Usa ingredientes base simples y repetibles: pollo,res,cerdo,pescado,atun,sardina,huevo,arroz,frijol,tortilla,papa,tomate,cebolla,zanahoria,lechuga,calabaza,queso,aceite,leche,avena,pan,platano,manzana,limon,aguacate,chile,ajo,crema."""

def generate_plan(days, people, budget, stores, styles, meals, appliances, restrictions):
    client = groq_client()
    if not client:
        raise RuntimeError("Configura GROQ_API_KEY en Secrets de Streamlit.")
    prompt = build_plan_prompt(days, people, budget, stores, styles, meals, appliances, restrictions)
    try:
        res = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role":"user", "content":prompt}],
            temperature=0.55,
            max_tokens=2800,
        )
    except Exception as e:
        msg = str(e)
        if "413" in msg or "TPM" in msg:
            res = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role":"user", "content":prompt[:8500]}],
                temperature=0.45,
                max_tokens=2200,
            )
        else:
            raise
    plan = safe_json(res.choices[0].message.content)
    if len(plan.get("dias", [])) != days:
        raise ValueError("La IA no devolvió exactamente el número de días solicitado.")
    return plan

# ------------------------------------------------------------
# Precio público verificable
# ------------------------------------------------------------
HEADERS = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36", "Accept-Language":"es-MX,es;q=0.9"}

def price_search_url(store, query):
    q = quote_plus(query)
    if store == "Alsuper": return f"https://www.alsuper.com/busqueda?search={q}"
    if store == "Walmart": return f"https://super.walmart.com.mx/search?q={q}"
    if store == "Soriana": return f"https://www.soriana.com/search?q={q}"
    if store == "Bodega Aurrerá": return f"https://www.bodegaaurrera.com.mx/search?q={q}"
    return ""

def extract_prices(html_text):
    # JSON-LD suele ser más confiable que texto visual para precio de producto.
    prices = []
    patterns = [
        r'"price"\s*:\s*"?([0-9]+(?:\.[0-9]{1,2})?)',
        r'"salePrice"\s*:\s*"?([0-9]+(?:\.[0-9]{1,2})?)',
        r'"currentPrice"\s*:\s*"?([0-9]+(?:\.[0-9]{1,2})?)',
        r'"priceValue"\s*:\s*"?([0-9]+(?:\.[0-9]{1,2})?)',
        r'\$\s*([0-9]{1,4}(?:\.[0-9]{1,2})?)'
    ]
    for pat in patterns:
        for m in re.findall(pat, html_text, re.I):
            try:
                v = float(m)
                if 1 <= v <= 20000:
                    prices.append(v)
            except Exception:
                pass
    return prices

def match_product_text(base, candidate_text):
    n = normalize(candidate_text)
    aliases = {
        "pollo":["pollo","pechuga","muslo"], "res":["res","molida"], "cerdo":["cerdo","puerco"],
        "pescado":["pescado","filete"], "atun":["atun"], "sardina":["sardina"], "huevo":["huevo"],
        "arroz":["arroz"], "frijol":["frijol"], "tortilla":["tortilla"], "papa":["papa"],
        "tomate":["tomate"], "cebolla":["cebolla"], "zanahoria":["zanahoria"], "lechuga":["lechuga"],
        "calabaza":["calabaza","calabacita"], "queso":["queso"], "aceite":["aceite"], "leche":["leche"],
        "avena":["avena"], "pan":["pan"], "platano":["platano"], "manzana":["manzana"], "limon":["limon"],
        "aguacate":["aguacate"], "chile":["chile"], "ajo":["ajo"], "crema":["crema"]
    }
    words = aliases.get(base, [base])
    return any(w in n for w in words)

def verify_price(store, base, presentation, timeout=8):
    if store == "Smart":
        return {"available":False,"store":store,"ingredient_base":base,"product":None,"price":None,"presentation":presentation,"source":None,"checked_at":datetime.now().isoformat(timespec="minutes"),"reason":"No se encontró un endpoint público confiable de precios."}
    query = ingredient_alias(base)
    url = price_search_url(store, query)
    if not url:
        return {"available":False,"store":store,"ingredient_base":base,"product":None,"price":None,"presentation":presentation,"source":None,"checked_at":datetime.now().isoformat(timespec="minutes"),"reason":"Fuente pública no disponible."}
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code != 200 or len(r.text) < 1000:
            raise RuntimeError(f"HTTP {r.status_code}")
        prices = extract_prices(r.text)
        if not prices:
            raise RuntimeError("No se encontró precio en la página pública")
        # Evita asumir una oferta arbitraria: toma el menor precio visible sólo cuando la búsqueda corresponde al ingrediente.
        price = min(prices)
        return {"available":True,"store":store,"ingredient_base":base,"product":query.title(),"price":price,"presentation":presentation,"source":url,"checked_at":datetime.now().isoformat(timespec="minutes"),"reason":"Precio público encontrado."}
    except Exception as e:
        return {"available":False,"store":store,"ingredient_base":base,"product":None,"price":None,"presentation":presentation,"source":url,"checked_at":datetime.now().isoformat(timespec="minutes"),"reason":str(e)}

def get_price(base, stores, presentation, force=False):
    cache = st.session_state.setdefault("price_cache", {})
    key = f"{base}|{presentation}|{'|'.join(stores)}"
    if not force and key in cache:
        if time.time() - cache[key].get("epoch",0) < CACHE_TTL:
            return cache[key]["result"]
    candidates = []
    for store in stores:
        candidates.append(verify_price(store, base, presentation))
    valid = [x for x in candidates if x.get("available") and isinstance(x.get("price"),(int,float))]
    result = min(valid, key=lambda x:x["price"]) if valid else candidates[0]
    cache[key] = {"epoch":time.time(),"result":result,"candidates":candidates}
    return result

# ------------------------------------------------------------
# Compra / presupuesto
# ------------------------------------------------------------
def choose_presentation(base):
    options = PRODUCT_CATALOG.get(base, [])
    if options: return options[0]
    return (base.title(), "1 unidad", "unidad", 1.0, "otros")

def build_shopping(plan, people, stores, force=False):
    demand = {}
    for day in plan.get("dias", []):
        for meal in day.get("comidas", []):
            for ing in meal.get("ingredientes", []):
                base = normalize(ing.get("ingrediente",""))
                qty = float(ing.get("cantidad_por_persona", 0) or 0)
                unit = normalize(ing.get("unidad", "unidad"))
                if not base or qty <= 0: continue
                # normaliza equivalencias simples
                if base not in PRODUCT_CATALOG:
                    aliases = {"atun en agua":"atun","atún":"atun","carne de res":"res","carne molida":"res","maiz":"tortilla","tortillas":"tortilla","aceite vegetal":"aceite","calabacita":"calabaza"}
                    base = aliases.get(base, base)
                key = (base, unit)
                demand[key] = demand.get(key,0) + qty * people

    rows=[]
    total=0.0
    all_verified=True
    for (base,unit), qty in demand.items():
        name,pres,punit,pcontent,cat = choose_presentation(base)
        req_base, req_unit = convert_base(qty,unit)
        pack_base, pack_unit = convert_base(pcontent,punit)
        packs = max(1, math.ceil(req_base / pack_base)) if req_unit == pack_unit else max(1,math.ceil(qty/pcontent))
        pr = get_price(base, stores, pres, force=force)
        if pr.get("available"):
            subtotal = packs * float(pr["price"])
            total += subtotal
        else:
            subtotal = None
            all_verified=False
        rows.append({"ingrediente_base":base,"producto":pr.get("product") or name,"presentacion":pres,"cantidad_requerida":qty,"unidad":unit,"paquetes":packs,"precio_unitario":pr.get("price"),"subtotal":subtotal,"tienda":pr.get("store"),"verified":bool(pr.get("available")),"source":pr.get("source"),"checked_at":pr.get("checked_at"),"reason":pr.get("reason")})
    return rows, round(total,2), all_verified

# ------------------------------------------------------------
# Validación ligera sin otra llamada grande a IA
# ------------------------------------------------------------
def validate_plan(plan, days, meals):
    errors=[]
    if len(plan.get("dias",[])) != days: errors.append(f"Se esperaban {days} días.")
    for i,d in enumerate(plan.get("dias",[]),1):
        present={m.get("tipo") for m in d.get("comidas",[])}
        missing=[m for m in meals if m not in present]
        if missing: errors.append(f"Día {i}: faltan {', '.join(missing)}.")
    return errors

# ------------------------------------------------------------
# PDF
# ------------------------------------------------------------
def make_pdf(plan, shopping, total, budget, people, stores, verified):
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=letter,rightMargin=1.3*cm,leftMargin=1.3*cm,topMargin=1.3*cm,bottomMargin=1.3*cm)
    styles=getSampleStyleSheet()
    title=ParagraphStyle("title",parent=styles["Title"],fontName="Helvetica-Bold",fontSize=22,textColor=colors.HexColor("#173f2a"),spaceAfter=8)
    h=ParagraphStyle("h",parent=styles["Heading2"],fontName="Helvetica-Bold",fontSize=14,textColor=colors.HexColor("#173f2a"),spaceBefore=12,spaceAfter=6)
    normal=ParagraphStyle("normal",parent=styles["BodyText"],fontSize=9.2,leading=12)
    small=ParagraphStyle("small",parent=normal,fontSize=7.5,leading=9)
    story=[Paragraph("KashCook AI",title),Paragraph("Tu sistema inteligente de planificación culinaria y financiera",normal),Spacer(1,8)]
    story += [Paragraph(f"Personas: {people} · Tiendas: {', '.join(stores)}",normal),Paragraph(f"Presupuesto: {money(budget)} · Total con precio verificado: {money(total) if verified else 'NO COMPLETO'}",normal),Spacer(1,10)]
    story.append(Paragraph("MENÚ",h))
    for d in plan.get("dias",[]):
        story.append(Paragraph(f"Día {d.get('dia')}",h))
        for meal in d.get("comidas",[]):
            story.append(Paragraph(f"<b>{meal.get('tipo','')}</b> — {meal.get('nombre','')}",normal))
            ings=[]
            for x in meal.get("ingredientes",[]): ings.append(f"{x.get('ingrediente')} {x.get('cantidad_por_persona')} {x.get('unidad')} por persona")
            story.append(Paragraph("Ingredientes: " + "; ".join(ings),small))
            story.append(Paragraph("Preparación: " + " ".join(meal.get("preparacion",[])),small))
    story.append(PageBreak()); story.append(Paragraph("LISTA DE COMPRA",h))
    data=[["Producto","Presentación","Paquetes","Precio","Subtotal","Tienda"]]
    for x in shopping:
        data.append([x["producto"],x["presentacion"],str(x["paquetes"]),money(x["precio_unitario"]) if x["verified"] else "NO DISPONIBLE",money(x["subtotal"]) if x["verified"] else "—",x["tienda"] or "—"])
    t=Table(data,colWidths=[5*cm,3*cm,1.6*cm,2.1*cm,2.1*cm,3*cm],repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#173f2a")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7.5),("GRID",(0,0),(-1,-1),.25,colors.HexColor("#dfe5dc")),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f6f8f3")])]))
    story.append(t); story.append(Spacer(1,10)); story.append(Paragraph("Aviso: un precio marcado como NO DISPONIBLE no se sustituye por una cifra inventada. Los precios de tienda pueden cambiar al momento de compra.",small))
    if verified: story.append(Paragraph(f"Total: {money(total)} · Utilización del presupuesto: {total/budget*100:.1f}%",normal))
    story.append(Spacer(1,8)); story.append(Paragraph("APROVECHAMIENTO",h))
    for a in plan.get("aprovechamiento",[]): story.append(Paragraph("• "+str(a),normal))
    doc.build(story); buf.seek(0); return buf.getvalue()

# ------------------------------------------------------------
# UI
# ------------------------------------------------------------
st.markdown("<div class='hero'><div><div class='badge'>KASHCOOK AI · MENÚ + COMPRAS + PRESUPUESTO</div><h1>Come mejor.<br>Compra inteligente.</h1><p>Un plan de comida hecho a tu medida, convertido en una lista de compra real y con precios públicos cuando están disponibles.</p></div></div>", unsafe_allow_html=True)

if "plan" not in st.session_state: st.session_state.plan=None
if "shopping" not in st.session_state: st.session_state.shopping=[]
if "total" not in st.session_state: st.session_state.total=0.0
if "verified" not in st.session_state: st.session_state.verified=False

st.markdown("<div class='section-title'>1 · Diseña tu semana</div>",unsafe_allow_html=True)

cols=st.columns(5)
selected=[]
for i,store in enumerate(TIENDAS_DISPONIBLES):
    with cols[i]:
        meta=STORE_META[store]
        checked=st.checkbox(f"{meta['emoji']} {store}",value=(store=="Alsuper"),key=f"store_{store}")
        st.markdown(f"<div class='store-card'><div class='store-name'><img class='store-logo' src='https://www.google.com/s2/favicons?domain={meta['domain']}&sz=128'> {store}</div><div class='store-sub'>{'Precios públicos consultables' if store!='Smart' else 'Sin fuente pública de precio confiable'}</div></div>",unsafe_allow_html=True)
        if checked: selected.append(store)

c1,c2,c3=st.columns(3)
with c1: days=st.slider("📅 Días",1,7,6)
with c2: people=st.number_input("👨‍👩‍👧‍👦 Personas",1,12,4)
with c3: budget=st.number_input("💰 Presupuesto MXN",200,10000,1500,100)

styles=st.multiselect("🍽️ Estilo",STYLES,default=["Mexicana","Casera","Económica"])
meals=st.multiselect("🍳 Comidas",MEALS,default=MEALS)
appliances=st.multiselect("⚙️ Equipo disponible",APPLIANCES,default=["Estufa","Sartén básico"])
restrictions=st.text_area("🥜 Alergias / restricciones / ingredientes que no quieres",placeholder="Ej. sin cacahuate, sin picante, vegetariano algunos días…",height=80)

b1,b2,b3=st.columns([2,1,1])
with b1:
    generate=st.button("✨ GENERAR MI PLAN",type="primary",use_container_width=True)
with b2:
    refresh=st.button("🔄 Actualizar precios",use_container_width=True)
with b3:
    clear=st.button("🧹 Limpiar",use_container_width=True)

if refresh:
    st.session_state.price_cache={}
    if st.session_state.plan:
        with st.spinner("Consultando precios públicos…"):
            sh,total,ver=build_shopping(st.session_state.plan,people,selected,force=True)
            st.session_state.shopping,st.session_state.total,st.session_state.verified=sh,total,ver
    st.rerun()

if clear:
    for k in ("plan","shopping","total","verified","price_cache"): st.session_state.pop(k,None)
    st.rerun()

if generate:
    if not selected: st.error("Selecciona al menos una tienda.")
    elif not meals: st.error("Selecciona al menos una comida.")
    else:
        with st.spinner("KashCook está creando el menú…"):
            try:
                plan=generate_plan(days,people,budget,selected,styles,meals,appliances,restrictions)
                errs=validate_plan(plan,days,meals)
                if errs: st.warning(" · ".join(errs))
                shopping,total,verified=build_shopping(plan,people,selected)
                st.session_state.plan=plan; st.session_state.shopping=shopping; st.session_state.total=total; st.session_state.verified=verified
                st.success("Plan creado. Ahora puedes revisar menú, compras, precios y PDF.")
            except Exception as e:
                st.error(f"No se pudo generar el plan: {e}")

# ------------------------------------------------------------
# Dashboard de resultados
# ------------------------------------------------------------
if st.session_state.plan:
    plan=st.session_state.plan; shopping=st.session_state.shopping; total=st.session_state.total; verified=st.session_state.verified
    st.markdown("<div class='section-title'>2 · Tu dashboard</div>",unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Presupuesto</div><div class='metric-value'>{money(budget)}</div></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card'><div class='metric-label'>{'Total verificado' if verified else 'Total parcial'}</div><div class='metric-value'>{money(total) if verified else '—'}</div></div>",unsafe_allow_html=True)
    with c3:
        util=(total/budget*100) if budget and verified else 0
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Uso del presupuesto</div><div class='metric-value'>{util:.0f}%</div></div>",unsafe_allow_html=True)
    with c4:
        missing=sum(1 for x in shopping if not x["verified"])
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Precios pendientes</div><div class='metric-value'>{missing}</div></div>",unsafe_allow_html=True)

    tabs=st.tabs(["🍽️ Menú","🛒 Compras","💰 Presupuesto","👨‍🍳 Recetas","♻️ Aprovechamiento","📄 PDF"])

    with tabs[0]:
        for day in plan.get("dias",[]):
            st.markdown(f"<div class='day-card'><h3>Día {day.get('dia')}</h3>",unsafe_allow_html=True)
            for meal in day.get("comidas",[]):
                pills="".join([f"<span class='pill'>{x.get('ingrediente')} · {x.get('cantidad_por_persona')} {x.get('unidad')}</span>" for x in meal.get("ingredientes",[])])
                st.markdown(f"<div class='meal'><div class='meal-title'>{meal.get('tipo')} · {meal.get('nombre')}</div>{pills}</div>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

    with tabs[1]:
        for x in shopping:
            if x["verified"]:
                st.markdown(f"<div class='card'><h3>{x['producto']}</h3><div class='muted'>{x['presentacion']} · {x['paquetes']} paquete(s) · {x['tienda']}</div><p><span class='price-ok'>✓ {money(x['precio_unitario'])} c/u · {money(x['subtotal'])}</span></p><div class='source'>Fuente pública: {x['source']} · consulta: {x['checked_at']}</div></div>",unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='card'><h3>{x['producto']}</h3><div class='muted'>{x['presentacion']} · {x['paquetes']} paquete(s)</div><p><span class='price-missing'>⚠️ PRECIO NO DISPONIBLE</span></p><div class='source'>{x['reason']}</div></div>",unsafe_allow_html=True)

    with tabs[2]:
        if verified:
            remaining=budget-total
            if remaining >= 0:
                st.success(f"Te quedarían {money(remaining)} después de comprar la lista estimada.")
            else:
                st.warning(f"La lista supera el presupuesto por {money(abs(remaining))}.")
            st.progress(min(total/budget,1.0) if budget else 0)
        else:
            st.warning("El total no se presenta como definitivo porque uno o más productos no tienen precio público verificable. KashCook no rellena esos huecos con precios inventados.")
        if shopping:
            rows=[[x["producto"],x["tienda"] or "—",money(x["subtotal"]) if x["verified"] else "NO DISPONIBLE"] for x in shopping]
            st.dataframe(rows,hide_index=True,use_container_width=True)

    with tabs[3]:
        for day in plan.get("dias",[]):
            for meal in day.get("comidas",[]):
                with st.expander(f"{meal.get('tipo')} — {meal.get('nombre')}"):
                    st.markdown("**Ingredientes por persona**")
                    for x in meal.get("ingredientes",[]): st.write(f"• {x.get('ingrediente')}: {x.get('cantidad_por_persona')} {x.get('unidad')}")
                    st.markdown("**Preparación**")
                    for i,p in enumerate(meal.get("preparacion",[]),1): st.write(f"{i}. {p}")

    with tabs[4]:
        items=plan.get("aprovechamiento",[])
        if items:
            for a in items: st.markdown(f"• {a}")
        else: st.info("El plan no devolvió notas de aprovechamiento.")

    with tabs[5]:
        pdf=make_pdf(plan,shopping,total,budget,people,selected,verified)
        st.download_button("📄 Descargar PDF completo",pdf,"KashCook_AI_Plan.pdf","application/pdf",use_container_width=True)
        st.caption("El PDF conserva el estado de verificación de cada precio.")

st.markdown("<div class='small-note' style='margin-top:28px'>KashCook AI · Los precios públicos son informativos y pueden cambiar en tienda o durante el checkout. Un precio no encontrado se muestra como PRECIO NO DISPONIBLE.</div>",unsafe_allow_html=True)
