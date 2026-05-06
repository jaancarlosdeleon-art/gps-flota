import pandas as pd

ARCHIVO = r"C:\GPS\data.csv"

# -------- LEER CSV (COLUMNAS BUENAS) --------
df_raw = pd.read_csv(ARCHIVO, sep=";", header=None, dtype=str)

df = df_raw[[3,4,5]].copy()
df.columns = ["fecha", "vehiculo", "km"]

# -------- LIMPIEZA --------
df["vehiculo"] = df["vehiculo"].astype(str).str.strip().str.upper()
df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
df["km"] = pd.to_numeric(df["km"], errors="coerce").fillna(0)

df = df.dropna(subset=["fecha", "vehiculo"])

# -------- PROGRAMA --------
while True:
    print("\n==============================")
    print("🚛 CONSULTA DE KILOMETRAJE")
    print("==============================")

    vehiculo = input("Ingrese el camión (ej: F04): ").strip().upper()
    desde = input("Fecha inicio (DD/MM/YYYY): ").strip()
    hasta = input("Fecha fin (DD/MM/YYYY): ").strip()

    try:
        desde = pd.to_datetime(desde, format="%d/%m/%Y")
        hasta = pd.to_datetime(hasta, format="%d/%m/%Y")

        resultado = df[
            (df["vehiculo"].str.startswith(vehiculo)) &
            (df["fecha"] >= desde) &
            (df["fecha"] <= hasta)
        ]

        total = resultado["km"].sum()

        print("\n📊 DETALLE:")
        print(resultado)

        print(f"\n🚛 TOTAL KM: {total:.2f}")

    except:
        print("\n❌ Error en la fecha. Usa formato DD/MM/YYYY")

    repetir = input("\n¿Quieres otra consulta? (s/n): ").lower()
    if repetir != "s":
        break