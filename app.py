import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Panel Académico Yataco", layout="wide", initial_sidebar_state="expanded")

# Colores del código original
COLORS = {
    'primary': '#2563eb',
    'shifts': {
        'Mañana': '#fbbf24',
        'Tarde': '#F97316',
        'Noche': '#1e3a8a',
        'Sin Turno': '#cbd5e1'
    }
}

# Estilo CSS para las tarjetas (Cards)
st.markdown("""
    <style>
    .sede-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Panel Académico - Yataco Academy")
st.caption("Gestión inteligente de sedes, turnos y periodos")

# --- CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("📂 Sube tu base de datos (Excel)", type=["xlsx", "csv"])

if uploaded_file:
    # Procesamiento inicial
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]

    # --- LÓGICA DE EXTRACCIÓN DE DATOS ---
    # 1. Extraer SEDE
    if 'Período' in df.columns:
        df['Sede_Limpia'] = df['Período'].str.split(' - ').str[0]
    else:
        df['Sede_Limpia'] = "Sin Sede"

    # 2. Extraer TURNO
    if 'Sede - turno' in df.columns:
        def get_turno(v):
            v = str(v).lower()
            if 'mañana' in v: return 'Mañana'
            if 'tarde' in v: return 'Tarde'
            if 'noche' in v: return 'Noche'
            return 'Sin Turno'
        df['Turno_Limpio'] = df['Sede - turno'].apply(get_turno)

    # 3. LÓGICA DEL PERIODO (NUEVO)
    if 'Fecha inicio' in df.columns:
        # Convertimos a formato fecha
        df['Fecha_DT'] = pd.to_datetime(df['Fecha inicio'], errors='coerce')
        # Creamos una etiqueta "Mes Año" (Ej: Enero 2026)
        df['Mes_Año'] = df['Fecha_DT'].dt.strftime('%B %Y').replace({
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
            'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
            'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        })
    else:
        df['Mes_Año'] = "Sin Fecha"

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.markdown("---")
    
    # Filtro 1: Sedes
    sedes_unicas = sorted(df['Sede_Limpia'].unique())
    sedes_sel = st.sidebar.multiselect("📍 Filtrar Sedes", sedes_unicas, default=sedes_unicas)

    # Filtro 2: Periodo (Mes/Año) - ¡AQUÍ ESTÁ LO QUE BUSCABAS!
    periodos_unicos = sorted(df['Mes_Año'].unique())
    periodo_sel = st.sidebar.multiselect("📅 Filtrar Periodo (Mes)", periodos_unicos, default=periodos_unicos)
    
    # APLICAR FILTROS
    df_filtrado = df[
        (df['Sede_Limpia'].isin(sedes_sel)) & 
        (df['Mes_Año'].isin(periodo_sel))
    ]

    # --- DASHBOARD VISUAL ---
    if not df_filtrado.empty:
        # Métricas principales
        st.subheader(f"Resumen: {', '.join(periodo_sel) if len(periodo_sel) < 3 else 'Múltiples Meses'}")
        m1, m2, m3, m4 = st.columns(4)
        
        total_est = int(df_filtrado['Estudiantes'].sum())
        total_cupos = int(df_filtrado['Cupo máximo'].sum()) if 'Cupo máximo' in df_filtrado.columns else 1
        ocupacion = (total_est / total_cupos) * 100 if total_cupos > 0 else 0

        m1.metric("Total Estudiantes", f"{total_est:,}")
        m2.metric("Cursos Activos", len(df_filtrado))
        m3.metric("Ocupación", f"{ocupacion:.1f}%")
        m4.metric("Sedes Activas", len(df_filtrado['Sede_Limpia'].unique()))

        # Gráficos
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.markdown("### Alumnos por Sede")
            fig_sede = px.bar(df_filtrado.groupby('Sede_Limpia')['Estudiantes'].sum().reset_index(),
                             x='Estudiantes', y='Sede_Limpia', orientation='h',
                             color_discrete_sequence=[COLORS['primary']], text_auto=True)
            fig_sede.update_layout(height=350, margin=dict(t=20, b=20), plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_sede, use_container_width=True)

        with c2:
            st.markdown("### Turnos")
            fig_turno = px.pie(df_filtrado, names='Turno_Limpio', values='Estudiantes',
                              hole=0.5, color='Turno_Limpio', color_discrete_map=COLORS['shifts'])
            fig_turno.update_layout(height=350, margin=dict(t=20, b=20))
            st.plotly_chart(fig_turno, use_container_width=True)

        # Módulos por Sede (Tarjetas)
        st.markdown("---")
        st.subheader("Módulos Detallados por Sede")
        cols = st.columns(3)
        for i, sede in enumerate(sedes_sel):
            target_col = cols[i % 3]
            sede_data = df_filtrado[df_filtrado['Sede_Limpia'] == sede]
            if not sede_data.empty:
                with target_col:
                    alumnos_sede = int(sede_data['Estudiantes'].sum())
                    cupos_sede = int(sede_data['Cupo máximo'].sum()) if 'Cupo máximo' in sede_data.columns else 1
                    pct = (alumnos_sede / cupos_sede) * 100
                    
                    st.markdown(f"""
                        <div class="sede-card">
                            <h4 style="color:#1e3a8a; margin:0;">📍 {sede}</h4>
                            <p style="color:#64748b; font-size:12px;">{len(sede_data)} Grupos en este periodo</p>
                            <div style="display:flex; justify-content:space-between; margin-top:10px;">
                                <span><b>{alumnos_sede}</b> Alumnos</span>
                                <span style="color:{'#ef4444' if pct > 90 else '#10b981'}; font-weight:bold;">{pct:.0f}% Ocupado</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    with st.expander("Ver detalle de cursos"):
                        st.table(sede_data[['Asignatura', 'Estudiantes']].head(10))

    else:
        st.warning("No hay datos para los filtros seleccionados. Intenta cambiar el mes o la sede.")

else:
    st.info("👋 Christopher, sube tu Excel para activar el filtro de periodo y los gráficos.")
