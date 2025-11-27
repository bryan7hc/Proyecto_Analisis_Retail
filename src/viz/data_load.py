# src/viz/data_load.py
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from db.db_utils import get_engine_from_env

def load_from_csv(path):
    try:
        return pd.read_csv(path, encoding="utf-8", parse_dates=True)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1", parse_dates=True)


def load_from_db(query, limit=None):
    """
    Ejecuta una consulta SQL y devuelve un DataFrame.
    Si limit está definido, se concatena LIMIT en la query.
    """
    engine = get_engine_from_env()
    if limit:
        query = f"{query.rstrip(';')} LIMIT {int(limit)};"
    return pd.read_sql_query(query, engine)
