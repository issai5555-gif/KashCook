    "Bodega Aurrerá": {"emoji":"🟢", "domain":"bodegaaurrera.com.mx"},
}

tiendas_seleccionadas=[]
columnas=st.columns(len(TIENDAS_DISPONIBLES))
for i,tienda in enumerate(TIENDAS_DISPONIBLES):
    with columnas[i]:
        meta=STORE_META_UI[tienda]
        seleccionada=st.checkbox(f"{meta['emoji']} {tienda}", value=(i==0), key=f"tienda_{i}")
        st.markdown(f"<div class='store-card'><div class='store-name'><img class='store-logo' src='https://www.google.com/s2/favicons?domain={meta['domain']}&sz=128'> {tienda}</div><div class='store-sub'>Catálogo de productos y presentaciones</div></div>", unsafe_allow_html=True)
        if seleccionada: tiendas_seleccionadas.append(tienda)
if "Smart" in tiendas_seleccionadas:
    st.info("S-Mart está habilitado para planificar el menú. Su página pública de ofertas no garantiza un catálogo completo con precio y presentación por producto; cualquier artículo que no pueda comprobarse en esa fuente quedará como precio pendiente y no se sumará como precio real.")

col1,col2,col3=st.columns(3)
with col1:
    dias=st.number_input("📅 Días",1,7,7,1)
    st.markdown("<div class='mobile-help'>Cuántos días quieres planear. KashCook generará exactamente esa cantidad.</div>",unsafe_allow_html=True)
with col2:
    personas=st.number_input("👨‍👩‍👧‍👦 Personas",1,10,4,1)
    st.markdown("<div class='mobile-help'>Número de personas que comerán. Las cantidades se escalan para todos.</div>",unsafe_allow_html=True)
with col3:
    presupuesto=st.number_input("💰 Presupuesto total (MXN)",200,10000,1500,100)
    st.markdown("<div class='mobile-help'>Monto máximo disponible para la compra del menú completo.</div>",unsafe_allow_html=True)

col1,col2=st.columns(2)
with col1:
    st.markdown("<div class='section-title' style='font-size:1.25rem'>🍽️ Estilo de comida</div>", unsafe_allow_html=True)
    estilos=st.multiselect("Selecciona uno o varios estilos",["Mexicana","Casera","Asiática","Italiana","Mediterránea","Saludable","Económica","Alta en proteína","Baja en carbohidratos","Desayunos mexicanos","Comida rápida casera"],default=["Mexicana","Casera","Económica"],label_visibility="collapsed")
    st.markdown("<div class='small-note'>KashCook combina las cocinas seleccionadas y busca variedad de platos, proteínas y preparaciones; no se limita a cambiar ingredientes de una misma receta.</div>", unsafe_allow_html=True)
with col2:
    st.markdown("<div class='section-title' style='font-size:1.25rem'>🍳 ¿Qué comidas quieres planear?</div>", unsafe_allow_html=True)
    comidas=st.multiselect("Selecciona las comidas",["Desayuno","Comida","Cena"],default=["Desayuno","Comida","Cena"],label_visibility="collapsed")

col1,col2=st.columns(2)
with col1:
    st.markdown("<div class='section-title' style='font-size:1.25rem'>⚙️ Electrodomésticos disponibles</div>", unsafe_allow_html=True)
    electrodomesticos=st.multiselect("Selecciona los que tienes",["Estufa","Horno","Microondas","Air Fryer","Licuadora","Freidora","Olla de presión","Olla lenta","Parrilla eléctrica"],default=["Estufa","Licuadora"],label_visibility="collapsed")
with col2:
    st.markdown("<div class='section-title' style='font-size:1.25rem'>⚠️ Restricciones y alergias</div>", unsafe_allow_html=True)
    restricciones=st.text_area("Indica alergias, alimentos que no consumen o restricciones",placeholder="Ejemplo: sin cacahuate, no picante, vegetariano...",label_visibility="collapsed")

st.markdown("<div class='section-title'>2 · Crear tu menú</div>", unsafe_allow_html=True)
colg1,colg2=st.columns([3,1])
with colg1: generar_menu=st.button("🚀 GENERAR MI MENÚ", type="primary", use_container_width=True)
with colg2: otra_opcion=st.button("🔄 OTRA OPCIÓN", use_container_width=True)

if otra_opcion:
    st.session_state["kc_semilla_menu"] = __import__("random").SystemRandom().randint(1,10**9)
    st.rerun()

if generar_menu:
    if not comidas:
        st.error("Selecciona al menos una comida.")
        st.stop()
    if not tiendas_seleccionadas:
        st.error("Selecciona al menos una tienda.")
        st.stop()
    catalogo=[]
    for tienda in tiendas_seleccionadas:
        catalogo.extend(copy.deepcopy(CATALOGOS.get(tienda,[])))
    if not catalogo:
        st.error("No hay productos disponibles para las tiendas seleccionadas.")
        st.stop()
    with st.spinner("KashCook está construyendo el menú y después verificará únicamente los productos que realmente necesita..."):
        try:
            # ETAPA 1: menú. NO hacemos búsquedas web todavía. Esto evita decenas
            # de consultas por ingredientes que finalmente ni siquiera se compran.
            # El presupuesto de planificación es deliberadamente un margen de búsqueda;
            # el presupuesto real solo se valida después con precios verificados.
            presupuesto_planificacion=max(float(presupuesto)*1.35, float(presupuesto)+250.0)
            try:
                plan,_=_generar_plan_local(
                    dias=int(dias),personas=int(personas),presupuesto=presupuesto_planificacion,
                    comidas=comidas,catalogo=catalogo,estilos=estilos,
                    electrodomesticos=electrodomesticos,restricciones=restricciones)
            except ValueError:
                presupuesto_planificacion=max(float(presupuesto)*1.60, float(presupuesto)+450.0)
                plan,_=_generar_plan_local(
                    dias=int(dias),personas=int(personas),presupuesto=presupuesto_planificacion,
                    comidas=comidas,catalogo=catalogo,estilos=estilos,
                    electrodomesticos=electrodomesticos,restricciones=restricciones)

            bases_necesarias=sorted({base for dia in plan.get("dias",[]) for comida in dia.get("comidas",[])
                                     for ing in comida.get("ingredientes",[])
                                     for base in [next((p.get("ingrediente_base") for p in catalogo if p.get("id")==ing.get("producto_id")),None)] if base})

            # ETAPA 2: precios. Solo buscamos los ingredientes del menú elegido.
            # Las consultas se hacen en paralelo y se guardan en caché.
            catalogo_optimizado=construir_catalogo_productos_optimo(
                catalogo,bases_necesarias=bases_necesarias,presupuesto=float(presupuesto))

            plan=_reemplazar_productos_por_verificados(plan,catalogo_optimizado)
            compra,total=calcular_compra(plan,catalogo_optimizado,personas)
            estado_verificacion=validar_precios_verificados(compra)

            # Integridad comercial: se puede entregar menú + lista, pero jamás
            # mostrar un total si queda al menos un producto sin precio actual verificado.
            total_verificado = bool(estado_verificacion["ok"])
            if total_verificado and total > float(presupuesto) + TOLERANCIA_PRESUPUESTO:
                # Se conserva el menú para revisión; no se falsean porciones ni precios.
                st.warning(
                    f"Los precios verificados suman ${total:,.2f}, por encima del presupuesto "
                    f"de ${float(presupuesto):,.2f}. KashCook conserva las porciones reales."
                )

            errores_verificacion = {}
            for tienda in tiendas_seleccionadas:
                errores_verificacion[tienda] = {}
                for base in bases_necesarias:
                    rr = PRECIO_CACHE.get(("candidatos", tienda, base), {}).get("resultado", {})
                    if not rr.get("candidatos"):
                        errores_verificacion[tienda][base] = rr.get("error") or "La tienda no devolvió producto/precio legible."

            st.session_state["plan"] = plan
            st.session_state["compra"] = compra
            st.session_state["total"] = total if total_verificado else None
            st.session_state["total_calculado_no_mostrar"] = total if not total_verificado else None
            st.session_state["catalogo_verificado"] = catalogo_optimizado
            st.session_state["estado_verificacion"] = estado_verificacion
            st.session_state["errores_verificacion"] = errores_verificacion
            st.session_state["total_es_real"] = total_verificado
            st.session_state["presupuesto"] = presupuesto
            st.session_state["personas"] = personas
            st.session_state["tiendas"] = tiendas_seleccionadas
            st.session_state["precios_verificados_en"] = datetime.now().astimezone().isoformat(timespec="minutes")
            if total_verificado:
                st.success("Plan generado. Todos los precios se verificaron en las tiendas consultadas.")
            else:
                n = estado_verificacion.get("faltantes", 0)
                st.warning(f"Menú y lista generados. {n} producto(s) siguen sin precio actual verificable; el total queda oculto. No se muestran precios de referencia como reales.")
        except Exception as e:
            st.error(f"Ocurrió un error al generar el plan: {e}")


# ============================================================
# RESULTADO — dashboard visual restaurado
# ============================================================
if "plan" in st.session_state:
    plan=st.session_state["plan"]
    compra=st.session_state["compra"]
    total=st.session_state["total"]
    presupuesto=st.session_state["presupuesto"]
    personas=st.session_state["personas"]
    tiendas=st.session_state["tiendas"]
    st.markdown("<div class='section-title'>3 · Tu dashboard</div>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.markdown(f"<div class='metric-card'><div class='metric-label'>Presupuesto</div><div class='metric-value'>${presupuesto:,.2f}</div></div>",unsafe_allow_html=True)
    with c2:
        valor_total = f"${total:,.2f}" if total is not None and total_es_real else "Sin verificar"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Compra verificada</div><div class='metric-value'>{valor_total}</div></div>",unsafe_allow_html=True)
    with c3:
        disponible = f"${max(0,presupuesto-total):,.2f}" if total is not None and total_es_real else "—"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Disponible</div><div class='metric-value'>{disponible}</div></div>",unsafe_allow_html=True)
    with c4:
        util=(total/presupuesto*100) if presupuesto and total is not None and total_es_real else None
        valor_uso=f"{util:.0f}%" if util is not None else "—"
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Uso del presupuesto</div><div class='metric-value'>{valor_uso}</div></div>",unsafe_allow_html=True)

    verif_hora=st.session_state.get("precios_verificados_en", "consulta actual")
