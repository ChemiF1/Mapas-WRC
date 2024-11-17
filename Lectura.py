import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from shapely.geometry import LineString
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

fiona.drvsupport.supported_drivers['kml'] = 'rw' # enable KML support which is disabled by default
fiona.drvsupport.supported_drivers['KML'] = 'rw' # enable KML support which is disabled by default


# Ruta al archivo KML
filename = "FORUM8 Rally Japan 2024.kml"
layers = fiona.listlayers(filename)


# Función para cargar el layer seleccionado y la subetapa
def seleccionar_layer_y_subetapa():
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Seleccionar Layer y Subetapa")
    
    # Zona para dibujar el mapa (vacía al principio)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')  # Inicialmente no mostrar nada

    # Incrustar el gráfico en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(padx=10, pady=10)

    # Variable para el layer y la subetapa seleccionados
    layer_var = tk.StringVar()
    subetapa_var = tk.StringVar()

    # Desplegable para seleccionar el layer
    layer_selector_label = tk.Label(root, text="Seleccionar Layer")
    layer_selector_label.pack(pady=10)

    layer_selector = ttk.Combobox(root, values=layers, textvariable=layer_var)
    layer_selector.pack(padx=10, pady=5)

    # Función para cargar las subetapas del layer seleccionado
    def cargar_subetapas(event):
        selected_layer = layer_var.get()
        # Cargar el archivo KML y obtener el layer
        gdf = gpd.read_file(filename, driver="KML", layer=selected_layer)
        subetapas = gdf['Name'].unique()
        
        # Crear el desplegable para seleccionar subetapa
        subetapa_selector = ttk.Combobox(root, values=subetapas, textvariable=subetapa_var)
        subetapa_selector.pack(pady=5)
    
    # Vinculamos el evento de selección del layer para cargar las subetapas
    layer_selector.bind("<<ComboboxSelected>>", cargar_subetapas)

    # Función para visualizar el mapa
    def visualizar_mapa():
        selected_layer = layer_var.get()
        selected_subetapa = subetapa_var.get()

        if selected_layer and selected_subetapa:
            # Cargar el archivo KML y obtener el layer
            gdf = gpd.read_file(filename, driver="KML", layer=selected_layer)

            # Filtrar por la subetapa seleccionada
            gdf_subetapa = gdf[gdf['Name'] == selected_subetapa]

            # Transformar a un CRS proyectado (por ejemplo, UTM o Web Mercator EPSG:3857)
            gdf_projected = gdf_subetapa.to_crs(epsg=3099)

            # Calcular la longitud de cada tramo en metros
            gdf_projected['length_m'] = gdf_projected.length

            # Convertir la longitud a kilómetros
            gdf_projected['length_km'] = gdf_projected['length_m'] / 1000

            # Obtener la longitud total
            longitud_total = gdf_projected['length_km'].sum()

            # Crear la figura y el eje con matplotlib
            fig, ax = plt.subplots(figsize=(10, 6))

            # Plotea las geometrías usando geopandas
            gdf_projected.plot(ax=ax, color='blue', edgecolor='black')

            # Personalizar el gráfico
            ax.set_title(f"{selected_subetapa} \n Distancia total {longitud_total:.2f} kms", fontsize=14)
            ax.set_xlabel("Longitud (m)", fontsize=10)
            ax.set_ylabel("Latitud (m)", fontsize=10)
            ax.axis("off")

            # Mostrar el mapa dentro de Tkinter
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        else:
            messagebox.showwarning("Advertencia", "Debe seleccionar un layer y una subetapa.")

    # Función para continuar con la creación de la leyenda
    def continuar_leyenda():
        selected_layer = layer_var.get()
        selected_subetapa = subetapa_var.get()
        if selected_layer and selected_subetapa:
            crear_leyenda(selected_layer, selected_subetapa)
        else:
            messagebox.showwarning("Advertencia", "Debe seleccionar un layer y una subetapa.")

    # Botón para visualizar el mapa
    boton_visualizar = tk.Button(root, text="Visualización", command=visualizar_mapa)
    boton_visualizar.pack(pady=10)

    # Botón para continuar con la leyenda
    boton_continuar = tk.Button(root, text="Continuar", command=continuar_leyenda)
    boton_continuar.pack(pady=10)

    # Ejecutar la ventana principal
    root.mainloop()

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

    # Variables globales para almacenar los colores y significados
    colors = []
    significados = []

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

    # Crear los campos para color y significado
    color_label = tk.Label(root, text="Ingresa el color (en formato nombre o hexadecimal):")
    color_label.pack(pady=5)
    color_entry = tk.Entry(root)
    color_entry.pack(pady=5)

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

    # Ejecutar la ventana de leyenda
    root.mainloop()

# Llamamos a la función principal para iniciar el proceso
seleccionar_layer_y_subetapa()
