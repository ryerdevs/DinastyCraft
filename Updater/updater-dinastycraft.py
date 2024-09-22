import os
import urllib.request
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import concurrent.futures
import configparser
from PIL import Image, ImageTk
import io
import shutil
import time
import ctypes

class ModpackUpdater:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.directorio = self.config['DEFAULT'].get('directorio', '')
        self.root = tk.Tk()
        self.root.geometry("1000x600")
        self.root.title("DinastyCraft Updater")
        self.root.resizable(False, False)
        # Cargar la imagen de fondo desde GitHub
        url = "https://raw.githubusercontent.com/ryerdevs/DinastyCraft/main/modpack-versions/Images/background.jpeg"
        with urllib.request.urlopen(url) as u:
            raw_data = u.read()
        im = Image.open(io.BytesIO(raw_data))
        self.background_image = ImageTk.PhotoImage(im)
        self.background_label = tk.Label(self.root, image=self.background_image)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.style = ttk.Style()
        self.style.configure("Custom.Horizontal.TProgressbar", thickness=10, troughcolor="black", background="black")
        self.progress_general = ttk.Progressbar(self.root, length=400, mode='determinate', style="Custom.Horizontal.TProgressbar")
        self.label_archivo = tk.Label(self.root, text="", bg="#0e912f", fg="white")
        self.setup_ui()
        self.errores = []
        self.contador = 0
        self.total_archivos = 0
        self.nombre_carpeta_label = tk.Label(self.root, text="", bg="#0e912f", fg="white")
        self.nombre_carpeta_label.place(relx=0.1, rely=0.9)
        # Obtener la ruta completa del archivo "icon.ico"
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
        # Cambiar el icono de la ventana
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        self.root.iconbitmap(icon_path)

        # Leer la configuración del archivo config.ini
        if 'DEFAULT' in self.config:
            self.directorio = self.config['DEFAULT'].get('directorio', '')
            self.nombre_carpeta_label.config(text=f"Carpeta seleccionada: {os.path.basename(self.directorio)}")

    def setup_ui(self):
        self.seleccionar_carpeta_btn = tk.Button(self.root, text="Elegir Carpeta", command=self.seleccionar_carpeta, bg="#0e912f", fg="#ffffff", font=("Minecrafter", 16), height=2, width=15)
        self.actualizar_btn = tk.Button(self.root, text="Actualizar", command=lambda: self.actualizar_modpacks(self.directorio), bg="#0e912f", fg="#ffffff", font=("Minecrafter", 16), height=2, width=15)
        self.seleccionar_carpeta_btn.place(relx=0.1, rely=0.8)
        self.actualizar_btn.place(relx=0.6, rely=0.8)
        self.progress_general.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.label_archivo.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    def seleccionar_carpeta(self):
        directorio = filedialog.askdirectory()
        if directorio:
            self.directorio = directorio  # Guardar la selección en la variable self.directorio
            self.config['DEFAULT']['directorio'] = directorio
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)
            self.nombre_carpeta_label.config(text=f"Carpeta seleccionada: {os.path.basename(directorio)}")

    def actualizar_modpacks(self, directorio):
        url = "https://raw.githubusercontent.com/ryerdevs/DinastyCraft/main/modpack-versions/lista_mods.json"
        with urllib.request.urlopen(url) as u:
            data = json.loads(u.read().decode())
        lista_archivos_online = set(data["mods"])
        directorio_mods = os.path.join(directorio, "mods")
        if not os.path.exists(directorio_mods):
            os.makedirs(directorio_mods)
        archivos_locales = set(os.listdir(directorio_mods))
        archivos_a_descargar = lista_archivos_online - archivos_locales
        archivos_a_eliminar = archivos_locales - lista_archivos_online
        self.progress_general['maximum'] = len(archivos_a_eliminar) + len(archivos_a_descargar)
        self.progress_general['value'] = 0
        self.total_archivos = len(archivos_a_eliminar) + len(archivos_a_descargar)
        self.contador = 0
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for archivo in archivos_a_descargar:
                try:
                    self.label_archivo.config(text=f"Descargando: {archivo}")
                    time.sleep(0.1)  # Delay para evitar lag en la interfaz
                    executor.submit(self.descargar_archivo, archivo, directorio_mods)
                    self.contador += 1
                    self.progress_general['value'] = self.contador
                    self.root.update()
                except Exception as e:
                    self.errores.append(str(e))
            for archivo in archivos_a_eliminar:
                try:
                    self.label_archivo.config(text=f"Eliminando: {archivo}")
                    time.sleep(0.1)  # Delay para evitar lag en la interfaz
                    executor.submit(self.eliminar_archivo, archivo, directorio_mods)
                    self.contador += 1
                    self.progress_general['value'] = self.contador
                    self.root.update()
                except Exception as e:
                    self.errores.append(str(e))
        if len(self.errores) > 0:
            messagebox.showinfo("Errores encontrados", "\n".join(self.errores))
        else:
            self.progress_general['value'] = self.total_archivos
            self.label_archivo.config(text="Actualizado con éxito")
            self.root.update()
            messagebox.showinfo("Actualización completada", "El modpack se ha actualizado correctamente.")

    def descargar_archivo(self, archivo, directorio_mods):
        url = f"https://raw.githubusercontent.com/ryerdevs/DinastyCraft/main/modpack-versions/mods/{archivo}"
        destino = os.path.join(directorio_mods, archivo)
        with urllib.request.urlopen(url) as u, open(destino, 'wb') as f:
            shutil.copyfileobj(u, f)

    def eliminar_archivo(self, archivo, directorio_mods):
        os.remove(os.path.join(directorio_mods, archivo))

if __name__ == "__main__":
    app = ModpackUpdater()
    app.root.mainloop()