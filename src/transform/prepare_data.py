import os 
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

# --- CONFIGURACION: ajustasegun tu entorno ---

DATA_IN_PATH = Path(__file__).resolve().parents[2] / "data" / "superstore.csv"
CLEAN_OUT_PATH = Path(__file__).resolve().parents[2] / "data" / "clean_superstore.csv"

# Cadena de conexión SQLAlchemy (ajusta usuario, password, host, port, db)
DB_CONFIG = {
    'drivername': 'postgresql+psycopg2',
    'username': 'retail_user',
    'password': 'retail_pass',
    'host': 'localhost',
    'port': '5432',
    'database': 'retail_db'
}
TABLE_NAME = "superstore_clean"
CHUNK_SIZE = 100000  # para CSV grande

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
        .str.replace(r'[^0-9a-z_]', '', regex=True)
    )
    return df

def to_numeric_safe(s):
    return pd.to_numeric(s, errors='coerce')

def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    # Normalizar columnas esperadas (intentar mapear variantes)
    rename_map = {}
    # variantes comunes
    if 'order_date' not in df.columns:
        for candidate in ['orderdate','order_date','orderdate', 'order date']:
            if candidate in df.columns:
                rename_map[candidate] = 'order_date'
    if 'ship_date' not in df.columns:
        for candidate in ['shipdate','ship_date','shipdate', 'ship date']:
            if candidate in df.columns:
                rename_map[candidate] = 'ship_date'
    # sales, profit, quantity, discount
    for col in df.columns:
        if col.replace('_','') == 'sales' or col == 'sales':
            rename_map[col] = 'sales'
        if col.replace('_','') == 'profit' or col == 'profit':
            rename_map[col] = 'profit'
        if col.replace('_','') == 'quantity' or col == 'quantity':
            rename_map[col] = 'quantity'
        if col.replace('_','') == 'discount' or col == 'discount':
            rename_map[col] = 'discount'
    if rename_map:
        df = df.rename(columns=rename_map)

    # Parsear fechas
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce', dayfirst=False)
    else:
        df['order_date'] = pd.NaT

    if 'ship_date' in df.columns:
        df['ship_date'] = pd.to_datetime(df['ship_date'], errors='coerce', dayfirst=False)
    else:
        df['ship_date'] = pd.NaT

    # Numericos
    if 'sales' in df.columns:
        df['sales'] = to_numeric_safe(df['sales'])
    else:
        df['sales'] = np.nan

    if 'profit' in df.columns:
        df['profit'] = to_numeric_safe(df['profit'])
    else:
        df['profit'] = np.nan

    if 'quantity' in df.columns:
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').astype('Int64')
    else:
        df['quantity'] = pd.NA

    if 'discount' in df.columns:
        df['discount'] = to_numeric_safe(df['discount'])
    else:
        df['discount'] = np.nan

    # Campos derivados
    df['profit_margin'] = np.where(df['sales'].fillna(0) != 0, df['profit'] / df['sales'], np.nan)
    df['order_year'] = df['order_date'].dt.year
    df['order_month'] = df['order_date'].dt.to_period('M').astype(str)
    df['order_month_num'] = df['order_date'].dt.month
    df['days_to_ship'] = (df['ship_date'] - df['order_date']).dt.days

    # Limpieza básica: eliminar filas sin order_id y sin sales y sin order_date
    cond_valid = (~df['order_date'].isna()) | (~df['sales'].isna())
    df = df[cond_valid].copy()

    # Rellenar valores que se requieran o truncar longitudes si necesario
    # (ejemplo) limitar strings largos:
    str_cols = df.select_dtypes(include=['object']).columns
    for c in str_cols:
        df[c] = df[c].astype(str).str.slice(0, 500)

    return df

def save_clean_csv(df: pd.DataFrame, out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"[INFO] CSV limpio guardado en: {out_path}")

def upload_to_postgres(df: pd.DataFrame, db_config: dict, table_name: str, chunk_size:int = CHUNK_SIZE):
    engine = create_engine(URL.create(**db_config), pool_pre_ping=True)
    # Reemplazar tabla si existe (puedes cambiar si_exists)
    df.to_sql(table_name, engine, if_exists='replace', index=False, method='multi', chunksize=chunk_size)
    print(f"[INFO] Tabla '{table_name}' cargada en Postgres (db={db_config['database']})")

def main():
    print("[INFO] Iniciando proceso ETL")
    if not DATA_IN_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo de origen: {DATA_IN_PATH}")
    # Leer en chunks si archivo muy grande
    df = pd.read_csv(DATA_IN_PATH, low_memory=False, encoding="latin1", on_bad_lines="skip")
    print(f"[INFO] Archivo cargado. Filas originales: {len(df)}")
    df_clean = prepare_dataframe(df)
    print(f"[INFO] Filas después limpieza: {len(df_clean)}")
    save_clean_csv(df_clean, CLEAN_OUT_PATH)
    upload_to_postgres(df_clean, DB_CONFIG, TABLE_NAME)
    print("[INFO] ETL finalizado correctamente.")

if __name__ == "__main__":
    main()