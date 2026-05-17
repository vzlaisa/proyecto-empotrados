from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout,
    QLineEdit, QPushButton, QMessageBox,
    QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QScrollArea
)

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

import sqlite3

from services.api_client import obtener_datos, enviar_config, obtener_params
from models.sensor_data import SensorData
from utils.config import INTERVALO_ACTUALIZACION

# Dashboard principal
class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        self.init_db()
        
        # VENTANA
        self.setWindowTitle("Monitor de Plantas")

        self.setGeometry(200, 100, 1200, 800)

        # ESTILO GENERAL
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f4f4;
                font-family: Arial;
                color: #2c3e50;
            }
        """)

        # SCROLL
        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
        """)

        container = QWidget()

        scroll.setWidget(container)

        # LAYOUT PRINCIPAL
        self.layout = QVBoxLayout(container)

        self.layout.setContentsMargins(
            30,
            30,
            30,
            30
        )

        self.layout.setSpacing(25)

        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main_layout.addWidget(scroll)

        # TITULO
        titulo = QLabel(
            "Monitor de cuidado de planta"
        )

        titulo.setAlignment(Qt.AlignCenter)

        titulo.setFont(
            QFont("Arial", 28, QFont.Bold)
        )

        titulo.setStyleSheet("""
            color: #2c3e50;
            margin-bottom: 10px;
        """)

        subtitulo = QLabel(
            "Datos actualizados en tiempo real"
        )

        subtitulo.setAlignment(Qt.AlignCenter)

        subtitulo.setStyleSheet("""
            color: #7f8c8d;
            font-size: 15px;
            margin-bottom: 20px;
        """)

        self.layout.addWidget(titulo)

        self.layout.addWidget(subtitulo)

        # ESTADO
        self.estado_label = QLabel(
            "Cargando..."
        )

        self.estado_label.setAlignment(
            Qt.AlignCenter
        )

        self.estado_label.setStyleSheet("""
            QLabel {
                background: white;
                border-radius: 18px;
                padding: 25px;
                font-size: 24px;
                font-weight: bold;
                color: #27ae60;
                border: 2px solid #c3e6cb;
            }
        """)

        self.layout.addWidget(
            self.estado_label
        )

        # TARJETAS
        grid = QGridLayout()

        grid.setHorizontalSpacing(20)

        grid.setVerticalSpacing(20)

        self.temp_card = self.create_card(
            "Temperatura"
        )

        self.hum_amb_card = self.create_card(
            "Humedad aire"
        )

        self.hum_suelo_card = self.create_card(
            "Humedad suelo"
        )

        self.luz_card = self.create_card(
            "Luz solar"
        )

        grid.addWidget(
            self.temp_card,
            0,
            0
        )

        grid.addWidget(
            self.hum_amb_card,
            0,
            1
        )

        grid.addWidget(
            self.hum_suelo_card,
            1,
            0
        )

        grid.addWidget(
            self.luz_card,
            1,
            1
        )

        self.layout.addLayout(grid)
        
        # TABLA TITULO
        tabla_titulo = QLabel(
            "Últimos registros"
        )

        tabla_titulo.setFont(
            QFont("Arial", 18, QFont.Bold)
        )

        tabla_titulo.setStyleSheet("""
            margin-top: 15px;
            margin-bottom: 10px;
        """)

        self.layout.addWidget(
            tabla_titulo
        )

        # TABLA
        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "Temperatura",
            "Hum. Aire",
            "Hum. Suelo",
            "Luz",
            "Estado"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setMinimumHeight(320)

        self.table.verticalHeader().setDefaultSectionSize(
            45
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.setShowGrid(False)

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border-radius: 18px;
                border: 1px solid #e8e8e8;
                padding: 10px;
                font-size: 14px;
                selection-background-color: #d4edda;
            }

            QHeaderView::section {
                background-color: #2ecc71;
                color: white;
                padding: 14px;
                border: none;
                font-size: 14px;
                font-weight: bold;
            }

            QTableCornerButton::section {
                background-color: #2ecc71;
                border: none;
            }
        """)

        self.layout.addWidget(
            self.table
        )

        # CONFIGURACION
        config_title = QLabel(
            "Parámetros configurables"
        )

        config_title.setFont(
            QFont("Arial", 18, QFont.Bold)
        )

        self.layout.addWidget(
            config_title
        )

        config_widget = QFrame()

        config_widget.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 20px;
                padding: 25px;
                border-left: 6px solid #2ecc71;
            }

            QLabel {
                background: transparent;
                font-weight: bold;
            }

            QLineEdit {
                background: #fafafa;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
            }

            QPushButton {
                background: #2ecc71;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 14px;
                font-size: 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #27ae60;
            }
        """)

        config_layout = QGridLayout()

        self.input_hum = QLineEdit()

        self.input_hum.setPlaceholderText(
            "Humedad mínima (%)"
        )

        self.input_temp = QLineEdit()

        self.input_temp.setPlaceholderText(
            "Temperatura máxima (°C)"
        )

        btn = QPushButton(
            "Guardar configuración"
        )

        btn.clicked.connect(
            self.guardar_config
        )

        config_layout.addWidget(
            QLabel("HUMEDAD MÍNIMA (%)"),
            0,
            0
        )

        config_layout.addWidget(
            self.input_hum,
            0,
            1
        )

        config_layout.addWidget(
            QLabel("TEMPERATURA MÁXIMA (°C)"),
            1,
            0
        )

        config_layout.addWidget(
            self.input_temp,
            1,
            1
        )

        config_layout.addWidget(
            btn,
            2,
            0,
            1,
            2
        )

        config_widget.setLayout(
            config_layout
        )

        self.layout.addWidget(
            config_widget
        )

        # TIMER PARA ACTUALIZAR DATOS
        self.timer = QTimer()

        self.timer.timeout.connect(
            self.actualizar
        )

        self.timer.start(
            INTERVALO_ACTUALIZACION
        )
        
        self.timer_params = QTimer()
        self.timer_params.timeout.connect(self.sincronizar_params)
        self.timer_params.start(5000)
        self.sincronizar_params()

        # Primera actualización
        self.actualizar()
        
        # Cargar configuración del ESP32
        self.cargar_configuracion()

    # CREAR TARJETA
    def create_card(self, titulo):
        frame = QFrame()

        frame.setStyleSheet("""
                QFrame {
                    background: white;
                    border-radius: 20px;
                    padding: 20px;
                    border: 1px solid #e8e8e8;
                }
            """)

        layout = QVBoxLayout()

        label_titulo = QLabel(titulo)

        label_titulo.setFont(
                QFont("Arial", 11)
            )

        label_titulo.setStyleSheet("""
                color:#7f8c8d;
            """)

        label_valor = QLabel("--")

        label_valor.setFont(
                QFont("Arial", 28, QFont.Bold)
            )

        label_valor.setStyleSheet("""
                color:#2c3e50;
            """)

        layout.addWidget(label_titulo)

        layout.addWidget(label_valor)

        frame.setLayout(layout)

        return frame

    # ACTUALIZAR DATOS
    def actualizar(self):
        data = obtener_datos()

        if not data:
            self.estado_label.setText(
                "Error de conexión"
            )

            self.estado_label.setStyleSheet("""
                QLabel {
                    background: #f8d7da;
                    color: #721c24;
                    border-radius: 18px;
                    padding: 25px;
                    font-size: 24px;
                    font-weight: bold;
                    border: 2px solid #f5c6cb;
                }
            """)

            return

        sensor = SensorData(data)

        # TARJETAS
        self.update_card(
            self.temp_card,
            sensor.temperatura,
            "°C"
        )

        self.update_card(
            self.hum_amb_card,
            sensor.humedad_ambiente,
            "%"
        )

        self.update_card(
            self.hum_suelo_card,
            sensor.humedad_suelo,
            "%"
        )

        self.update_card(
            self.luz_card,
            sensor.luz,
            "%"
        )

        # ESTADO
        if sensor.tipo == "alert":
            self.estado_label.setStyleSheet("""
                QLabel {
                    background: #f8d7da;
                    color: #721c24;
                    border-radius: 18px;
                    padding: 25px;
                    font-size: 24px;
                    font-weight: bold;
                    border: 2px solid #f5c6cb;
                }
            """)

        else:
            self.estado_label.setStyleSheet("""
                QLabel {
                    background: #d4edda;
                    color: #155724;
                    border-radius: 18px;
                    padding: 25px;
                    font-size: 24px;
                    font-weight: bold;
                    border: 2px solid #c3e6cb;
                }
            """)

        self.estado_label.setText(
            sensor.estado
        )

        # SQLITE
        self.guardar_registro(sensor)

        self.cargar_tabla()
        
    # ACTUALIZAR TARJETAS
    def update_card(self, card, value, unidad):
        layout = card.layout()

        label_valor = layout.itemAt(1).widget()

        label_valor.setText(
            f"{value}{unidad}"
        )

    # GUARDAR CONFIGURACIÓN
    def guardar_config(self):
        temp = self.input_temp.text()

        hum = self.input_hum.text()

        if enviar_config(temp, hum):
            self.cargar_configuracion()

            QMessageBox.information(
                self,
                "OK",
                "Configuración guardada"
            )

        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo conectar"
            )

    # CARGAR CONFIGURACIÓN DESDE ESP32
    def cargar_configuracion(self):
        data = obtener_params()

        if not data:
            return

        if "humedadMin" in data:
            self.input_hum.setText(str(data["humedadMin"]))

        if "tempMax" in data:
            self.input_temp.setText(str(data["tempMax"]))

    # SQLITE
    def init_db(self):
        self.conn = sqlite3.connect(
            "sensores.db"
        )

        self.cursor = self.conn.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperatura REAL,
                humedad_aire REAL,
                humedad_suelo REAL,
                luz REAL,
                estado TEXT
            )
        """)

        self.conn.commit()

    # GUARDAR REGISTRO
    def guardar_registro(self, sensor):
        self.cursor.execute("""
            INSERT INTO registros (
                temperatura,
                humedad_aire,
                humedad_suelo,
                luz,
                estado
            )
            VALUES (?, ?, ?, ?, ?)
        """, (

            sensor.temperatura,
            sensor.humedad_ambiente,
            sensor.humedad_suelo,
            sensor.luz,
            sensor.estado
        ))

        self.conn.commit()

    # CARGAR TABLA
    def cargar_tabla(self):
        self.cursor.execute("""
            SELECT
                temperatura,
                humedad_aire,
                humedad_suelo,
                luz,
                estado
            FROM registros
            ORDER BY id DESC
            LIMIT 5
        """)

        registros = self.cursor.fetchall()

        self.table.setRowCount(
            len(registros)
        )

        for fila, registro in enumerate(registros):
            for columna, valor in enumerate(registro):
                self.table.setItem(
                    fila,
                    columna,
                    QTableWidgetItem(
                        str(valor)
                    )
                )
                
    # SINCRONIZAR PARAMS DESDE ESP32
    def sincronizar_params(self):
        # No actualizar si el usuario está escribiendo
        if self.input_temp.hasFocus() or self.input_hum.hasFocus():
            return

        data = obtener_params()

        if not data:
            return

        if self.input_temp.text() != str(data.get("tempMax", "")):
            self.input_temp.setText(str(data["tempMax"]))

        if self.input_hum.text() != str(data.get("humedadMin", "")):
            self.input_hum.setText(str(data["humedadMin"]))