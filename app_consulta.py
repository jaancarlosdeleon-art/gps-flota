import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import os
import pywhatkit

ARCHIVO_DATA = r"C:\GPS\data.csv"
ARCHIVO_HISTORIAL = r"C:\GPS\historial_mantenimiento.csv"
ARCHIVO_REPORTE = r"C:\GPS\reporte_mantenimiento.csv"

TELEFONO = "+18093994496"

LIMITES = {
    "F01": 5000, "F13": 5000, "F05": 5000,
    "F02": 6000, "F11": 6000, "F12": 6000, "F06": 6000,
    "F07": 6000, "F08": 6000, "F09": 6000,
    "F03": 8000, "F04": 8000, "F10": 8000,
    "F14": 8000, "F18": 8000, "F16": 8000
}

def cargar_data():
    df = pd.read_csv(ARCHIVO_DATA, sep=";")
    df.columns = ["fecha","vehiculo","km"]
    df["fecha"] = pd.to_datetime(df["fecha"], dayfirst=True, errors="coerce")
    df["vehiculo"] = df["vehiculo"].str.upper().str.strip()
    df["km"] = pd.to_numeric(df["km"], errors="coerce").fillna(0)
    return df

def cargar_historial():
    if not os.path.exists(ARCHIVO_HISTORIAL):
        return pd.DataFrame(columns=["vehiculo","fecha","km"])
    df = pd.read_csv(ARCHIVO_HISTORIAL, sep=";")
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["km"] = pd.to_numeric(df["km"], errors="coerce").fillna(0)
    return df

def calcular():
    df = cargar_data()
    hist = cargar_historial()

    lista = sorted(df["vehiculo"].unique())
    combo["values"] = lista

    box.delete("1.0", tk.END)
    alertas = []
    reporte = []

    for vehiculo in lista:

        df_v = df[df["vehiculo"] == vehiculo]
        km_actual = df_v["km"].iloc[-1]

        hist_v = hist[hist["vehiculo"] == vehiculo]

        # -------- KM REAL --------
        if hist_v.empty:
            km_total = km_actual
            fecha_base = df_v["fecha"].iloc[-1]
        else:
            ultimo = hist_v.iloc[-1]
            km_total = km_actual - ultimo["km"]
            fecha_base = ultimo["fecha"]

        codigo = vehiculo.split()[0]
        limite = LIMITES.get(codigo, 8000)

        fecha_limite = fecha_base + timedelta(days=120)
        dias_restantes = (fecha_limite - datetime.now()).days

        estado = "OK"
        color = "green"

        if km_total >= limite or dias_restantes <= 0:
            estado = "CAMBIO YA"
            color = "red"
            alertas.append(f"{vehiculo} requiere mantenimiento")

        elif km_total >= limite - 1000 or dias_restantes <= 30:
            estado = "PRÓXIMO"
            color = "orange"

        if filtro_rojos.get() and estado != "CAMBIO YA":
            continue

        texto = f"{vehiculo} → {int(km_total)}/{limite} → {estado}\n"
        texto += f"   Último: {fecha_base.strftime('%d/%m/%Y')} | Límite: {fecha_limite.strftime('%d/%m/%Y')} ({dias_restantes} días)\n\n"

        box.insert(tk.END, texto, color)

        reporte.append([vehiculo, km_total, limite, estado])

    box.tag_config("green", foreground="#00E676")
    box.tag_config("orange", foreground="#FFD740")
    box.tag_config("red", foreground="#FF1744")

    if alertas:
        messagebox.showwarning("ALERTA", "\n".join(alertas))

        try:
            for a in alertas:
                pywhatkit.sendwhatmsg_instantly(
                    TELEFONO,
                    f"ALERTA: {a}",
                    wait_time=10,
                    tab_close=True
                )
        except:
            pass

    global data_reporte
    data_reporte = reporte

def exportar():
    df = pd.DataFrame(data_reporte, columns=["vehiculo","km","limite","estado"])
    df.to_csv(ARCHIVO_REPORTE, index=False)
    messagebox.showinfo("OK","Reporte exportado")

def marcar():
    vehiculo = combo.get()
    fecha_manual = calendario.get_date()

    df = cargar_data()
    km_actual = df[df["vehiculo"] == vehiculo]["km"].iloc[-1]

    if os.path.exists(ARCHIVO_HISTORIAL):
        df_hist = pd.read_csv(ARCHIVO_HISTORIAL, sep=";")
    else:
        df_hist = pd.DataFrame(columns=["vehiculo","fecha","km"])

    df_hist = pd.concat([df_hist, pd.DataFrame([{
        "vehiculo": vehiculo,
        "fecha": fecha_manual.strftime("%Y-%m-%d"),
        "km": km_actual
    }])], ignore_index=True)

    df_hist.to_csv(ARCHIVO_HISTORIAL, index=False, sep=";")

    messagebox.showinfo("OK","Mantenimiento guardado")
    calcular()

root = tk.Tk()
root.title("Sistema PRO")
root.geometry("900x650")
root.configure(bg="#0D1117")

tk.Label(root, text="🚛 PANEL DE MANTENIMIENTO",
         font=("Segoe UI", 16, "bold"),
         bg="#0D1117", fg="#00E5FF").pack(pady=10)

combo = ttk.Combobox(root, width=40)
combo.pack()

calendario = DateEntry(root, date_pattern="dd/mm/yyyy")
calendario.pack(pady=5)

frame = tk.Frame(root, bg="#0D1117")
frame.pack()

tk.Button(frame, text="Marcar mantenimiento", command=marcar).grid(row=0,column=0,padx=5)
tk.Button(frame, text="Actualizar", command=calcular).grid(row=0,column=1,padx=5)
tk.Button(frame, text="Exportar", command=exportar).grid(row=0,column=2,padx=5)

filtro_rojos = tk.BooleanVar()
tk.Checkbutton(root, text="Solo críticos", variable=filtro_rojos,
               bg="#0D1117", fg="white", command=calcular).pack()

box = tk.Text(root, bg="#161B22", fg="white", height=28)
box.pack(fill="both", expand=True)

data_reporte = []

calcular()
root.mainloop()