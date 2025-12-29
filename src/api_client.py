import requests
import urllib3

# Desactivamos alertas SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AgroClimaClient:
    def __init__(self):
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        self.elevation_url = "https://api.open-meteo.com/v1/elevation"
        self.solar_url = "https://api.sunrise-sunset.org/json"
        self.geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    def buscar_opciones_ciudades(self, nombre):
        """
        Busca hasta 10 coincidencias y devuelve una lista para que el usuario elija.
        """
        try:
            # Pedimos 10 resultados ('count': 10)
            params = {"name": nombre, "count": 10, "language": "es", "format": "json"}
            resp = requests.get(self.geocoding_url, params=params, verify=False, timeout=5).json()
            
            opciones = []
            if "results" in resp:
                for r in resp["results"]:
                    # Armamos una etiqueta clara: "Nombre, Región, País"
                    pais = r.get("country", "")
                    region = r.get("admin1", "") # admin1 suele ser la región/departamento
                    nombre_lugar = r.get("name", "")
                    
                    etiqueta = f"{nombre_lugar}, {region} ({pais})"
                    
                    opciones.append({
                        "label": etiqueta,
                        "lat": r["latitude"],
                        "lon": r["longitude"],
                        "pais": pais
                    })
            return opciones
        except:
            return []

    def obtener_todo(self, lat, lon):
        clima = self._get_clima(lat, lon)
        pendiente, altitud = self._get_pendiente_altitud(lat, lon)
        horas_luz = self._get_datos_solares(lat, lon)
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
        except:
            # Valores por defecto si falla la API
            return {"temp_actual": 20, "humedad": 60, "precipitacion_anual_estimada": 500}

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
        try:
            params = {"lat": lat, "lng": lon, "formatted": 0}
            resp = requests.get(self.solar_url, params=params, verify=False, timeout=5).json()
            day_length_sec = resp["results"]["day_length"]
            return round(day_length_sec / 3600, 1)
        except:
            return 12.0

    def _estimar_ph_logico(self, lat, lon, lluvia_anual):
        if lluvia_anual > 2000: ph_base = 5.0
        elif lluvia_anual > 1000: ph_base = 6.0
        elif lluvia_anual > 400: ph_base = 7.0
        else: ph_base = 7.8
        return ph_base