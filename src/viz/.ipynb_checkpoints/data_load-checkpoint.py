# src/viz/data_load.py
import pandas as pd
from src.db.db_utils import get_engine_from_env

def load_from_csv(path):
    """Carga el CSV local (útil en desarrollo offline)."""
    return pd.read_csv(path, parse_dates=True, infer_datetime_format=True)

def load_from_db(query, limit=None):
    """
    Ejecuta una consulta SQL y devuelve un DataFrame.
    Si limit está definido, se concatena LIMIT en la query.
    """
    engine = get_engine_from_env()
    if limit:
        query = f"{query.rstrip(';')} LIMIT {int(limit)};"
    return pd.read_sql_query(query, engine)
