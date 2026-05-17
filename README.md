# Monitor de Cuidado de Planta

Sistema de monitoreo en tiempo real para una maceta inteligente, desarrollado con ESP32. Permite visualizar y configurar los parámetros de la planta desde una interfaz web y una aplicación de escritorio en Python.


---

## Integrantes
00000253088 Ximena Rosales Panduro  
00000253301 Isabel Valcomoenzuela Rocha  

---

## Descripción
 
Este proyecto implementa una maceta inteligente capaz de monitorear en tiempo real:

- Temperatura ambiente
- Humedad ambiental
- Humedad del suelo
- Nivel de luz solar

El sistema utiliza un microcontrolador ESP32 como servidor web y controlador principal.
Los datos son mostrados tanto en una página web responsive como en una aplicación de escritorio desarrollada con PyQt5.

Además, el sistema incluye:

- Alertas visuales
- Alertas sonoras mediante buzzer
- Pantalla LCD
- Configuración remota de parámetros
- Almacenamiento local de registros con SQLite
 
---
## Elementos usados  

### Sensores
 - Sensor de temperatura y humedad DHT11
 - Sensor de humedad del suelo YL-69
 - Fotoresistencia LDR

### Actuadores
- Zumbador activo
- Pantalla LCD 1602

---
 
## Estados del sistema
 
| Estado | Condición | Buzzer | LCD |
|--------|-----------|--------|-----|
| `NORMAL` | Todo dentro de rangos | OFF | Humedad del suelo |
| `ALERTA_TEMPERATURA` | `temperatura > TEMP_MAX` | ON | Humedad del suelo |
| `ALERTA_HUMEDAD` | `humedadSuelo < HUMEDAD_MIN` | OFF | Humedad del suelo |
| `ERROR` | Falla en lectura | OFF | Humedad del suelo |
 
---
 
## API REST
 
### `GET /datos`
Devuelve las lecturas actuales de los sensores junto con los parámetros configurados.
 
```json
{
  "estado": "Planta en buen estado",
  "tipoEstado": "ok",
  "temperatura": 24.5,
  "humedadSuelo": 62,
  "luz": 78,
  "humedadAmbiente": 55.0,
  "tempMax": 40,
  "humedadMin": 40
}
```
 
### `GET /params`
Devuelve únicamente los parámetros configurables.
 
```json
{
  "tempMax": 40,
  "humedadMin": 40
}
```
 
### `GET /config?temp={valor}&hum={valor}`
Actualiza los umbrales de alerta en el ESP32.
 
```
GET /config?temp=35&hum=30
→ 200 OK
```
 
--- 
 
## Estructura del proyecto Python
 
```
proyecto/
├── main.py
├── sensores.db
├── models/
│   └── sensor_data.py
├── services/
│   └── api_client.py        # obtener_datos, enviar_config, obtener_params
├── utils/
│   └── config.py            # ESP32_IP, INTERVALO_ACTUALIZACION
└── views/
    └── dashboard.py         # Interfaz PyQt5
```
 
---
 
## Requisitos Python
 
```
PyQt5
requests
```
 
Instalar con:
 
```bash
pip install PyQt5 requests
```
 
---
 
## Configuración
 
En `utils/config.py` define la IP del ESP32 y el intervalo de actualización:
 
```python
ESP32_IP = "http://192.168.x.x"
INTERVALO_ACTUALIZACION = 2000  # milisegundos
```
 
---
 
## Parámetros configurables
 
Los umbrales de alerta se pueden modificar en tiempo real desde la interfaz web o desde la app de escritorio. El cambio se propaga automáticamente al otro cliente en el siguiente ciclo de sincronización (máximo 5 segundos).
 
| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `TEMP_MAX` | Temperatura máxima permitida (°C) | 40 |
| `HUMEDAD_MIN` | Humedad mínima del suelo (%) | 40 |

---
## *Pasos para correr el proyecto*
 
### 1. Instalar librerías en Arduino IDE
 
Abrir el gestor de librerías (`Sketch → Include Library → Manage Libraries`) e instalar:
 
- `DHT sensor library` — de Adafruit
- `LiquidCrystal` — de Arduino
- `AsyncTCP` — de dvarrel
- `ESPAsyncWebServer` — de lacamera
---
 
### 2. Configurar credenciales WiFi en el ESP32
 
En el archivo `.ino`, editar estas dos líneas con la red a usar:
 
```cpp
const char* ssid     = "TU_RED_WIFI";
const char* password = "TU_CONTRASEÑA";
```
 
---
 
### 3. Subir el HTML al ESP32 (LittleFS)
 
El archivo `index.html` debe estar en una carpeta llamada `data` dentro del proyecto de Arduino:
 
```
proyecto/
├── proyecto.ino
└── data/
    └── index.html
```
Conectar el ESP32 al dispositivo.  
Luego, subir el .html al ESP32 desde Arduino IDE con:
`ctrl + shift + p -> Upload LittleFS to Pico/ESP8266/ESP32`
 
---
 
### 4. Subir el sketch al ESP32
 
Compilar y subir el `.ino` normalmente con el botón de carga. Abrir el Monitor Serial a **115200 baudios** y espera a ver la IP asignada:
 
```
Conexion establecida
IP: 192.168.x.x
```
 
Anotar esa IP, se necesitará en el siguiente paso.
 
---
 
### 5. Configurar la IP en el proyecto Python
 
En `utils/config.py`, reemplazar la IP con la que apareció en el Monitor Serial:
 
```python
ESP32_IP = "http://192.168.x.x"
INTERVALO_ACTUALIZACION = 2000
```
 
---
 
### 6. Instalar dependencias Python
 
```bash
pip install PyQt5 requests
```
 
---
 
### 7. Correr la app de escritorio
 
Desde la raíz del proyecto Python:
 
```bash
python main.py
```
 
---
 
### 8. Abrir la interfaz web
 
Con el ESP32 encendido y conectado a la misma red, abrir en el navegador:
 
```
http://192.168.x.x
```
 
Ambas interfaces, la web y la app Python, funcionan simultáneamente y se sincronizan entre sí.
 
---
 
## Librerías ESP32
 
- `DHT` — lectura de temperatura y humedad
- `LiquidCrystal` — control del LCD 16x2
- `AsyncTCP` + `ESPAsyncWebServer` — servidor web asíncrono
- `LittleFS` — sistema de archivos para servir el HTML
