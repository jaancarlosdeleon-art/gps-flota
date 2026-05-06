import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import os

# =====================================================
# ARCHIVOS
# =====================================================

ARCHIVO_DATA = r"C:\GPS\data.csv"
ARCHIVO_CONFIG = r"C:\GPS\config_mantenimiento.csv"
ARCHIVO_HISTORIAL = r"C:\GPS\historial_mantenimiento.csv"

# =====================================================
# CREAR CONFIG SI NO EXISTE
# =====================================================

if not os.path.exists(ARCHIVO_CONFIG):

    df_config = pd.DataFrame([
        ["F01",5000,"15W40"],
        ["F02",6000,"15W40"],
        ["F03",8000,"15W40"],
        ["F04",8000,"15W40"],
        ["F05",5000,"15W40"],
        ["F06",6000,"15W40"],
        ["F07",6000,"15W40"],
        ["F08",6000,"15W40"],
        ["F09",6000,"15W40"],
        ["F10",8000,"15W40"],
        ["F11",6000,"15W40"],
        ["F12",6000,"15W40"],
        ["F13",5000,"15W40"],
        ["F14",8000,"15W40"],
        ["F16",8000,"15W40"],
        ["F18",8000,"15W40"]
    ], columns=["ficha","limite","aceite"])

    df_config.to_csv(
        ARCHIVO_CONFIG,
        index=False,
        sep=";"
    )

# =====================================================
# CARGAR DATA
# =====================================================

def cargar_data():

    df = pd.read_csv(
        ARCHIVO_DATA,
        sep=";"
    )

    df.columns = [
        "fecha",
        "vehiculo",
        "km"
    ]

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    df["vehiculo"] = (
        df["vehiculo"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace("-", "", regex=False)
    )

    df["km"] = pd.to_numeric(
        df["km"],
        errors="coerce"
    ).fillna(0)

    return df

# =====================================================
# CONFIG
# =====================================================

def cargar_config():

    return pd.read_csv(
        ARCHIVO_CONFIG,
        sep=";"
    )

def guardar_config(df):

    df.to_csv(
        ARCHIVO_CONFIG,
        index=False,
        sep=";"
    )

# =====================================================
# HISTORIAL
# =====================================================

def cargar_historial():

    if not os.path.exists(ARCHIVO_HISTORIAL):

        return pd.DataFrame(
            columns=[
                "vehiculo",
                "fecha",
                "km",
                "aceite"
            ]
        )

    df = pd.read_csv(
        ARCHIVO_HISTORIAL,
        sep=";"
    )

    if not df.empty:

        df["fecha"] = pd.to_datetime(
            df["fecha"],
            format="mixed",
            errors="coerce"
        )

        df["vehiculo"] = (
            df["vehiculo"]
            .astype(str)
            .str.upper()
            .str.strip()
            .str.replace("-", "", regex=False)
        )

    return df

# =====================================================
# CALCULAR
# =====================================================

def calcular():

    box.delete("1.0", tk.END)

    df = cargar_data()
    config = cargar_config()
    historial = cargar_historial()

    lista = sorted(df["vehiculo"].unique())

    combo["values"] = lista
    combo_config["values"] = lista

    alertas = []

    for vehiculo in lista:

        ficha = vehiculo.split()[0]

        conf = config[
            config["ficha"] == ficha
        ]

        if conf.empty:

            limite = 8000
            aceite = "NO DEFINIDO"

        else:

            limite = float(
                conf["limite"].iloc[0]
            )

            aceite = conf["aceite"].iloc[0]

        df_v = df[
            df["vehiculo"] == vehiculo
        ].copy()

        fecha_base = df_v["fecha"].min()

        hist_v = historial[
            historial["vehiculo"] == vehiculo
        ]

        if not hist_v.empty:

            ultima_fecha = pd.to_datetime(
                hist_v["fecha"]
            ).max()

            fecha_base = ultima_fecha

            df_v = df_v[
                df_v["fecha"] >= ultima_fecha
            ]

        km_total = df_v["km"].sum()

        # =====================================================
        # VALIDAR FECHA
        # =====================================================

        if pd.isna(fecha_base):

            fecha_texto = "SIN FECHA"

            fecha_limite = datetime.now()

            fecha_limite_texto = "N/A"

            dias_restantes = 999

        else:

            fecha_limite = (
                fecha_base +
                timedelta(days=120)
            )

            dias_restantes = (
                fecha_limite - datetime.now()
            ).days

            fecha_texto = fecha_base.strftime(
                "%d/%m/%Y"
            )

            fecha_limite_texto = fecha_limite.strftime(
                "%d/%m/%Y"
            )

        # =====================================================
        # ESTADO
        # =====================================================

        estado = "OK"
        color = "green"

        if (
            km_total >= limite
            or dias_restantes <= 0
        ):

            estado = "CAMBIO YA"
            color = "red"

            alertas.append(
                f"{vehiculo} necesita mantenimiento"
            )

        elif (
            km_total >= limite - 1000
            or dias_restantes <= 30
        ):

            estado = "PRÓXIMO"
            color = "orange"

        # =====================================================
        # TEXTO
        # =====================================================

        texto = (
            f"{vehiculo} → "
            f"{km_total:.2f}/{int(limite)} "
            f"→ {estado}\n"
        )

        texto += (
            f"Aceite: {aceite}\n"
        )

        texto += (
            f"Último mantenimiento: "
            f"{fecha_texto}\n"
        )

        texto += (
            f"Próximo límite: "
            f"{fecha_limite_texto} "
            f"({dias_restantes} días)\n\n"
        )

        box.insert(
            tk.END,
            texto,
            color
        )

    # =====================================================
    # COLORES
    # =====================================================

    box.tag_config(
        "green",
        foreground="#00E676"
    )

    box.tag_config(
        "orange",
        foreground="#FFD740"
    )

    box.tag_config(
        "red",
        foreground="#FF5252"
    )

    # =====================================================
    # ALERTAS
    # =====================================================

    if len(alertas) > 0:

        messagebox.showwarning(
            "ALERTA",
            "\n".join(alertas)
        )

# =====================================================
# GUARDAR MANTENIMIENTO
# =====================================================

def marcar_mantenimiento():

    vehiculo = combo.get()

    vehiculo = (
        vehiculo
        .upper()
        .strip()
        .replace("-", "")
    )

    if vehiculo == "":

        messagebox.showerror(
            "Error",
            "Selecciona un vehículo"
        )

        return

    fecha = calendario.get_date()

    df = cargar_data()

    df_v = df[
        df["vehiculo"] == vehiculo
    ]

    km_total = df_v["km"].sum()

    config = cargar_config()

    ficha = vehiculo.split()[0]

    conf = config[
        config["ficha"] == ficha
    ]

    aceite = conf["aceite"].iloc[0]

    historial = cargar_historial()

    nuevo = pd.DataFrame([{
        "vehiculo": vehiculo,
        "fecha": fecha.strftime("%Y-%m-%d"),
        "km": km_total,
        "aceite": aceite
    }])

    historial = pd.concat([
        historial,
        nuevo
    ])

    historial.to_csv(
        ARCHIVO_HISTORIAL,
        index=False,
        sep=";"
    )

    messagebox.showinfo(
        "OK",
        "Mantenimiento guardado"
    )

    calcular()

# =====================================================
# HISTORIAL
# =====================================================

def ver_historial():

    historial_box.delete(
        "1.0",
        tk.END
    )

    historial = cargar_historial()

    if historial.empty:

        historial_box.insert(
            tk.END,
            "SIN HISTORIAL"
        )

        return

    historial_box.insert(
        tk.END,
        historial.to_string(index=False)
    )

# =====================================================
# GUARDAR CONFIG
# =====================================================

def guardar_configuracion():

    vehiculo = combo_config.get()

    if vehiculo == "":

        messagebox.showerror(
            "Error",
            "Selecciona vehículo"
        )

        return

    ficha = vehiculo.split()[0]

    nuevo_limite = limite_entry.get()
    nuevo_aceite = aceite_entry.get()

    config = cargar_config()

    idx = config[
        config["ficha"] == ficha
    ].index

    if len(idx) == 0:

        nuevo = pd.DataFrame([{
            "ficha": ficha,
            "limite": nuevo_limite,
            "aceite": nuevo_aceite
        }])

        config = pd.concat([
            config,
            nuevo
        ])

    else:

        config.loc[
            idx,
            "limite"
        ] = float(nuevo_limite)

        config.loc[
            idx,
            "aceite"
        ] = nuevo_aceite

    guardar_config(config)

    messagebox.showinfo(
        "OK",
        "Configuración guardada"
    )

    calcular()

# =====================================================
# EXPORTAR
# =====================================================

def exportar():

    texto = box.get(
        "1.0",
        tk.END
    )

    ruta = r"C:\GPS\reporte_mantenimiento.txt"

    with open(
        ruta,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(texto)

    messagebox.showinfo(
        "OK",
        f"Reporte exportado:\n{ruta}"
    )

# =====================================================
# INTERFAZ
# =====================================================

root = tk.Tk()

root.title(
    "Sistema Profesional de Mantenimiento"
)

root.geometry("1200x820")

root.configure(
    bg="#0D1117"
)

titulo = tk.Label(
    root,
    text="🚛 PANEL PROFESIONAL DE MANTENIMIENTO",
    font=("Segoe UI",20,"bold"),
    bg="#0D1117",
    fg="#00E5FF"
)

titulo.pack(
    pady=10
)

notebook = ttk.Notebook(root)

notebook.pack(
    fill="both",
    expand=True
)

# =====================================================
# TAB DASHBOARD
# =====================================================

tab1 = tk.Frame(
    notebook,
    bg="#0D1117"
)

notebook.add(
    tab1,
    text="Dashboard"
)

top_frame = tk.Frame(
    tab1,
    bg="#0D1117"
)

top_frame.pack(
    pady=10
)

combo = ttk.Combobox(
    top_frame,
    width=35
)

combo.grid(
    row=0,
    column=0,
    padx=10
)

calendario = DateEntry(
    top_frame,
    date_pattern="dd/mm/yyyy"
)

calendario.grid(
    row=0,
    column=1,
    padx=10
)

btn_mantenimiento = tk.Button(
    top_frame,
    text="Guardar mantenimiento",
    bg="#00C853",
    fg="white",
    font=("Segoe UI",10,"bold"),
    command=marcar_mantenimiento
)

btn_mantenimiento.grid(
    row=0,
    column=2,
    padx=10
)

btn_actualizar = tk.Button(
    top_frame,
    text="Actualizar",
    bg="#2962FF",
    fg="white",
    font=("Segoe UI",10,"bold"),
    command=calcular
)

btn_actualizar.grid(
    row=0,
    column=3,
    padx=10
)

btn_exportar = tk.Button(
    top_frame,
    text="Exportar",
    bg="#FF6D00",
    fg="white",
    font=("Segoe UI",10,"bold"),
    command=exportar
)

btn_exportar.grid(
    row=0,
    column=4,
    padx=10
)

box = tk.Text(
    tab1,
    bg="#161B22",
    fg="white",
    font=("Consolas",11)
)

box.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

# =====================================================
# TAB CONFIG
# =====================================================

tab2 = tk.Frame(
    notebook,
    bg="#0D1117"
)

notebook.add(
    tab2,
    text="Configuración"
)

config_frame = tk.Frame(
    tab2,
    bg="#0D1117"
)

config_frame.pack(
    pady=30
)

tk.Label(
    config_frame,
    text="Vehículo",
    bg="#0D1117",
    fg="white"
).grid(row=0,column=0,pady=10)

combo_config = ttk.Combobox(
    config_frame,
    width=35
)

combo_config.grid(row=0,column=1)

tk.Label(
    config_frame,
    text="Límite KM",
    bg="#0D1117",
    fg="white"
).grid(row=1,column=0,pady=10)

limite_entry = tk.Entry(
    config_frame,
    width=20
)

limite_entry.grid(row=1,column=1)

tk.Label(
    config_frame,
    text="Aceite",
    bg="#0D1117",
    fg="white"
).grid(row=2,column=0,pady=10)

aceite_entry = tk.Entry(
    config_frame,
    width=20
)

aceite_entry.grid(row=2,column=1)

btn_guardar_config = tk.Button(
    config_frame,
    text="Guardar configuración",
    bg="#AA00FF",
    fg="white",
    font=("Segoe UI",10,"bold"),
    command=guardar_configuracion
)

btn_guardar_config.grid(
    row=3,
    column=1,
    pady=20
)

# =====================================================
# TAB HISTORIAL
# =====================================================

tab3 = tk.Frame(
    notebook,
    bg="#0D1117"
)

notebook.add(
    tab3,
    text="Historial"
)

btn_historial = tk.Button(
    tab3,
    text="Actualizar historial",
    bg="#FF1744",
    fg="white",
    font=("Segoe UI",10,"bold"),
    command=ver_historial
)

btn_historial.pack(
    pady=10
)

historial_box = tk.Text(
    tab3,
    bg="#161B22",
    fg="white",
    font=("Consolas",10)
)

historial_box.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

# =====================================================
# INICIO
# =====================================================

calcular()

root.mainloop()