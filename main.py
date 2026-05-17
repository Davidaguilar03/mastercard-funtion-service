import functions_framework
import psycopg
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

LOG_PATH = os.getenv("LOG_PATH", "logs/mastercard.log")

def log(nivel: str, mensaje: str, extra: dict = {}):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entrada = {
        "timestamp": datetime.now().isoformat(),
        "servicio": "mastercard",
        "nivel": nivel,
        "mensaje": mensaje,
        **extra
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entrada) + "\n")

def get_connection():
    return psycopg.connect(DATABASE_URL)

def existe_usuario(numero_tarjeta: str, usuario: str) -> bool:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1 FROM clientes_mastercard
            WHERE numero_tarjeta = %s
              AND usuario = %s
            """,
            (numero_tarjeta, usuario)
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()

@functions_framework.http
def validar_mastercard(request):
    numero_tarjeta = request.args.get("numero_tarjeta")
    usuario = request.args.get("usuario")

    log("INFO", "Solicitud de validación Mastercard", {"usuario": usuario, "numero_tarjeta": numero_tarjeta})

    if not numero_tarjeta or not usuario:
        log("ERROR", "Parámetros faltantes", {})
        return {"error": "Faltan parámetros numero_tarjeta y usuario"}, 400

    if existe_usuario(numero_tarjeta, usuario):
        log("INFO", "Tarjeta válida", {"usuario": usuario})
        return {"valido": True, "mensaje": "Tarjeta válida"}, 200

    log("ERROR", "Tarjeta no encontrada", {"usuario": usuario})
    return {"valido": False, "mensaje": "Tarjeta no válida"}, 200