import requests
import urllib3
from datetime import datetime, timedelta

# Desactivamos alertas SSL (Tal como lo tenías)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AgroClimaClient:
    def __init__(self):
        # API de Pronóstico (Para clima actual)
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        
        # NUEVA: API Histórica (Para saber cuánto llovió el último año real)
        self.archive_url = "https://archive-api.open-meteo.com/v1/archive"
        
        # API de Búsqueda
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    def buscar_opciones_ciudades(self, nombre_ciudad):
        """Busca ciudades y devuelve una lista compatible con tu buscador nuevo."""
        if not nombre_ciudad: return []
        try:
            params = {"name": nombre_ciudad, "count": 5, "language": "es", "format": "json"}
            resp = requests.get(self.geocoding_url, params=params, verify=False, timeout=5).json()
            
            if "results" not in resp: return []
                
            opciones = []
            for r in resp["results"]:
                label = f"{r['name']}, {r.get('country', '')}"
                opciones.append({"label": label, "lat": r["latitude"], "lon": r["longitude"]})
            return opciones
        except:
            return []

    def _obtener_lluvia_real_anual(self, lat, lon):
        """
        Consulta el ARCHIVO HISTÓRICO (últimos 365 días)
        para obtener el dato REAL de lluvia, no una estimación.
        """
        try:
            # Calculamos las fechas: Desde hace 1 año hasta ayer
            fecha_fin = datetime.now() - timedelta(days=1)
            fecha_inicio = fecha_fin - timedelta(days=365)
            
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": fecha_inicio.strftime("%Y-%m-%d"),
                "end_date": fecha_fin.strftime("%Y-%m-%d"),
                "daily": "precipitation_sum",
                "timezone": "auto"
            }
            
            # Llamamos a la API de ARCHIVO (no a la de forecast)
            resp = requests.get(self.archive_url, params=params, verify=False, timeout=10).json()
            
            if "daily" in resp and "precipitation_sum" in resp["daily"]:
                # Sumamos la lluvia de cada día del último año
                lluvias = resp["daily"]["precipitation_sum"]
                # Filtramos valores nulos (None) y sumamos
                total = sum(x for x in lluvias if x is not None)
                return total
            
            return 0.0 # Si falla, retorna 0
        except Exception as e:
            print(f"Error lluvia histórica: {e}")
            return 0.0

    def obtener_todo(self, lat, lon):
        """Obtiene datos actuales + históricos combinados."""
        try:
            # 1. Obtener Lluvia Real (Usando la función nueva)
            lluvia_real = self._obtener_lluvia_real_anual(lat, lon)

            # 2. Obtener Clima Actual (Forecast API)
            params_clima = {
                "latitude": lat, 
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m"],
                "daily": "sunshine_duration", # Horas de sol
                "timezone": "auto"
            }
            resp = requests.get(self.weather_url, params=params_clima, verify=False, timeout=5).json()
            
            # Procesar Horas Luz (vienen en segundos)
            horas_luz = 12.0
            if "daily" in resp and "sunshine_duration" in resp["daily"]:
                segundos = resp["daily"]["sunshine_duration"][0]
                if segundos: horas_luz = round(segundos / 3600, 1)

            # Obtener Altitud (Open-Meteo lo incluye a veces, si no usamos valor por defecto)
            altitud = resp.get("elevation", 500) 

            return {
                "clima": {
                    "temp_actual": resp["current"]["temperature_2m"],
                    "humedad": resp["current"]["relative_humidity_2m"],
                    "precipitacion_anual_estimada": lluvia_real # <--- DATO REAL
                },
                "topografia": {
                    "altitud": altitud,
                    "pendiente": 0 # Simplificado
                },
                "solar": {
                    "horas_luz": horas_luz
                },
                "suelo": {
                    "ph": 6.5 # Valor por defecto editable en la app
                }
            }
        except Exception as e:
            print(f"Error general API: {e}")
            # Datos de respaldo para que no se rompa la app
            return {
                "clima": {"temp_actual": 20, "humedad": 60, "precipitacion_anual_estimada": 0},
                "topografia": {"altitud": 0},
                "solar": {"horas_luz": 12},
                "suelo": {"ph": 6.5}
            }