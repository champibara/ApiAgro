import streamlit as st
import pandas as pd
import time
import folium
from streamlit_folium import st_folium

# --- IMPORTACIONES DE TUS MÓDULOS ---
# Asegúrate de que la carpeta "src" tenga los archivos correctos
from src.api_client import AgroClimaClient
from src.agro_logic import AgroAnalisis

# --- FUNCIONES CIENTÍFICAS AUXILIARES ---
def calcular_ith(temp, humedad):
    """Calcula el Índice de Temperatura y Humedad (THI) para ganado (Thom, 1959)"""
    return (0.8 * temp) + ((humedad / 100) * (temp - 14.4)) + 46.4

def interpretar_ith(ith):
    """Devuelve el estado de alerta según el ITH calculado"""
    if ith < 72: return "Confort (Sin estrés)", "success"
    elif ith < 78: return "Alerta (Estrés Leve)", "warning"
    elif ith < 88: return "Peligro (Estrés Moderado)", "orange"
    else: return "Emergencia (Estrés Severo)", "inverse"

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="AgroDecision Pro", page_icon="🌱", layout="wide")

st.title("🌱 AgroDecision: Sistema de Zonificación Agropecuaria")
st.markdown("**Análisis de viabilidad técnica usando datos satelitales en tiempo real.**")

# --- INICIALIZAR ESTADO (RECORDAR CLIC EN EL MAPA) ---
if 'lat_clicked' not in st.session_state:
    st.session_state['lat_clicked'] = -12.0464  # Lima por defecto
    st.session_state['lon_clicked'] = -77.0428

# --- ESTRUCTURA PRINCIPAL: COLUMNAS (MAPA A LA IZQUIERDA, MENU A LA DERECHA) ---
col_mapa, col_config = st.columns([2, 1])

with col_mapa:
    st.subheader("📍 Paso 1: Ubica tu terreno")
    
    # Crear mapa
    m = folium.Map(location=[st.session_state['lat_clicked'], st.session_state['lon_clicked']], zoom_start=6)
    m.add_child(folium.LatLngPopup()) # Permite hacer clic
    
    # Poner marcador rojo en el punto seleccionado
    folium.Marker(
        [st.session_state['lat_clicked'], st.session_state['lon_clicked']],
        popup="Punto de Análisis",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Mostrar mapa
    map_output = st_folium(m, height=450, width="100%")

    # Actualizar coordenadas si el usuario hace clic
    if map_output['last_clicked']:
        st.session_state['lat_clicked'] = map_output['last_clicked']['lat']
        st.session_state['lon_clicked'] = map_output['last_clicked']['lng']
        st.rerun()

with col_config:
    st.subheader("⚙️ Paso 2: Configuración")
    st.info(f"**Lat:** {st.session_state['lat_clicked']:.4f}\n\n**Lon:** {st.session_state['lon_clicked']:.4f}")
    
    # Selectores
    categoria = st.selectbox("Sistema Productivo", ["cultivos", "bovinos", "porcinos", "aves"])
    
    # Cargar lógica de negocio
    analista = AgroAnalisis()
    df_reglas = analista.cargar_reglas(categoria)

    if df_reglas is not None:
        variedad = st.selectbox("Especie / Variedad", df_reglas['variedad'].unique())
        boton_analizar = st.button("🔎 Ejecutar Análisis Completo", type="primary")
    else:
        st.error(f"⚠️ No se encontró el archivo CSV para {categoria}")
        boton_analizar = False

st.divider()

# --- LÓGICA DE EJECUCIÓN ---
if boton_analizar:
    lat = st.session_state['lat_clicked']
    lon = st.session_state['lon_clicked']
    
    # Barra de carga
    with st.spinner('📡 Conectando con satélites (Clima, Topografía y Fotoperiodo)...'):
        time.sleep(1) # Simulación visual
        cliente = AgroClimaClient()
        
        try:
            # 1. OBTENER DATOS DE LAS 3 APIS
            datos = cliente.obtener_todo(lat, lon) 
            
            # --- ZONA DE CALIBRACIÓN (Slider de pH) ---
            st.subheader("🧪 Paso 3: Calibración de Datos de Campo")
            col_aj1, col_aj2 = st.columns(2)
            
            with col_aj1:
                ph_inicial = datos['suelo']['ph']
                ph_final = st.slider(
                    "pH del Suelo (Ajuste Manual)", 
                    4.0, 9.0, float(ph_inicial), 0.1,
                    help="Si tienes análisis de suelo real, ajusta este valor."
                )
                datos['suelo']['ph'] = ph_final # Sobreescribimos el dato

            with col_aj2:
                if ph_final < 5.5: st.warning("⚠️ Suelo Ácido (Requiere encalado)")
                elif ph_final > 7.5: st.warning("⚠️ Suelo Alcalino (Bloqueo de nutrientes)")
                else: st.success("✅ pH Óptimo (Disponibilidad de nutrientes)")

            # 2. ANALIZAR VIABILIDAD
            score, razones, riesgo_extra = analista.analizar(datos, categoria, variedad)
            
            st.divider()
            
            # --- MOSTRAR RESULTADOS ---
            st.subheader(f"📊 Informe Técnico: {variedad}")
            
            # Pestañas para organizar la información
            tab1, tab2, tab3 = st.tabs(["🏆 Resultados Generales", "🧬 Fisiología y Estrés", "📝 Detalles y Recomendaciones"])

            # PESTAÑA 1: RESUMEN Y MÉTRICAS
            with tab1:
                col_res1, col_res2 = st.columns([1, 2])
                
                with col_res1:
                    # Mostrar imagen según categoría
                    img_map = {
                        "bovinos": "https://img.freepik.com/free-photo/cows-field_1160-244.jpg",
                        "porcinos": "https://img.freepik.com/free-photo/pigs-farm_1160-239.jpg",
                        "aves": "https://img.freepik.com/free-photo/chicken-farm_1160-205.jpg",
                        "cultivos": "https://img.freepik.com/free-photo/corn-field_1160-213.jpg"
                    }
                    st.image(img_map.get(categoria, "https://placehold.co/400x300"), use_container_width=True)
                    
                    # Puntaje
                    if score >= 80:
                        st.success(f"## ✅ {score}/100\n**APTO**")
                    elif score >= 50:
                        st.warning(f"## ⚠️ {score}/100\n**RIESGO**")
                    else:
                        st.error(f"## ⛔ {score}/100\n**NO APTO**")
                    st.progress(score/100)

                with col_res2:
                    st.write("#### 📡 Datos Ambientales Detectados:")
                    
                    # FILA 1: CLIMA
                    m1, m2, m3 = st.columns(3)
                    m1.metric("🌡️ Temp. Media", f"{datos['clima']['temp_actual']} °C")
                    m2.metric("💧 Humedad", f"{datos['clima']['humedad']} %")
                    m3.metric("🌧️ Lluvia Anual", f"{int(datos['clima']['precipitacion_anual_estimada'])} mm")
                    
                    # FILA 2: GEOGRAFÍA Y SOL (AQUÍ ESTÁ LA 3RA API)
                    m4, m5, m6 = st.columns(3)
                    m4.metric("⛰️ Altitud", f"{datos['topografia']['altitud']:.0f} msnm")
                    
                    horas_sol = datos['solar']['horas_luz']
                    m5.metric("☀️ Horas Luz", f"{horas_sol} h/día", help="Calculado con API de Astronomía")
                    
                    m6.metric("🧪 pH Final", f"{ph_final}")

            # PESTAÑA 2: ANÁLISIS CIENTÍFICO (ZOOTECNIA O AGRONOMÍA)
            with tab2:
                if categoria in ["bovinos", "porcinos", "aves"]:
                    st.markdown("### 🐄 Análisis de Bienestar Animal (Zootecnia)")
                    
                    ith = calcular_ith(datos['clima']['temp_actual'], datos['clima']['humedad'])
                    estado_ith, color_ith = interpretar_ith(ith)
                    
                    c_ith1, c_ith2 = st.columns(2)
                    with c_ith1:
                        st.metric("Índice ITH Actual", f"{ith:.1f}")
                        if color_ith == "success": st.success(f"Estado: {estado_ith}")
                        elif color_ith == "warning": st.warning(f"Estado: {estado_ith}")
                        else: st.error(f"Estado: {estado_ith}")
                    
                    with c_ith2:
                        st.info("💡 **El ITH (Índice de Temperatura y Humedad)** mide el estrés calórico. Valores altos reducen la producción de leche/carne y afectan la reproducción.")

                elif categoria == "cultivos":
                    st.markdown("### 🌽 Balance Hídrico Simplificado (Agronomía)")
                    
                    lluvia = datos['clima']['precipitacion_anual_estimada']
                    # Requerimiento base promedio (esto podría mejorarse con datos específicos por cultivo)
                    requerimiento = 800 
                    balance = lluvia - requerimiento
                    
                    c_agua1, c_agua2 = st.columns(2)
                    with c_agua1:
                        st.metric("Oferta Hídrica (Lluvia)", f"{int(lluvia)} mm")
                        st.metric("Demanda Hídrica (Aprox)", f"{requerimiento} mm")
                    
                    with c_agua2:
                        if balance >= 0:
                            st.success(f"💧 **Superávit (+{int(balance)} mm):** Condiciones de humedad adecuadas.")
                        else:
                            st.error(f"🔥 **Déficit ({int(balance)} mm):** Es OBLIGATORIO instalar sistema de riego.")

            # PESTAÑA 3: DETALLES
            with tab3:
                st.write("### Factores Limitantes y Recomendaciones")
                for r in razones:
                    if "⛔" in r: st.error(r)
                    elif "⚠️" in r: st.warning(r)
                    elif "✅" in r: st.success(r)
                
                if riesgo_extra:
                    st.info(f"📋 **Observación:** {riesgo_extra}")

        except Exception as e:
            st.error(f"❌ Ocurrió un error en el análisis: {e}")
            st.warning("Verifica tu conexión a internet o intenta con otra ubicación.")