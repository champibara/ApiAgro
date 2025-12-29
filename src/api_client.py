import requests
import urllib3

# Desactivamos alertas SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AgroClimaClient:
    def __init__(self):
        # API 1: Clima (Open-Meteo)
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        # API 2: Elevación (Open-Meteo)
        self.elevation_url = "https://api.open-meteo.com/v1/elevation"
        # API 3: Datos Solares (Sunrise-Sunset.org) - ¡NUEVA!
        self.solar_url = "https://api.sunrise-sunset.org/json"

    def obtener_todo(self, lat, lon):
        """Función maestra que consulta 3 APIs distintas"""
        
        # 1. Llamada a API de Clima
        clima = self._get_clima(lat, lon)
        
        # 2. Llamada a API de Topografía
        pendiente, altitud = self._get_pendiente_altitud(lat, lon)
        
        # 3. Llamada a API Solar (NUEVO)
        horas_luz = self._get_datos_solares(lat, lon)
        
        # 4. Lógica interna (sin API externa)
        ph = self._estimar_ph_logico(lat, lon, clima['precipitacion_anual_estimada'])
        
        return {
            "clima": clima,
            "topografia": {"pendiente": pendiente, "altitud": altitud},
            "solar": {"horas_luz": horas_luz},
            "suelo": {"ph": ph}
        }

    def _get_clima(self, lat, lon):
        try:
            params = {
                "latitude": lat, "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m"],
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
                "timezone": "auto"
            }
            resp = requests.get(self.weather_url, params=params, verify=False, timeout=5).json()
            lluvia_anual = sum(resp["daily"]["precipitation_sum"]) * (365/7)
            return {
                "temp_actual": resp["current"]["temperature_2m"],
                "humedad": resp["current"]["relative_humidity_2m"],
                "precipitacion_anual_estimada": lluvia_anual,
                "temp_min_dia": resp["daily"]["temperature_2m_min"][0],
                "temp_max_dia": resp["daily"]["temperature_2m_max"][0]
            }
        except Exception:
            return {"temp_actual": 25, "humedad": 60, "precipitacion_anual_estimada": 800}

    def _get_pendiente_altitud(self, lat, lon):
        try:
            lat_b = lat + 0.001 
            resp = requests.get(
                self.elevation_url, 
                params={"latitude": [lat, lat_b], "longitude": [lon, lon]},
                verify=False, timeout=5
            ).json()
            elevs = resp.get("elevation", [0, 0])
            if elevs[0] is None: elevs = [0,0]
            h1, h2 = elevs
            pendiente = (abs(h2 - h1) / 111.0) * 100
            return pendiente, h1
        except:
            return 0, 0

    def _get_datos_solares(self, lat, lon):
        """Consulta la API de Sunrise-Sunset para obtener el fotoperiodo"""
        try:
            params = {"lat": lat, "lng": lon, "formatted": 0}
            # Esta es la TERCERA API
            resp = requests.get(self.solar_url, params=params, verify=False, timeout=5).json()
            
            # La API devuelve segundos de luz, convertimos a horas
            day_length_sec = resp["results"]["day_length"]
            horas = day_length_sec / 3600 
            return round(horas, 1)
        except:
            return 12.0 # Promedio en el ecuador si falla

    def _estimar_ph_logico(self, lat, lon, lluvia_anual):
        if lluvia_anual > 2000: ph_base = 5.0
        elif lluvia_anual > 1000: ph_base = 6.0
        elif lluvia_anual > 400: ph_base = 7.0
        else: ph_base = 7.8
        return ph_base