import requests
import urllib3
from datetime import datetime, timedelta

# Desactivamos alertas SSL para asegurar la compatibilidad en diferentes entornos de red
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AgroClimaClient:
    """
    MÓDULO DE EXTRACCIÓN (api_client.py)
    Esta clase actúa como el cliente principal para la obtención de datos externos.
    Gestiona tres endpoints de la API Open-Meteo: Pronóstico, Archivo Histórico y Geocodificación.
    """

    def __init__(self):
        """
        Inicializa las URLs base para los distintos servicios de extracción de datos.
        """
        # API de Pronóstico: Extrae variables climáticas actuales
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        
        # API Histórica: Extrae acumulados anuales reales (Estructuración de datos históricos)
        self.archive_url = "https://archive-api.open-meteo.com/v1/archive"
        
        # API de Búsqueda: Extrae coordenadas geográficas a partir de nombres de ciudades
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    def buscar_opciones_ciudades(self, nombre_ciudad):
        """
        FUENTE: API de Geocodificación.
        Busca ciudades y devuelve una lista de coordenadas (latitud/longitud).
        """
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
        EXTRACCIÓN HISTÓRICA: Consulta el ARCHIVO (últimos 365 días).
        Calcula el acumulado real de precipitaciones, evitando estimaciones genéricas.
        """
        try:
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
            
            resp = requests.get(self.archive_url, params=params, verify=False, timeout=10).json()
            
            if "daily" in resp and "precipitation_sum" in resp["daily"]:
                lluvias = resp["daily"]["precipitation_sum"]
                total = sum(x for x in lluvias if x is not None)
                return total
            
            return 0.0
        except Exception as e:
            print(f"Error lluvia histórica: {e}")
            return 0.0

    def obtener_todo(self, lat, lon):
        """
        ORQUESTADOR DE EXTRACCIÓN: Combina datos dinámicos y estáticos.
        Integra Clima, Topografía (Altitud) y Datos Solares en un solo objeto estructurado.
        """
        try:
            # 1. Obtención de Lluvia Real (Dato Histórico)
            lluvia_real = self._obtener_lluvia_real_anual(lat, lon)

            # 2. Obtención de Clima Actual y Horas de Sol (Dato en Tiempo Real)
            params_clima = {
                "latitude": lat, 
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m"],
                "daily": "sunshine_duration",
                "timezone": "auto"
            }
            resp = requests.get(self.weather_url, params=params_clima, verify=False, timeout=5).json()
            
            # Procesar Horas Luz: Conversión de segundos a horas (Normalización)
            horas_luz = 12.0
            if "daily" in resp and "sunshine_duration" in resp["daily"]:
                segundos = resp["daily"]["sunshine_duration"][0]
                if segundos: horas_luz = round(segundos / 3600, 1)

            altitud = resp.get("elevation", 500) 

            return {
                "clima": {
                    "temp_actual": resp["current"]["temperature_2m"],
                    "humedad": resp["current"]["relative_humidity_2m"],
                    "precipitacion_anual_estimada": lluvia_real
                },
                "topografia": {"altitud": altitud, "pendiente": 0},
                "solar": {"horas_luz": horas_luz},
                "suelo": {"ph": 6.5}
            }
        except Exception as e:
            print(f"Error general API: {e}")
            return {
                "clima": {"temp_actual": 20, "humedad": 60, "precipitacion_anual_estimada": 0},
                "topografia": {"altitud": 0},
                "solar": {"horas_luz": 12},
                "suelo": {"ph": 6.5}
            }