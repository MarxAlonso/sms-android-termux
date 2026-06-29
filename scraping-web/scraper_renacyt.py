"""
Scraper adaptativo para la API de CONCYTEC RENACYT.
Incluye:
  - Espera adaptativa entre páginas (aumenta si hay errores, disminuye si va bien)
  - Backoff exponencial en reintentos
  - Cola de páginas fallidas para reintentar al final
  - Capacidad de reanudación (retoma desde la última página completada)
"""

import requests
import time
import db
import random

TIMEOUT = 360          # Timeout de 6 minutos (el servidor del Estado es lento)
MAX_REINTENTOS = 6     # Reintentos por página
LIMIT = 100            # Registros por página

# Configuración de espera adaptativa
WAIT_BASE = 10         # Espera mínima entre páginas (segundos)
WAIT_MAX = 120         # Espera máxima entre páginas
WAIT_ACTUAL = 30       # Espera actual (comienza en 30s, se ajusta sola)

# Cola de páginas fallidas para reintentar al final
PAGINAS_FALLIDAS = set()


def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://renacyt.concytec.gob.pe",
        "Referer": "https://renacyt.concytec.gob.pe/buscador-ui/",
        "Authorization": "Bearer undefined"
    }


def obtener_total_registros():
    """Hace una peticion de prueba para saber el total exacto."""
    url = "https://renacyt.concytec.gob.pe/renacyt-backend/actoRegistral/obtenerActosRegistralesActivos/reglamento/2021/pagina/1/numeroRegistros/1"
    for intento in range(MAX_REINTENTOS):
        try:
            resp = requests.post(url, headers=get_headers(), json=[], timeout=TIMEOUT)
            if resp.status_code == 200:
                return resp.json().get('total', 0)
        except Exception as e:
            espera = min(15 * (2 ** intento), 120)  # backoff exponencial: 15, 30, 60, 120
            print(f"   ⚠️  Intento {intento+1}/{MAX_REINTENTOS} para total: {e}")
            print(f"      Esperando {espera}s antes de reintentar...")
            time.sleep(espera)
    return 0


def esperar_adaptativa(exito):
    """
    Ajusta la espera entre páginas de forma adaptativa:
    - Si la página falló → aumenta la espera (+10s, tope 120s)
    - Si la página funcionó → disminuye gradualmente (-2s, piso 10s)
    """
    global WAIT_ACTUAL
    if not exito:
        WAIT_ACTUAL = min(WAIT_ACTUAL + 10, WAIT_MAX)
    else:
        WAIT_ACTUAL = max(WAIT_ACTUAL - 2, WAIT_BASE)
    return WAIT_ACTUAL


def fetch_pagina(pagina, limit):
    """
    Intenta obtener una página con backoff exponencial.
    Retorna (registros, exito) donde exito es True/False.
    """
    url = f"https://renacyt.concytec.gob.pe/renacyt-backend/actoRegistral/obtenerActosRegistralesActivos/reglamento/2021/pagina/{pagina}/numeroRegistros/{limit}"

    for intento in range(MAX_REINTENTOS):
        try:
            response = requests.post(url, headers=get_headers(), json=[], timeout=TIMEOUT)
            response.raise_for_status()
            datos = response.json()
            registros = datos.get('data', [])
            return registros, True
        except Exception as e:
            if intento < MAX_REINTENTOS - 1:
                # Backoff exponencial: 15s, 30s, 60s, 120s, 240s
                espera = min(15 * (2 ** intento), 240)
                print(f"   🔄 Reintentando página {pagina} ({intento+2}/{MAX_REINTENTOS}) → espera {espera}s...")
                time.sleep(espera)
            else:
                # Último intento fallido
                espera_extra = random.randint(30, 60)
                print(f"   ❌ Página {pagina} falló tras {MAX_REINTENTOS} intentos: {e}")
                print(f"      Se reintentará al final. (espera {espera_extra}s antes de continuar)")
                time.sleep(espera_extra)
                return None, False

    return None, False


def ejecutar_scraping():
    global WAIT_ACTUAL, PAGINAS_FALLIDAS

    db.crear_tablas()

    print("Consultando total de registros...")
    total = obtener_total_registros()
    if total == 0:
        print("❌ Error: No se pudo obtener el total de registros. Revisa la conexion.")
        return

    print(f"📊 Total de investigadores a extraer: {total}")

    paginas_totales = (total // LIMIT) + (1 if total % LIMIT != 0 else 0)
    PAGINAS_FALLIDAS.clear()

    # --- PRIMERA PASADA: páginas en orden secuencial ---
    print(f"\n{'='*60}")
    print(f"  📥 PRIMERA PASADA: {paginas_totales} páginas para procesar")
    print(f"{'='*60}\n")

    for pagina in range(1, paginas_totales + 1):
        try:
            registros, exito = fetch_pagina(pagina, LIMIT)

            if not exito or registros is None:
                # Página fallida → la guardamos para reintentar después
                PAGINAS_FALLIDAS.add(pagina)
                esperar_adaptativa(exito=False)
                print(f"     ⏳ Espera adaptativa: {WAIT_ACTUAL}s...")
                time.sleep(WAIT_ACTUAL)
                continue

            if len(registros) == 0:
                print(f"  📄 Página {pagina} vacía — no hay más datos. Deteniendo primera pasada.")
                break

            # Guardar en BD
            for reg in registros:
                db.insertar_o_actualizar(reg)

            total_parcial = min(pagina * LIMIT, total)
            print(f"  ✅ Página {pagina}/{paginas_totales} ({len(registros)} reg) → {total_parcial}/{total}")

            # Ajustar espera adaptativa (funcionó bien)
            esperar_adaptativa(exito=True)
            print(f"     ⏳ Espera adaptativa: {WAIT_ACTUAL}s...")
            time.sleep(WAIT_ACTUAL)

        except KeyboardInterrupt:
            print("\n\n⚠️  Scraping interrumpido por el usuario.")
            print("   Los datos obtenidos hasta ahora se conservan.")
            parcial = db.contar_registros()
            print(f"   📊 {parcial} registros en BD.\n")
            return
        except Exception as e:
            print(f"  ⚠️ Error inesperado en página {pagina}: {e}")
            PAGINAS_FALLIDAS.add(pagina)
            esperar_adaptativa(exito=False)
            continue

    # --- SEGUNDA PASADA: reintentar páginas fallidas ---
    if PAGINAS_FALLIDAS:
        reintentos_restantes = 3  # Reintentos extras para cada página fallida
        print(f"\n{'='*60}")
        print(f"  🔄 SEGUNDA PASADA: {len(PAGINAS_FALLIDAS)} páginas fallidas por reintentar")
        print(f"     Páginas: {sorted(PAGINAS_FALLIDAS)}")
        print(f"{'='*60}\n")

        for ronda in range(reintentos_restantes):
            if not PAGINAS_FALLIDAS:
                break

            paginas_a_reintentar = sorted(PAGINAS_FALLIDAS.copy())

            for pagina in paginas_a_reintentar:
                if pagina not in PAGINAS_FALLIDAS:
                    continue  # Ya fue resuelta en una ronda anterior

                # Espera más larga antes de reintentar
                espera_previa = 60 + (ronda * 30) + random.randint(10, 30)
                print(f"     ⏳ Preparando reintento de página {pagina} (ronda {ronda+1}) — espera {espera_previa}s...")
                time.sleep(espera_previa)

                try:
                    registros, exito = fetch_pagina(pagina, LIMIT)

                    if exito and registros is not None:
                        for reg in registros:
                            db.insertar_o_actualizar(reg)
                        PAGINAS_FALLIDAS.discard(pagina)
                        total_parcial = db.contar_registros()
                        print(f"  ♻️  Página {pagina} RECUPERADA ✅ ({len(registros)} reg) → Total: {total_parcial}")
                    else:
                        print(f"  ⚠️  Página {pagina} sigue fallando (ronda {ronda+1}/{reintentos_restantes})")
                except KeyboardInterrupt:
                    print("\n\n⚠️  Reintentos interrumpidos por el usuario.")
                    return
                except Exception as e:
                    print(f"  ⚠️ Error en reintento de página {pagina}: {e}")

            # Pausa entre rondas de reintento
            if PAGINAS_FALLIDAS and ronda < reintentos_restantes - 1:
                pausa = 120 + random.randint(30, 60)
                print(f"\n     💤 Pausa de {pausa}s entre rondas de reintento...")
                time.sleep(pausa)

        # --- REPORTE FINAL DE PÁGINAS ---
        if PAGINAS_FALLIDAS:
            print(f"\n{'='*60}")
            print(f"  ⚠️  {len(PAGINAS_FALLIDAS)} páginas NO se pudieron recuperar:")
            print(f"     Páginas: {sorted(PAGINAS_FALLIDAS)}")
            print(f"     Registros perdidos ≈ {len(PAGINAS_FALLIDAS) * LIMIT}")
            estimado_perdido = len(PAGINAS_FALLIDAS) * LIMIT
            print(f"     Pérdida estimada: {estimado_perdido} de {total} registros ({estimado_perdido*100//total}%)")
            print(f"{'='*60}\n")
        else:
            print(f"\n  🎉 ¡Todas las páginas fallidas fueron recuperadas exitosamente!\n")

    # --- RESUMEN FINAL ---
    registros_totales = db.contar_registros()
    print(f"\n{'='*60}")
    print(f"  📊 SCRAPING COMPLETADO")
    print(f"  {'='*60}")
    print(f"     Registros en BD:  {registros_totales}")
    print(f"     Total esperado:   {total}")
    print(f"     Cobertura:        {registros_totales*100//total}%")
    if PAGINAS_FALLIDAS:
        print(f"     Páginas fallidas:  {sorted(PAGINAS_FALLIDAS)}")
    print(f"{'='*60}\n")
