import os
import time
from datetime import datetime, timedelta
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# ---------------- CONFIG ----------------
USUARIO = "damascodeleon@hotmail.com"
PASSWORD = "Sisnk0192&’Oqiwn##.@28..a"  # ⚠️ cámbiala luego

VEHICULOS = ["F02"]

ARCHIVO = r"C:\GPS\data.csv"

# -------- FECHAS (AYER AUTOMÁTICO) --------
hoy = datetime.now()
ayer = hoy - timedelta(days=1)

fecha_inicio = ayer.strftime("%Y-%m-%d 00:00:00")
fecha_fin = ayer.strftime("%Y-%m-%d 23:59:59")
fecha_guardar = ayer.strftime("%Y-%m-%d")

# -------- DRIVER (USANDO TU CHROMEDRIVER LOCAL) --------
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 20)

driver.get("https://eu.tracksolidpro.com")

# esperar campo usuario REAL
usuario_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Account']")))
usuario_input.click()
usuario_input.clear()
usuario_input.send_keys(USUARIO)

# contraseña
password_input = driver.find_element(By.XPATH, "//input[@placeholder='Password']")
password_input.click()
password_input.clear()
password_input.send_keys(PASSWORD)

# botón login
wait.until(EC.element_to_be_clickable((By.XPATH, "//button"))).click()

time.sleep(5)

# -------- IR A REPORT --------
wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Report')]"))).click()
time.sleep(1)

# -------- CLICK EN SEGUNDA PESTAÑA (Motion Overview) --------
tabs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'el-tabs__item')]")))

# 0 = Device Overview
# 1 = Motion Overview  👈 ESTE NOS INTERESA
tabs[1].click()

time.sleep(2)

# -------- ABRIR DROPDOWN DE FECHA (FORZADO) --------
driver.execute_script("""
document.querySelectorAll('.el-range-editor, .el-date-editor').forEach(el => el.click());
""")

time.sleep(1)

# -------- CLICK EN YESTERDAY (FORZADO) --------
driver.execute_script("""
document.querySelectorAll('span').forEach(el => {
    if (el.innerText && el.innerText.trim() === 'Yesterday') {
        el.click();
    }
});
""")

time.sleep(1)

# -------- ABRIR SELECT DEVICE --------
driver.execute_script("""
document.querySelectorAll('input.el-input__inner').forEach(el => {
    if (el.placeholder && el.placeholder.toLowerCase().includes('select')) {
        el.click();
    }
});
""")

time.sleep(2)

# -------- SELECT ALL --------
wait.until(EC.element_to_be_clickable((
    By.XPATH, "//span[contains(text(),'Select All')]"
))).click()

time.sleep(1)

# -------- CONFIRM --------
wait.until(EC.element_to_be_clickable((
    By.XPATH, "//span[contains(text(),'Confirm')]"
))).click()

time.sleep(2)

# -------- CLICK SEARCH (FORZADO) --------
driver.execute_script("""
document.querySelectorAll('button').forEach(btn => {
    if (btn.innerText.includes('Search')) {
        btn.click();
    }
});
""")

time.sleep(5)

# -------- EXTRAER TABLA --------
rows = driver.find_elements(By.XPATH, "//table//tbody/tr")

resultados = []

for row in rows:
    try:
        cols = row.find_elements(By.TAG_NAME, "td")

        nombre = cols[1].text.strip()
        km = cols[4].text.strip()

        print(nombre, km)

        resultados.append({
            "fecha": fecha_guardar,
            "vehiculo": nombre,
            "km": km
        })

    except:
        continue

# -------- PAGINA 2 --------
try:
    next_btn = driver.find_element(By.XPATH, "//button[contains(@class,'btn-next')]")
    
    if "disabled" not in next_btn.get_attribute("class"):
        next_btn.click()
        time.sleep(3)

        rows = driver.find_elements(By.XPATH, "//table//tbody/tr")

        for row in rows:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")

                nombre = cols[1].text.strip()
                km = cols[4].text.strip().replace(",", "")

                km = float(km) if km else 0

                print(nombre, km)

                resultados.append({
                    "fecha": fecha_guardar,
                    "vehiculo": nombre,
                    "km": km
                })

            except:
                continue

except:
    pass



# -------- GUARDAR DATA SIN DUPLICADOS --------
import pandas as pd
import os

df_nuevo = pd.DataFrame(resultados)

df_nuevo["km"] = pd.to_numeric(df_nuevo["km"], errors="coerce").fillna(0)

# si ya existe el archivo, combinar
if os.path.exists(ARCHIVO):
    df_existente = pd.read_csv(ARCHIVO, sep=";")

    df_total = pd.concat([df_existente, df_nuevo], ignore_index=True)

    # 🔥 eliminar duplicados (CLAVE)
    df_total = df_total.drop_duplicates(subset=["fecha", "vehiculo"], keep="last")

    df_total.to_csv(ARCHIVO, index=False, sep=";")
else:
    df_nuevo.to_csv(ARCHIVO, index=False, sep=";")

print("✅ DATA GUARDADA SIN DUPLICADOS")


# -------- VALIDAR SI SE GUARDÓ TODO --------
ALERTA = r"C:\GPS\alerta.txt"

try:
    df_check = pd.read_csv(ARCHIVO, sep=";")

    # filtrar datos de hoy (lo que acabas de guardar)
    df_hoy = df_check[df_check["fecha"] == fecha_guardar]

    # lista de vehículos únicos esperados (los que salieron hoy)
    vehiculos_hoy = df_hoy["vehiculo"].unique()

    # si no hay datos
    if len(df_hoy) == 0:
        with open(ALERTA, "a", encoding="utf-8") as f:
            f.write(f"⚠️ {fecha_guardar} - NO SE GUARDÓ NADA\n")

    # si hay pocos (ejemplo: menos de 5 camiones)
    elif len(vehiculos_hoy) < 15:
        with open(ALERTA, "a", encoding="utf-8") as f:
            f.write(f"⚠️ {fecha_guardar} - FALTAN CAMIONES ({len(vehiculos_hoy)})\n")

    else:
        print("✅ VALIDACIÓN OK")

except Exception as e:
    with open(ALERTA, "a", encoding="utf-8") as f:
        f.write(f"❌ ERROR VALIDACIÓN {fecha_guardar}: {str(e)}\n")

import subprocess
subprocess.run(["C:\\Python314\\python.exe", "C:\\GPS\\mantenimiento.py"])