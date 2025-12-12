import json
import os
from pathlib import Path

import requests

# URL oficial de los datos de premios Nobel
NOBEL_URL = "https://api.nobelprize.org/v1/prize.json"

# Rutas de archivos dentro de la carpeta del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent  # carpeta nobel_api_tp
DATA_DIR = BASE_DIR / "data"
RAW_FILE = DATA_DIR / "prizes_raw.json"
DB_FILE = DATA_DIR / "prizes_db.json"

def descargar_json():
    """Descarga el JSON desde la API de Nobel y lo guarda en prizes_raw.json."""
    print(f"Descargando datos desde {NOBEL_URL} ...")
    resp = requests.get(NOBEL_URL, timeout=30)

    # Verificamos que la respuesta sea correcta
    if resp.status_code != 200:
        raise RuntimeError(f"Error al descargar datos: {resp.status_code}")

    # transformamos json en diccionario python
    data = resp.json()

    # Nos aseguramos de que exista la carpeta data
    os.makedirs(DATA_DIR, exist_ok=True)

    # Guardamos el JSON crudo
    with RAW_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Datos guardados en {RAW_FILE}")

    return data

def cargar_desde_archivo(path: Path):
    """Carga un JSON desde el archivo indicado."""
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def crear_base_de_datos_inicial(data: dict):
    """
    Crea el archivo prizes_db.json a partir de los datos descargados.
    Este será el archivo que usará el servidor como 'base de datos'.
    """
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Base de datos inicial creada en {DB_FILE}")

def analizar_estructura(data: dict):
    """Muestra por pantalla información útil para el informe."""
    prizes = data.get("prizes", [])
    print(f"Cantidad total de premios (len(prizes)): {len(prizes)}")

    if not prizes:
        print("No hay premios en los datos.")
        return

    primer_premio = prizes[0]
    print("\nEjemplo de un premio (primer elemento de 'prizes'):")
    print(json.dumps(primer_premio, indent=2))

    print("\nClaves de un premio:")
    for key in primer_premio.keys():
        print(f"  - {key}")

    laureates = primer_premio.get("laureates", [])
    if laureates:
        primer_laureado = laureates[0]
        print("\nEjemplo de un laureado dentro de 'laureates':")
        print(json.dumps(primer_laureado, indent=2))

        print("\nClaves de un laureado:")
        for key in primer_laureado.keys():
            print(f"  - {key}")
    else:
        print("\nEste premio no tiene laureados listados.")

def main():
    if RAW_FILE.exists():
        print(f"Usando archivo ya existente: {RAW_FILE}")
        data = cargar_desde_archivo(RAW_FILE)
    else:
        data = descargar_json()

    crear_base_de_datos_inicial(data)

    print("\n===== Análisis de estructura de datos =====")
    analizar_estructura(data)


if __name__ == "__main__":
    main()