/*
 *
 * Este programa implementa un sistema de monitoreo para una "Maceta Inteligente" 
 * utilizando el microcontrolador ESP32. El sistema integra sensores de 
 * temperatura y humedad ambiental (DHT11), humedad de suelo y niveles de luz.
 * 
 * El dispositivo funciona como un servidor web asíncrono (AsyncWebServer) que 
 * permite la visualización de datos en tiempo real mediante una interfaz web 
 * almacenada en el sistema de archivos LittleFS.
 * 
 * Incluye una lógica de control por estados que gestiona alertas visuales 
 * en una pantalla LCD y alertas sonoras mediante un buzzer activo. Los umbrales 
 * de activación para la temperatura máxima y la humedad mínima del suelo 
 * son configurables de manera dinámica a través de una API REST.
 * 
 * Integrantes del equipo:
 * 00000253088 Ximena Rosales Panduro
 * 00000253301 Isabel Valenzuela Rocha
 */

#include "DHT.h"
#include <LiquidCrystal.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <LittleFS.h>

// ----------- PINES -----------
int ldrPin = 34;
int humedadPin = 32;

#define DHTPIN 27
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

int buzzer = 25;

LiquidCrystal lcd(19, 18, 5, 17, 16, 4);

// ----------- ESTADOS DEL SISTEMA -----------
enum EstadoSistema {
  INICIAL,
  NORMAL,
  ALERTA_TEMPERATURA,
  ALERTA_HUMEDAD,
  ERROR
};

// ----------- ENUMS -----------
enum EstadoHumedad {
  SECA,
  MEDIA,
  HUMEDA
};

EstadoSistema estadoActual = INICIAL;

// ----------- VARIABLES -----------
int luz;
int humedadSuelo;
float temperatura;
float humedadAmbiente;

float TEMP_MAX = 40;
int HUMEDAD_MIN = 40;

// ----------- WIFI -----------
const char* ssid = "MEGACABLE-2.4G-FCA5";
const char* password = "R54tgjp3nD";

AsyncWebServer server(80);

// Conectarse a la red
void conectarWifi() {
  WiFi.mode(WIFI_STA);

  Serial.print("Conectandose a la red ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConexion establecida");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

// API para datos
void configurarAPI() {

  // html
  server.on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
    request->send(LittleFS, "/index.html", "text/html");
  });

  // Datos
  server.on("/datos", HTTP_GET, [](AsyncWebServerRequest* request) {

    int humedadPorcentaje = map(humedadSuelo, 0, 4095, 100, 0);
    int luzPorcentaje = map(luz, 0, 4095, 0, 100);

    String json = "{";
    json += "\"estado\":\"" + obtenerEstadoTexto(estadoActual) + "\",";
    json += "\"tipoEstado\":\"" + obtenerTipoEstado(estadoActual) + "\",";
    json += "\"temperatura\":" + String(temperatura) + ",";
    json += "\"humedadSuelo\":" + String(humedadPorcentaje) + ",";
    json += "\"luz\":" + String(luzPorcentaje) + ",";
    json += "\"humedadAmbiente\":" + String(humedadAmbiente) + ",";
    json += "\"tempMax\":" + String(TEMP_MAX) + ",";
    json += "\"humedadMin\":" + String(HUMEDAD_MIN);
    json += "}";

    request->send(200, "application/json", json);
  });

  server.on("/params", HTTP_GET, [](AsyncWebServerRequest* request) {

    String json = "{";
    json += "\"tempMax\":" + String(TEMP_MAX) + ",";
    json += "\"humedadMin\":" + String(HUMEDAD_MIN);
    json += "}";

    request->send(200, "application/json", json);
  });

  // Parámetros configurables
  server.on("/config", HTTP_GET, [](AsyncWebServerRequest* request) {

    if (request->hasParam("temp")) {
      TEMP_MAX = request->getParam("temp")->value().toFloat();
    }

    if (request->hasParam("hum")) {
      HUMEDAD_MIN = request->getParam("hum")->value().toInt();
    }

    Serial.println("---- CONFIG ACTUALIZADA ----");
    Serial.print("TEMP_MAX: "); Serial.println(TEMP_MAX);
    Serial.print("HUMEDAD_MIN (%): "); Serial.println(HUMEDAD_MIN);

    request->send(200, "text/plain", "OK");
  });

  server.begin();
  Serial.println("Servidor web listo");
}

// ----------- SETUP -----------
void setup() {
  Serial.begin(115200);

  dht.begin();
  pinMode(buzzer, OUTPUT);
  lcd.begin(16, 2);

  conectarWifi();

  if (!LittleFS.begin(true)) {
    Serial.println("Error montando LittleFS");
    return;
  }

  configurarAPI();
}

// ----------- LOOP -----------
void loop() {

  leerSensores();
  actualizarEstado();
  ejecutarEstado();

  delay(2000);
}

// ----------- FUNCIONES -----------

// Leer sensores
void leerSensores() {
  luz = analogRead(ldrPin);
  humedadSuelo = analogRead(humedadPin);

  temperatura = dht.readTemperature();
  humedadAmbiente = dht.readHumidity();
}

// Actualizar el estado
void actualizarEstado() {

  if (isnan(temperatura) || isnan(humedadAmbiente)) {
    estadoActual = ERROR;
    return;
  }

  int humedadPorcentaje = map(humedadSuelo, 0, 4095, 100, 0);

  Serial.print("Humedad %: ");
  Serial.println(humedadPorcentaje);

  if (temperatura > TEMP_MAX) {
    estadoActual = ALERTA_TEMPERATURA;
  } 
  else if (humedadPorcentaje < HUMEDAD_MIN) {
    estadoActual = ALERTA_HUMEDAD;
  } 
  else {
    estadoActual = NORMAL;
  }
}

// Ejecutar actuadores
void ejecutarEstado() {

  EstadoHumedad estadoH = obtenerEstadoHumedad(humedadSuelo);

  // Pantalla para humedad del suelo
  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print("Humedad suelo:");

  lcd.setCursor(0, 1);
  lcd.print(obtenerHumedadTexto(estadoH));

  // Buzzer para temperatura
  if (estadoActual == ALERTA_TEMPERATURA) {
    digitalWrite(buzzer, HIGH);
  } else {
    digitalWrite(buzzer, LOW);
  }

  mostrarSerial();
}

// Imprimir en serial
void mostrarSerial() {
  Serial.print("Estado: ");
  Serial.print(obtenerEstadoTexto(estadoActual));

  Serial.print(" | Temp: ");
  Serial.print(temperatura);

  Serial.print(" | Humedad RAW: ");
  Serial.print(humedadSuelo);

  Serial.print(" | Luz: ");
  Serial.println(luz);
}

// ----------- TEXTO -----------
String obtenerEstadoTexto(EstadoSistema estado) {
  switch (estado) {
    case INICIAL: return "Iniciando";
    case NORMAL: return "Planta en buen estado";
    case ALERTA_TEMPERATURA: return "Alta temperatura";
    case ALERTA_HUMEDAD: return "Suelo seco";
    case ERROR: return "Error sensor";
    default: return "Desconocido";
  }
}

String obtenerTipoEstado(EstadoSistema estado) {
  switch (estado) {
    case NORMAL: return "ok";
    case ALERTA_TEMPERATURA:
    case ALERTA_HUMEDAD:
    case ERROR: return "alert";
    default: return "ok";
  }
}

// ----------- HUMEDAD -----------
EstadoHumedad obtenerEstadoHumedad(int valor) {
  int porcentaje = map(valor, 0, 4095, 100, 0);

  if (porcentaje < HUMEDAD_MIN) {
    return SECA;
  } else if (porcentaje < 70) {
    return MEDIA;
  } else {
    return HUMEDA;
  }
}

String obtenerHumedadTexto(EstadoHumedad estado) {
  switch (estado) {
    case SECA: return "SECA";
    case MEDIA: return "MEDIA";
    case HUMEDA: return "HUMEDA";
    default: return "";
  }
}