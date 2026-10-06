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

# ==========================================
# ESTILOS CSS AVANZADOS (GAMING / RETRO PIXEL ART)
# ==========================================
st.markdown("""
<!-- Cargar Fuentes Retro de Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323&display=swap" rel="stylesheet">

<style>
    /* Fondo general estilo noche de aventura */
    .stApp {
        background: radial-gradient(circle, #2D1452 0%, #110826 100%);
        color: white;
    }

    /* Cabecera Título Arcade */
    .arcade-header {
        background: #3A1C6A;
        border: 4px solid #FFE135;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 0 20px rgba(255, 225, 53, 0.4), inset 0 0 10px rgba(0,0,0,0.8);
        margin-bottom: 25px;
    }
    
    .arcade-header h1 {
        font-family: 'Press Start 2P', cursive;
        color: #FFE135;
        font-size: 18px;
        text-shadow: 3px 3px #000, -2px -2px #FF4757;
        margin: 0;
    }

    .arcade-header p {
        font-family: 'VT323', monospace;
        color: #70A1FF;
        font-size: 20px;
        margin: 5px 0 0 0;
    }

    /* Tarjetas de Explorador (Ranking) */
    .explorer-card {
        background: rgba(47, 53, 66, 0.95);
        border: 3px solid #70A1FF;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.5);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .explorer-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(112, 161, 255, 0.6);
        border-color: #FFE135;
    }

    /* Estilo del Top 1 (Oro) */
    .top1-card {
        border: 4px solid #FFE135 !important;
        background: linear-gradient(135deg, rgba(58, 28, 106, 0.95), rgba(75, 45, 120, 0.95));
        box-shadow: 0 0 20px rgba(255, 225, 53, 0.5) !important;
    }

    /* Tipografías dentro de la tarjeta */
    .card-name {
        font-family: 'Press Start 2P', cursive;
        font-size: 13px;
        color: #FFFFFF;
        text-shadow: 2px 2px #000;
    }

    .card-stats {
        font-family: 'VT323', monospace;
        font-size: 22px;
        color: #2ED573;
    }

    .card-level {
        font-family: 'Press Start 2P', cursive;
        font-size: 11px;
        color: #FFA500;
        text-shadow: 1px 1px #000;
    }

    /* Modificación de barras de progreso de Streamlit */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #2ED573 0%, #FFE135 50%, #FF4757 100%) !important;
        box-shadow: 0 0 10px #2ED573;
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
    conn.commit()
    conn.close()

init_db()

# CABECERA VISUAL CON LOGO RETRO
st.markdown("""
<div class="arcade-header">
    <h1>🌲 LOBULNES: MISSION MATH 🌲</h1>
    <p>🐺 Hall de la Fama & Registro de Misiones 📜</p>
</div>
""", unsafe_allow_html=True)

# MENÚ LATERAL PARA ACCESO DOCENTE
st.sidebar.title("🔐 Acceso Docente")
modo_docente = st.sidebar.checkbox("Modo Administración")

CLAVE_CORRECTA = "lobulnes2026"

if modo_docente:
    clave_ingresada = st.sidebar.text_input("Ingresa la clave de profesor:", type="password")
    
    if clave_ingresada == CLAVE_CORRECTA:
        st.sidebar.success("✅ Modo Administración Activado")
        
        tab_admin1, tab_admin2, tab_admin3 = st.tabs(["⚡ Registrar Guía", "➕ Agregar Alumnos", "⚙️️ Reiniciar Juego"])
        
        # SUB-PESTAÑA 1: REGISTRAR GUÍAS
        with tab_admin1:
            st.markdown("### ⚡ Registro de Guía (+100 EXP)")
            conn = sqlite3.connect('lobulnes_web.db')
            df_alumnos = pd.read_sql_query("SELECT nfc_uid, nombre FROM estudiantes ORDER BY nombre ASC", conn)
            conn.close()

            if not df_alumnos.empty:
                opciones = {row['nombre']: row['nfc_uid'] for _, row in df_alumnos.iterrows()}
                alumno_sel = st.selectbox("Selecciona al estudiante:", list(opciones.keys()))
                uid_sel = opciones[alumno_sel]

                conn = sqlite3.connect('lobulnes_web.db')
                c = conn.cursor()
                c.execute("SELECT guias_entregadas, total_exp, nivel FROM estudiantes WHERE nfc_uid = ?", (uid_sel,))
                res = c.fetchone()
                conn.close()

                if res:
                    guias, exp, nivel = res
                    st.info(f"**{alumno_sel}:** Nivel {nivel} | {exp} EXP | {guias} Guías Entregadas")

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
                        st.success(f"🎉 ¡Guardado! {alumno_sel} tiene ahora {nueva_exp} EXP.")
                        st.rerun()
            else:
                st.warning("⚠️ No hay estudiantes registrados. Ve a la pestaña 'Agregar Alumnos' para ingresar la lista del curso.")

        # SUB-PESTAÑA 2: AGREGAR ESTUDIANTES
        with tab_admin2:
            st.markdown("### ➕ Cargar Lista de Estudiantes")
            
            st.markdown("#### Carga masiva (pegar lista del curso)")
            lista_texto = st.text_area("Pega aquí los nombres de los alumnos (un nombre por línea):", placeholder="Camila Silva\nMateo Rossi\nSofía Henríquez")
            
            if st.button("Cargar Lista Masiva"):
                nombres = [n.strip() for n in lista_texto.split("\n") if n.strip()]
                if nombres:
                    conn = sqlite3.connect('lobulnes_web.db')
                    c = conn.cursor()
                    agregados = 0
                    for idx, nom in enumerate(nombres):
                        uid_auto = f"NFC_{idx+1:03d}_{int(datetime.now().timestamp())}"
                        try:
                            c.execute("INSERT INTO estudiantes (nfc_uid, nombre) VALUES (?, ?)", (uid_auto, nom))
                            agregados += 1
                        except Exception:
                            pass
                    conn.commit()
                    conn.close()
                    st.success(f"🎉 Se agregaron {agregados} estudiantes a la base de datos.")
                    st.rerun()

        # SUB-PESTAÑA 3: REINICIAR
        with tab_admin3:
            st.markdown("### ⚙️ Reiniciar Aventura")
            if st.button("💥 BORRAR TODO Y REINICIAR (Eliminar Alumnos y Puntos)"):
                conn = sqlite3.connect('lobulnes_web.db')
                c = conn.cursor()
                c.execute("DELETE FROM estudiantes")
                conn.commit()
                conn.close()
                st.success("🔥 Base de datos borrada completamente.")
                st.rerun()

    elif clave_ingresada != "":
        st.sidebar.error("❌ Clave incorrecta")

# ==========================================
# VISTA PÚBLICA / HALL DE LA FAMA (MEJORADO)
# ==========================================
st.markdown("### 🏆 TABLA DE POSICIONES DE EXPLORADORES")

conn = sqlite3.connect('lobulnes_web.db')
df_ranking = pd.read_sql_query('''
    SELECT nombre, nivel, total_exp, guias_entregadas 
    FROM estudiantes 
    ORDER BY total_exp DESC, guias_entregadas DESC
''', conn)
conn.close()

if not df_ranking.empty:
    for idx, row in df_ranking.iterrows():
        posicion = idx + 1
        
        # Medallas e íconos especiales por posición
        if posicion == 1:
            medalla = "🥇 LÍDER"
            estilo_card = "explorer-card top1-card"
        elif posicion == 2:
            medalla = "🥈 2° LUGAR"
            estilo_card = "explorer-card"
        elif posicion == 3:
            medalla = "🥉 3° LUGAR"
            estilo_card = "explorer-card"
        else:
            medalla = f"#{posicion}"
            estilo_card = "explorer-card"

        exp_nivel = row['total_exp'] % 500
        progreso = exp_nivel / 500

        # Renderizado de Tarjeta Pixel Art
        st.markdown(f"""
        <div class="{estilo_card}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="card-name">{medalla} - {row['nombre']}</span>
                <span class="card-level">NIVEL {row['nivel']}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center;" class="card-stats">
                <span>📜 Guías: {row['guias_entregadas']}</span>
                <span>⭐ {row['total_exp']} EXP</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Barra de EXP RPG
        st.progress(progreso)
        st.caption(f"Progreso de Nivel: {exp_nivel} / 500 EXP")
        st.write("")
else:
    st.info("👋 ¡Bienvenidos! Próximamente el profesor registrará a los exploradores de la aventura.")
