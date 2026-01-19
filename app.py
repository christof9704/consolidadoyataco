import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Panel Académico Yataco", layout="wide")

# Colores personalizados
COLORS = {
    'Mañana': '#fbbf24',
    'Tarde': '#F97316',
    'Noche': '#1e3a8a',
    'Sin Turno': '#cbd5e1'
}

st.title("📊 Sistema de Gestión Académica - Yataco Academy")
st.markdown("---")

# --- CARGA DE DATOS ---
st.sidebar.header("Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu Excel aquí (ej. cursos cuantitativo...)", type=["xlsx", "csv"])

if uploaded_file:
    # 1. Leer el archivo
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Limpiar nombres de columnas (quitar espacios extra)
        df.columns = [c.strip() for c in df.columns]

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    # 2. Filtros en la barra lateral
    st.sidebar.subheader("Filtros")
    
    # Detectar la columna de Sede automáticamente
    if 'SEDE' in df.columns:
        todas_sedes = df['SEDE'].unique()
        sedes_sel = st.sidebar.multiselect("Filtrar por Sede:", todas_sedes, default=todas_sedes)
        
        # Aplicar filtro
        df_filtrado = df[df['SEDE'].isin(sedes_sel)]
    else:
        st.warning("No encontré la columna 'SEDE' en tu Excel. Mostrando todos los datos.")
        df_filtrado = df

    # 3. Métricas Principales (KPIs)
    col1, col2, col3 = st.columns(3)
    
    # Calcular totales (validando que existan las columnas)
    total_estudiantes = df_filtrado['Estudiantes'].sum() if 'Estudiantes' in df_filtrado.columns else 0
    total_cupos = df_filtrado['Cupo'].sum() if 'Cupo' in df_filtrado.columns else 0
    total_cursos = len(df_filtrado)
    
    # Mostrar métricas
    col1.metric("Total Alumnos", f"{total_estudiantes}")
    col2.metric("Total Cupos", f"{total_cupos}")
    col3.metric("Cursos Activos", f"{total_cursos}")

    st.markdown("---")

    # 4. Gráficos
    if not df_filtrado.empty:
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("Alumnos por Sede")
            if 'SEDE' in df_filtrado.columns and 'Estudiantes' in df_filtrado.columns:
                datos_sede = df_filtrado.groupby('SEDE')['Estudiantes'].sum().reset_index()
                fig_bar = px.bar(datos_sede, x='SEDE', y='Estudiantes', text_auto=True, title="Totales por Sede")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Faltan columnas 'SEDE' o 'Estudiantes' para este gráfico.")

        with g2:
            st.subheader("Distribución por Turno")
            # Intentar buscar la columna de turno (puede llamarse 'Turno' o 'TurnoOriginal')
            col_turno = 'Turno' if 'Turno' in df_filtrado.columns else 'TurnoOriginal'
            
            if col_turno in df_filtrado.columns:
                # ESTA ES LA LÍNEA QUE SE CORTÓ ANTES:
                fig_pie = px.pie(df_filtrado, names=col_turno, values='Estudiantes', title="Alumnos por Turno", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info(f"No encontré la columna de Turno (busqué 'Turno' o 'TurnoOriginal').")

        # 5. Tabla de Datos Detallada
        st.subheader("Detalle de Cursos")
        st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")

else:
    # Mensaje de bienvenida cuando no hay archivo
    st.info("👋 Hola Christopher. Sube el archivo Excel en el menú de la izquierda para comenzar.")
