import os
import urllib.request
import json
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox

class ModpackUpdater:
    def __init__(self):
        self.setup_ui()
        self.errores = []
        self.contador = 0
        self.total_archivos = 0
    
    def setup_ui(self):
        self.root = tk.Tk()  
        self.root.geometry("500x300")
        self.root.configure(bg="#36393f")
        self.root.title("Actualizador de Modpack DinastyCraft v0.3 por Ryer")
        
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("TProgressbar", thickness=20, background='#7289da', troughcolor ='#36393f', bordercolor='#36393f')
        
        self.seleccionar_carpeta_btn = tk.Button(self.root, text="Seleccionar carpeta", command=self.seleccionar_carpeta, bg="#7289da", fg="white", font=("Helvetica", 16), height=2, width=30)
        self.progress_general = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.status_label = tk.Label(self.root, text="", bg="#36393f", fg="white")
        self.archivo_label = tk.Label(self.root, text="", bg="#36393f", fg="white")
        
        for widget in [self.seleccionar_carpeta_btn, self.progress_general, self.status_label, self.archivo_label]:
            widget.pack(pady=10)
    
    def seleccionar_carpeta(self):
        directorio = filedialog.askdirectory()
        if directorio:
            self.seleccionar_carpeta_btn.config(text="Actualizar", command=lambda: self.actualizar_modpacks(directorio))
    
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
        
        for archivo in archivos_a_descargar:
            self.archivo_label.config(text=f"Descargando: {archivo}")
            self.descargar_archivo(archivo, directorio_mods)
            self.contador += 1
            self.progress_general['value'] = self.contador
            self.root.update()
        
        for archivo in archivos_a_eliminar:
            self.archivo_label.config(text=f"Eliminando: {archivo}")
            self.eliminar_archivo(archivo, directorio_mods)
            self.contador += 1
            self.progress_general['value'] = self.contador
            self.root.update()
        
        self.status_label.config(text="¡Modpack actualizado correctamente!")
        self.archivo_label.config(text="")
        
        messagebox.showinfo("Actualización completada", "El modpack se ha actualizado correctamente.")
    
    def descargar_archivo(self, archivo, directorio_mods):
        url = f"https://raw.githubusercontent.com/ryerdevs/DinastyCraft/main/modpack-versions/mods/{archivo}"
        destino = os.path.join(directorio_mods, archivo)
        
        with urllib.request.urlopen(url) as u:
            data = u.read()
        
        with open(destino, 'wb') as f:
            f.write(data)
    
    def eliminar_archivo(self, archivo, directorio_mods):
        os.remove(os.path.join(directorio_mods, archivo))

if __name__ == "__main__":
    app = ModpackUpdater()
    app.root.mainloop()