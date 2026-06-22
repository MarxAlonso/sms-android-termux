import sqlite3
from datetime import datetime

DB_PATH = "renacyt.db"

def get_connection(db_path=DB_PATH):
    return sqlite3.connect(db_path)

def crear_tablas():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS investigadores (
        id INTEGER PRIMARY KEY,
        codigo_registro TEXT,
        tipo_documento TEXT,
        numero_documento TEXT,
        apellido_paterno TEXT,
        apellido_materno TEXT,
        nombres TEXT,
        email TEXT,
        orcid TEXT,
        cti_vitae TEXT,
        grupo TEXT,
        nivel TEXT,
        fecha_inicio_vigencia TEXT,
        fecha_fin_vigencia TEXT,
        institucion_principal TEXT,
        institucion_actual TEXT,
        areas_ocde TEXT,
        genero TEXT,
        condicion TEXT,
        fecha_ingreso_renacyt TEXT,
        fecha_ultima_produccion TEXT,
        calificaciones_previas TEXT,
        url_ficha TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )
    """)
    
    # Índices para acelerar las gráficas y consultas
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nivel ON investigadores(nivel)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_institucion ON investigadores(institucion_actual)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_genero ON investigadores(genero)")
    
    conn.commit()
    conn.close()

def insertar_o_actualizar(registro):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Función auxiliar para convertir timestamp de milisegundos a fecha
    def parse_ts(ts):
        if ts:
            try:
                return datetime.fromtimestamp(int(ts)/1000).strftime('%Y-%m-%d %H:%M:%S')
            except:
                return None
        return None

    url_ficha = f"https://servicio-renacyt.concytec.gob.pe/ficha-renacyt/?idInvestigador={registro.get('ctiVitae', '')}"

    datos = (
        registro.get('id'), registro.get('codigoRegistro'), registro.get('tipoDocumento'),
        registro.get('numeroDocumento'), registro.get('apellidoPaterno'), registro.get('apellidoMaterno'),
        registro.get('nombres'), registro.get('emailNotificar'), registro.get('orcid'),
        registro.get('ctiVitae'), registro.get('grupo'), registro.get('nivel'),
        parse_ts(registro.get('fechaInicioVigencia')), parse_ts(registro.get('fechaFinVigencia')),
        registro.get('institucionLaboralPrincipal'), registro.get('institucionLaboralActual'),
        registro.get('areasOcde'), registro.get('genero'), registro.get('condicion'),
        parse_ts(registro.get('fechaIngresoRenacyt')), parse_ts(registro.get('fechaUltimaProdCientifica')),
        registro.get('calificacionesPrevias'), url_ficha
    )

    cursor.execute("""
    INSERT OR REPLACE INTO investigadores (
        id, codigo_registro, tipo_documento, numero_documento, apellido_paterno, apellido_materno,
        nombres, email, orcid, cti_vitae, grupo, nivel, fecha_inicio_vigencia, fecha_fin_vigencia,
        institucion_principal, institucion_actual, areas_ocde, genero, condicion, fecha_ingreso_renacyt,
        fecha_ultima_produccion, calificaciones_previas, url_ficha
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, datos)
    
    conn.commit()
    conn.close()

def contar_registros():
    """Devuelve cuántos registros hay actualmente en la BD.
    Si la tabla no existe (primera ejecución), devuelve 0.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM investigadores")
        count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        # La tabla aún no existe, es la primera ejecución
        count = 0
    finally:
        conn.close()
    return count
