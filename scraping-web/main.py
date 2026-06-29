"""
============================================
SISTEMA DE EXTRACCIÓN RENACYT - CONCYTEC
============================================
Ejecuta todo de una vez:
  1. Scraping de la API (descarga ~14,600 registros)
  2. Exportación a CSV (sin DNI ni emails)
  3. Gráficas estadísticas (niveles, género, universidades)
  4. PDF profesional (si weasyprint está instalado)

Uso:
  python main.py

Si ya tienes la base de datos y solo quieres generar informes:
  python main.py --solo-reportes
"""

import sys
import db
import scraper_renacyt
import exporters


def main():
    solo_reportes = "--solo-reportes" in sys.argv
    rescrapear = "--rescrapear" in sys.argv
    reanudar = "--reanudar" in sys.argv

    print("=" * 50)
    print("  SISTEMA DE EXTRACCIÓN RENACYT")
    print("=" * 50)

    # Asegurar que la tabla exista antes de cualquier operacion
    db.crear_tablas()

    # --- FASE 1: SCRAPING ---
    debe_scrapear = False
    if solo_reportes:
        print("\n⏩ Modo 'solo reportes': saltando scraping...")
    elif reanudar:
        print("\n🔍 FASE 1: Reanudando scraping desde donde se quedó (conserva BD)...")
        debe_scrapear = True
    elif rescrapear:
        print("\n🔍 FASE 1: Rescrapeando desde cero (se sobreescribe la BD)...")
        debe_scrapear = True
    else:
        registros_actuales = db.contar_registros()
        if registros_actuales > 0:
            print(f"\n🔍 Ya existen {registros_actuales} registros en la BD.")
            print("   Para rescrapear desde cero:  python main.py --rescrapear")
            print("   Para reanudar scraping:      python main.py --reanudar")
            print("   Para solo generar reportes:  python main.py --solo-reportes")
        else:
            debe_scrapear = True

    if debe_scrapear:
        print("\n🔍 FASE 1: Extrayendo datos desde la API de CONCYTEC...")
        try:
            scraper_renacyt.ejecutar_scraping()
        except KeyboardInterrupt:
            print("\n⚠️  Scraping interrumpido por el usuario.")
        except Exception as e:
            print(f"\n⚠️  Error en scraping: {e}")
        
        # Pase lo que pase, revisamos cuantos datos quedaron
        parcial = db.contar_registros()
        print(f"   → {parcial} registros capturados en esta ejecucion.")

    # --- FASE 2: REPORTES ---
    print("\n📊 FASE 2: Generando reportes...")

    registros = db.contar_registros()
    if registros == 0:
        print("\n⚠️  No hay datos en la base de datos.")
        print("   Ejecuta:  python main.py")
        print("   (sin --solo-reportes) para hacer el scraping primero.\n")
        return

    print(f"   {registros} registros disponibles para exportar.\n")

    # CSV
    csv_ruta = exporters.exportar_csv()

    # Gráficas + PDF
    pdf_ruta = exporters.generar_pdf()

    # --- RESUMEN FINAL ---
    print("\n" + "=" * 50)
    print("  🎉 PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 50)
    print(f"  📁 BD:       renacyt.db ({registros} registros)")
    print(f"  📄 CSV:      {csv_ruta}")
    print(f"  📊 Gráficas: grafica_niveles.png, grafica_genero.png, grafica_universidades.png")
    if pdf_ruta:
        print(f"  📕 PDF:      {pdf_ruta}")
    print("=" * 50)


if __name__ == "__main__":
    main()
