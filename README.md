# 🏆 Nobel Prizes API — TP Redes de Datos · TUIA · UNR
 
Trabajo Práctico de la materia **Redes de Datos** — TUIA, Universidad Nacional de Rosario (2025).
 
API REST construida con **FastAPI** sobre datos históricos de los Premios Nobel (1901–2025), que implementa autenticación, rate limiting y operaciones CRUD completas.
 
---
 
## 📁 Estructura del proyecto
 
```
TP_Redes-de-datos/
├── nobel_api_tp/
│   ├── data/
│   │   ├── prizes_raw.json        # Datos crudos descargados de la API oficial Nobel
│   │   └── prizes_db.json         # Base de datos local usada por el servidor
│   ├── app/
│   │   ├── main.py                # Definición de rutas, middlewares y seguridad
│   │   ├── models.py              # Modelos Pydantic: Laureate, Prize, PrizeCreate
│   │   └── repository.py          # Lógica de acceso y modificación de datos
│   └── setup.py                   # Descarga y preparación inicial del dataset
└── requirements.txt
```
 
---
 
## 🔧 Funcionalidades
 
### API REST — Endpoints disponibles
 
| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| `GET` | `/prizes` | No | Lista todos los premios. Filtra por `year` y/o `category` |
| `GET` | `/prizes/{year}/{category}` | No | Obtiene un premio específico |
| `POST` | `/prizes` | Sí | Crea un nuevo premio |
| `PUT` | `/prizes/{year}/{category}` | Sí | Modifica un premio existente |
| `DELETE` | `/prizes/{year}/{category}` | Sí | Elimina un premio (204 No Content) |
 
### Seguridad
 
**HTTP Basic Auth** con contraseña hasheada (SHA-256 + salt) para todos los endpoints que modifican datos (`POST`, `PUT`, `DELETE`). Las credenciales no se almacenan en texto plano.
 
### Rate Limiting
 
Limitación por IP: máximo 10 requests por ventana de 60 segundos. Devuelve HTTP 429 al exceder el límite. El estado se mantiene en memoria por IP.
 
### CORS
 
Habilitado para todas las origins (`*`), pensado para facilitar pruebas desde herramientas externas como Postman o Thunder Client.
 
---
 
## 📦 Dataset
 
- **Fuente:** [API oficial Nobel Prize](https://api.nobelprize.org/v1/prize.json)
- **Cobertura:** 1901–2025, categorías: physics, chemistry, medicine, literature, peace, economics
- **Formato:** JSON con estructura `{ "prizes": [ { year, category, laureates: [...] } ] }`
- **Inicialización:** el script `setup.py` descarga el dataset y genera `prizes_db.json` como base de datos local
---
 
## 🛠️ Tecnologías utilizadas
 
| Tecnología | Uso |
|---|---|
| `FastAPI` | Framework web y definición de rutas |
| `Pydantic` | Validación de modelos de datos |
| `uvicorn` | Servidor ASGI |
| `hashlib` (SHA-256) | Hash de contraseñas |
| `requests` | Descarga del dataset desde la API Nobel |
 
---
 
## ⚙️ Instalación y ejecución
 
```bash
git clone https://github.com/Ftedp/TP_Redes-de-datos.git
cd TP_Redes-de-datos
pip install -r requirements.txt
 
# Inicializar la base de datos local
python setup.py
 
# Levantar el servidor
uvicorn nobel_api_tp.app.main:app --reload
```
 
La documentación interactiva queda disponible en `http://localhost:8000/docs` (Swagger UI).
 
### Ejemplos de uso
 
```bash
# Listar todos los premios
GET /prizes
 
# Filtrar por año y categoría
GET /prizes?year=2024&category=physics
 
# Obtener un premio específico
GET /prizes/2024/chemistry
 
# Crear un premio (requiere autenticación)
POST /prizes
Authorization: Basic <credentials>
Content-Type: application/json
{
  "year": 2025,
  "category": "physics",
  "laureates": [...]
}
```
 
---
 
## 🏫 Contexto académico
 
| Campo | Detalle |
|---|---|
| Materia | Redes de Datos |
| Carrera | TUIA — Tecnicatura Universitaria en Inteligencia Artificial |
| Universidad | FCEIA — Universidad Nacional de Rosario (UNR) |
| Año | 2025 |
