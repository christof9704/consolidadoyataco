import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN E IDENTIDAD ---
st.set_page_config(page_title="Panel Académico Yataco", layout="wide")

# Colores similares a tu código original
COLORS = {
    'Mañana': '#fbbf24',
    'Tarde': '#F97316',
    'Noche': '#1e3a8a',
    'Sin Turno': '#cbd5e1'
}

st.title("📊 Sistema de Gestión Académica - Yataco Academy")

# --- CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("Sube tu base de datos (Excel/CSV)", type=["xlsx", "csv"])

if uploaded_file:
    # Leer archivo
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # --- LIMPIEZA BÁSICA (Similar a tu Parser) ---
    # Intentamos detectar columnas clave
    df.columns = [c.strip() for c in df.columns]
    
    # Filtros en el Sidebar
    st.sidebar.header("Filtros")
    todas_sedes = df['SEDE'].unique() if 'SEDE' in df.columns else []
    sedes_sel = st.sidebar.multiselect("Seleccionar Sedes", todas_sedes, default=todas_sedes)

    # Filtrar datos
    if 'SEDE' in df.columns:
        df = df[df['SEDE'].isin(sedes_sel)]

    # --- DASHBOARD GENERAL ---
    col1, col2, col3 = st.columns(3)
    total_estudiantes = df['Estudiantes'].sum() if 'Estudiantes' in df.columns else 0
    total_cursos = len(df)
    
    col1.metric("Total Estudiantes", total_students)
    col2.metric("Cursos Activos", total_courses)
    col3.metric("Sedes Filtradas", len(sedes_sel))

    st.markdown("---")
    
# --- DASHBOARD GENERAL ---
    col1, col2, col3 = st.columns(3)
    
    # Usamos nombres consistentes para las variables
    total_estudiantes = df['Estudiantes'].sum() if 'Estudiantes' in df.columns else 0
    total_cursos = len(df)
    sedes_activas = len(sedes_sel)
    
    # Aquí es donde estaba el error: ahora los nombres coinciden
    col1.metric("Total Estudiantes", total_estudiantes)
    col2.metric("Cursos Activos", total_cursos)
    col3.metric("Sedes Filtradas", sedes_activas)
    # --- GRÁFICOS ---
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("Alumnos por Sede")
        if 'SEDE' in df.columns and 'Estudiantes' in df.columns:
            fig_sede = px.bar(df.groupby('SEDE')['Estudiantes'].sum().reset_index(), 
                             x='SEDE', y='Estudiantes', color='SEDE',
                             text_auto=True)
            st.plotly_chart(fig_sede, use_container_width=True)

    with g2:
        st.subheader("Distribución por Turnos")
        # Ajuste de turnos similar a tu lógica
        if 'TurnoOriginal' in df.columns:
            fig_pie = px.pie(df, names='TurnoOriginal', values='Estudiantes',
                            color='TurnoOriginal', color_discrete_map=COLORS)
            st.plotly_chart(fig_pie, use_container_width=True)

    # --- TABLA DETALLE ---
    st.subheader("Detalle de Programación")
    st.dataframe(df, use_container_width=True)

else:
    st.info("👋 Christopher, por favor sube el archivo Excel de Yataco en la izquierda para ver las métricas.")
