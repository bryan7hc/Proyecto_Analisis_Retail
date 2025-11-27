# src/viz/streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from src.viz.data_load import load_from_db, load_from_csv
import os

st.set_page_config(page_title="Dashboard Retail - Nivel 1", layout="wide")

# ---------------------------
# Configuración: modo de desarrollo (CSV) o producción (DB)
# ---------------------------
USE_CSV = os.getenv("USE_CSV", "true").lower() in ("1", "true", "yes")
CSV_PATH = os.getenv("CSV_PATH", "../../data/superstore.csv")  # ajustar si hace falta

# ---------------------------
# Carga de datos (con cache)
# ---------------------------
@st.cache_data(ttl=600)
def get_data(limit=None):
    """
    Retorna el DataFrame principal.
    - En desarrollo puede usar CSV.
    - En integración final usará Postgres vía load_from_db.
    """
    if USE_CSV:
        df = load_from_csv(CSV_PATH)
    else:
        q = "SELECT * FROM orders"  # adapta el nombre de la tabla si difiere
        df = load_from_db(q, limit=limit)
    # Asegurarse de tipos básicos
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    return df

df = get_data(limit=200000)  # límite para evitar consumo excesivo en desarrollo

# ---------------------------
# INTERFAZ: Sidebar (filtros)
# ---------------------------
st.sidebar.header("Filtros")
min_date = st.sidebar.date_input("Fecha mínima", value=df['order_date'].min().date() if 'order_date' in df.columns else None)
max_date = st.sidebar.date_input("Fecha máxima", value=df['order_date'].max().date() if 'order_date' in df.columns else None)

region_options = df['region'].dropna().unique().tolist() if 'region' in df.columns else []
region_selected = st.sidebar.multiselect("Región", options=region_options, default=region_options)

category_options = df['category'].dropna().unique().tolist() if 'category' in df.columns else []
category_selected = st.sidebar.multiselect("Categoría", options=category_options, default=category_options)

# Aplicar filtros
if 'order_date' in df.columns:
    mask = (df['order_date'].dt.date >= min_date) & (df['order_date'].dt.date <= max_date)
else:
    mask = pd.Series([True]*len(df))
if 'region' in df.columns:
    mask &= df['region'].isin(region_selected)
if 'category' in df.columns:
    mask &= df['category'].isin(category_selected)

df_filtered = df[mask].copy()

# ---------------------------
# KPIs
# ---------------------------
st.title("Dashboard Retail — Proyecto Integral (Nivel 1)")
st.markdown("**Resumen ejecutivo**: filtros aplicados y métricas clave.")

col1, col2, col3, col4 = st.columns(4)
total_sales = df_filtered['sales'].sum() if 'sales' in df_filtered.columns else 0
total_profit = df_filtered['profit'].sum() if 'profit' in df_filtered.columns else 0
total_orders = df_filtered.shape[0]
avg_order_value = total_sales / total_orders if total_orders > 0 else 0
margin = (total_profit / total_sales) if total_sales != 0 else 0

col1.metric("Ventas (Total)", f"{total_sales:,.2f}")
col2.metric("Profit (Total)", f"{total_profit:,.2f}")
col3.metric("Número de registros", f"{total_orders:,}")
col4.metric("Margen", f"{margin:.2%}")

# ---------------------------
# Gráfica 1: Serie temporal de ventas
# ---------------------------
st.subheader("Ventas por fecha")
if 'order_date' in df_filtered.columns and 'sales' in df_filtered.columns:
    ts = df_filtered.groupby(df_filtered['order_date'].dt.to_period('M'))['sales'].sum().reset_index()
    ts['order_date'] = ts['order_date'].dt.to_timestamp()
    fig_ts = px.line(ts, x='order_date', y='sales', labels={'order_date': 'Fecha', 'sales': 'Ventas'})
    st.plotly_chart(fig_ts, use_container_width=True)
else:
    st.info("No hay columnas 'order_date' o 'sales' en el dataset filtrado.")

# ---------------------------
# Gráfica 2: Top productos por profit
# ---------------------------
st.subheader("Top productos por Profit")
if 'product_name' in df_filtered.columns and 'profit' in df_filtered.columns:
    top_products = (df_filtered.groupby('product_name')['profit']
                    .sum().reset_index().sort_values('profit', ascending=False).head(15))
    fig_top = px.bar(top_products, x='profit', y='product_name', orientation='h', labels={'profit': 'Profit', 'product_name': 'Producto'})
    st.plotly_chart(fig_top, use_container_width=True)
else:
    st.info("No hay columnas 'product_name' o 'profit' en el dataset filtrado.")

# ---------------------------
# Tabla interactiva y descarga
# ---------------------------
st.subheader("Tabla de datos (muestra)")
st.dataframe(df_filtered.head(100))

@st.cache_data()
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_bytes = convert_df_to_csv(df_filtered.head(1000))
st.download_button(label="Descargar muestra (CSV)", data=csv_bytes, file_name="retail_sample.csv", mime="text/csv")
