import streamlit as st
import pandas as pd
import time
import folium
from streamlit_folium import st_folium

# --- IMPORTACIONES DE TUS MÓDULOS ---
from src.api_client import AgroClimaClient
from src.agro_logic import AgroAnalisis

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroDecision Pro", page_icon="🌱", layout="wide")

# --- ESTILOS CSS (Para que se vea profesional) ---
st.markdown("""
    <style>
    .big-font { font-size:18px !important; }
    .stAlert { padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- MOTOR DE INTELIGENCIA AGRONÓMICA (La parte "Profunda") ---
def generar_consejos_experto(datos, categoria, ph_suelo):
    """
    Motor de inferencia agronómica avanzada.
    Analiza sinergias entre temperatura, humedad, luz y suelo.
    """
    consejos = []
    
    # Extraemos variables
    temp = datos['clima']['temp_actual']
    humedad = datos['clima']['humedad']
    lluvia = datos['clima']['precipitacion_anual_estimada']
    horas_luz = datos['solar']['horas_luz']
    altitud = datos['topografia']['altitud']

    # 1. ANÁLISIS AGRONÓMICO (CULTIVOS)
    if categoria == "cultivos":
        # A. Fisiología y Clima
        if temp > 30 and humedad < 40:
            consejos.append("🍂 **Cierre Estomático:** La planta ha dejado de hacer fotosíntesis para no deshidratarse. El riego debe ser nocturno para evitar evaporación inmediata.")
        elif temp > 25 and humedad > 80:
            consejos.append("🍄 **Alerta Fitosanitaria (Alta):** Caldo de cultivo perfecto para hongos (Roya, Mildiu, Botrytis). Se recomienda aplicación preventiva de fungicidas y poda de ventilación.")
        elif temp < 10:
            consejos.append("❄️ **Dormancia/Daño:** Metabolismo vegetal detenido. Riesgo de heladas. Si el cultivo está en floración, la pérdida puede ser total. Usar mantas térmicas.")

        # B. Nutrición y Suelo (pH Profundo)
        if ph_suelo < 5.0:
            consejos.append("☠️ **Toxicidad por Aluminio:** A este pH, el aluminio se vuelve soluble y quema las raíces. El Fósforo está bloqueado. **Solución:** Encalado obligatorio 2 meses antes de siembra.")
        elif 5.0 <= ph_suelo < 6.0:
            consejos.append("🧪 **Deficiencia de Macronutrientes:** El Nitrógeno y Potasio no se absorben bien. Aumentar dosis de fertilizante en un 20% para compensar pérdidas.")
        elif ph_suelo > 7.5:
            consejos.append("🧪 **Clorosis Férrica:** El Hierro está bloqueado. Las hojas se pondrán amarillas. Aplicar Quelatos de Hierro vía foliar (no al suelo).")

        # C. Fotoperiodo
        if horas_luz < 11:
            consejos.append("📉 **Baja Radiación:** Rendimiento fotosintético limitado. Menor acumulación de grados brix (azúcares) en frutos.")

    # 2. ANÁLISIS ZOOTÉCNICO (ANIMALES)
    elif categoria in ["bovinos", "porcinos", "aves"]:
        
        # A. Estrés Térmico
        if categoria == "porcinos" and temp > 28:
            consejos.append("🐷 **Peligro Mortal:** Los cerdos no sudan. Con >28°C hay riesgo de paro cardíaco. Es obligatorio usar duchas/nebulizadores y ventilación forzada.")
        
        if categoria == "bovinos" and humedad > 80:
            consejos.append("🐄 **Pérdida de Producción:** El ganado dejará de comer (baja ingesta de materia seca) para no generar calor digestivo. Se espera una caída del 10-15% en leche.")

        # B. Fotoperiodo (Aves)
        if categoria == "aves" and horas_luz < 14:
            horas_faltantes = 16 - horas_luz
            consejos.append(f"💡 **Programa de Luz:** Faltan {horas_faltantes:.1f} horas de luz para estimular la glándula pituitaria. Sin luz artificial, la postura caerá drásticamente.")
            
        # C. Altitud (Mal de altura)
        if categoria == "bovinos" and altitud > 3000:
            consejos.append("⛰️ **Mal de Altura (Brisket):** Riesgo de insuficiencia cardíaca derecha en razas lecheras (Holstein). Se recomienda usar razas rústicas (Brown Swiss) o cruces.")

        # D. Sanidad
        if humedad > 85:
            consejos.append("🦠 **Bacteriología:** La cama/suelo húmedo dispara los niveles de E. Coli y Mastitis ambiental. Usar secantes (cal, viruta seca) diariamente.")

    return consejos

# --- FUNCIONES AUXILIARES (ITH) ---
def calcular_ith(temp, humedad):
    return (0.8 * temp) + ((humedad / 100) * (temp - 14.4)) + 46.4

def interpretar_ith(ith):
    if ith < 72: return "Confort (Óptimo)", "success", "El animal expresa su máximo potencial genético."
    elif ith < 78: return "Alerta (Leve)", "warning", "Baja ingesta de materia seca. Proveer sombra."
    elif ith < 88: return "Peligro (Moderado)", "orange", "Pérdida de producción. Necesario ventiladores/aspersores."
    else: return "Emergencia (Severo)", "error", "Riesgo de muerte. Detener manejo, mojar animales inmediatamente."

# --- INICIALIZAR ESTADO (SESSION STATE) ---
# Esto evita que se borre todo al mover el mapa o el slider
if 'lat' not in st.session_state: st.session_state['lat'] = -12.0464
if 'lon' not in st.session_state: st.session_state['lon'] = -77.0428
if 'analisis_listo' not in st.session_state: st.session_state['analisis_listo'] = False
if 'datos_api' not in st.session_state: st.session_state['datos_api'] = None

# --- UI PRINCIPAL ---
st.title("🌱 AgroDecision: Sistema de Zonificación Agropecuaria")

col_mapa, col_config = st.columns([2, 1])

with col_mapa:
    st.subheader("📍 Paso 1: Ubicación")
    
    # --- BUSCADOR DE CIUDADES ---
    col_search1, col_search2 = st.columns([3, 1])
    with col_search1:
        busqueda = st.text_input("Buscar ciudad (Ej: Cajamarca, Oxapampa)", "")
    with col_search2:
        if st.button("Buscar 🔎"):
            cliente_temp = AgroClimaClient()
            # Asumimos que implementaste buscar_ciudad en api_client.py
            resultado = cliente_temp.buscar_ciudad(busqueda) 
            if resultado:
                st.session_state['lat'], st.session_state['lon'], nombre, pais = resultado
                st.success(f"📍 {nombre}, {pais}")
                st.session_state['analisis_listo'] = False # Resetear análisis al cambiar lugar
            else:
                st.error("No encontrado")

    # --- MAPA ---
    m = folium.Map(location=[st.session_state['lat'], st.session_state['lon']], zoom_start=10 if busqueda else 6)
    folium.Marker([st.session_state['lat'], st.session_state['lon']], icon=folium.Icon(color="red")).add_to(m)
    m.add_child(folium.LatLngPopup())
    
    map_output = st_folium(m, height=400, width="100%")

    if map_output['last_clicked']:
        st.session_state['lat'] = map_output['last_clicked']['lat']
        st.session_state['lon'] = map_output['last_clicked']['lng']
        st.session_state['analisis_listo'] = False 
        st.rerun()

with col_config:
    st.subheader("⚙️ Paso 2: Configuración")
    categoria = st.selectbox("Sistema Productivo", ["cultivos", "bovinos", "porcinos", "aves"])
    
    analista = AgroAnalisis()
    df_reglas = analista.cargar_reglas(categoria)
    
    variedad = None
    if df_reglas is not None:
        variedad = st.selectbox("Especie / Variedad", df_reglas['variedad'].unique())
        
        # BOTÓN DE ANÁLISIS
        if st.button("🔎 Ejecutar Análisis", type="primary"):
            with st.spinner('📡 Consultando satélites (Clima, Topografía, Fotoperiodo)...'):
                cliente = AgroClimaClient()
                datos = cliente.obtener_todo(st.session_state['lat'], st.session_state['lon'])
                st.session_state['datos_api'] = datos
                st.session_state['analisis_listo'] = True

st.divider()

# --- RESULTADOS (SOLO SI EL ANÁLISIS ESTÁ LISTO) ---
if st.session_state['analisis_listo'] and st.session_state['datos_api']:
    datos = st.session_state['datos_api']
    
    # --- CALIBRACIÓN DE SUELO (PERSISTENTE) ---
    st.subheader("🧪 Paso 3: Calibración y Ajuste")
    col_cal1, col_cal2 = st.columns([1, 2])
    with col_cal1:
        # El slider lee y actualiza la variable en memoria
        ph_user = st.slider("pH del Suelo Real", 4.0, 9.0, float(datos['suelo']['ph']), 0.1)
        datos['suelo']['ph'] = ph_user # Guardamos el cambio
    with col_cal2:
         st.info("💡 **Nota:** Ajusta este valor si tienes un análisis de suelo de laboratorio. El sistema recalculará la viabilidad y las recomendaciones químicas automáticamente.")

    # Ejecutar lógica de viabilidad con los datos actuales
    score, razones, riesgo_extra = analista.analizar(datos, categoria, variedad)
    consejos_tecnicos = generar_consejos_experto(datos, categoria, ph_user)

    # --- PESTAÑAS DE RESULTADOS ---
    t1, t2, t3 = st.tabs(["🏆 Informe General", "🧬 Fisiología y Estrés", "📝 Recomendaciones Técnicas"])

    with t1:
        c1, c2 = st.columns([1, 2])
        with c1:
            # Imágenes Profesionales (Unsplash)
            imgs = {
                "cultivos": "https://images.unsplash.com/photo-1625246333195-551e50514689?auto=format&fit=crop&w=600&q=80",
                "bovinos": "https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=600&q=80",
                "porcinos": "https://images.unsplash.com/photo-1604848698030-c434ba08ece1?auto=format&fit=crop&w=600&q=80",
                "aves": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?auto=format&fit=crop&w=600&q=80"
            }
            st.image(imgs.get(categoria), caption=f"Evaluación para: {variedad}", use_container_width=True)
            
            # Semáforo de Puntaje
            if score >= 80: st.success(f"## ✅ {score}/100 - EXCELENTE")
            elif score >= 50: st.warning(f"## ⚠️ {score}/100 - REGULAR")
            else: st.error(f"## ⛔ {score}/100 - NO APTO")

        with c2:
            st.write("#### 📡 Variables Ambientales Detectadas")
            # Fila 1
            m1, m2, m3 = st.columns(3)
            m1.metric("🌡️ Temperatura", f"{datos['clima']['temp_actual']} °C")
            m2.metric("💧 Humedad", f"{datos['clima']['humedad']} %")
            m3.metric("🌧️ Lluvia", f"{int(datos['clima']['precipitacion_anual_estimada'])} mm")
            # Fila 2
            m4, m5, m6 = st.columns(3)
            m4.metric("⛰️ Altitud", f"{datos['topografia']['altitud']:.0f} msnm")
            m5.metric("☀️ Luz Solar", f"{datos['solar']['horas_luz']} h/día")
            m6.metric("🧪 pH Suelo", f"{ph_user}")

    with t2:
        if categoria in ["bovinos", "porcinos", "aves"]:
            st.markdown("### 🐄 Monitor de Confort Animal")
            ith = calcular_ith(datos['clima']['temp_actual'], datos['clima']['humedad'])
            est, col, consejo_ith = interpretar_ith(ith)
            
            col_z1, col_z2 = st.columns(2)
            with col_z1:
                st.metric("Índice ITH", f"{ith:.1f}", delta=est, delta_color="inverse" if col == "error" else "normal")
            with col_z2:
                if col == "success": st.success(f"✅ **Interpretación:** {consejo_ith}")
                elif col == "warning": st.warning(f"⚠️ **Acción:** {consejo_ith}")
                else: st.error(f"🚨 **URGENTE:** {consejo_ith}")
            
        else:
            st.markdown("### 🌿 Fisiología Vegetal (Balance Hídrico)")
            req_agua = 800 # Promedio referencial
            balance = datos['clima']['precipitacion_anual_estimada'] - req_agua
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.metric("Balance Hídrico", f"{int(balance)} mm", delta="Superávit" if balance > 0 else "Déficit")
            with col_b2:
                if balance < 0:
                    st.error(f"🔥 **Déficit Hídrico:** El cultivo requiere {abs(int(balance))}mm adicionales. OBLIGATORIO sistema de riego.")
                else:
                    st.success("💧 **Humedad Suficiente:** La lluvia cubre los requerimientos básicos del cultivo.")

    with t3:
        st.subheader("📋 Plan de Manejo Recomendado (Consultoría Técnica)")
        
        if consejos_tecnicos:
            for consejo in consejos_tecnicos:
                st.info(consejo)
        else:
            st.success("✅ Las condiciones actuales no presentan riesgos críticos específicos para esta variedad.")

        st.divider()
        st.write("**Factores Limitantes Detectados:**")
        if not razones:
            st.write("Ninguno. Zona ideal.")
        for r in razones:
            if "⛔" in r: st.error(r)
            elif "⚠️" in r: st.warning(r)
            else: st.success(r)