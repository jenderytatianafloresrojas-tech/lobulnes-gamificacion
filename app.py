import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuración de página estilo Gamer Arcade
st.set_page_config(
    page_title="Exploradores de conocimientos secretos",
    page_icon="🎮",
    layout="centered"
)

# Estilos CSS Retro Pixel Art
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap" rel="stylesheet">
<style>
    .stApp { background: radial-gradient(circle, #2D1452 0%, #110826 100%); color: white; }
    .arcade-header {
        background: #3A1C6A; border: 4px solid #FFE135; border-radius: 12px;
        padding: 15px; text-align: center; box-shadow: 0 0 20px rgba(255, 225, 53, 0.4);
        margin-bottom: 25px;
    }
    .arcade-header h1 { font-family: 'Press Start 2P', cursive; color: #FFE135; font-size: 16px; margin: 0; line-height: 1.4; }
    .arcade-header p { font-family: 'VT323', monospace; color: #70A1FF; font-size: 20px; margin: 5px 0 0 0; }
    
    /* Panel de Misión Actual / Próxima Misión */
    .mission-card {
        background: rgba(26, 18, 52, 0.95);
        border: 3px double #FFE135;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 25px;
        box-shadow: 0 0 15px rgba(255, 225, 53, 0.2);
    }
    .mission-title {
        font-family: 'Press Start 2P', cursive;
        font-size: 13px;
        color: #FFE135;
        margin-bottom: 12px;
        text-shadow: 2px 2px #000;
    }
    .mission-item {
        font-family: 'VT323', monospace;
        font-size: 20px;
        margin-bottom: 8px;
    }
    .mission-date {
        color: #FF4757;
        font-weight: bold;
    }
    
    .explorer-card {
        background: rgba(47, 53, 66, 0.95); border: 3px solid #70A1FF; border-radius: 12px;
        padding: 15px; margin-bottom: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.5);
    }
    .top1-card { border: 4px solid #FFE135 !important; background: linear-gradient(135deg, rgba(58, 28, 106, 0.95), rgba(75, 45, 120, 0.95)); }
    .card-name { font-family: 'Press Start 2P', cursive; font-size: 13px; color: #FFFFFF; }
    .card-stats { font-family: 'VT323', monospace; font-size: 22px; color: #2ED573; }
    .card-level { font-family: 'Press Start 2P', cursive; font-size: 11px; color: #FFA500; }
    .stProgress > div > div > div > div { background-image: linear-gradient(90deg, #2ED573 0%, #FFE135 50%, #FF4757 100%) !important; }
</style>
""", unsafe_allow_html=True)

# URL directa de tu planilla en Google Sheets
URL_GSHEETS = "https://docs.google.com/spreadsheets/d/1A5MdJZjYG8tchBIBisyW-UdgpQjWic3nLGZ9fO7cj-c/edit"

# Conexión para LEER desde Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos_normalizados():
    try:
        df_sheet = conn.read(spreadsheet=URL_GSHEETS, ttl=0)
        columnas_limpias = []
        for col in df_sheet.columns:
            col_str = str(col).lower().strip()
            col_str = col_str.replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o").replace("ú", "u")
            columnas_limpias.append(col_str)
        df_sheet.columns = columnas_limpias
        return df_sheet
    except Exception as e:
        st.error(f"Error al conectar con la hoja: {e}")
        return pd.DataFrame()

df_estudiantes = obtener_datos_normalizados()

# Variables para la información de las Misiones
if "guia_actual" not in st.session_state:
    st.session_state.guia_actual = "Guía N°3: Fracciones y Decimales en la Recta"
if "fecha_limite" not in st.session_state:
    st.session_state.fecha_limite = "Viernes 16 de Octubre - 14:00 hrs"
if "proxima_guia" not in st.session_state:
    st.session_state.proxima_guia = "Guía N°4: Razones y Proporciones"

# Cabecera Visual
st.markdown("""
<div class="arcade-header">
    <h1>🎮 EXPLORADORES DE CONOCIMIENTOS SECRETOS 🧮</h1>
    <p>🐺 Hall de la Fama & Registro de Misiones 🏆</p>
</div>
""", unsafe_allow_html=True)

# Menú lateral para acceso del Docente
st.sidebar.title("🔐 Acceso Docente")
modo_docente = st.sidebar.checkbox("Modo Administración")
CLAVE_CORRECTA = "lobulnes2026"

if modo_docente:
    clave_ingresada = st.sidebar.text_input("Ingresa la clave de profesor:", type="password")
    if clave_ingresada == CLAVE_CORRECTA:
        st.sidebar.success("✅ Modo Administración Activado")
        tab1, tab2, tab3 = st.tabs(["⚡ Registrar Guía (+100 EXP)", "📜 Configurar Misiones", "🔄 Sincronizar Lista"])

        with tab1:
            st.markdown("### ⚡ Registro de Guía (+100 EXP)")
            if not df_estudiantes.empty and "nombre" in df_estudiantes.columns:
                lista_nombres = df_estudiantes["nombre"].dropna().tolist()
                alumno_sel = st.selectbox("Selecciona al estudiante:", lista_nombres)
                idx = df_estudiantes[df_estudiantes["nombre"] == alumno_sel].index[0]

                col_exp = "total_exp" if "total_exp" in df_estudiantes.columns else df_estudiantes.columns[3]
                col_guias = "guias_entregadas" if "guias_entregadas" in df_estudiantes.columns else df_estudiantes.columns[2]
                col_nivel = "nivel" if "nivel" in df_estudiantes.columns else df_estudiantes.columns[4]

                exp_act = int(df_estudiantes.loc[idx, col_exp]) if pd.notnull(df_estudiantes.loc[idx, col_exp]) else 0
                guias_act = int(df_estudiantes.loc[idx, col_guias]) if pd.notnull(df_estudiantes.loc[idx, col_guias]) else 0
                lvl_act = int(df_estudiantes.loc[idx, col_nivel]) if pd.notnull(df_estudiantes.loc[idx, col_nivel]) else 1

                st.info(f"**{alumno_sel}:** Nivel {lvl_act} | {exp_act} EXP | {guias_act} Guías Entregadas")

                if st.button("➕ Sumar +100 EXP por Guía Entregada", use_container_width=True):
                    df_estudiantes.loc[idx, col_guias] = guias_act + 1
                    df_estudiantes.loc[idx, col_exp] = exp_act + 100
                    df_estudiantes.loc[idx, col_nivel] = ((exp_act + 100) // 500) + 1

                    st.balloons()
                    st.success(f"🎉 ¡Guardado! {alumno_sel} tiene ahora {exp_act + 100} EXP.")
                    st.rerun()
            else:
                st.warning("⚠️ No se pudieron cargar los nombres desde Google Sheets.")

        with tab2:
            st.markdown("### 📜 Actualizar Información de Misiones")
            nueva_guia = st.text_input("Guía / Misión Actual:", value=st.session_state.guia_actual)
            nueva_fecha = st.text_input("Fecha Límite de Entrega (Máx EXP):", value=st.session_state.fecha_limite)
            nueva_proxima = st.text_input("Próxima Guía a Trabajar:", value=st.session_state.proxima_guia)

            if st.button("💾 Guardar Cambios de Misión"):
                st.session_state.guia_actual = nueva_guia
                st.session_state.fecha_limite = nueva_fecha
                st.session_state.proxima_guia = nueva_proxima
                st.success("✅ ¡Información de misiones actualizada con éxito!")
                st.rerun()

        with tab3:
            st.markdown("### 🔄 Sincronizar Lista")
            if st.button("Re-cargar alumnos desde Google Sheets"):
                st.cache_data.clear()
                st.rerun()

    elif clave_ingresada != "":
        st.sidebar.error("❌ Clave incorrecta")

# SECCIÓN DE INFORMACIÓN DE MISIONES PARA JUGADORES
st.markdown(f"""
<div class="mission-card">
    <div class="mission-title">⚔️ MISIONES MATEMÁTICAS Y GUÍAS ⚔️</div>
    <div class="mission-item">📜 <b>Misión Actual:</b> <span style="color: #70A1FF;">{st.session_state.guia_actual}</span></div>
    <div class="mission-item">⏳ <b>Fecha Límite (+100 EXP):</b> <span class="mission-date">{st.session_state.fecha_limite}</span></div>
    <div class="mission-item">🔮 <b>Próxima Misión:</b> <span style="color: #2ED573;">{st.session_state.proxima_guia}</span></div>
</div>
""", unsafe_allow_html=True)

# VISTA PÚBLICA / HALL DE LA FAMA
st.markdown("### 🏆 TABLA DE POSICIONES DE EXPLORADORES")

if not df_estudiantes.empty and "nombre" in df_estudiantes.columns:
    col_exp = "total_exp" if "total_exp" in df_estudiantes.columns else df_estudiantes.columns[3]
    col_guias = "guias_entregadas" if "guias_entregadas" in df_estudiantes.columns else df_estudiantes.columns[2]
    col_nivel = "nivel" if "nivel" in df_estudiantes.columns else df_estudiantes.columns[4]

    df_estudiantes[col_exp] = pd.to_numeric(df_estudiantes[col_exp], errors='coerce').fillna(0)
    df_estudiantes[col_guias] = pd.to_numeric(df_estudiantes[col_guias], errors='coerce').fillna(0)

    df_sorted = df_estudiantes.sort_values(by=[col_exp, col_guias], ascending=[False, False]).reset_index(drop=True)

    for idx, row in df_sorted.iterrows():
        pos = idx + 1
        medalla = "🥇 LÍDER" if pos == 1 else ("🥈 2° LUGAR" if pos == 2 else ("🥉 3° LUGAR" if pos == 3 else f"#{pos}"))
        card_class = "explorer-card top1-card" if pos == 1 else "explorer-card"

        exp_act = int(row[col_exp])
        exp_nivel = exp_act % 500
        lvl = int(row[col_nivel]) if pd.notnull(row[col_nivel]) else 1
        guias = int(row[col_guias])

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between;">
                <span class="card-name">{medalla} - {row['nombre']}</span>
                <span class="card-level">NIVEL {lvl}</span>
            </div>
            <div style="display: flex; justify-content: space-between;" class="card-stats">
                <span>📜 Guías: {guias}</span>
                <span>⭐ {exp_act} EXP</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(exp_nivel / 500)
        st.caption(f"Progreso de Nivel: {exp_nivel} / 500 EXP")
        st.write("")
else:
    st.info("👋 ¡Bienvenidos! Verifica la conexión a tu hoja de cálculo para cargar los estudiantes.")
