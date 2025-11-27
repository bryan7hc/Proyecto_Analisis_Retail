# src/db/db_utils.py
from sqlalchemy import create_engine
import os
from urllib.parse import quote_plus

def get_engine_from_env():
    """
    Crea y devuelve un engine SQLAlchemy a PostgreSQL usando variables de entorno:
    DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME.
    """
    user = os.getenv("DB_USER", "retail_user")
    password = os.getenv("DB_PASS", "retail_pwd")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db = os.getenv("DB_NAME", "retail_db")

    # Escapa la contraseña por si tiene caracteres especiales
    password_quoted = quote_plus(password)
    uri = f"postgresql+psycopg2://{user}:{password_quoted}@{host}:{port}/{db}"
    engine = create_engine(uri, echo=False)
    return engine
