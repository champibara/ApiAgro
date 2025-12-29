import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

# --- IMPORTACIONES ---
# Se importan los módulos de extracción (API) y procesamiento (Lógica)
from src.api_client import AgroClimaClient
from src.agro_logic import AgroAnalisis

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroDecision Pro", page_icon="🌱", layout="wide")

# --- 1. FUNCIÓN DE CONSEJOS (CORREGIDA PARA pH MANUAL) ---
def generar_consejos_experto(datos, categoria, ph_manual):
    """
    SISTEMA EXPERTO DE DIAGNÓSTICO:
    Analiza las variables extraídas y genera alertas agronómicas.
    Recibe el ph_manual directamente del input del usuario para asegurar reactividad.
    """
    consejos = []
    
    # Extraer variables del clima (usamos .get para evitar errores)
    temp = datos['clima'].get('temp_actual', 20)
    humedad = datos['clima'].get('humedad', 60)
    altitud = datos['topografia'].get('altitud', 500)
    lluvia = datos['clima'].get('precipitacion_anual_estimada', 0)
    
    # Usamos EXPLICITAMENTE el ph_manual modificado por el usuario
    ph_suelo = float(ph_manual) 
    
    # =======================================================
    # 🚨 ANÁLISIS DE CULTIVOS
    # =======================================================
    if categoria == "cultivos":
        
        # --- LÓGICA DE pH (Reacciona al cambio del usuario) ---
        if ph_suelo < 5.5:
            msg = (
                f"☠️ **ACIDEZ DETECTADA (pH {ph_suelo})**\n\n"
                "**Diagnóstico:** El suelo es demasiado ácido. Hay toxicidad por Aluminio y bloqueo de Fósforo.\n"
                "**🛡️ Solución:** Aplicar **Cal Dolomita** inmediatamente (aprox 2 ton/ha)."
            )
            consejos.append((msg, "error"))
            
        elif ph_suelo > 7.8:
            msg = (
                f"⚠️ **ALCALINIDAD ALTA (pH {ph_suelo})**\n\n"
                "**Diagnóstico:** Bloqueo de micronutrientes (Hierro, Zinc).\n"
                "**🛡️ Solución:** Aplicar materia orgánica acidificante o Azufre elemental."
            )
            consejos.append((msg, "warning"))

        # --- LÓGICA CLIMÁTICA ---
        if altitud > 3500 and temp < 10:
            consejos.append(("❄️ **RIESGO DE HELADAS**\n\n**Diagnóstico:** Radiación nocturna extrema.\n**🛡️ Plan:** Riego al atardecer y Potasio foliar.", "error"))
        
        if temp > 22 and humedad > 80:
            consejos.append(("🍄 **ALERTA HONGOS**\n\n**Diagnóstico:** Alta humedad + calor.\n**🛡️ Plan:** Poda de ventilación y Trichoderma.", "error"))
        
        if temp > 28 and humedad < 40:
            consejos.append(("🍂 **ESTRÉS HÍDRICO (Aire Seco)**\n\n**Diagnóstico:** Cierre de estomas.\n**🛡️ Plan:** Riegos cortos frecuentes y cobertura (Mulch).", "warning"))
        
        if lluvia < 500:
            consejos.append((f"💧 **DÉFICIT LLUVIA ({int(lluvia)} mm)**\n\n**Diagnóstico:** Requiere riego.\n**🛡️ Plan:** Instalar sistema por goteo.", "warning"))

    # =======================================================
    # 🚨 ANÁLISIS DE ANIMALES
    # =======================================================
    elif categoria in ["bovinos", "porcinos", "aves"]:
        if categoria == "bovinos" and altitud > 2800:
            consejos.append(("⛰️ **RIESGO: MAL DE ALTURA**\n\n**Diagnóstico:** Hipoxia.\n**🛡️ Plan:** Evitar Holstein puro.", "error"))
        if categoria == "porcinos" and temp > 27:
            consejos.append(("🐷 **ESTRÉS TÉRMICO**\n\n**Diagnóstico:** Riesgo de infarto.\n**🛡️ Plan:** Nebulizadores y ventilación.", "error"))
        if humedad > 85:
            consejos.append(("🦠 **BACTERIOSIS**\n\n**Diagnóstico:** Camas húmedas.\n**🛡️ Plan:** Cal viva y reducir densidad.", "warning"))

    # =======================================================
    # ✅ SI TODO ESTÁ BIEN
    # =======================================================
    if not consejos:
        consejos.append(("✨ **CONDICIONES IDEALES**\n\nEl ambiente es favorable.\n**🚀 Plan:** Enfocarse en nutrición para alto rendimiento.", "success"))

    return consejos

# --- ESTADO DE SESIÓN ---
# Mantiene la persistencia de datos entre interacciones de la interfaz
if 'lat' not in st.session_state: st.session_state['lat'] = -12.0464
if 'lon' not in st.session_state: st.session_state['lon'] = -77.0428
if 'analisis_listo' not in st.session_state: st.session_state['analisis_listo'] = False
if 'datos_api' not in st.session_state: st.session_state['datos_api'] = None
if 'lista_opciones' not in st.session_state: st.session_state['lista_opciones'] = []

# --- INTERFAZ PRINCIPAL ---
st.title("🌱 AgroDecision: Sistema de Zonificación")

col_mapa, col_config = st.columns([2, 1])

# --- COLUMNA 1: MAPA Y BUSCADOR ---
with col_mapa:
    st.subheader("📍 Ubicación")
    
    # Pestañas de búsqueda: Implementación de geocodificación y GPS manual
    tab_buscar, tab_coords = st.tabs(["🔍 Buscador", "🌐 GPS Manual"])
    
    with tab_buscar:
        c1, c2 = st.columns([3, 1])
        texto = c1.text_input("Lugar:", label_visibility="collapsed", placeholder="Ej: Cajamarca, Peru")
        if c2.button("Buscar"):
            cli = AgroClimaClient()
            st.session_state['lista_opciones'] = cli.buscar_opciones_ciudades(texto)
        
        if st.session_state['lista_opciones']:
            opciones = {op['label']: op for op in st.session_state['lista_opciones']}
            sel = st.selectbox("Resultados encontrados:", list(opciones.keys()))
            if st.button("📍 Ir a esta ubicación"):
                lugar = opciones[sel]
                st.session_state['lat'] = lugar['lat']
                st.session_state['lon'] = lugar['lon']
                st.session_state['analisis_listo'] = False # Resetear análisis al mover mapa
                st.rerun()

    with tab_coords:
        c_lat, c_lon = st.columns(2)
        n_lat = c_lat.number_input("Latitud", value=st.session_state['lat'], format="%.5f")
        n_lon = c_lon.number_input("Longitud", value=st.session_state['lon'], format="%.5f")
        if st.button("Actualizar Mapa"):
            st.session_state['lat'] = n_lat
            st.session_state['lon'] = n_lon
            st.session_state['analisis_listo'] = False
            st.rerun()

    # --- SELECCIÓN DE CAPA DE MAPA (SATÉLITE O CALLES) ---
    st.write("🎨 **Estilo de Mapa:**")
    tipo_mapa = st.radio("Capa", ["Satélite (ESRI)", "Calles (OSM)"], horizontal=True, label_visibility="collapsed")
    
    if "Satélite" in tipo_mapa:
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
        attr = 'Esri'
    else:
        tiles = 'OpenStreetMap'
        attr = 'OSM'

    # Renderizar mapa dinámico usando Folium
    m = folium.Map(location=[st.session_state['lat'], st.session_state['lon']], zoom_start=14, tiles=tiles, attr=attr)
    folium.Marker([st.session_state['lat'], st.session_state['lon']], icon=folium.Icon(color="red", icon="leaf")).add_to(m)
    st_folium(m, height=350, width="100%")

# --- COLUMNA 2: CONFIGURACIÓN DE CULTIVO/ANIMAL ---
with col_config:
    st.subheader("⚙️ Configuración")
    categoria = st.selectbox("Categoría", ["cultivos", "bovinos", "porcinos", "aves"])
    
    # Cargar reglas técnicas desde archivos CSV (Capa de Estructuración)
    analista = AgroAnalisis()
    df_reglas = analista.cargar_reglas(categoria)
    
    variedad = None
    if df_reglas is not None and not df_reglas.empty:
        variedad = st.selectbox("Variedad / Raza", df_reglas['variedad'].unique())
        st.write("")
        st.info("Presiona el botón para consultar datos satelitales.")
        
        if st.button("📊 ANALIZAR VIABILIDAD", type="primary"):
            with st.spinner("Consultando satélites y clima histórico..."):
                cli = AgroClimaClient()
                # Orquestación: Obtención de datos climáticos e históricos
                st.session_state['datos_api'] = cli.obtener_todo(st.session_state['lat'], st.session_state['lon'])
                st.session_state['analisis_listo'] = True
    else:
        st.error("Error cargando base de conocimientos (agro_logic.py).")

st.divider()

# --- SECCIÓN DE RESULTADOS ---
if st.session_state['analisis_listo'] and st.session_state['datos_api']:
    datos = st.session_state['datos_api']
    
    # =========================================================
    # 🛠️ INPUT DE pH REACTIVO
    # =========================================================
    st.subheader("🧪 Análisis de Suelo")
    col_input_ph, col_info_ph = st.columns([1, 4])
    
    with col_input_ph:
        # Permite al usuario ajustar manualmente el pH para ver el cambio en los consejos
        ph_user = st.number_input(
            "pH del Suelo", 
            min_value=3.0, 
            max_value=10.0, 
            value=float(datos['suelo']['ph']), 
            step=0.1,
            key="ph_manual_input" 
        )
    
    with col_info_ph:
        st.success(f"Analizando consejos para **pH {ph_user}**...")

    # Actualizamos el diccionario localmente para que el 'analista' lo use también
    datos['suelo']['ph'] = ph_user 

    # =========================================================
    # 📡 DASHBOARD DE DATOS (Métricas Clave)
    # =========================================================
    st.write("")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("🌡️ Temp", f"{datos['clima']['temp_actual']} °C")
    m2.metric("💧 Humedad", f"{datos['clima']['humedad']} %")
    m3.metric("⛰️ Altitud", f"{datos['topografia']['altitud']:.0f} m")
    m4.metric("☀️ Luz", f"{datos['solar']['horas_luz']} h")
    m5.metric("🌧️ Lluvia", f"{int(datos['clima']['precipitacion_anual_estimada'])} mm")

    # =========================================================
    # 🧠 PROCESAMIENTO (Capa de Lógica)
    # =========================================================
    try:
        # 1. Puntuación (Score): Ejecuta el algoritmo de aptitud
        score, razones, riesgo = analista.analizar(datos, categoria, variedad)
        
        # 2. Consejos: Genera diagnósticos según el contexto
        consejos_expertos = generar_consejos_experto(datos, categoria, ph_user)
        
        # 3. Datos de referencia: Obtiene la fila técnica del CSV
        regla_actual = df_reglas[df_reglas['variedad'] == variedad].iloc[0]

    except Exception as e:
        st.error(f"Error en cálculos internos: {e}")
        st.stop()

    # =========================================================
    # 📑 PESTAÑAS DE DETALLE (Visualización Avanzada)
    # =========================================================
    t1, t2, t3 = st.tabs(["📊 INFORME", "🧬 FISIOLOGÍA", "📝 PLAN DE MANEJO"])

    # --- PESTAÑA 1: INFORME DE APTITUD ---
    with t1:
        if score >= 80: st.success(f"### ✅ APTO ({score}/100) - {variedad}")
        elif score >= 50: st.warning(f"### ⚠️ RIESGO MEDIO ({score}/100) - {variedad}")
        else: st.error(f"### ⛔ NO APTO ({score}/100) - {variedad}")
        
        if razones:
            for r in razones: st.write(r)
        else:
            st.success("✅ Todos los parámetros están en rango óptimo.")

    # --- PESTAÑA 2: FISIOLOGÍA (Cálculos Biológicos) ---
    with t2:
        try:
            st.subheader(f"Fisiología: {variedad}")
            
            if categoria in ["bovinos", "porcinos", "aves"]:
                # --- ANIMALES: Cálculo del ITH y Consumo de Agua ---
                temp_a = datos['clima']['temp_actual']
                hum_a = datos['clima']['humedad']
                
                # ITH (Índice Temperatura Humedad): Métrica estándar de estrés calórico
                ith = (0.8 * temp_a) + ((hum_a/100) * (temp_a - 14.4)) + 46.4
                
                # Agua Estimada según especie y temperatura ambiente
                consumo_base = 50 if categoria == "bovinos" else (6 if categoria == "porcinos" else 0.3)
                factor = 1 + ((temp_a - 18) * 0.05) if temp_a > 18 else 1
                agua = consumo_base * factor
                
                c1, c2 = st.columns(2)
                c1.metric("Índice ITH", f"{ith:.1f}")
                if ith < 72: c1.success("Zona de Confort")
                elif ith < 78: c1.warning("Alerta Leve")
                else: c1.error("Estrés Severo")
                
                c2.metric("Consumo Agua Estimado", f"{agua:.1f} Lt/día")
            
            else:
                # --- CULTIVOS: Grados Día (GDD) y Balance Hídrico ---
                temp_c = datos['clima']['temp_actual']
                lluvia_c = datos['clima']['precipitacion_anual_estimada']
                
                # GDD (Grados día): Mide la acumulación de calor para el desarrollo
                gdd = max(0, temp_c - 10) # Grados día (Base 10)
                balance = lluvia_c - 800
                
                c1, c2 = st.columns(2)
                c1.metric("Crecimiento (GDD)", f"{gdd:.1f}")
                if gdd > 8: c1.success("Crecimiento Rápido")
                elif gdd > 0: c1.warning("Crecimiento Lento")
                else: c1.error("Sin Crecimiento")
                
                c2.metric("Balance Hídrico", f"{int(balance)} mm")
                if balance < 0: c2.error("Déficit")
                else: c2.success("Superávit")
                
        except Exception as e:
            st.error(f"Error mostrando fisiología: {e}")

    # --- PESTAÑA 3: PLAN DE MANEJO (RECOMENDACIONES) ---
    with t3:
        try:
            st.subheader("Plan de Manejo y Soluciones")
            
            # Verificación comparativa de parámetros básicos
            t_min = float(regla_actual['temp_min'])
            t_max = float(regla_actual['temp_max'])
            t_act = datos['clima']['temp_actual']
            
            # Comparativa Temperatura API vs Referencia CSV
            if t_act < t_min or t_act > t_max:
                st.warning(f"⚠️ Temperatura actual ({t_act}°C) fuera de rango ideal ({t_min}-{t_max}°C).")
            else:
                st.success("✅ Temperatura ideal para la especie.")

            # Comparativa pH dinámico
            if categoria == "cultivos":
                if ph_user < 5.5:
                    st.error(f"⚠️ pH Ácido ({ph_user}). Requiere encalado urgente.")
                elif ph_user > 7.8:
                    st.error(f"⚠️ pH Alcalino ({ph_user}). Requiere acidificación.")
                else:
                    st.success(f"✅ pH ({ph_user}) correcto.")

            st.divider()
            
            # Renderizado de la lista de acciones recomendadas por el sistema experto
            st.write("**🛡️ Acciones Recomendadas:**")
            
            for texto, tipo in consejos_expertos:
                if tipo == "error": st.error(texto)
                elif tipo == "warning": st.warning(texto)
                elif tipo == "success": st.success(texto)
                else: st.info(texto)
                
        except Exception as e:
            st.error(f"Error en el plan de manejo: {e}")