import geopandas as gpd
import fiona
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas)
from matplotlib.figure import Figure

import sys
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget,
                             QVBoxLayout, QComboBox, QPushButton, QLabel, QHBoxLayout, QColorDialog, QLineEdit, QMessageBox, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

fiona.drvsupport.supported_drivers['kml'] = 'rw' # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = Figure(figsize=(16, 10)), None
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot(self, x, y, longitud_total):
        self.ax.clear()
        self.ax.plot(x, y, lw = 2, color = "black")
        self.ax.set_title(name + " - Longitud: " + f"{longitud_total:.2f} km" )
        # self.ax.set_xlabel('X-axis')
        # self.ax.set_ylabel('Y-axis')
        self.ax.axis("off")
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self, layers):
        super().__init__()
        self.setWindowTitle("Selección de Tramo")
        
        QApplication.setStyle("Fusion")
        # QApplication.primaryScreen()
        
        
        
        screen = app.primaryScreen()
        screen_size = screen.size()
        self.setGeometry(0, 0, screen_size.width(), screen_size.height())
        self.showMaximized()
        
        self.layers = layers
        self.legend_items = []  # Inicializar la lista de elementos de la leyenda
        self.longitud_total = 0  # Inicializar la longitud total
        self.length_label = QLabel("Longitud Total: 0.00 km")
        
        self.longitud_total = 0  # Inicializar la longitud total
        
        # Inicializar las variables inicio_tramo y fin_tramo con valores predeterminados
        self.inicio_tramo = 0.0  # Inicio por defecto en 0 km
        self.fin_tramo = 10.0    # Fin por defecto en 10 km (o la longitud total del tramo)
        self.section_size_input = 0.500 # Tamaño de la sección por defecto en 500 m
        
        self.tramos = []  # Lista para almacenar los tramos
        self.tramos_colores = []  # Lista para los colores de los tramos (por ejemplo, estados)
        self.current_start = 0.0  # Inicio del tramo actual
        
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # First Tab
        self.first_tab = QWidget()
        self.tab_widget.addTab(self.first_tab, "Visualización del Tramo")

        self.second_tab = QWidget()
        self.tab_widget.addTab(self.second_tab, "Leyenda")
        
        self.third_tab = QWidget()
        self.tab_widget.addTab(self.third_tab, "Tramos")
        
        self.init_first_tab()
        self.init_second_tab()
        self.init_third_tab()

        # Botones de navegación
        self.navigation_layout = QHBoxLayout()
        self.previous_button = QPushButton("Anterior")
        self.previous_button.clicked.connect(self.go_to_previous_tab)
        self.next_button = QPushButton("Siguiente")
        self.next_button.clicked.connect(self.go_to_next_tab)

        self.navigation_layout.addWidget(self.previous_button)
        self.navigation_layout.addWidget(self.next_button)

        # Configurar estado inicial de botones
        self.update_navigation_buttons()

        # Añadir layout de navegación al final
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addLayout(self.navigation_layout)

        # Widget central
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)
        
        # FUNCIONES PARA PRIMERA PESTAÑA ****************************************************
    def init_first_tab(self):
        layout = QVBoxLayout()

        self.first_dropdown = QComboBox()
        self.first_dropdown.addItems(["Select Track"] + self.layers) 
        self.first_dropdown.currentIndexChanged.connect(self.update_second_dropdown)

        self.second_dropdown = QComboBox()
        self.second_dropdown.addItem("Select Option")

        self.plot_button = QPushButton("Generate Plot")
        self.plot_button.clicked.connect(self.generate_plot)
        self.plot_button.setEnabled(False)

        self.plot_canvas = PlotCanvas(self)

        self.status_label = QLabel("Select values from both dropdowns.")
        self.status_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.first_dropdown)
        layout.addWidget(self.second_dropdown)
        layout.addWidget(self.plot_button)
        layout.addWidget(self.plot_canvas)
        layout.addWidget(self.status_label)

        self.first_tab.setLayout(layout)

    def update_second_dropdown(self):
        global gdf
        global gdf_list
        self.second_dropdown.clear()
        selection = self.first_dropdown.currentText()

        gdf = gpd.read_file(filename, driver="KML", layer=selection)
        gdf_list = [gdf.iloc[[i]] for i in range(len(gdf))]
        Names = []
        for i in range(len(gdf_list)):
            Names.append(gdf_list[i]["Name"].iloc[0])
            
        self.second_dropdown.addItems(["Select Tramo"] + Names)
        self.plot_button.setEnabled(True)

    def generate_plot(self):
        
        global name
        selection = self.first_dropdown.currentText()
        name = self.second_dropdown.currentText()
        
        gdf = next(gdf_part for gdf_part in gdf_list if gdf_part["Name"].iloc[0] == name)
        
                # Actualiza la longitud total aquí
        
        # Transformar a un CRS proyectado (por ejemplo, UTM o Web Mercator EPSG:3857)
        gdf_projected = gdf.to_crs(epsg=3099)
        # Calcular la longitud de cada tramo en metros
        gdf_projected['length_m'] = gdf_projected.length
        # Convertir la longitud a kilómetros
        gdf_projected['length_km'] = gdf_projected['length_m'] / 1000
        
        # Mostrar las longitudes en kilómetros
        self.longitud_total = gdf_projected['length_km'].iloc[0]
        
        # Actualizar la tercera pestaña con la longitud total
        self.update_third_tab_from_first_tab()
        
        x,y, = gdf_projected.geometry.iloc[0].xy
        
        self.plot_canvas.plot(x,y,self.longitud_total)
        self.status_label.setText(f"Longitud total del tramo {name}: {self.longitud_total:.2f} km")

    def update_third_tab_from_first_tab(self):
        # Aquí actualizamos los elementos de la tercera pestaña
        if hasattr(self, 'third_tab'):
            self.inicio_label.setText(f"Inicio del tramo: 0.00 km")  # O el valor que desees
            self.fin_label.setText(f"Fin del tramo: {self.longitud_total:.2f} km")
            self.fin_tramo_input.setText(f"{self.longitud_total:.2f}")  # Actualiza el QLineEdit
            

    # FUNCIONES PARA SEGUNDA PESTAÑA ****************************************************
    def init_second_tab(self):
        layout = QVBoxLayout()

        # Selector de color
        self.color_label = QLabel("Color seleccionado: Ninguno")
        self.color_label.setAlignment(Qt.AlignCenter)

        self.color_button = QPushButton("Seleccionar color")
        self.color_button.clicked.connect(self.select_color)

        # Campo de texto
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Introduce descripción aquí...")

        # Botón para añadir a la leyenda
        self.add_button = QPushButton("Añadir a la leyenda")
        self.add_button.clicked.connect(self.add_to_legend)

        # Lienzo para la leyenda
        self.legend_canvas = PlotCanvas(self)

        # Añadir widgets al layout
        layout.addWidget(self.color_label)
        layout.addWidget(self.color_button)
        layout.addWidget(self.text_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.legend_canvas)


        self.second_tab.setLayout(layout)

    def select_color(self):
        # Abre un diálogo para seleccionar color
        color = QColorDialog.getColor()

        if color.isValid():
            self.selected_color = color.name()
            self.color_label.setText(f"Color seleccionado: {self.selected_color}")
            self.color_label.setStyleSheet(f"background-color: {self.selected_color}; color: white;")
        else:
            self.color_label.setText("No se seleccionó ningún color.")
            self.selected_color = None

    def add_to_legend(self):
        # Validar que se haya seleccionado un color y que el texto no esté vacío
        color = getattr(self, "selected_color", None)
        text = self.text_input.text().strip()

        if not color:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un color.")
            return

        if not text:
            QMessageBox.warning(self, "Error", "Por favor, introduce una descripción.")
            return

        # Añadir el elemento a la lista de leyenda
        self.legend_items.append((color, text))
        self.update_legend()
        self.update_legend_dropdown()

    def update_legend(self):
        # Dibujar la leyenda en el lienzo
        self.legend_canvas.ax.clear()

        for i, (color, text) in enumerate(self.legend_items):
            y_pos = -i * 1  # Espaciado vertical entre elementos
            self.legend_canvas.ax.add_patch(
                plt.Rectangle((0, y_pos), 2, 1, color=color)  # Rectángulo para el color
            )
            self.legend_canvas.ax.text(2.5, y_pos + 0.5, text, va='center', fontsize=10)  # Texto asociado

        # Configurar límites y ocultar ejes
        self.legend_canvas.ax.set_xlim(-1, 10)
        self.legend_canvas.ax.set_ylim(-len(self.legend_items) * 1.5, 1.5)
        self.legend_canvas.ax.axis('off')

        # Dibujar el canvas
        self.legend_canvas.draw()
            
    def update_legend_dropdown(self):
        self.legend_dropdown.clear()  # Limpiar el ComboBox
        for color, text in self.legend_items:
            self.legend_dropdown.addItem(text)  # Añadir solo el texto al ComboBox
    
# FUNCIONES PARA TERCERA PESTAÑA ****************************************************
    def init_third_tab(self):
        layout = QVBoxLayout()

        # Layout para la sección superior
        top_layout = QHBoxLayout()

        # Añadir los widgets de Inicio y Fin con bordes y estilos
        self.inicio_label = QLabel("Inicio:")
        self.inicio_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E86C1;")
        self.inicio_tramo_input = QLineEdit()
        self.inicio_tramo_input.setText(f"{self.inicio_tramo:.2f}")
        self.inicio_tramo_input.setAlignment(Qt.AlignCenter)
        self.inicio_tramo_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                border: 1px solid #AED6F1;
                border-radius: 6px;
                padding: 5px;
            }
        """)

        self.fin_label = QLabel("Fin:")
        self.fin_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2E86C1;")
        self.fin_tramo_input = QLineEdit()
        self.fin_tramo_input.setText(f"{self.longitud_total:.2f}")
        self.fin_tramo_input.setAlignment(Qt.AlignCenter)
        self.fin_tramo_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                border: 1px solid #AED6F1;
                border-radius: 6px;
                padding: 5px;
            }
        """)

        # Botón Finalizar estilizado
        self.finish_button = QPushButton("Finalizar")
        self.finish_button.clicked.connect(self.finalize_limits)
        self.finish_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #5DADE2; /* Azul brillante */
                border: 2px solid #2E86C1;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2E86C1; /* Azul más oscuro al pasar el cursor */
            }
        """)

        # Añadir widgets al layout de la parte superior
        top_layout.addWidget(self.inicio_label)
        top_layout.addWidget(self.inicio_tramo_input)
        top_layout.addWidget(self.fin_label)
        top_layout.addWidget(self.fin_tramo_input)
        top_layout.addWidget(self.finish_button)

        # Layout para "Inicio actual"
        self.current_start_label = QLabel(f"Inicio actual: -")
        self.current_start_label.setAlignment(Qt.AlignCenter)
        self.current_start_label.setStyleSheet("""
            QLabel {
                font-size: 24px;           /* Tamaño de letra grande */
                font-weight: bold;         /* Letra en negrita */
                color: #2E86C1;            /* Color azul atractivo */
                border: 2px solid #AED6F1; /* Borde alrededor del texto */
                border-radius: 8px;        /* Bordes redondeados */
                background-color: #EAF2F8; /* Fondo suave azul */
                padding: 10px;             /* Espaciado interno */
            }
        """)
        self.current_start_label.setFixedHeight(60)  # Altura fija para mayor visibilidad

        # Campo para ingresar el tamaño de cada sección
        section_layout = QHBoxLayout()
        section_label = QLabel("Tamaño del segmento (km):")
        self.section_size_input = QLineEdit()
        self.section_size_input.setText("0.50")  # Valor predeterminado
        self.section_size_input.setAlignment(Qt.AlignCenter)
        self.section_size_input.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                border: 1px solid #AED6F1;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        section_layout.addWidget(section_label)
        section_layout.addWidget(self.section_size_input)

        # Crear el ComboBox (dropdown) para mostrar las descripciones de la leyenda
        self.legend_dropdown = QComboBox()
        self.legend_dropdown.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                border: 1px solid #AED6F1;
                border-radius: 6px;
                padding: 5px;
            }
        """)
        
        # Añadir el ComboBox al layout encima del botón de agregar tramo
        section_layout.addWidget(self.legend_dropdown)

        # Botones para agregar segmentos y finalizar proceso
        self.add_segment_button = QPushButton("Agregar Tramo")
        self.add_segment_button.clicked.connect(self.add_segment)
        self.add_segment_button.setEnabled(False)  # Deshabilitado hasta que se finalice el tramo
        self.add_segment_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #58D68D; /* Verde brillante */
                border: 2px solid #28B463;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #28B463; /* Verde más oscuro al pasar el cursor */
            }
        """)

        # Añadir todo al layout principal
        layout.addLayout(top_layout)  # Layout superior (Inicio, Fin, Finalizar)
        layout.addWidget(self.current_start_label)  # Visible y estilizado
        layout.addLayout(section_layout)  # Campo de tamaño de segmento
        layout.addWidget(self.add_segment_button)  # Botón para agregar segmentos
        
        self.third_tab.setLayout(layout)





    def finalize_limits(self):
        try:
            # Leer valores de inicio y fin del tramo
            inicio_tramo = float(self.inicio_tramo_input.text())
            fin_tramo = float(self.fin_tramo_input.text())

            if inicio_tramo >= fin_tramo:
                QMessageBox.warning(self, "Error", "El inicio del tramo debe ser menor que el fin.")
                return

            # Actualizar límites y bloquear inputs
            self.inicio_tramo = inicio_tramo
            self.fin_tramo = fin_tramo
            self.inicio_tramo_input.setEnabled(False)
            self.fin_tramo_input.setEnabled(False)

            # Inicializar current_start y actualizar la etiqueta
            self.current_start = self.inicio_tramo
            self.current_start_label.setText(f"Inicio actual: {self.current_start:.2f} km")

            # Habilitar botón para agregar segmentos
            self.add_segment_button.setEnabled(True)

            QMessageBox.information(self, "Rango Establecido", "El rango del tramo ha sido establecido correctamente.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor, ingresa valores válidos para los límites.")

    def add_segment(self):
        try:
            # Leer tamaño del segmento
            segment_size = float(self.section_size_input.text())

            if segment_size <= 0:
                QMessageBox.warning(self, "Error", "El tamaño del segmento debe ser mayor a 0.")
                return

            # Calcular fin del tramo actual
            current_end = self.current_start + segment_size

            # Verificar que no exceda el fin del tramo
            if current_end > self.fin_tramo:
                QMessageBox.warning(self, "Error", "El tramo excede el rango total.")
                return

            # Agregar tramo a la lista
            self.tramos.append((self.current_start, current_end))

            # Actualizar current_start y etiqueta
            self.current_start = current_end
            self.current_start_label.setText(f"Inicio actual: {self.current_start:.2f} km")

            # Habilitar botón de finalizar proceso si hay al menos un tramo
            # self.finish_process_button.setEnabled(True)

            # Mostrar mensaje de confirmación
            QMessageBox.information(
                self,
                "Tramo Agregado",
                f"Tramo agregado: {self.tramos[-1][0]:.2f} km - {self.tramos[-1][1]:.2f} km"
            )

            # Deshabilitar botón si se alcanza el fin del tramo
            if self.current_start >= self.fin_tramo:
                QMessageBox.information(self, "Proceso Finalizado", "Se han completado todos los tramos.")
                self.add_segment_button.setEnabled(False)
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor, ingresa un tamaño válido para el segmento.")

    def finish_process(self):
        if self.tramos:
            print("Tramos finalizados:", self.tramos)
            QMessageBox.information(self, "Proceso Finalizado", "Los tramos han sido procesados correctamente.")
        else:
            QMessageBox.warning(self, "Error", "No se han definido tramos.")
        
    # FUNCIONES PARA PANEL DE NAVEGACION ****************************************************
    def go_to_previous_tab(self):
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.setCurrentIndex(current_index - 1)
        self.update_navigation_buttons()

    def go_to_next_tab(self):
        current_index = self.tab_widget.currentIndex()
        self.tab_widget.setCurrentIndex(current_index + 1)    

        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        current_index = self.tab_widget.currentIndex()
        total_tabs = self.tab_widget.count()

        self.previous_button.setEnabled(current_index > 0)
        self.next_button.setEnabled(current_index < total_tabs - 1)


def LoadKmlDialog():
    qfd = QFileDialog()
    filename = QFileDialog.getOpenFileName(qfd, 'Cargar KML', "./", "kml(*.kml)")[0]
    layers = fiona.listlayers(filename)
    return filename, layers
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(Path(__file__).parent / "resources" / "icon.ico")))
    filename, layers = LoadKmlDialog()
    main_window = MainWindow(layers)
    main_window.show()
    sys.exit(app.exec_())