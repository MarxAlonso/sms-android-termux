import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

def get_df():
    conn = sqlite3.connect("renacyt.db")
    df = pd.read_sql_query("SELECT * FROM investigadores", conn)
    conn.close()
    return df

def exportar_csv():
    df = get_df()
    
    # 1. CSV COMPLETO con todos los campos (para tu uso local)
    ruta_completo = "Investigadores_Renacyt_Completo.csv"
    df.to_csv(ruta_completo, index=False, encoding='utf-8-sig')
    print(f"📄 CSV COMPLETO exportado: {ruta_completo} (con DNI, emails, etc.)")
    
    # 2. CSV LIMPIO sin DNI ni email (para presentar en tesis)
    df_limpio = df.drop(columns=['numero_documento', 'email'], errors='ignore')
    ruta_limpio = "Investigadores_Renacyt_Limpio.csv"
    df_limpio.to_csv(ruta_limpio, index=False, encoding='utf-8-sig')
    print(f"📄 CSV LIMPIO exportado: {ruta_limpio} (sin DNI ni emails, para tesis)")
    
    return ruta_limpio

def generar_graficas():
    df = get_df()
    
    # Configuración de estilo
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # 1. Gráfica de Barras: Distribución por Nivel RENACYT
    plt.figure(figsize=(10, 5))
    orden_niveles = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']
    conteo_nivel = df['nivel'].value_counts().reindex(orden_niveles, fill_value=0)
    conteo_nivel.plot(kind='bar', color='#2c3e50')
    plt.title('Distribución de Investigadores por Nivel RENACYT')
    plt.xlabel('Nivel')
    plt.ylabel('Cantidad de Investigadores')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('grafica_niveles.png')
    plt.close()
    print("📊 Gráfica de niveles guardada.")

    # 2. Gráfica de Pastel: Género
    plt.figure(figsize=(7, 7))
    conteo_genero = df['genero'].value_counts()
    colores = ['#3498db', '#e74c3c', '#95a5a6']
    conteo_genero.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=colores[:len(conteo_genero)])
    plt.title('Proporción por Género')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig('grafica_genero.png')
    plt.close()
    print("📊 Gráfica de género guardada.")

    # 3. Top 10 Universidades con más investigadores
    plt.figure(figsize=(12, 6))
    top_unis = pd.concat([df['institucion_principal'], df['institucion_actual']]).dropna().value_counts().head(10)
    top_unis.plot(kind='barh', color='#27ae60')
    plt.title('Top 10 Instituciones con más Investigadores RENACYT')
    plt.xlabel('Cantidad')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('grafica_universidades.png')
    plt.close()
    print("📊 Gráfica de universidades guardada.")

def generar_pdf():
    """Genera el PDF con gráficas y tabla de datos. Si no está weasyprint, solo deja las imágenes."""
    # Primero generamos las gráficas (sean o no para el PDF)
    generar_graficas()
    
    try:
        from weasyprint import HTML
        
        df = get_df()
        df_limpio = df.drop(columns=['numero_documento', 'email'], errors='ignore')
        
        # Convertimos el DataFrame a una tabla HTML (primeros 50 registros)
        tabla_html = df_limpio.head(50).to_html(classes='table table-striped', index=False)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; }}
                h1 {{ color: #2c3e50; text-align: center; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                .stats {{ font-size: 1.2em; background: #ecf0f1; padding: 15px; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.8em; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #2c3e50; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .chart-container {{ text-align: center; margin: 20px 0; page-break-inside: avoid; }}
                .chart-container img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Reporte de Investigadores RENACYT - Perú</h1>
            
            <div class="stats">
                <strong>Total de registros extraídos:</strong> {len(df)} <br>
                <strong>Registros mostrados en tabla (muestra):</strong> 50 (Ver archivo CSV para el total)
            </div>

            <div class="chart-container">
                <h2>Distribución por Nivel</h2>
                <img src="grafica_niveles.png" alt="Niveles RENACYT">
            </div>

            <div class="chart-container">
                <h2>Distribución por Género</h2>
                <img src="grafica_genero.png" alt="Género">
            </div>

            <div class="chart-container">
                <h2>Top 10 Instituciones</h2>
                <img src="grafica_universidades.png" alt="Universidades">
            </div>

            <h2>Muestra de Datos (Tabla)</h2>
            {tabla_html}
        </body>
        </html>
        """
        
        ruta_pdf = "Reporte_Renacyt_Tesis.pdf"
        HTML(string=html_content).write_pdf(ruta_pdf)
        print(f"📕 PDF exportado exitosamente: {ruta_pdf}")
        return ruta_pdf
        
    except Exception as e:
        print(f"⚠️ No se pudo generar el PDF: {e}")
        print("   (Las graficas se guardaron como imagenes y el CSV se exporto correctamente)")
        return None
