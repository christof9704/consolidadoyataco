import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN E IDENTIDAD VISUAL ---
st.set_page_config(page_title="Panel Académico Yataco", layout="wide", initial_sidebar_state="expanded")

# Colores del código React
COLORS = {
    'primary': '#2563eb',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'shifts': {
        'Mañana': '#fbbf24',
        'Tarde': '#F97316',
        'Noche': '#1e3a8a',
        'Sin Turno': '#cbd5e1'
    }
}

# Estilo CSS para imitar las tarjetas de React
st.markdown("""
    <style>
    .kpi-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .sede-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Panel Académico - Yataco Academy")
st.caption("Gestión inteligente de sedes, turnos y programaciones")

# --- CARGA DE DATOS ---
uploaded_file = st.sidebar.file_uploader("📂 Sube tu base de datos", type=["xlsx", "csv"])

if uploaded_file:
    # Procesamiento inicial
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]

    # Lógica de limpieza igual al React
    if 'Período' in df.columns:
        df['Sede'] = df['Período'].str.split(' - ').str[0]
    
    if 'Sede - turno' in df.columns:
        def extract_turno(val):
            val = str(val).lower()
            if 'mañana' in val: return 'Mañana'
            if 'tarde' in val: return 'Tarde'
            if 'noche' in val: return 'Noche'
            return 'Sin Turno'
        df['Turno'] = df['Sede - turno'].apply(extract_turno)

    # Filtros SideBar
    st.sidebar.markdown("---")
    sedes_unicas = sorted(df['Sede'].unique()) if 'Sede' in df.columns else []
    sedes_sel = st.sidebar.multiselect("📍 Filtrar Sedes", sedes_unicas, default=sedes_unicas)
    
    df_filtrado = df[df['Sede'].isin(sedes_sel)]

    # --- MÉTRICAS (Resumen General) ---
    st.subheader("Resumen General")
    m1, m2, m3, m4 = st.columns(4)
    
    total_est = df_filtrado['Estudiantes'].sum()
    capacidad = df_filtrado['Cupo máximo'].sum() if 'Cupo máximo' in df_filtrado.columns else 1
    ocupacion = (total_est / capacidad) * 100

    m1.metric("Total Estudiantes", f"{total_est:,}")
    m2.metric("Cursos Activos", len(df_filtrado))
    m3.metric("Ocupación Global", f"{ocupacion:.1f}%")
    m4.metric("Sedes", len(sedes_sel))

    # --- GRÁFICOS PRINCIPALES ---
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("### Alumnos por Sede")
        fig_sede = px.bar(
            df_filtrado.groupby('Sede')['Estudiantes'].sum().reset_index(),
            x='Estudiantes', y='Sede', orientation='h',
            color_discrete_sequence=[COLORS['primary']],
            text_auto=True
        )
        fig_sede.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sede, use_container_width=True)

    with col_right:
        st.markdown("### Preferencia de Turnos")
        fig_turno = px.pie(
            df_filtrado, names='Turno', values='Estudiantes',
            hole=0.5, color='Turno',
            color_discrete_map=COLORS['shifts']
        )
        fig_turno.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=300, showlegend=True)
        st.plotly_chart(fig_turno, use_container_width=True)

    # --- GRID DE SEDES (Igual al diseño de tarjetas de React) ---
    st.markdown("---")
    st.subheader("Módulos por Sede")
    
    # Creamos un grid de 3 columnas
    cols = st.columns(3)
    for i, sede in enumerate(sedes_sel):
        target_col = cols[i % 3]
        sede_data = df_filtrado[df_filtrado['Sede'] == sede]
        
        with target_col:
            st.markdown(f"""
                <div class="sede-card">
                    <h4 style="color:#1e3a8a; margin-bottom:5px;">📍 {sede}</h4>
                    <p style="font-size:12px; color:#64748b;">{len(sede_data)} Grupos programados</p>
                    <hr style="margin:10px 0;">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="font-size:14px;"><b>{sede_data['Estudiantes'].sum()}</b> Alumnos</span>
                        <span style="color:#10b981; font-weight:bold;">{((sede_data['Estudiantes'].sum() / sede_data['Cupo máximo'].sum())*100):.0f}% Ocupado</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Mini tabla de detalles dentro de la tarjeta
            with st.expander(f"Ver cursos en {sede}"):
                st.dataframe(
                    sede_data[['Asignatura', 'Turno', 'Estudiantes']], 
                    hide_index=True, 
                    use_container_width=True
                )

else:
    # Pantalla de bienvenida (Landing)
    st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: #2563eb;">Bienvenido al Panel Yataco</h1>
            <p>Sube tu archivo Excel para generar los reportes visuales automáticamente.</p>
        </div>
    """, unsafe_allow_html=True)
