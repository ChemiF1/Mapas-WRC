import geopandas as gpd
import fiona
import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Para incrustar gráficos en Tkinter
import geopandas as gpd
import fiona
import matplotlib.pyplot as plt
import folium
from IPython.display import IFrame
from IPython.display import display
from shapely.geometry import LineString
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from ipywidgets import Dropdown
from ipywidgets import interact
import numpy as np
import time
import matplotlib.pyplot as plt
from tkinter import colorchooser

fiona.drvsupport.supported_drivers['kml'] = 'rw' # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default
# Ruta al archivo KML
filename = "FORUM8 Rally Japan 2024.kml"
layers = fiona.listlayers(filename)

# Función para seleccionar el layer
def seleccionar_layer():
    global selected_layer
    # Crear la ventana
    root = tk.Tk()
    root.title("Seleccionar Layer")

    # Variable para el layer seleccionado
    layer_var = tk.StringVar()

    # Desplegable para seleccionar el layer
    layer_selector = ttk.Combobox(root, values=layers, textvariable=layer_var)
    layer_selector.pack(padx=10, pady=10)

    # Función para proceder con la selección del layer y abrir la ventana de subetapas
    def continuar_seleccion():
        global selected_layer
        selected_layer = layer_var.get()
        root.destroy()  # Cerrar la ventana actual
        seleccionar_subetapa(selected_layer)  # Llamar a la siguiente ventana

    # Botón para continuar
    boton_continuar = tk.Button(root, text="Continuar", command=continuar_seleccion)
    boton_continuar.pack(pady=10)

    # Ejecutar la ventana
    root.mainloop()

# Función para seleccionar la subetapa del layer elegido
def seleccionar_subetapa(selected_layer):
    # Cargar el archivo KML y obtener el layer
    gdf = gpd.read_file(filename, driver="KML", layer=selected_layer)

    # Obtener las subetapas disponibles (asumimos que están en el campo 'Name')
    subetapas = gdf['Name'].unique()

    # Crear la ventana para seleccionar la subetapa
    root = tk.Tk()
    root.title(f"Seleccionar Subetapa de {selected_layer}")

    # Variable para la subetapa seleccionada
    subetapa_var = tk.StringVar()

    # Desplegable para seleccionar la subetapa
    subetapa_selector = ttk.Combobox(root, values=subetapas, textvariable=subetapa_var)
    subetapa_selector.pack(padx=10, pady=10)

    # Función para proceder con la selección de subetapa
    def continuar_seleccion_subetapa():
        selected_subetapa = subetapa_var.get()
        root.destroy()  # Cerrar la ventana actual
        crear_leyenda(selected_layer, selected_subetapa)  # Llamar a la ventana para crear leyenda

    # Botón para continuar
    boton_continuar = tk.Button(root, text="Continuar", command=continuar_seleccion_subetapa)
    boton_continuar.pack(pady=10)

    # Ejecutar la ventana
    root.mainloop()

# Variables globales para almacenar los colores y significados
colors = []
significados = []
import tkinter as tk
from tkinter import simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Variables globales para almacenar los colores y significados
colors = []
significados = []

# Variables globales para almacenar los colores y significados
colors = []
significados = []

# Función para crear la leyenda
def crear_leyenda(layer, subetapa):
    # Crear la ventana de creación de leyenda
    root = tk.Tk()
    root.title("Crear Leyenda")

    # Crear la figura y el eje solo una vez
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis('off')  # Ocultar los ejes

    # Incrustar el gráfico en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack()

    # Función para agregar color y significado
    def agregar_color_significado():
        color = color_entry.get()  # Obtener el color seleccionado
        significado = significado_entry.get()  # Obtener el significado ingresado

        if color and significado:  # Solo agregar si ambos son válidos
            colors.append(color)
            significados.append(significado)
            graficar_leyenda()  # Actualizar la leyenda con los nuevos datos
            # Limpiar los campos para la siguiente entrada
            color_entry.delete(0, tk.END)
            significado_entry.delete(0, tk.END)

    # Función para graficar la leyenda
    def graficar_leyenda():
        # Limpiar los ejes antes de graficar nuevamente
        ax.clear()
        ax.axis('off')  # Asegurarse de que los ejes estén ocultos

        # Dibujar cada color y su significado
        for i, (color, significado) in enumerate(zip(colors, significados)):
            ax.add_patch(plt.Rectangle((0, i), 2, 1, color=color))  # Rectángulo con el color
            ax.text(2.1, i + 0.45, significado, va='center', fontsize=12)

        # Ajustar los límites del gráfico
        ax.set_xlim(0, 3)
        ax.set_ylim(0, len(colors))

        # Actualizar la imagen en el canvas
        canvas.draw()

    # Función para abrir el color chooser y asignar el color seleccionado al campo de entrada
    def elegir_color():
        color = colorchooser.askcolor()[1]  # Obtiene el color en formato hexadecimal
        if color:  # Si se seleccionó un color
            color_entry.delete(0, tk.END)  # Limpiar la entrada de color
            color_entry.insert(0, color)  # Insertar el color seleccionado en la entrada

    # Crear los campos para color y significado
    color_label = tk.Label(root, text="Ingresa el color (o elige con el selector):")
    color_label.pack(pady=5)

    color_entry = tk.Entry(root)
    color_entry.pack(pady=5)

    # Botón para abrir el color chooser
    boton_color = tk.Button(root, text="Seleccionar Color", command=elegir_color)
    boton_color.pack(pady=5)

    significado_label = tk.Label(root, text="Ingresa el significado:")
    significado_label.pack(pady=5)

    significado_entry = tk.Entry(root)
    significado_entry.pack(pady=5)

    # Botón para agregar color y significado
    boton_agregar = tk.Button(root, text="Agregar Color y Significado", command=agregar_color_significado)
    boton_agregar.pack(pady=10)

    # Botón para ir al siguiente paso
    def siguiente_paso():
        print("Avanzar al siguiente paso")  # Aquí puedes definir lo que debe hacer el siguiente paso

    boton_siguiente = tk.Button(root, text="Siguiente Paso", command=siguiente_paso)
    boton_siguiente.pack(pady=10)

    # Asegurarse de que la ventana de agregar color/significado esté al frente
    root.lift()

    # Ejecutar la ventana
    root.mainloop()

# Iniciar la selección de layer
seleccionar_layer()
