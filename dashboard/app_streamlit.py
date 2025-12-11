# dashboard/app_streamlit.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
import plotly.express as px
import io

st.set_page_config(layout="wide", page_title="Dashboard Retail — Proyecto Integral (Nivel 1)")

# --- CONFIG: usa DB si USE_DB True, si no usa CSV limpio ---
USE_DB = True
DB_CONFIG = {
    'drivername': 'postgresql+psycopg2',
    'username': 'retail_user',
    'password': 'retail_pass',
    'host': 'localhost',
    'port': '5432',
    'database': 'retail_db'
}
TABLE_NAME = "superstore_clean"
CSV_PATH = "../data/clean_superstore.csv"  # si USE_DB=False

@st.cache_data(ttl=3600)
def load_data_from_db(limit: int = None):
    engine = create_engine(URL.create(**DB_CONFIG))
    query = f"SELECT * FROM {TABLE_NAME}"
    if limit:
        query += f" LIMIT {limit}"
    return pd.read_sql(query, engine, parse_dates=['order_date','ship_date'])

@st.cache_data(ttl=3600)
def load_data_from_csv(path):
    return pd.read_csv(path, parse_dates=['order_date','ship_date'])

# Carga
if USE_DB:
    try:
        df = load_data_from_db()
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        st.stop()
else:
    df = load_data_from_csv(CSV_PATH)

# Normalizar nombres (por si acaso)
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)

# Sidebar filtros
st.sidebar.header("Filtros")
min_date = st.sidebar.date_input("Fecha mínima", value=df['order_date'].min().date() if not df['order_date'].isna().all() else None)
max_date = st.sidebar.date_input("Fecha máxima", value=df['order_date'].max().date() if not df['order_date'].isna().all() else None)
regions = st.sidebar.multiselect("Región", options=sorted(df['region'].dropna().unique()), default=[])
categories = st.sidebar.multiselect("Categoría", options=sorted(df['category'].dropna().unique()), default=[])
segments = st.sidebar.multiselect("Segmento", options=sorted(df['segment'].dropna().unique()), default=[])

# Aplicar filtros
df_filtered = df.copy()
if min_date:
    df_filtered = df_filtered[df_filtered['order_date'] >= pd.to_datetime(min_date)]
if max_date:
    df_filtered = df_filtered[df_filtered['order_date'] <= pd.to_datetime(max_date)]
if regions:
    df_filtered = df_filtered[df_filtered['region'].isin(regions)]
if categories:
    df_filtered = df_filtered[df_filtered['category'].isin(categories)]
if segments:
    df_filtered = df_filtered[df_filtered['segment'].isin(segments)]

# KPIs
total_sales = df_filtered['sales'].sum(min_count=1)
total_profit = df_filtered['profit'].sum(min_count=1)
n_orders = df_filtered['order_id'].nunique() if 'order_id' in df_filtered.columns else len(df_filtered)
margin = (total_profit / total_sales) if total_sales and not pd.isna(total_sales) else 0
avg_ticket = (total_sales / n_orders) if n_orders else 0

st.title("Dashboard Retail — Proyecto Integral (Nivel 1)")
st.markdown("**Resumen ejecutivo:** filtros aplicados y métricas clave.")

k1, k2, k3, k4 = st.columns([1.5,1.5,1.2,1.2])
k1.metric("Ventas (Total)", f"${total_sales:,.2f}")
k2.metric("Profit (Total)", f"${total_profit:,.2f}")
k3.metric("Nº de órdenes (únicas)", f"{n_orders:,}")
k4.metric("Margen", f"{margin*100:.2f}%")

st.markdown("---")

# Gráfico 1: Ventas por fecha (serie temporal)
st.subheader("Ventas por fecha")
if 'order_date' in df_filtered.columns and 'sales' in df_filtered.columns:
    ts = df_filtered.set_index('order_date').resample('M')['sales'].sum().reset_index()
    fig_ts = px.line(ts, x='order_date', y='sales', title='Ventas mensuales', labels={'order_date':'Fecha','sales':'Ventas'})
    st.plotly_chart(fig_ts, use_container_width=True)
else:
    st.info("No hay columnas 'order_date' o 'sales' en el dataset filtrado.")

# Gráfico 2: Top productos por Profit
st.subheader("Top productos por Profit")
if 'product_name' in df_filtered.columns and 'profit' in df_filtered.columns:
    top_prod = (df_filtered.groupby('product_name')['profit']
                .sum()
                .reset_index()
                .sort_values('profit', ascending=False)
                .head(10))
    fig_prod = px.bar(top_prod, x='profit', y='product_name', orientation='h',
                      title='Top 10 productos por profit', labels={'product_name':'Producto','profit':'Profit'})
    st.plotly_chart(fig_prod, use_container_width=True)
else:
    st.info("No hay columnas 'product_name' o 'profit' en el dataset filtrado.")

# Gráfico 3: Ventas por región
st.subheader("Ventas por región")
if 'region' in df_filtered.columns and 'sales' in df_filtered.columns:
    region_sales = df_filtered.groupby('region')['sales'].sum().reset_index().sort_values('sales', ascending=False)
    fig_region = px.bar(region_sales, x='region', y='sales', title='Ventas por región', labels={'sales':'Ventas','region':'Region'})
    st.plotly_chart(fig_region, use_container_width=True)
else:
    st.info("No hay columnas 'region' o 'sales' en el dataset filtrado.")

st.markdown("---")
# Tabla de datos (muestra)
st.subheader("Tabla de datos (muestra)")
st.dataframe(df_filtered.head(200), use_container_width=True)

# Descargar CSV filtrado
def convert_df_to_csv_bytes(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode('utf-8')

csv_bytes = convert_df_to_csv_bytes(df_filtered)
st.download_button(label="Descargar datos filtrados (CSV)", data=csv_bytes, file_name="superstore_filtered.csv", mime="text/csv")

st.markdown("### Nota técnica")
st.markdown("- Fuente de datos: `superstore_clean` (Postgres) o `data/clean_superstore.csv`.\n- El ETL se realiza en `src/transform/prepare_data.py` y crea campos derivados como `profit_margin`, `days_to_ship`, `order_year` y `order_month`.")
