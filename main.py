import functions_framework
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
print("DATABASE_URL:", os.getenv("DATABASE_URL"))

DATABASE_URL = os.getenv("DATABASE_URL")

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
              AND habilitado = 1
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

    if not numero_tarjeta or not usuario:
        return {"error": "Faltan parámetros numero_tarjeta y usuario"}, 400

    if existe_usuario(numero_tarjeta, usuario):
        return {"valido": True, "mensaje": "Tarjeta válida"}, 200
    return {"valido": False, "mensaje": "Tarjeta no válida o no habilitada"}, 200