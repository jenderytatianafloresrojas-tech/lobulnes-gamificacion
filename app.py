import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de página estilo Gamer
st.set_page_config(
    page_title="LoBulnes: Aventura Matemática",
    page_icon="🐺",
    layout="centered"
)

# Estilo CSS Arcade Retro
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle, #2D1452 0%, #110826 100%);
        color: white;
    }
    .main-title {
        color: #FFE135;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        text-shadow: 2px 2px #000;
        padding: 10px;
        background-color: #3A1C6A;
        border: 3px solid #FFE135;
        border-radius: 10px;
    }
    .badge-exp {
        background-color: #2ED573;
        color: black;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar Base de Datos SQLite local/persistent
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
    # Cargar datos iniciales si está vacía
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

# Título y Cabecera
st.markdown('<div class="main-title">🌲 LOBULNES: MISSION MATH 🌲</div>', unsafe_allow_html=True)
st.write("")

# Menú de pestañas
tab1, tab2 = st.tabs(["🎮 Zona de Escaneo / Registro", "🏆 Hall de la Fama (Ranking)"])

with tab1:
    st.markdown("### 🐺 ¡Hola Explorador!")
    
    conn = sqlite3.connect('lobulnes_web.db')
    df_alumnos = pd.read_sql_query("SELECT nfc_uid, nombre FROM estudiantes", conn)
    conn.close()

    # Selección de alumno
    opciones = {row['nombre']: row['nfc_uid'] for _, row in df_alumnos.iterrows()}
    alumno_sel = st.selectbox("Selecciona tu nombre o pasa tu tarjeta NFC:", list(opciones.keys()))
    
    uid_sel = opciones[alumno_sel]

    # Cargar estado actual
    conn = sqlite3.connect('lobulnes_web.db')
    c = conn.cursor()
    c.execute("SELECT guias_entregadas, total_exp, nivel FROM estudiantes WHERE nfc_uid = ?", (uid_sel,))
    guias, exp, nivel = c.fetchone()
    conn.close()

    # Mostrar Barra de EXP
    exp_nivel = exp % 500
    st.progress(exp_nivel / 500)
    st.caption(f"**Nivel {nivel}** | Puntos en este nivel: {exp_nivel}/500 EXP (Total Acumulado: {exp} EXP)")

    # Botón para registrar entrega (+100 EXP)
    if st.button("⚡ Registrar Entrega de Guía (+100 EXP)", use_container_width=True):
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
        st.success(f"🎉 ¡Felicidades {alumno_sel}! Guardado +100 EXP. Total: {nueva_exp} EXP.")
        st.experimental_rerun()

with tab2:
    st.markdown("### 🏆 Ranking del Curso")
    conn = sqlite3.connect('lobulnes_web.db')
    df_ranking = pd.read_sql_query('''
        SELECT nombre AS Explorador, nivel AS Nivel, total_exp AS 'Puntos EXP', guias_entregadas AS 'Guías' 
        FROM estudiantes 
        ORDER BY total_exp DESC
    ''', conn)
    conn.close()

    # Formatear tabla
    st.dataframe(df_ranking, use_container_width=True)
