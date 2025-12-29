import pandas as pd
import os

class AgroAnalisis:
    """
    MÓDULO DE PROCESAMIENTO (agro_logic.py)
    Esta clase ejecuta el motor de inferencia del sistema.
    Cruce de datos climáticos (API) con parámetros técnicos (CSV) para
    determinar la viabilidad agropecuaria mediante un sistema de puntaje (Score).
    """

    def __init__(self):
        # ESTRUCTURACIÓN: Ruta base hacia el repositorio de datos técnicos
        self.base_path = "data/referencias"

    def cargar_reglas(self, categoria):
        """
        ESTRUCTURACIÓN DE DATOS:
        Utiliza Pandas para cargar archivos estructurados (.CSV) dinámicamente.
        Normaliza la fuente de datos para su procesamiento en memoria.
        """
        archivo = os.path.join(self.base_path, f"{categoria}.csv")
        try:
            return pd.read_csv(archivo)
        except FileNotFoundError:
            return None

    def analizar(self, datos_api, categoria, variedad_nombre):
        """
        PROCESAMIENTO LÓGICO Y CÁLCULO DE APTITUD:
        Aplica un algoritmo de penalización basado en umbrales técnicos.
        
        1. Valida condiciones comunes (Temperatura y Pendiente).
        2. Aplica lógica específica según especie (pH/Lluvia para cultivos, Altitud/Humedad para animales).
        3. Genera un Score final de 0-100 y una lista de argumentos técnicos.
        """
        df = self.cargar_reglas(categoria)
        if df is None: return 0, ["Error al cargar datos"], "N/A"

        # Localización de la regla específica mediante filtrado en DataFrame
        regla = df[df['variedad'] == variedad_nombre].iloc[0]
        
        clima = datos_api['clima']
        topo = datos_api['topografia']
        suelo = datos_api['suelo']
        
        score = 100
        razones = []

        # --- 1. PROCESAMIENTO: VALIDACIONES COMUNES ---
        
        # Validación de Temperatura (API vs CSV)
        if not (regla['temp_min'] <= clima['temp_actual'] <= regla['temp_max']):
            score -= 20
            razones.append(f"⚠️ Temperatura actual ({clima['temp_actual']}°C) fuera de rango ideal ({regla['temp_min']}-{regla['temp_max']}°C).")
        else:
            razones.append(f"✅ Temperatura adecuada.")

        # Validación de Pendiente del Terreno
        if topo['pendiente'] > regla['pendiente_max']:
            penalizacion = 30 if "Cultivo" in regla['especie'] else 15
            score -= penalizacion
            razones.append(f"⛔ Pendiente del terreno ({topo['pendiente']:.1f}%) excede el máximo permitido ({regla['pendiente_max']}%).")
        
        # --- 2. PROCESAMIENTO: VALIDACIONES POR TIPO DE ESPECIE ---

        if "Cultivo" in regla['especie']:
            # Lógica para Vegetales: Validar pH y Necesidad Hídrica (Lluvia Real Anual)
            if not (regla['ph_min'] <= suelo['ph'] <= regla['ph_max']):
                score -= 25
                razones.append(f"⚠️ pH del suelo ({suelo['ph']}) inadecuado. Ideal: {regla['ph_min']}-{regla['ph_max']}.")
            else:
                razones.append(f"✅ pH del suelo óptimo.")
            
            lluvia = clima['precipitacion_anual_estimada']
            if lluvia < regla['precip_min_mm']:
                score -= 20
                razones.append(f"💧 Falta de agua estimada ({lluvia:.0f}mm). Requiere: {regla['precip_min_mm']}mm.")
        
        else:
            # Lógica para Animales: Validar Altitud (Estrés por Hipoxia) y Humedad (Sanidad)
            if topo['altitud'] > regla['altitud_max_m']:
                score -= 40
                razones.append(f"⛔ Altitud excesiva ({topo['altitud']:.0f} msnm). Riesgo de mal de altura (Máx: {regla['altitud_max_m']}m).")
            else:
                razones.append(f"✅ Altitud segura.")

            if clima['humedad'] > regla['humedad_max']:
                score -= 10
                razones.append(f"⚠️ Humedad alta ({clima['humedad']}%). Riesgo de patógenos.")

        # Normalización del Score final
        score = max(0, min(100, score))
        return score, razones, regla.get('riesgo_extra', 'N/A')