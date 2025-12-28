import requests
import urllib3

# Desactivamos alertas SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AgroClimaClient:
    def __init__(self):
        self.weather_url = "https://api.open-meteo.com/v1/forecast"
        self.elevation_url = "https://api.open-meteo.com/v1/elevation"
        # YA NO usamos SoilGrids porque falla mucho

    def obtener_todo(self, lat, lon):
        """Función maestra que obtiene clima real y estima el suelo"""
        
        # 1. Clima y Topografía (APIs de Open-Meteo que SÍ funcionan)
        clima = self._get_clima(lat, lon)
        pendiente, altitud = self._get_pendiente_altitud(lat, lon)
        
        # 2. Suelo (Estimación lógica basada en ubicación para no depender de APIs caídas)
        ph = self._estimar_ph_logico(lat, lon, clima['precipitacion_anual_estimada'])
        
        return {
            "clima": clima,
            "topografia": {"pendiente": pendiente, "altitud": altitud},
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
            # verify=False para evitar bloqueos de antivirus/red
            resp = requests.get(self.weather_url, params=params, verify=False, timeout=5).json()
            
            # Estimación simple de lluvia anual
            lluvia_anual = sum(resp["daily"]["precipitation_sum"]) * (365/7) # Proyección anual basada en la semana

            return {
                "temp_actual": resp["current"]["temperature_2m"],
                "humedad": resp["current"]["relative_humidity_2m"],
                "precipitacion_anual_estimada": lluvia_anual,
                "temp_min_dia": resp["daily"]["temperature_2m_min"][0],
                "temp_max_dia": resp["daily"]["temperature_2m_max"][0]
            }
        except Exception as e:
            print(f"⚠️ Error Clima: {e}")
            return {"temp_actual": 25, "humedad": 60, "precipitacion_anual_estimada": 800, "temp_min_dia": 15, "temp_max_dia": 28}

    def _get_pendiente_altitud(self, lat, lon):
        try:
            lat_b = lat + 0.001 
            resp = requests.get(
                self.elevation_url, 
                params={"latitude": [lat, lat_b], "longitude": [lon, lon]},
                verify=False, 
                timeout=5
            ).json()
            
            elevs = resp.get("elevation", [0, 0])
            if elevs[0] is None: elevs = [0,0] # Corrección para océano
            
            h1, h2 = elevs
            pendiente = (abs(h2 - h1) / 111.0) * 100
            
            return pendiente, h1
        except:
            return 0, 0

    def _estimar_ph_logico(self, lat, lon, lluvia_anual):
        """
        Alternativa a SoilGrids:
        Estima el pH basándose en reglas agronómicas generales.
        Mayor lluvia = Más acidez (pH bajo).
        Zonas áridas = Más alcalinidad (pH alto).
        """
        # Regla base: El pH suele ser inverso a la lluvia (lixiviación de bases)
        if lluvia_anual > 2000:
            # Selva / Bosque húmedo -> Muy Ácido
            ph_base = 5.0
        elif lluvia_anual > 1000:
            # Sierra / Zona templada -> Ligeramente Ácido
            ph_base = 6.0
        elif lluvia_anual > 400:
            # Valles secos -> Neutro
            ph_base = 7.0
        else:
            # Desierto / Costa -> Alcalino
            ph_base = 7.8
            
        return ph_base