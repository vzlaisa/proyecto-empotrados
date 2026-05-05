# ---------------------------------------------------
# Esta clase representa los datos obtenidos del ESP32.
# Sirve como modelo para facilitar el acceso a los valores.
# ---------------------------------------------------
class SensorData:
    def __init__(self, data):
        self.temperatura = data.get("temperatura", 0)
        self.humedad_suelo = data.get("humedadSuelo", 0)
        self.luz = data.get("luz", 0)
        self.humedad_ambiente = data.get("humedadAmbiente", 0)
        self.estado = data.get("estado", "Sin datos")
        self.tipo = data.get("tipoEstado", "ok")