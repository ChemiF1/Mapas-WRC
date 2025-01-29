import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QListWidget, QLineEdit, QLabel, QMessageBox
)

class TramosApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Tramos")
        self.setGeometry(100, 100, 400, 300)

        # Lista de tramos
        self.tramos = []

        # Configuración de la interfaz
        self.init_ui()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()

        # Input para inicio y fin
        input_layout = QHBoxLayout()
        self.inicio_input = QLineEdit()
        self.inicio_input.setPlaceholderText("Inicio del tramo")
        self.fin_input = QLineEdit()
        self.fin_input.setPlaceholderText("Fin del tramo")
        input_layout.addWidget(QLabel("Inicio:"))
        input_layout.addWidget(self.inicio_input)
        input_layout.addWidget(QLabel("Fin:"))
        input_layout.addWidget(self.fin_input)
        main_layout.addLayout(input_layout)

        # Botones para añadir, editar y eliminar
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Añadir tramo")
        self.add_button.clicked.connect(self.add_tramo)
        self.edit_button = QPushButton("Editar tramo")
        self.edit_button.clicked.connect(self.edit_tramo)
        self.delete_button = QPushButton("Eliminar tramo")
        self.delete_button.clicked.connect(self.delete_tramo)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        main_layout.addLayout(button_layout)

        # Lista para mostrar los tramos
        self.tramos_list = QListWidget()
        main_layout.addWidget(self.tramos_list)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def add_tramo(self):
        try:
            inicio = int(self.inicio_input.text())
            fin = int(self.fin_input.text())

            if inicio >= fin:
                raise ValueError("El inicio debe ser menor que el fin.")

            # Verificar solapamientos
            for tramo in self.tramos:
                if not (fin <= tramo[0] or inicio >= tramo[1]):
                    raise ValueError("El tramo se solapa con uno existente.")

            # Añadir tramo
            self.tramos.append((inicio, fin))
            self.tramos.sort()  # Ordenar los tramos por el inicio
            self.update_tramos_list()
            self.inicio_input.clear()
            self.fin_input.clear()
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Entrada inválida: {e}")

    def edit_tramo(self):
        try:
            selected_items = self.tramos_list.selectedItems()
            if not selected_items:
                raise ValueError("No se ha seleccionado ningún tramo para editar.")

            selected_item = selected_items[0]
            selected_index = self.tramos_list.row(selected_item)

            # Prellenar los inputs con los valores del tramo seleccionado
            inicio, fin = self.tramos[selected_index]
            self.inicio_input.setText(str(inicio))
            self.fin_input.setText(str(fin))

            # Eliminar el tramo de la lista temporalmente
            del self.tramos[selected_index]
            self.update_tramos_list()
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error al editar: {e}")

    def delete_tramo(self):
        try:
            selected_items = self.tramos_list.selectedItems()
            if not selected_items:
                raise ValueError("No se ha seleccionado ningún tramo para eliminar.")

            selected_item = selected_items[0]
            selected_index = self.tramos_list.row(selected_item)

            # Eliminar el tramo de la lista
            del self.tramos[selected_index]
            self.update_tramos_list()
        except ValueError as e:
            QMessageBox.critical(self, "Error", f"Error al eliminar: {e}")

    def update_tramos_list(self):
        self.tramos_list.clear()
        for inicio, fin in self.tramos:
            self.tramos_list.addItem(f"{inicio} - {fin}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TramosApp()
    window.show()
    sys.exit(app.exec())
