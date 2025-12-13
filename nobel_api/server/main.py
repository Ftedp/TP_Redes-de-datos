from typing import List, Optional
import time
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from hashlib import sha256 
from .models import Prize, PrizeCreate, Laureate
from . import repository as repo

app = FastAPI(
    title="Nobel Prizes API",
    description="API para el TP de Redes de Datos basada en premios Nobel",
    version="1.0.0",
)

#----HTTP_SECURITY_HASH_VERIFICACION-----------------------------------------------------------------------------

security = HTTPBasic()

# Salt simple para el TP 
PASSWORD_SALT = "nobel_tp_2025"

# Hash pre-calculado de la contraseña "admin1234" + salt
ADMIN_PASSWORD_HASH = "9bb0461dfa1c28a20ac121d76ffa1f6a02b874f68658491b3b4c6fe45c45a8ab"


def hash_password(password: str) -> str:
    """
    Devuelve el hash SHA-256 de (SALT + password).
    """
    texto = PASSWORD_SALT + password
    return sha256(texto.encode()).hexdigest()


def verificar_usuario(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """
    Verifica usuario/contraseña usando HTTP Basic Auth y contraseña hasheada.
    Solo se usa para endpoints que modifican datos.
    """
    username = credentials.username
    password = credentials.password

    # Por ahora solo tenemos un usuario admin
    if username != "admin":
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # Calculamos el hash del password enviado
    candidate_hash = hash_password(password)

    # Comparamos con el hash almacenado
    if candidate_hash != ADMIN_PASSWORD_HASH:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return True

#----RATE_LIMITING-------------------------------------------------------------------------------------

# ip -> (requests permitidos, inicio_ventana)
rate_limit_state: dict[str, tuple[int, float]] = {}

# Configuración del rate limiting
RATE_LIMIT_MAX = 10       # máximo de requests permitidas
RATE_LIMIT_WINDOW = 60.0  # ventana de tiempo en segundos 

def limitar_requests(request: Request) -> None:
    """
    Rate limiting por IP.
    Si se excede el límite, lanza HTTP 429 (Too Many Requests).
    """
    ip = request.client.host
    ahora = time.time()

    contador, inicio_ventana = rate_limit_state.get(ip, (0, ahora))

    # Si ya pasó la ventana de tiempo, reiniciamos contador y ventana
    if (ahora - inicio_ventana) > RATE_LIMIT_WINDOW:
        contador = 0
        inicio_ventana = ahora

    # Contamos esta nueva request
    contador += 1

    # Actualizamos el estado
    rate_limit_state[ip] = (contador, inicio_ventana)

    # Si se supera el límite, lanzamos error 429
    if contador > RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes desde esta IP. Intente nuevamente más tarde.",
        )
    
#---------------------------------------------------------------------------------------------

# (Opcional) Permitir CORS para facilitar pruebas desde otras máquinas / herramientas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#-----RUTAS-------------------------------------------------------------------------------------

@app.get("/prizes", response_model=List[Prize])
def listar_prizes(year: Optional[int] = None, category: Optional[str] = None, _: None = Depends(limitar_requests)):
    """
    Lista premios. Se puede filtrar por year, category o ambos.
    Ejemplos:
      - GET /prizescodigo
      - GET /prizes?year=2025
      - GET /prizes?category=chemistry
      - GET /prizes?year=2025&category=chemistry
    """
    return repo.filtrar_prizes(year=year, category=category)


@app.get("/prizes/{year}/{category}", response_model=Prize)
def obtener_prize(year: int, category: str, _: None = Depends(limitar_requests)):
    """
    Obtiene un premio específico por year y category.
    Ejemplo: GET /prizes/2025/chemistry
    Devuelve un objeto Prize
    """
    prize = repo.obtener_prize(year, category)
    if prize is None:
        raise HTTPException(status_code=404, detail="Premio no encontrado")
    return prize


@app.post("/prizes", response_model=Prize, status_code=201)
def crear_prize(datos: PrizeCreate,
    _: bool = Depends(verificar_usuario),
    __: None = Depends(limitar_requests)):
    """
    Crea un nuevo premio.
    """
    try:
        nuevo = repo.agregar_prize(datos)
        return nuevo
    except ValueError as e:
        # Ya existe year+category
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/prizes/{year}/{category}", response_model=Prize)
def modificar_prize(year: int, category: str, datos: PrizeCreate, 
    _: bool = Depends(verificar_usuario),
    __: None = Depends(limitar_requests)):
    """
    Modifica un premio existente identificado por year+category.
    """
    actualizado = repo.actualizar_prize(year, category, datos)
    if actualizado is None:
        raise HTTPException(status_code=404, detail="Premio no encontrado")
    return actualizado


@app.delete("/prizes/{year}/{category}", status_code=204)
def borrar_prize(year: int, category: str, _: bool = Depends(verificar_usuario),
    __: None = Depends(limitar_requests)):
    """
    Elimina un premio. Devuelve 204 No Content si se elimina.
    """
    ok = repo.eliminar_prize(year, category)
    if not ok:
        raise HTTPException(status_code=404, detail="Premio no encontrado")
    return
