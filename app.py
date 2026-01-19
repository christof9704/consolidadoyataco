import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Dashboard Yataco Academy", layout="wide")

st.title("📊 Sistema de Gestión Académica - Yataco Academy")
st.markdown("---")

# --- CARGA DE DATOS ---
st.sidebar.header("Carga de Datos")
uploaded_file = st.sidebar.file_uploader("Sube tu Excel aquí", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # 1. Leer el archivo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Limpiar nombres de columnas
        df.columns = [c.strip() for c in df.columns]

        # 2. INTELIGENCIA DE COLUMNAS (Ajuste para el formato de Christopher)
        # Extraer SEDE desde la columna 'Período' (Ej: "VIRTUAL - I_25" -> "VIRTUAL")
        if 'Período' in df.columns:
            df['SEDE_EXTRAIDA'] = df['Período'].str.split(' - ').str[0]
        else:
            df['SEDE_EXTRAIDA'] = "Sin Sede"

        # Extraer TURNO desde la columna 'Sede - turno' (Ej: "YATACO PRINCIPAL - Noche" -> "Noche")
        if 'Sede - turno' in df.columns:
            df['TURNO_EXTRAIDO'] = df['Sede - turno'].str.split(' - ').str[-1]
        else:
            df['TURNO_EXTRAIDO'] = "Sin Turno"

        # Mapear Cupo Máximo
        col_cupo = 'Cupo máximo' if 'Cupo máximo' in df.columns else ('Cupo' if 'Cupo' in df.columns else None)

        # 3. FILTROS
        st.sidebar.subheader("Filtros")
        todas_sedes = sorted(df['SEDE_EXTRAIDA'].unique())
        sedes_sel = st.sidebar.multiselect("Seleccionar Sedes:", todas_sedes, default=todas_sedes)
        
        df_filtrado = df[df['SEDE_EXTRAIDA'].isin(sedes_sel)]

        # 4. MÉTRICAS (KPIs)
        col1, col2, col3 = st.columns(3)
        total_estudiantes = df_filtrado['Estudiantes'].sum() if 'Estudiantes' in df_filtrado.columns else 0
        total_cupos = df_filtrado[col_cupo].sum() if col_cupo else 0
        total_cursos = len(df_filtrado)

        col1.metric("Total Alumnos", f"{int(total_estudiantes)}")
        col2.metric("Total Cupos", f"{int(total_cupos)}")
        col3.metric("Cursos Activos", f"{total_cursos}")

        st.markdown("---")

        # 5. GRÁFICOS
        g1, g2 = st.columns(2)

        with g1:
            st.subheader("Alumnos por Sede")
            if 'Estudiantes' in df_filtrado.columns:
                datos_sede = df_filtrado.groupby('SEDE_EXTRAIDA')['Estudiantes'].sum().reset_index()
                fig_bar = px.bar(datos_sede, x='SEDE_EXTRAIDA', y='Estudiantes', 
                                 text_auto=True, title="Distribución por Sede",
                                 labels={'SEDE_EXTRAIDA': 'Sede', 'Estudiantes': 'Alumnos'})
                st.plotly_chart(fig_bar, use_container_width=True)

        with g2:
            st.subheader("Distribución por Turno")
            fig_pie = px.pie(df_filtrado, names='TURNO_EXTRAIDO', values='Estudiantes', 
                            title="Alumnos por Turno", hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)

        # 6. TABLA DETALLADA
        st.subheader("Detalle de Cursos")
        st.dataframe(df_filtrado, use_container_width=True)

    except Exception as e:
        st.error(f"Hubo un problema al procesar los datos: {e}")
else:
    st.info("👋 Sube tu archivo Excel para activar el Dashboard.")
