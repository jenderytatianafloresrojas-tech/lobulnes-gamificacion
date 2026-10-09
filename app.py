import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuración de página estilo Gamer Arcade
st.set_page_config(
    page_title="LoBulnes: Math Quest",
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
    .arcade-header h1 { font-family: 'Press Start 2P', cursive; color: #FFE135; font-size: 18px; margin: 0; }
    .arcade-header p { font-family: 'VT323', monospace; color: #70A1FF; font-size: 20px; margin: 5px 0 0 0; }
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

# Conexión para LEER desde Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def obtener_datos_normalizados():
    try:
        df_sheet = conn.read(ttl=0)
        # Normalizar nombres de columnas a minúsculas y sin tildes
        df_sheet.columns = [
            c.lower().replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o").replace("ú", "u").strip() 
            for c in df_sheet.columns
        ]
        return df_sheet
    except Exception:
        return pd.DataFrame(columns=["nfc_uid", "nombre", "guias_entregadas", "total_exp", "nivel", "fecha_ultimo_escaneo"])

if "estudiantes_df" not in st.session_state:
    st.session_state.estudiantes_df = obtener_datos_normalizados()

# Cabecera Visual
st.markdown("""
<div class="arcade-header">
    <h1>🎮 LOBULNES: MATH QUEST 🧮</h1>
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
        tab1, tab2 = st.tabs(["⚡ Registrar Guía (+100 EXP)", "🔄 Sincronizar desde Google Sheets"])

        with tab1:
            st.markdown("### ⚡ Registro de Guía (+100 EXP)")
            df = st.session_state.estudiantes_df
            
            if not df.empty and "nombre" in df.columns:
                alumno_sel = st.selectbox("Selecciona al estudiante:", df["nombre"].dropna().tolist())
                idx = df[df["nombre"] == alumno_sel].index[0]
                
                exp_act = int(df.loc[idx, "total_exp"]) if pd.notnull(df.loc[idx, "total_exp"]) else 0
                guias_act = int(df.loc[idx, "guias_entregadas"]) if pd.notnull(df.loc[idx, "guias_entregadas"]) else 0
                lvl_act = int(df.loc[idx, "nivel"]) if pd.notnull(df.loc[idx, "nivel"]) else 1

                st.info(f"**{alumno_sel}:** Nivel {lvl_act} | {exp_act} EXP | {guias_act} Guías Entregadas")

                if st.button("➕ Sumar +100 EXP por Guía Entregada", use_container_width=True):
                    nuevas_guias = guias_act + 1
                    nueva_exp = exp_act + 100
                    nuevo_nivel = (nueva_exp // 500) + 1

                    st.session_state.estudiantes_df.loc[idx, "guias_entregadas"] = nuevas_guias
                    st.session_state.estudiantes_df.loc[idx, "total_exp"] = nueva_exp
                    st.session_state.estudiantes_df.loc[idx, "nivel"] = nuevo_nivel
                    st.session_state.estudiantes_df.loc[idx, "fecha_ultimo_escaneo"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    st.balloons()
                    st.success(f"🎉 ¡Guardado! {alumno_sel} tiene ahora {nueva_exp} EXP.")
                    st.rerun()
            else:
                st.warning("⚠️ No se encontraron alumnos. Revisa los encabezados en tu hoja de Google Sheets.")

        with tab2:
            st.markdown("### 🔄 Sincronizar Lista")
            if st.button("Re-cargar alumnos desde Google Sheets"):
                st.session_state.estudiantes_df = obtener_datos_normalizados()
                st.success("✅ Lista de alumnos sincronizada.")
                st.rerun()

    elif clave_ingresada != "":
        st.sidebar.error("❌ Clave incorrecta")

# VISTA PÚBLICA / HALL DE LA FAMA
st.markdown("### 🏆 TABLA DE POSICIONES DE EXPLORADORES")

df_pub = st.session_state.estudiantes_df

if not df_pub.empty and "nombre" in df_pub.columns:
    df_sorted = df_pub.sort_values(by=["total_exp", "guias_entregadas"], ascending=[False, False]).reset_index(drop=True)
    for idx, row in df_sorted.iterrows():
        pos = idx + 1
        medalla = "🥇 LÍDER" if pos == 1 else ("🥈 2° LUGAR" if pos == 2 else ("🥉 3° LUGAR" if pos == 3 else f"#{pos}"))
        card_class = "explorer-card top1-card" if pos == 1 else "explorer-card"
        
        exp_act = int(row["total_exp"]) if pd.notnull(row["total_exp"]) else 0
        exp_nivel = exp_act % 500
        lvl = int(row["nivel"]) if pd.notnull(row["nivel"]) else 1
        guias = int(row["guias_entregadas"]) if pd.notnull(row["guias_entregadas"]) else 0

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
    st.info("👋 ¡Bienvenidos! Agrega alumnos en tu archivo de Google Sheets para que aparezcan en el ranking.")
