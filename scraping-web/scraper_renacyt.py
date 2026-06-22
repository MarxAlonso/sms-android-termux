import requests
import time
import db

TIMEOUT = 360  # Timeout de 6 minutos porque el servidor del Estado es extremadamente lento
MAX_REINTENTOS = 6

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
            print(f"   Intento {intento+1}/{MAX_REINTENTOS} fallo: {e}")
            time.sleep(3)
    return 0

def ejecutar_scraping():
    db.crear_tablas()

    print("Consultando total de registros...")
    total = obtener_total_registros()
    if total == 0:
        print("Error: No se pudo obtener el total de registros. Revisa la conexion.")
        return

    print(f"Total de investigadores a extraer: {total}")

    limit = 100
    paginas_totales = (total // limit) + (1 if total % limit != 0 else 0)

    for pagina in range(1, paginas_totales + 1):
        # Permitir interrupcion limpia con Ctrl+C
        try:
            url = f"https://renacyt.concytec.gob.pe/renacyt-backend/actoRegistral/obtenerActosRegistralesActivos/reglamento/2021/pagina/{pagina}/numeroRegistros/{limit}"

            # Intentar hasta MAX_REINTENTOS por pagina
            registros = None
            for intento in range(MAX_REINTENTOS):
                try:
                    response = requests.post(url, headers=get_headers(), json=[], timeout=TIMEOUT)
                    response.raise_for_status()
                    datos = response.json()
                    registros = datos.get('data', [])
                    break  # Salir del bucle de reintentos si funciona
                except Exception as e:
                    if intento < MAX_REINTENTOS - 1:
                        espera = 15  # esperar 15s entre reintentos
                        print(f"   Reintentando pagina {pagina} ({intento+2}/{MAX_REINTENTOS}) — esperando {espera}s...")
                        time.sleep(espera)
                    else:
                        print(f"   ❌ Pagina {pagina} fallo tras {MAX_REINTENTOS} intentos: {e}")
                        print(f"     → Pasando a la pagina {pagina+1}...")

            if registros is None:
                # Fueron todos los reintentos, saltamos a la siguiente pagina
                continue
            elif len(registros) == 0:
                # API devolvio lista vacia, ya no hay mas datos
                print(f"Pagina {pagina} vacia. Scraping finalizado.")
                break

            for reg in registros:
                db.insertar_o_actualizar(reg)

            # Barra de progreso compacta
            total_parcial = pagina * limit
            if total_parcial > total:
                total_parcial = total
            print(f"  Pagina {pagina}/{paginas_totales} ({len(registros)} registros) — {total_parcial}/{total}")

            # Pausa respetuosa: esperar 30s entre paginas para no saturar el servidor del Estado
            print(f"     ⏳ Esperando 30 segundos antes de la siguiente pagina...")
            time.sleep(30)

        except KeyboardInterrupt:
            print("\n  Scraping interrumpido por el usuario. Los datos obtenidos hasta ahora se conservan.")
            return
        except Exception as e:
            print(f"  ⚠️ Error inesperado en pagina {pagina}: {e}. Saltando a la siguiente pagina...")
            continue  # Intentar con la siguiente pagina

    print("Scraping completado.")
