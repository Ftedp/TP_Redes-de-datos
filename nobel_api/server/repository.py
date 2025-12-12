import json
from pathlib import Path
from typing import List, Optional

from .models import Prize, PrizeCreate, Laureate

"- Repository se encarga de leer de la base de datos (data)"
"- Guardar cambios"
"- todas las operaciones básicas de datos encapsuladas."

# __file__  ->  .../nobel_api/server/repository.py
# parent    ->  .../nobel_api/server
# parent.parent -> .../nobel_api   (raíz del proyecto)

BASE_DIR = Path(__file__).resolve().parent.parent  # carpeta nobel_api
DATA_DIR = BASE_DIR / "data"
DB_FILE = DATA_DIR / "prizes_db.json"


def cargar_prizes() -> List[Prize]:
    """Carga todos los premios desde prizes_db.json como objetos Prize."""
    # 1) Abrimos el archivo JSON
    with DB_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # 2) Obtenemos la lista de premios "crudos" (dicts)
    prizes_raw = data.get("prizes", [])

    # 3) Transformamos cada dict en un objeto Prize de Pydantic
    prizes = [Prize(**p) for p in prizes_raw]

    # 4) Devolvemos la lista de objetos Prize
    return prizes


def guardar_prizes(prizes: List[Prize]) -> None:
    """Guarda la lista de premios en prizes_db.json."""
    # 1) Convertimos cada Prize (objeto) a dict
    prizes_dicts = []
    for p in prizes:
        prizes_dicts.append(p.model_dump())

    # 2) Armamos el dict raíz con la clave "prizes"
    data = {"prizes": prizes_dicts}

    # 3) Escribimos el JSON en el archivo
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def filtrar_prizes(year: Optional[str] = None,
                   category: Optional[str] = None) -> List[Prize]:
    """Devuelve premios filtrando por year y/o category."""
    # 1) Cargo todos los premios
    prizes = cargar_prizes()

    # 2) Empiezo con todos como resultado
    resultados = prizes

    # 3) Si me pasaron un año, filtro por año
    if year is not None:
        resultados = [p for p in resultados if p.year == year]

    # 4) Si me pasaron una categoría, filtro por categoría
    if category is not None:
        resultados = [p for p in resultados if p.category == category]

    # 5) Devuelvo la lista filtrada
    return resultados



def obtener_prize(year: str, category: str) -> Optional[Prize]:
    """Devuelve un premio específico por year y category, o None si no existe."""
    prizes = cargar_prizes()
    for p in prizes:
        if p.year == year and p.category == category:
            return p
    return None


def agregar_prize(nuevo: PrizeCreate) -> Prize:
    """Agrega un premio nuevo y lo guarda en el archivo."""
    # 1) Cargo todos los premios actuales
    prizes = cargar_prizes()

    # 2) Verifico que no exista ya un premio con mismo year+category
    for p in prizes:
        if p.year == nuevo.year and p.category == nuevo.category:
            raise ValueError("Ya existe un premio para ese año y categoría.")

    # 3) Creo una nueva instancia Prize a partir de PrizeCreate. (**: es el operador de desempaquedato de diccionario)
    prize_obj = Prize(**nuevo.model_dump())

    # 4) Lo agrego a la lista
    prizes.append(prize_obj)

    # 5) Guardo toda la lista actualizada en el archivo
    guardar_prizes(prizes)

    # 6) Devuelvo el nuevo premio
    return prize_obj



def actualizar_prize(year: str, category: str, actualizado: PrizeCreate) -> Optional[Prize]:
    """
    Actualiza un premio existente. Devuelve el premio actualizado
    o None si no existía.
    """
    prizes = cargar_prizes()
    encontrado = False
    indice_encontrado = -1

    # 1) Busco el premio que quiero actualizar
    for i, p in enumerate(prizes):
        if p.year == year and p.category == category:
            indice_encontrado = i
            encontrado = True
            break

    # 2) Si no lo encontré, devuelvo None
    if not encontrado:
        return None

    # 3) Reemplazo el premio en esa posición con los nuevos datos
    nuevo_prize = Prize(**actualizado.model_dump())
    prizes[indice_encontrado] = nuevo_prize

    # 4) Guardo la lista en el archivo
    guardar_prizes(prizes)

    # 5) Devuelvo el premio actualizado
    return nuevo_prize



def eliminar_prize(year: str, category: str) -> bool:
    """
    Elimina un premio por year+category.
    Devuelve True si lo eliminó, False si no existía.
    """
    prizes = cargar_prizes()
    original_len = len(prizes)

    prizes = [p for p in prizes if not (p.year == year and p.category == category)]

    if len(prizes) == original_len:
        # No se eliminó nada
        return False

    guardar_prizes(prizes)
    return True