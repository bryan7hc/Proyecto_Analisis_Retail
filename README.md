# Activar entorno virtual
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt


# 📊 Proyecto de Análisis Retail — Dashboard + ETL + PostgreSQL

Este proyecto implementa un flujo completo de **Análisis de Datos**, desde la ingesta del dataset crudo, su transformación mediante un pipeline ETL, la carga a una base de datos PostgreSQL, hasta la visualización interactiva mediante un dashboard construido en **Streamlit**.

El objetivo principal es demostrar habilidades profesionales en:

* Limpieza y transformación de datos (ETL)
* Modelado y carga en base de datos
* Desarrollo de dashboards analíticos
* Organización modular de proyectos
* Conexión entre Python, SQL y aplicaciones interactivas

---

## 🗂️ Arquitectura General del Proyecto

```
proyecto_analisis_retail/
│
├── data/
│   ├── superstore.csv
│   └── clean_superstore.csv
│
├── src/
│   ├── transform/
│   │     └── prepare_data.py
│   └── dashboard/
│         └── app_streamlit.py
│
├── .venv/
├── requirements.txt
└── README.md
```

### 📁 `data/`

Contiene los datasets utilizados:

* **superstore.csv:** dataset crudo, tal cual fue descargado.
* **clean_superstore.csv:** dataset limpio generado automáticamente por el ETL.

### 📁 `src/transform/prepare_data.py`

Este archivo implementa el pipeline ETL:

1. **Extract:** carga el CSV crudo desde `data/superstore.csv`.
2. **Transform:**

   * Limpieza de nombres de columnas.
   * Conversión de tipos (fechas, numéricos, cadenas).
   * Cálculo de nuevas métricas: profit margin, days to ship, año y mes de orden.
   * Manejo de encoding (`latin1`) y valores corruptos.
3. **Load:** carga el dataframe limpio a PostgreSQL como la tabla `superstore_clean`.

Este proceso garantiza que los datos estén listos para análisis y visualización.

### 📁 `src/dashboard/app_streamlit.py`

Aplicación visual interactiva construida con Streamlit. Se encarga de:

* Conectarse a PostgreSQL.
* Ejecutar consultas dinámicas.
* Mostrar KPIs (ventas, profit, margen, órdenes).
* Visualizar gráficos:

  * Ventas por mes
  * Profit por categoría
  * Top productos
* Mostrar una tabla final filtrable.

La aplicación permite un análisis exploratorio completo.

---

## 🛠️ Tecnologías Utilizadas

### **Backend y ETL**

* Python 3.x
* Pandas
* SQLAlchemy
* Psycopg2
* Python-Decouple

### **Base de Datos**

* PostgreSQL 18
* Esquema `public`
* Tabla: `superstore_clean`

### **Dashboard**

* Streamlit
* Plotly (visualizaciones)

### **Entorno de desarrollo**

* Visual Studio Code
* Entorno virtual `.venv`

---

## 🚀 Flujo Completo del Proyecto

```
superstore.csv (crudo)
      │
      ▼
prepare_data.py (ETL)
      │
      ▼
clean_superstore.csv (procesado)
      │
      ▼
PostgreSQL → superstore_clean
      │
      ▼
Streamlit → Dashboard Interactivo
```

Este flujo demuestra conocimientos en ingeniería de datos, visualización e integración.

---

## ▶️ Cómo Encender el Proyecto

### 1. Activar entorno virtual

```
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias

```
pip install -r requirements.txt
```

### 3. Ejecutar ETL

```
python src/transform/prepare_data.py
```

### 4. Encender dashboard

```
streamlit run src/dashboard/app_streamlit.py
```

---

## 📌 Objetivo del Proyecto en Portafolio

Este proyecto fue diseñado para demostrar:

* Competencia sólida en análisis de datos.
* Capacidad para trabajar con infraestructura real (bases de datos + Python).
* Buenas prácticas en organización de proyectos.
* Habilidad para entregar soluciones visuales comprensibles y funcionales.

Es un proyecto ideal para aplicar a posiciones de:

* Data Analyst
* Business Intelligence
* Data Engineer (nivel junior)
* Data Science (nivel inicial)

---

## 📞 Contacto

*Aquí puedes agregar tus redes, correo o portafolio personal.*
