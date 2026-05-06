from flask import Flask, render_template
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)

ARQUIVO = "data.csv"

LIMITES = {
    "F02": 6000,
    "F03": 8000,
    "F04": 8000,
    "F05": 5000,
    "F06": 6000,
    "F07": 6000,
    "F08": 6000,
    "F09": 6000,
    "F10": 8000,
    "F11": 6000,
    "F12": 6000,
    "F13": 5000,
    "F14": 8000,
    "F16": 8000,
    "F18": 8000
}

@app.route("/")

def home():

    if not os.path.exists(ARQUIVO):
        return "No existe data.csv"

    df = pd.read_csv(
        ARQUIVO,
        sep=";"
    )

    df.columns = ["fecha", "vehiculo", "km"]

    df["km"] = pd.to_numeric(
        df["km"],
        errors="coerce"
    ).fillna(0)

    resultado = []

    agrupado = df.groupby("vehiculo")

    for vehiculo, grupo in agrupado:

        km_total = grupo["km"].sum()

        fila = grupo.iloc[-1]

        fecha = pd.to_datetime(
            fila["fecha"],
            dayfirst=True,
            errors="coerce"
        )

        ficha = vehiculo.split()[0]

        limite = LIMITES.get(ficha, 6000)

        dias = 999
        fecha_limite = "N/A"

        if pd.notna(fecha):

            fecha_limite_dt = fecha + timedelta(days=120)

            dias = (fecha_limite_dt - datetime.now()).days

            fecha_limite = fecha_limite_dt.strftime("%d/%m/%Y")

        estado = "OK"
        color = "#00ff88"

        if km_total >= limite or dias <= 0:
            estado = "CAMBIO YA"
            color = "#ff3b30"

        elif km_total >= (limite - 1000) or dias <= 30:
            estado = "PRÓXIMO"
            color = "#ffcc00"

        resultado.append({
            "vehiculo": vehiculo,
            "km": round(km_total, 2),
            "limite": limite,
            "estado": estado,
            "color": color,
            "fecha": fecha.strftime("%d/%m/%Y") if pd.notna(fecha) else "SIN FECHA",
            "limite_fecha": fecha_limite,
            "dias": dias
        })

    resultado = sorted(
        resultado,
        key=lambda x: (
            x["estado"] != "CAMBIO YA",
            x["estado"] != "PRÓXIMO"
        )
    )

    return render_template(
        "dashboard.html",
        camiones=resultado,
        fecha=datetime.now().strftime("%d/%m/%Y %H:%M")
    )

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )