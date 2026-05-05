import sys
from PyQt5.QtWidgets import QApplication
from ui.dashboard import Dashboard

# ---------------------------------------------------
# Punto de entrada de la aplicación
#
# Integrantes del equipo:
# 00000253088 Ximena Rosales Panduro
# 00000253301 Isabel Valenzuela Rocha
# ---------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())