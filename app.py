import streamlit as st
import pandas as pd
import time
import folium
from streamlit_folium import st_folium
from src.api_client import AgroClimaClient
from src.agro_logic import AgroAnalisis

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AgroDecision Pro", page_icon="🌱", layout="wide")

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
    <style>
    .big-font { font-size:18px !important; }
    .stAlert { padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES DE LÓGICA EXPERTA (NUEVO) ---
def generar_consejos_experto(datos, categoria, ph_suelo):
    """Genera recomendaciones técnicas detalladas basadas en condiciones"""
    consejos = []
    
    # 1. Análisis de Humedad y Plagas
    humedad = datos['clima']['humedad']
    temp = datos['clima']['temp_actual']
    
    if categoria == "cultivos":
        if humedad > 80 and temp > 20:
            consejos.append("🍄 **Alto Riesgo Fúngico:** Condiciones ideales para Roya, Oidio y Botrytis. Se recomienda aplicar fungicidas preventivos y mejorar la ventilación entre surcos.")
        elif humedad < 40:
            consejos.append("🍂 **Estrés Hídrico Atmosférico:** La planta cerrará estomas. Riego por aspersión recomendado para subir humedad relativa.")
            
    elif categoria in ["bovinos", "porcinos", "aves"]:
        if humedad > 80 and temp > 25:
            consejos.append("🪰 **Riesgo Sanitario:** Alta proliferación de vectores (moscas, garrapatas) y bacterias. Incrementar frecuencia de limpieza de camas y corrales.")
        if categoria == "aves" and humedad > 70:
            consejos.append("🦠 **Coccidiosis:** Riesgo elevado en camas húmedas. Usar secuestrantes de humedad y remover cama apelmazada.")

    # 2. Análisis de Suelo (pH)
    if ph_suelo < 5.5:
        consejos.append("🧪 **Acidez Excesiva:** Bloqueo de Fósforo y Magnesio. Posible toxicidad por Aluminio. **Solución:** Aplicar Cal Dolomita 30 días antes de la siembra.")
    elif ph_suelo > 7.5:
        consejos.append("🧪 **Alcalinidad:** Deficiencia de Micronutrientes (Hierro, Zinc). **Solución:** Aplicar materia orgánica compostada o fertilizantes acidificantes (Sulfato de Amonio).")

    # 3. Análisis de Fotoperiodo
    horas_luz = datos['solar']['horas_luz']
    if categoria == "aves" and horas_luz < 14:
        consejos.append("💡 **Fotoperiodo Corto:** Para mantener postura >90%, es obligatorio complementar con luz artificial hasta llegar a 16 horas luz totales.")

    return consejos

def calcular_ith(temp, humedad):
    return (0.8 * temp) + ((humedad / 100) * (temp - 14.4)) + 46.4

def interpretar_ith(ith):
    if ith < 72: return "Confort (Óptimo)", "success", "El animal expresa su máximo potencial genético."
    elif ith < 78: return "Alerta (Leve)", "warning", "Baja ingesta de materia seca. Proveer sombra y agua fresca."
    elif ith < 88: return "Peligro (Moderado)", "orange", "Pérdida de producción leche/carne. Necesario ventiladores/aspersores."
    else: return "Emergencia (Severo)", "error", "Riesgo de muerte. Detener manejo, mojar animales inmediatamente."

# --- INICIALIZAR ESTADO (SESSION STATE) ---
if 'lat' not in st.session_state: st.session_state['lat'] = -12.0464
if 'lon' not in st.session_state: st.session_state['lon'] = -77.0428
if 'analisis_listo' not in st.session_state: st.session_state['analisis_listo'] = False
if 'datos_api' not in st.session_state: st.session_state['datos_api'] = None

# --- UI PRINCIPAL ---
st.title("🌱 AgroDecision: Sistema de Zonificación Agropecuaria")

col_mapa, col_config = st.columns([2, 1])

with col_mapa:
    st.subheader("📍 Paso 1: Ubicación")
    
    # --- BUSCADOR DE CIUDADES (NUEVO) ---
    col_search1, col_search2 = st.columns([3, 1])
    with col_search1:
        busqueda = st.text_input("Buscar ciudad o lugar (Ej: Arequipa, Oxapampa)", "")
    with col_search2:
        if st.button("Buscar 🔎"):
            cliente_temp = AgroClimaClient()
            resultado = cliente_temp.buscar_ciudad(busqueda)
            if resultado:
                st.session_state['lat'], st.session_state['lon'], nombre, pais = resultado
                st.success(f"📍 Encontrado: {nombre}, {pais}")
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
        st.session_state['analisis_listo'] = False # Resetear si cambia el punto
        st.rerun()

with col_config:
    st.subheader("⚙️ Paso 2: Configuración")
    categoria = st.selectbox("Sistema Productivo", ["cultivos", "bovinos", "porcinos", "aves"])
    analista = AgroAnalisis()
    df_reglas = analista.cargar_reglas(categoria)
    
    variedad = st.selectbox("Especie / Variedad", df_reglas['variedad'].unique()) if df_reglas is not None else None
    
    # BOTÓN DE ANÁLISIS
    if st.button("🔎 Ejecutar Análisis", type="primary"):
        with st.spinner('📡 Consultando satélites y procesando modelos...'):
            cliente = AgroClimaClient()
            datos = cliente.obtener_todo(st.session_state['lat'], st.session_state['lon'])
            st.session_state['datos_api'] = datos
            st.session_state['analisis_listo'] = True

st.divider()

# --- RESULTADOS (SOLO SI EL ANÁLISIS ESTÁ LISTO) ---
if st.session_state['analisis_listo'] and st.session_state['datos_api']:
    datos = st.session_state['datos_api']
    
    # --- CALIBRACIÓN DE SUELO (AHORA NO BORRA EL REPORTE) ---
    st.subheader("🧪 Paso 3: Calibración y Ajuste")
    col_cal1, col_cal2 = st.columns([1, 2])
    with col_cal1:
        # El slider actualiza el script, pero como 'analisis_listo' es True, entra aquí directo
        ph_user = st.slider("pH del Suelo Real", 4.0, 9.0, float(datos['suelo']['ph']), 0.1)
        datos['suelo']['ph'] = ph_user
    with col_cal2:
         st.info("💡 **Nota:** Ajusta este valor si tienes un análisis de suelo de laboratorio. El sistema recalculará la viabilidad automáticamente.")

    # Ejecutar lógica de viabilidad
    score, razones, riesgo_extra = analista.analizar(datos, categoria, variedad)
    consejos_tecnicos = generar_consejos_experto(datos, categoria, ph_user)

    # --- PESTAÑAS DE RESULTADOS ---
    t1, t2, t3 = st.tabs(["🏆 Informe General", "🧬 Fisiología y Estrés", "📝 Recomendaciones Técnicas"])

    with t1:
        c1, c2 = st.columns([1, 2])
        with c1:
            # Imágenes más profesionales (Unsplash)
            imgs = {
                "cultivos": "https://images.unsplash.com/photo-1625246333195-551e50514689?auto=format&fit=crop&w=600&q=80",
                "bovinos": "https://images.unsplash.com/photo-1546445317-29f4545e9d53?auto=format&fit=crop&w=600&q=80",
                "porcinos": "https://images.unsplash.com/photo-1604848698030-c434ba08ece1?auto=format&fit=crop&w=600&q=80",
                "aves": "https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?auto=format&fit=crop&w=600&q=80"
            }
            st.image(imgs.get(categoria), caption=f"Análisis para {variedad}", use_container_width=True)
            
            if score >= 80: st.success(f"## ✅ {score}/100 - EXCELENTE")
            elif score >= 50: st.warning(f"## ⚠️ {score}/100 - REGULAR")
            else: st.error(f"## ⛔ {score}/100 - NO APTO")

        with c2:
            st.write("#### 📡 Variables Ambientales Detectadas")
            m1, m2, m3 = st.columns(3)
            m1.metric("🌡️ Temperatura", f"{datos['clima']['temp_actual']} °C")
            m2.metric("💧 Humedad", f"{datos['clima']['humedad']} %")
            m3.metric("🌧️ Lluvia", f"{int(datos['clima']['precipitacion_anual_estimada'])} mm")
            
            m4, m5, m6 = st.columns(3)
            m4.metric("⛰️ Altitud", f"{datos['topografia']['altitud']:.0f} msnm")
            m5.metric("☀️ Luz Solar", f"{datos['solar']['horas_luz']} h")
            m6.metric("🧪 pH Suelo", f"{ph_user}")

    with t2:
        if categoria in ["bovinos", "porcinos", "aves"]:
            st.markdown("### 🐄 Monitor de Confort Animal")
            ith = calcular_ith(datos['clima']['temp_actual'], datos['clima']['humedad'])
            est, col, consejo_ith = interpretar_ith(ith)
            st.metric("Índice ITH", f"{ith:.1f}", delta=est, delta_color="inverse" if col == "error" else "normal")
            
            if col == "success": st.success(f"✅ **Interpretación:** {consejo_ith}")
            elif col == "warning": st.warning(f"⚠️ **Acción:** {consejo_ith}")
            else: st.error(f"🚨 **URGENTE:** {consejo_ith}")
            
        else:
            st.markdown("### 🌿 Fisiología Vegetal")
            req_agua = 800 # Ejemplo
            balance = datos['clima']['precipitacion_anual_estimada'] - req_agua
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.metric("Balance Hídrico", f"{int(balance)} mm", delta="Superávit" if balance > 0 else "Déficit")
            with col_b2:
                if balance < 0:
                    st.error(f"**Interpretación:** El cultivo sufrirá estrés hídrico severo. **Acción:** Diseñar sistema de riego para suplir {abs(int(balance))}mm faltantes.")
                else:
                    st.success("**Interpretación:** Lluvia suficiente para el desarrollo vegetativo. Vigilar drenaje para evitar asfixia radicular.")

    with t3:
        st.subheader("📋 Plan de Manejo Recomendado")
        
        # Mostrar los consejos generados dinámicamente
        if consejos_tecnicos:
            for consejo in consejos_tecnicos:
                st.info(consejo)
        else:
            st.success("✅ No se detectaron riesgos críticos en clima o suelo para esta especie.")

        st.write("---")
        st.write("**Factores Limitantes Específicos:**")
        for r in razones:
            if "⛔" in r: st.error(r)
            elif "⚠️" in r: st.warning(r)
            else: st.success(r)