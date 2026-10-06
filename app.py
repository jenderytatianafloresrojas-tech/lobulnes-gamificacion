import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de página estilo Gamer Arcade
st.set_page_config(
    page_title="LoBulnes: Hall de la Fama",
    page_icon="🐺",
    layout="centered"
)

# Estilos CSS Retro Pixel Art
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle, #2D1452 0%, #110826 100%);
        color: white;
        font-family: 'Courier New', Courier, monospace;
    }
    .main-title {
        color: #FFE135;
        text-align: center;
        font-size: 26px;
        font-weight: bold;
        text-shadow: 2px 2px #000;
        padding: 12px;
        background-color: #3A1C6A;
        border: 3px solid #FFE135;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .card-ranking {
        background-color: rgba(47, 53, 66, 0.9);
        border: 2px solid #70A1FF;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Función para inicializar la base de datos
def init_db():
    conn = sqlite3.connect('lobulnes_web.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            nfc_uid TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            guias_entregadas INTEGER DEFAULT 0,
            total_exp INTEGER DEFAULT 0,
            nivel INTEGER DEFAULT 1,
            fecha_ultimo_escaneo TEXT
        )
    ''')
    c.execute("SELECT COUNT(*) FROM estudiantes")
    if c.fetchone()[0] == 0:
        alumnos_demo = [
            ("04A23F8B", "Camila Silva", 2, 200, 1, str(datetime.now())),
            ("04F98E12", "Mateo Rossi", 4, 400, 1, str(datetime.now())),
            ("04C72B90", "Sofía Henríquez", 8, 800, 2, str(datetime.now()))
        ]
        c.executemany("INSERT INTO estudiantes VALUES (?, ?, ?, ?, ?, ?)", alumnos_demo)
        conn.commit()
    conn.close()

init_db()

# Cabecera Principal
st.markdown('<div class="main-title">🌲 LOBULNES: HALL DE LA FAMA 🌲</div>', unsafe_allow_html=True)

# Menú lateral para acceso del Docente
st.sidebar.title("🔐 Acceso Docente")
modo_docente = st.sidebar.checkbox("Modo Administración / Registro")

if modo_docente:
    clave_ingresada = st.sidebar.text_input("Ingresa la clave de profesor:", type="password")
    
    # Define aquí tu contraseña de profesor (ejemplo: "lobulnes2026")
    CLAVE_CORRECTA = "lobulnes2026"
    
    if clave_ingresada == CLAVE_CORRECTA:
        st.sidebar.success("✅ Modo Administración Activado")
        st.markdown("### ⚡ Panel de Registro de Guías (Solo Profesor)")
        
        conn = sqlite3.connect('lobulnes_web.db')
        df_alumnos = pd.read_sql_query("SELECT nfc_uid, nombre FROM estudiantes", conn)
        conn.close()

        opciones = {row['nombre']: row['nfc_uid'] for _, row in df_alumnos.iterrows()}
        alumno_sel = st.selectbox("Selecciona al estudiante que entregó su guía:", list(opciones.keys()))
        uid_sel = opciones[alumno_sel]

        conn = sqlite3.connect('lobulnes_web.db')
        c = conn.cursor()
        c.execute("SELECT guias_entregadas, total_exp, nivel FROM estudiantes WHERE nfc_uid = ?", (uid_sel,))
        guias, exp, nivel = c.fetchone()
        conn.close()

        st.info(f"**Estado de {alumno_sel}:** Nivel {nivel} | {exp} EXP Acumulada | {guias} Guías Entregadas")

        if st.button("➕ Sumar +100 EXP por Guía Entregada", use_container_width=True):
            nuevas_guias = guias + 1
            nueva_exp = exp + 100
            nuevo_nivel = (nueva_exp // 500) + 1
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            conn = sqlite3.connect('lobulnes_web.db')
            c = conn.cursor()
            c.execute('''
                UPDATE estudiantes 
                SET guias_entregadas = ?, total_exp = ?, nivel = ?, fecha_ultimo_escaneo = ?
                WHERE nfc_uid = ?
            ''', (nuevas_guias, nueva_exp, nuevo_nivel, ahora, uid_sel))
            conn.commit()
            conn.close()

            st.balloons()
            st.success(f"🎉 ¡Registrado con éxito! {alumno_sel} ahora tiene {nueva_exp} EXP.")
            st.rerun()
    elif clave_ingresada != "":
        st.sidebar.error("❌ Clave incorrecta")

# VISTA PÚBLICA PARA ESTUDIANTES (SOLO LECTURA)
st.markdown("### 🏆 Tabla de Posiciones de la Aventura")
st.caption("Consulte sus puntos acumulados y compare su progreso con sus compañeros.")

conn = sqlite3.connect('lobulnes_web.db')
df_ranking = pd.read_sql_query('''
    SELECT nombre, nivel, total_exp, guias_entregadas 
    FROM estudiantes 
    ORDER BY total_exp DESC, guias_entregadas DESC
''', conn)
conn.close()

# Renderizado visual del Ranking para Estudiantes
for idx, row in df_ranking.iterrows():
    posicion = idx + 1
    if posicion == 1:
        medalla = "🥇 "
    elif posicion == 2:
        medalla = "🥈 "
    elif posicion == 3:
        medalla = "🥉 "
    else:
        medalla = f"#{posicion} "

    exp_nivel = row['total_exp'] % 500
    progreso = exp_nivel / 500

    with st.container():
        col1, col2, col3 = st.columns([1, 3, 2])
        with col1:
            st.markdown(f"### {medalla}")
        with col2:
            st.markdown(f"**{row['nombre']}**")
            st.caption(f"📜 Guías completadas: {row['guias_entregadas']}")
        with col3:
            st.markdown(f"**Nivel {row['nivel']}** ({row['total_exp']} EXP)")
        
        st.progress(progreso)
        st.markdown("---")
