import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de la página estilo Gamer Arcade
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

# Cabecera Principal
st.markdown('<div class="main-title">🌲 LOBULNES: HALL DE LA FAMA 🌲</div>', unsafe_allow_html=True)

# Menú lateral para acceso del Docente
st.sidebar.title("🔐 Acceso Docente")
modo_docente = st.sidebar.checkbox("Modo Administración")

CLAVE_CORRECTA = "lobulnes2026" # Puedes cambiar tu clave aquí

if modo_docente:
    clave_ingresada = st.sidebar.text_input("Ingresa la clave de profesor:", type="password")
    
    if clave_ingresada == CLAVE_CORRECTA:
        st.sidebar.success("✅ Modo Administración Activado")
        
        tab_admin1, tab_admin2, tab_admin3 = st.tabs(["⚡ Registrar Guía", "➕ Agregar Alumnos", "⚙️ Reiniciar Juego"])
        
        # --- SUB-PESTAÑA 1: REGISTRAR GUÍAS Y SUMAR PUNTOS ---
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

        # --- SUB-PESTAÑA 2: AGREGAR ESTUDIANTES AL CURSO ---
        with tab_admin2:
            st.markdown("### ➕ Cargar Lista de Estudiantes")
            
            # Opción A: Agregar individualmente
            st.markdown("#### Opción A: Agregar un alumno")
            nuevo_nombre = st.text_input("Nombre y Apellido del Estudiante:")
            nuevo_uid = st.text_input("Código de Tarjeta NFC (o deja blanco para código automático):")

            if st.button("Guardar Estudiante"):
                if nuevo_nombre.strip():
                    uid_final = nuevo_uid.strip() if nuevo_uid.strip() else f"UID_{int(datetime.now().timestamp())}"
                    
                    conn = sqlite3.connect('lobulnes_web.db')
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO estudiantes (nfc_uid, nombre) VALUES (?, ?)", (uid_final, nuevo_nombre.strip()))
                        conn.commit()
                        st.success(f"✅ Estudiante '{nuevo_nombre}' agregado con éxito.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ El código de tarjeta o ID ya existe.")
                    finally:
                        conn.close()
                else:
                    st.error("Ingresa al menos el nombre del alumno.")

            st.markdown("---")
            # Opción B: Carga Masiva pegando la lista
            st.markdown("#### Opción B: Carga masiva (pegar lista del curso)")
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

        # --- SUB-PESTAÑA 3: REINICIAR Y BORRAR DATOS ---
        with tab_admin3:
            st.markdown("### ⚙️ Reiniciar Aventura")
            st.warning("🚨 **¡Atención!** Las siguientes acciones no se pueden deshacer.")

            if st.button("🔄 Reiniciar Puntos a 0 (Conservar Lista de Alumnos)"):
                conn = sqlite3.connect('lobulnes_web.db')
                c = conn.cursor()
                c.execute("UPDATE estudiantes SET total_exp = 0, guias_entregadas = 0, nivel = 1, fecha_ultimo_escaneo = NULL")
                conn.commit()
                conn.close()
                st.success("✅ Puntos y niveles reajustados a 0 para todo el curso.")
                st.rerun()

            st.write("")
            if st.button("💥 BORRAR TODO Y REINICIAR (Eliminar Alumnos y Puntos)"):
                conn = sqlite3.connect('lobulnes_web.db')
                c = conn.cursor()
                c.execute("DELETE FROM estudiantes")
                conn.commit()
                conn.close()
                st.success("🔥 Base de datos borrada completamente. La aplicación está en blanco desde cero.")
                st.rerun()

    elif clave_ingresada != "":
        st.sidebar.error("❌ Clave incorrecta")

# ==========================================
# VISTA PÚBLICA PARA ESTUDIANTES (HALL DE LA FAMA)
# ==========================================
st.markdown("### 🏆 Tabla de Posiciones de la Aventura")

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
else:
    st.info("👋 ¡Bienvenidos a la Aventura de LoBulnes! Próximamente se publicará la lista oficial de exploradores.")
