import streamlit as st
import folium
from streamlit_folium import st_folium

# --- IMPORTACIONES ---
from src.api_client import AgroClimaClient
from src.agro_logic import AgroAnalisis

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroDecision Pro", page_icon="🌱", layout="wide")

# --- LÓGICA DE INTERPRETACIÓN EXPERTA ---
def generar_consejos_experto(datos, categoria, ph_suelo):
    """
    Genera la interpretación profunda y consultoría técnica.
    """
    consejos = []
    
    # Variables
    temp = datos['clima']['temp_actual']
    humedad = datos['clima']['humedad']
    altitud = datos['topografia']['altitud']
    
    # 1. CULTIVOS
    if categoria == "cultivos":
        if altitud > 3500 and temp < 10:
            consejos.append(("❄️ **Riesgo de Helada:** A esta altitud la radiación nocturna es alta. Usar mallas o variedades nativas.", "warning"))
        
        if temp > 28 and humedad < 40:
            consejos.append(("🍂 **Estrés Hídrico Atmosférico:** La planta cerrará estomas. El riego debe ser frecuente y nocturno.", "warning"))
        elif temp > 25 and humedad > 80:
            consejos.append(("🍄 **Alerta Fúngica:** Calor + Humedad = Roya/Mildiu. Aplicar fungicida preventivo.", "error"))
        
        if ph_suelo < 5.2:
            consejos.append(("☠️ **Acidez Severa:** El Aluminio tóxico está libre y quema raíces. Aplicar cal dolomita urgentemente.", "error"))
        elif ph_suelo > 7.5:
            consejos.append(("⚠️ **Bloqueo de Nutrientes:** pH Alcalino. El hierro se insolubiliza (hojas amarillas). Usar quelatos.", "warning"))

    # 2. ANIMALES
    elif categoria in ["bovinos", "porcinos", "aves"]:
        if categoria == "bovinos" and altitud > 2800:
            consejos.append(("⛰️ **Riesgo de Mal de Altura (Brisket):** Baja presión de oxígeno. Evitar Holstein puro.", "error"))
        
        if categoria == "porcinos" and temp > 27:
            consejos.append(("🐷 **Estrés Térmico:** Los cerdos no sudan. Riesgo de muerte. Necesitan duchas/nebulizadores.", "error"))
        
        if humedad > 85:
            consejos.append(("🦠 **Riesgo Sanitario:** Cama húmeda = Bacterias y Amoníaco. Ventilar y limpiar hoy mismo.", "warning"))

    return consejos

# --- ESTADO DE SESIÓN ---
if 'lat' not in st.session_state: st.session_state['lat'] = -12.0464
if 'lon' not in st.session_state: st.session_state['lon'] = -77.0428
if 'analisis_listo' not in st.session_state: st.session_state['analisis_listo'] = False
if 'datos_api' not in st.session_state: st.session_state['datos_api'] = None
if 'lista_opciones' not in st.session_state: st.session_state['lista_opciones'] = []

# --- TÍTULO ---
st.title("🌱 AgroDecision: Sistema de Zonificación")

col_mapa, col_config = st.columns([2, 1])

# --- COLUMNA 1: MAPA ---
with col_mapa:
    st.subheader("📍 Ubicación")
    
    tab_buscar, tab_coords = st.tabs(["🔍 Buscador", "🌐 GPS"])
    
    with tab_buscar:
        # AQUÍ ESTÁ EL CAMBIO: Espaciado para bajar el buscador
        st.write("") 
        st.write("") 
        
        c1, c2 = st.columns([3, 1])
        texto = c1.text_input("Lugar:", placeholder="Ej: Lurin, Peru", label_visibility="collapsed") # label_collapsed para que se vea más limpio
        
        if c2.button("Buscar 🔎"):
            cli = AgroClimaClient()
            st.session_state['lista_opciones'] = cli.buscar_opciones_ciudades(texto)
            if not st.session_state['lista_opciones']:
                st.error("No encontrado.")

        if st.session_state['lista_opciones']:
            st.write("") # Un poco más de aire
            opciones = {op['label']: op for op in st.session_state['lista_opciones']}
            sel = st.selectbox("Selecciona la coincidencia:", list(opciones.keys()))
            if st.button("📍 Ir al lugar seleccionado"):
                lugar = opciones[sel]
                st.session_state['lat'] = lugar['lat']
                st.session_state['lon'] = lugar['lon']
                st.session_state['analisis_listo'] = False
                st.rerun()

    with tab_coords:
        st.write("") # Espaciado también aquí
        c_lat, c_lon = st.columns(2)
        n_lat = c_lat.number_input("Latitud", value=st.session_state['lat'], format="%.5f")
        n_lon = c_lon.number_input("Longitud", value=st.session_state['lon'], format="%.5f")
        if st.button("Actualizar"):
            st.session_state['lat'] = n_lat
            st.session_state['lon'] = n_lon
            st.session_state['analisis_listo'] = False
            st.rerun()

    # Mapa
    tipo = st.radio("Capa:", ["Satélite", "Calles"], horizontal=True)
    tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' if tipo == "Satélite" else "OpenStreetMap"
    attr = 'Esri' if tipo == "Satélite" else "OSM"

    m = folium.Map(location=[st.session_state['lat'], st.session_state['lon']], zoom_start=14, tiles=tiles, attr=attr)
    folium.Marker([st.session_state['lat'], st.session_state['lon']], icon=folium.Icon(color="red", icon="leaf")).add_to(m)
    st_folium(m, height=350, width="100%")

# --- COLUMNA 2: CONFIGURACIÓN ---
with col_config:
    st.subheader("⚙️ Configuración")
    categoria = st.selectbox("Categoría", ["cultivos", "bovinos", "porcinos", "aves"])
    
    analista = AgroAnalisis()
    df_reglas = analista.cargar_reglas(categoria)
    
    variedad = None
    if df_reglas is not None:
        variedad = st.selectbox("Variedad / Raza", df_reglas['variedad'].unique())
        st.write("")
        if st.button("Analizar Viabilidad", type="primary"):
            with st.spinner("Consultando satélites..."):
                cli = AgroClimaClient()
                st.session_state['datos_api'] = cli.obtener_todo(st.session_state['lat'], st.session_state['lon'])
                st.session_state['analisis_listo'] = True

st.divider()

# --- RESULTADOS ---
if st.session_state['analisis_listo'] and st.session_state['datos_api']:
    datos = st.session_state['datos_api']
    
    # 1. Ajuste de pH
    col_ph1, col_ph2 = st.columns([1, 3])
    with col_ph1:
        ph_user = st.number_input("pH Suelo", 4.0, 9.0, float(datos['suelo']['ph']), 0.1)
        datos['suelo']['ph'] = ph_user
    with col_ph2:
        st.info("💡 Ajusta el pH si tienes análisis de laboratorio.")

    # 2. Métricas (5 Columnas con LUZ)
    st.subheader("📡 Condiciones Ambientales")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("🌡️ Temp", f"{datos['clima']['temp_actual']} °C")
    m2.metric("💧 Humedad", f"{datos['clima']['humedad']} %")
    m3.metric("⛰️ Altitud", f"{datos['topografia']['altitud']:.0f} msnm")
    m4.metric("☀️ Horas Luz", f"{datos['solar']['horas_luz']} h") 
    m5.metric("🌧️ Lluvia", f"{int(datos['clima']['precipitacion_anual_estimada'])} mm")

    # 3. Análisis
    score, razones_raw, riesgo = analista.analizar(datos, categoria, variedad)
    consejos_expertos = generar_consejos_experto(datos, categoria, ph_user)
    
    # Obtener regla específica para comparar (Para el mensaje "Ideal vs Actual")
    regla_actual = df_reglas[df_reglas['variedad'] == variedad].iloc[0]

    # Pestañas
    t1, t2, t3 = st.tabs(["📊 Informe General", "🧬 Fisiología", "📝 Plan de Manejo"])

    with t1:
        if score >= 80: st.success(f"### ✅ APTO - Puntuación: {score}/100")
        elif score >= 50: st.warning(f"### ⚠️ RIESGO MEDIO - Puntuación: {score}/100")
        else: st.error(f"### ⛔ NO APTO - Puntuación: {score}/100")
        
        st.write("**Diagnóstico Rápido:**")
        if not razones_raw: st.success("Todas las variables están en rango óptimo.")
        else:
             for r in razones_raw:
                if "⛔" in r: st.error(r)
                elif "⚠️" in r: st.warning(r)
                else: st.info(r)

    with t2:
        st.write(f"### Fisiología: {variedad}")
        if categoria in ["bovinos", "porcinos", "aves"]:
            ith = (0.8 * datos['clima']['temp_actual']) + ((datos['clima']['humedad']/100) * (datos['clima']['temp_actual'] - 14.4)) + 46.4
            st.metric("Índice de Confort (ITH)", f"{ith:.1f}")
            if ith < 72: st.success("Confort térmico óptimo.")
            elif ith < 78: st.warning("Alerta leve de estrés.")
            else: st.error("Peligro: Estrés calórico severo.")
        else:
            balance = datos['clima']['precipitacion_anual_estimada'] - 800
            st.metric("Balance Hídrico", f"{int(balance)} mm", delta="Exceso" if balance > 0 else "Falta")
            if balance < 0: st.warning(f"Se necesita riego.")
            else: st.success("Lluvia suficiente.")

    with t3:
        st.subheader("Consultoría Técnica Detallada")
        
        # --- AQUI ESTÁ LA MAGIA DE LOS MENSAJES COMPARATIVOS ---
        # 1. Mensajes de Comparación (Ideal vs Actual)
        hay_problemas = False
        
        # Temp
        if datos['clima']['temp_actual'] < regla_actual['temp_min'] or datos['clima']['temp_actual'] > regla_actual['temp_max']:
            st.warning(f"⚠️ Temperatura actual ({datos['clima']['temp_actual']}°C) fuera de rango ideal ({regla_actual['temp_min']}-{regla_actual['temp_max']}°C).")
            hay_problemas = True
            
        # pH (Solo cultivos)
        if categoria == "cultivos":
            if ph_user < regla_actual['ph_min'] or ph_user > regla_actual['ph_max']:
                st.warning(f"⚠️ pH del suelo ({ph_user}) inadecuado. Ideal: {regla_actual['ph_min']}-{regla_actual['ph_max']}.")
                hay_problemas = True

        # Agua (Solo cultivos)
        if categoria == "cultivos":
            req_agua = 500 # Valor base referencia
            if datos['clima']['precipitacion_anual_estimada'] < req_agua:
                faltante = req_agua - datos['clima']['precipitacion_anual_estimada']
                st.info(f"💧 Falta de agua estimada ({int(datos['clima']['precipitacion_anual_estimada'])}mm). Requiere: {req_agua}mm. Déficit: {int(faltante)}mm.")
                hay_problemas = True

        if not hay_problemas:
            st.success("✅ Temperatura, pH y Agua están dentro de los parámetros ideales.")

        st.divider()
        
        # 2. Consejos Expertos (Interpretación)
        st.write("**Plan de Acción:**")
        if not consejos_expertos:
            st.info("Las condiciones son estándar. Aplicar plan de manejo preventivo normal.")
        
        for texto, tipo in consejos_expertos:
            if tipo == "error": st.error(texto)
            elif tipo == "warning": st.warning(texto)
            else: st.info(texto)