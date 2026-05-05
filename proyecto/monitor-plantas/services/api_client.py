import requests
from utils.config import ESP32_IP

# ---------------------------------------------------
# Esta función realiza una petición GET al endpoint /datos
# del ESP32 para obtener los valores actuales de los sensores.
# 
# Retorna: Diccionario JSON con los datos si todo va bien, o
# None si ocurre un error de conexión
# ---------------------------------------------------
def obtener_datos():
    try:
        response = requests.get(f"{ESP32_IP}/datos", timeout=2)
        return response.json()
    except:
        return None
    

# ---------------------------------------------------
# Esta función envía nuevos parámetros de configuración
# al ESP32 (temperatura máxima y humedad mínima)
# 
# Parámetros: temp (temperatura máxima permitida),
# hum  (humedad mínima del suelo)
# 
# Retorna: True si se envió correctamente, o False si
# hubo error
# ---------------------------------------------------
def enviar_config(temp, hum):
    try:
        requests.get(f"{ESP32_IP}/config?temp={temp}&hum={hum}", timeout=2)
        return True
    except:
        return False