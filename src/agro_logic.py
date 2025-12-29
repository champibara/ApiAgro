import pandas as pd
import os

class AgroAnalisis:
    def __init__(self):
        self.base_path = "data/referencias"

    def cargar_reglas(self, categoria):
        archivo = os.path.join(self.base_path, f"{categoria}.csv")
        try:
            return pd.read_csv(archivo)
        except FileNotFoundError:
            return None

    def analizar(self, datos_api, categoria, variedad_nombre):
        df = self.cargar_reglas(categoria)
        # Buscar la fila de la raza/cultivo seleccionado
        regla = df[df['variedad'] == variedad_nombre].iloc[0]
        
        clima = datos_api['clima']
        topo = datos_api['topografia']
        suelo = datos_api['suelo']
        
        score = 100
        razones = []

        # --- 1. VALIDACIONES COMUNES (Temperatura y Pendiente) ---
        
        # Temperatura (usamos la actual como referencia rápida)
        if not (regla['temp_min'] <= clima['temp_actual'] <= regla['temp_max']):
            score -= 20
            razones.append(f"⚠️ Temperatura actual ({clima['temp_actual']}°C) fuera de rango ideal ({regla['temp_min']}-{regla['temp_max']}°C).")
        else:
            razones.append(f"✅ Temperatura adecuada.")

        # Pendiente
        if topo['pendiente'] > regla['pendiente_max']:
            penalizacion = 30 if "Cultivo" in regla['especie'] else 15
            score -= penalizacion
            razones.append(f"⛔ Pendiente del terreno ({topo['pendiente']:.1f}%) excede el máximo permitido ({regla['pendiente_max']}%).")
        
        # --- 2. VALIDACIONES ESPECÍFICAS ---

        if "Cultivo" in regla['especie']:
            # VALIDAR SUELO (pH)
            if not (regla['ph_min'] <= suelo['ph'] <= regla['ph_max']):
                score -= 25
                razones.append(f"⚠️ pH del suelo ({suelo['ph']}) inadecuado. Ideal: {regla['ph_min']}-{regla['ph_max']}.")
            else:
                razones.append(f"✅ pH del suelo óptimo.")
            
            # VALIDAR LLUVIA (Estimada)
            lluvia = clima['precipitacion_anual_estimada']
            if lluvia < regla['precip_min_mm']:
                score -= 20
                razones.append(f"💧 Falta de agua estimada ({lluvia:.0f}mm). Requiere: {regla['precip_min_mm']}mm.")
        
        else:
            # ES ANIMAL (Bovino, Porcino, Ave) -> VALIDAR ALTITUD
            # Los CSVs de animales tienen la columna 'altitud_max_m'
            if topo['altitud'] > regla['altitud_max_m']:
                score -= 40
                razones.append(f"⛔ Altitud excesiva ({topo['altitud']:.0f} msnm). Riesgo de mal de altura (Máx: {regla['altitud_max_m']}m).")
            else:
                razones.append(f"✅ Altitud segura.")

            # VALIDAR HUMEDAD
            if clima['humedad'] > regla['humedad_max']:
                score -= 10
                razones.append(f"⚠️ Humedad alta ({clima['humedad']}%). Riesgo de patógenos.")

        # Limitar score
        score = max(0, min(100, score))
        return score, razones, regla.get('riesgo_extra', 'N/A')