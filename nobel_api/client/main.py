# client/main.py

import requests
from getpass import getpass

BASE_URL = "http://127.0.0.1:8000"


def make_auth():
    print("== Autenticación para operaciones de escritura ==")
    username = input("Usuario (admin): ").strip()
    password = getpass("Contraseña: ")
    return (username, password)


def listar_prizes():
    year = input("Filtrar por año (ENTER para ninguno): ").strip() or None
    category = input("Filtrar por categoría (ENTER para ninguna): ").strip() or None

    params = {}
    if year:
        params["year"] = int(year)
    if category:
        params["category"] = category

    resp = requests.get(f"{BASE_URL}/prizes", params=params)
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nSe encontraron {len(data)} premios:\n")
        for p in data[:10]:  # mostramos solo los primeros 10 
            print(f"- {p['year']} | {p['category']} | laureados: {len(p.get('laureates') or [])}")
        if len(data) > 10:
            print(f"... (total {len(data)} premios)")
    elif resp.status_code == 429:
        print("Error 429: Demasiadas solicitudes. Probá de nuevo en unos segundos.")
    else:
        print(f"Error {resp.status_code}: {resp.text}")


def ver_prize():
    year = int(input("Año: ").strip())
    category = input("Categoría: ").strip()
    resp = requests.get(f"{BASE_URL}/prizes/{year}/{category}")
    if resp.status_code == 200:
        p = resp.json()
        print("\nPremio encontrado:")
        print(p)
    elif resp.status_code == 404:
        print("No existe premio para ese año y categoría.")
    elif resp.status_code == 429:
        print("Error 429: Demasiadas solicitudes. Probá de nuevo en unos segundos.")
    else:
        print(f"Error {resp.status_code}: {resp.text}")


def crear_prize(auth):
    year = int(input("Año: ").strip())
    category = input("Categoría: ").strip()

    laureates = []
    while True:
        add = input("¿Agregar laureado? (s/n): ").strip().lower()
        if add != "s":
            break
        lid = input("  id (número): ").strip()
        firstname = input("  nombre: ").strip()
        surname = input("  apellido (ENTER si no tiene): ").strip() or None
        motivation = input("  motivación: ").strip()
        share = input("  share (número): ").strip()

        laureates.append({
            "id": int(lid),
            "firstname": firstname,
            "surname": surname,
            "motivation": motivation,
            "share": int(share),
        })

    payload = {
        "year": int(year),
        "category": category,
        "laureates": laureates or None,
    }

    resp = requests.post(f"{BASE_URL}/prizes", json=payload, auth=auth)
    if resp.status_code == 201:
        print("Premio creado correctamente:")
        print(resp.json())
    elif resp.status_code == 401:
        print("No autorizado: credenciales inválidas.")
    elif resp.status_code == 409:
        print("Conflicto: ya existe un premio con ese año y categoría.")
    elif resp.status_code == 429:
        print("Error 429: Demasiadas solicitudes.")
    else:
        print(f"Error {resp.status_code}: {resp.text}")

def modificar_prize(auth):
    print("== Modificar premio existente (PUT) ==")
    year_old = int(input("Año del premio a modificar (ID del recurso): ").strip())
    category_old = input("Categoría del premio a modificar (ID del recurso): ").strip()

    print("\nAhora ingresá el NUEVO contenido del premio (reemplaza todo).")
    year_new = input("Nuevo año (ENTER para mantener el mismo): ").strip()
    category_new = input("Nueva categoría (ENTER para mantener la misma): ").strip()

    # Si el usuario no pone nada, mantenemos los valores viejos
    year_final = int(year_new) if year_new else int(year_old)
    category_final = category_new if category_new else category_old

    laureates = []
    while True:
        add = input("¿Agregar laureado? (s/n): ").strip().lower()
        if add != "s":
            break

        lid = int(input("  id (número): ").strip())
        firstname = input("  nombre: ").strip()
        surname = input("  apellido (ENTER si no tiene): ").strip() or None
        motivation = input("  motivación: ").strip()
        share = int(input("  share (número): ").strip())

        laureates.append({
            "id": int(lid),
            "firstname": firstname,
            "surname": surname,
            "motivation": motivation,
            "share": int(share),
        })

    payload = {
        "year": year_final,
        "category": category_final,
        "laureates": laureates or None,
    }

    # PUT al recurso identificado por year_old/category_old
    resp = requests.put(
        f"{BASE_URL}/prizes/{year_old}/{category_old}",
        json=payload,
        auth=auth
    )

    if resp.status_code == 200:
        print("Premio modificado correctamente:")
        print(resp.json())
    elif resp.status_code == 404:
        print("No existe premio para ese año y categoría (no se puede modificar).")
    elif resp.status_code == 401:
        print("No autorizado: credenciales inválidas.")
    elif resp.status_code == 422:
        print("Error 422: Datos inválidos (validación). Revisá year/category/laureates.")
        print(resp.text)
    elif resp.status_code == 429:
        print("Error 429: Demasiadas solicitudes.")
    else:
        print(f"Error {resp.status_code}: {resp.text}")


def borrar_prize(auth):
    year = input("Año del premio a borrar: ").strip()
    category = input("Categoría: ").strip()
    resp = requests.delete(f"{BASE_URL}/prizes/{year}/{category}", auth=auth)
    if resp.status_code == 204:
        print("Premio borrado correctamente.")
    elif resp.status_code == 404:
        print("No existe ese premio.")
    elif resp.status_code == 401:
        print("No autorizado: credenciales inválidas.")
    elif resp.status_code == 429:
        print("Error 429: Demasiadas solicitudes.")
    else:
        print(f"Error {resp.status_code}: {resp.text}")


def menu():
    auth = None

    while True:
        print("\n===== Cliente Nobel API =====")
        print("1) Listar premios")
        print("2) Ver premio específico")
        print("3) Autenticarse como admin")
        print("4) Crear premio (requiere admin)")
        print("5) Modificar premio (requiere admin)")
        print("6) Borrar premio (requiere admin)")
        print("0) Salir")

        opcion = input("Opción: ").strip()

        if opcion == "1":
            listar_prizes()
        elif opcion == "2":
            ver_prize()
        elif opcion == "3":
            auth = make_auth()
        elif opcion == "4":
            if not auth:
                print("Primero autenticáte (opción 3).")
            else:
                crear_prize(auth)
        elif opcion == "5":
            if not auth:
                print("Primero autenticáte (opción 3).")
            else:
                modificar_prize(auth)
        elif opcion == "6":
            if not auth:
                print("Primero autenticáte (opción 3).")
            else:
                borrar_prize(auth)
        elif opcion == "0":
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")


if __name__ == "__main__":
    menu()
