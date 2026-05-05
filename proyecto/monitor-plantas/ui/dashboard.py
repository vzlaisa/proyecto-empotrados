from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
from collections import deque

from services.api_client import obtener_datos, enviar_config
from models.sensor_data import SensorData
from utils.config import INTERVALO_ACTUALIZACION

# ---------------------------------------------------
# Esta clase crea la interfaz gráfica principal de la aplicación.
# Muestra datos en tiempo real y permite configurar parámetros.
# ---------------------------------------------------
class Dashboard(QWidget):
    def __init__(self):
        super().__init__()

        # Configurar la ventana principal
        self.setWindowTitle("Monitor de Plantas")
        self.setGeometry(200, 100, 900, 600)

        # Buffers para almacenar datos de gráficas con un máximo de 50 puntos
        self.temp_data = deque(maxlen=50)
        self.hum_data = deque(maxlen=50)

        # Layout principal vertical
        self.layout = QVBoxLayout()

        # -------- ESTADO --------
        # Muestra el estado actual de la planta
        self.estado_label = QLabel("Cargando...")
        self.estado_label.setAlignment(Qt.AlignCenter)
        self.estado_label.setFont(QFont("Arial", 16))
        self.layout.addWidget(self.estado_label)

        # -------- TARJETAS --------
        # Contenedor en grid para mostrar sensores
        grid = QGridLayout()

        self.temp_card = self.create_card("Temperatura")
        self.hum_amb_card = self.create_card("Humedad Aire")
        self.hum_suelo_card = self.create_card("Humedad Suelo")
        self.luz_card = self.create_card("Luz")

        grid.addWidget(self.temp_card, 0, 0)
        grid.addWidget(self.hum_amb_card, 0, 1)
        grid.addWidget(self.hum_suelo_card, 1, 0)
        grid.addWidget(self.luz_card, 1, 1)

        self.layout.addLayout(grid)

        # -------- GRÁFICAS --------
        # Gráfica de temperatura
        self.plot_temp = pg.PlotWidget(title="Temperatura")
        # Gráfica de humedad del suelo
        self.plot_hum = pg.PlotWidget(title="Humedad del Suelo")

        self.layout.addWidget(self.plot_temp)
        self.layout.addWidget(self.plot_hum)

        # -------- CONFIGURACIÓN --------
        # Inputs para modificar parámetros del sistema
        config_layout = QGridLayout()

        self.input_temp = QLineEdit()
        self.input_temp.setPlaceholderText("Temp max")

        self.input_hum = QLineEdit()
        self.input_hum.setPlaceholderText("Hum min")

        btn = QPushButton("Guardar")
        btn.clicked.connect(self.guardar_config)

        config_layout.addWidget(QLabel("Temp Max"), 0, 0)
        config_layout.addWidget(self.input_temp, 0, 1)
        config_layout.addWidget(QLabel("Hum Min"), 1, 0)
        config_layout.addWidget(self.input_hum, 1, 1)
        config_layout.addWidget(btn, 2, 0, 1, 2)

        self.layout.addLayout(config_layout)

        self.setLayout(self.layout)

        # -------- TIMER --------
        # Actualiza los datos cada cierto intervalo (2 segundos según el intervalo configurado)
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar)
        self.timer.start(INTERVALO_ACTUALIZACION)

    # Función para crear tarjeta visual mostrada
    def create_card(self, titulo):
        frame = QFrame()

        # Estilo visual
        frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout()

        label_titulo = QLabel(titulo)
        label_valor = QLabel("--")

        label_titulo.setFont(QFont("Arial", 10))
        label_valor.setFont(QFont("Arial", 18))

        layout.addWidget(label_titulo)
        layout.addWidget(label_valor)

        frame.setLayout(layout)
        return frame

    # Función que obtiene datos del ESP32 y actualiza la UI
    def actualizar(self):
        data = obtener_datos()

        # Maneja el error de la conexión
        if not data:
            self.estado_label.setText("Error de conexión")
            self.estado_label.setStyleSheet("background:#f8d7da; color:red;")
            return

        sensor = SensorData(data)

        # -------- ACTUALIZAR TARJETAS --------
        self.update_card(self.temp_card, sensor.temperatura, "°C")
        self.update_card(self.hum_amb_card, sensor.humedad_ambiente, "%")
        self.update_card(self.hum_suelo_card, sensor.humedad_suelo, "%")
        self.update_card(self.luz_card, sensor.luz, "%")

        # -------- ESTADO --------
        if sensor.tipo == "alert":
            self.estado_label.setStyleSheet("background:#f8d7da; color:red; padding:10px;")
        else:
            self.estado_label.setStyleSheet("background:#d4edda; color:green; padding:10px;")

        self.estado_label.setText(sensor.estado)

        # -------- GRÁFICAS --------
        self.temp_data.append(sensor.temperatura)
        self.hum_data.append(sensor.humedad_suelo)

        self.plot_temp.clear()
        self.plot_temp.plot(list(self.temp_data))

        self.plot_hum.clear()
        self.plot_hum.plot(list(self.hum_data))

    # Esta función actualiza el valor mostrado en una tarjeta
    def update_card(self, card, value, unidad):
        layout = card.layout()
        label_valor = layout.itemAt(1).widget()
        label_valor.setText(f"{value}{unidad}")

    # Esta función envía nueva configuración de los datos al ESP32
    def guardar_config(self):
        temp = self.input_temp.text()
        hum = self.input_hum.text()

        if enviar_config(temp, hum):
            QMessageBox.information(self, "OK", "Configuración guardada")
        else:
            QMessageBox.warning(self, "Error", "No se pudo conectar")