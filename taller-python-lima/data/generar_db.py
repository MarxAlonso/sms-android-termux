"""
Genera `bodega.db`: una base de datos SQLite de ejemplo para el taller.

Simula una bodega peruana con 4 tablas:
  - productos       (catálogo: nombre, categoría, precio, stock)
  - clientes        (nombre, distrito de Lima, fecha de registro)
  - ventas          (cabecera: cliente, fecha, total)
  - detalle_ventas  (líneas de cada venta: producto, cantidad, subtotal)

Los datos son DETERMINÍSTICOS (usamos una semilla fija), así que todos los
asistentes obtienen exactamente la misma base de datos y las demos dan los
mismos resultados.

Uso:
    python data/generar_db.py
"""

import os
import random
import sqlite3
from datetime import date, timedelta

from faker import Faker

# --- Reproducibilidad: misma semilla -> misma base de datos para todos --------
SEMILLA = 42
random.seed(SEMILLA)
fake = Faker("es_ES")
Faker.seed(SEMILLA)

RUTA_DB = os.path.join(os.path.dirname(__file__), "bodega.db")

# --- Catálogo realista de una bodega peruana ----------------------------------
# (nombre, categoría, precio en soles)
PRODUCTOS = [
    # Bebidas
    ("Inca Kola 500ml", "Bebidas", 2.50),
    ("Inca Kola 1.5L", "Bebidas", 6.50),
    ("Coca Cola 500ml", "Bebidas", 2.50),
    ("Chicha Morada 1L", "Bebidas", 5.00),
    ("Agua San Luis 625ml", "Bebidas", 1.50),
    ("Cerveza Pilsen 650ml", "Bebidas", 6.00),
    ("Cerveza Cusqueña 620ml", "Bebidas", 7.00),
    ("Frugos Durazno 1L", "Bebidas", 4.50),
    ("Sporade 500ml", "Bebidas", 3.00),
    ("Red Bull 250ml", "Bebidas", 8.50),
    # Abarrotes
    ("Arroz Costeño 1kg", "Abarrotes", 4.20),
    ("Azúcar Rubia 1kg", "Abarrotes", 3.80),
    ("Aceite Primor 1L", "Abarrotes", 9.50),
    ("Fideos Don Vittorio 500g", "Abarrotes", 3.20),
    ("Atún Florida lata", "Abarrotes", 5.50),
    ("Leche Gloria lata", "Abarrotes", 4.00),
    ("Café Altomayo 50g", "Abarrotes", 7.50),
    ("Sal Marina 1kg", "Abarrotes", 1.80),
    ("Lenteja 500g", "Abarrotes", 4.50),
    ("Harina Blanca Flor 1kg", "Abarrotes", 4.80),
    # Snacks
    ("Galletas Soda Field", "Snacks", 1.50),
    ("Chizitos", "Snacks", 1.00),
    ("Papas Lays clásicas", "Snacks", 3.50),
    ("Chocolate Sublime", "Snacks", 2.00),
    ("Galleta Casino", "Snacks", 1.20),
    ("Doña Pepa", "Snacks", 1.50),
    ("Chifles 100g", "Snacks", 3.00),
    ("Cua Cua", "Snacks", 1.00),
    # Limpieza
    ("Detergente Bolívar 780g", "Limpieza", 8.00),
    ("Jabón Bolívar barra", "Limpieza", 2.50),
    ("Papel Higiénico Suave x4", "Limpieza", 6.50),
    ("Lejía Clorox 1L", "Limpieza", 4.00),
    ("Pasta Dental Dento", "Limpieza", 3.50),
    # Panadería / varios
    ("Pan Francés (unidad)", "Panadería", 0.30),
    ("Huevos (docena)", "Panadería", 7.00),
    ("Gas Doméstico 10kg", "Hogar", 48.00),
]

# Distritos de Lima
DISTRITOS = [
    "Miraflores", "San Juan de Lurigancho", "Comas", "Villa El Salvador",
    "San Martín de Porres", "Los Olivos", "Santiago de Surco", "Ate",
    "Chorrillos", "Breña", "Independencia", "Callao", "San Miguel",
    "La Victoria", "Surquillo",
]

# Nombres y apellidos peruanos (para que los datos "suenen" locales)
NOMBRES = [
    "José", "María", "Luis", "Rosa", "Carlos", "Carmen", "Jorge", "Ana",
    "Juan", "Lucía", "Pedro", "Sofía", "Miguel", "Elena", "Víctor", "Julia",
    "Manuel", "Patricia", "Walter", "Yolanda", "César", "Gloria", "Raúl",
    "Milagros", "Fernando", "Rocío", "Alberto", "Pilar", "Marco", "Vanessa",
]
APELLIDOS = [
    "Quispe", "Mamani", "Flores", "Huamán", "Condori", "Vargas", "Rojas",
    "Sánchez", "Torres", "Ramírez", "Chávez", "Díaz", "Castillo", "Espinoza",
    "Gutiérrez", "Vásquez", "Rivera", "Cárdenas", "Salazar", "Paredes",
]


def crear_esquema(cur: sqlite3.Cursor) -> None:
    cur.executescript(
        """
        DROP TABLE IF EXISTS detalle_ventas;
        DROP TABLE IF EXISTS ventas;
        DROP TABLE IF EXISTS clientes;
        DROP TABLE IF EXISTS productos;

        CREATE TABLE productos (
            id        INTEGER PRIMARY KEY,
            nombre    TEXT    NOT NULL,
            categoria TEXT    NOT NULL,
            precio    REAL    NOT NULL,
            stock     INTEGER NOT NULL
        );

        CREATE TABLE clientes (
            id              INTEGER PRIMARY KEY,
            nombre          TEXT NOT NULL,
            distrito        TEXT NOT NULL,
            fecha_registro  TEXT NOT NULL
        );

        CREATE TABLE ventas (
            id         INTEGER PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            fecha      TEXT    NOT NULL,
            total      REAL    NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        );

        CREATE TABLE detalle_ventas (
            id              INTEGER PRIMARY KEY,
            venta_id        INTEGER NOT NULL,
            producto_id     INTEGER NOT NULL,
            cantidad        INTEGER NOT NULL,
            precio_unitario REAL    NOT NULL,
            subtotal        REAL    NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        );
        """
    )


def poblar(cur: sqlite3.Cursor) -> None:
    hoy = date.today()

    # 1) Productos
    productos_ids = []
    for i, (nombre, categoria, precio) in enumerate(PRODUCTOS, start=1):
        stock = random.randint(10, 200)
        cur.execute(
            "INSERT INTO productos (id, nombre, categoria, precio, stock) VALUES (?, ?, ?, ?, ?)",
            (i, nombre, categoria, precio, stock),
        )
        productos_ids.append((i, precio))

    # 2) Clientes (registrados en el último año)
    NUM_CLIENTES = 90
    for i in range(1, NUM_CLIENTES + 1):
        nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
        distrito = random.choice(DISTRITOS)
        fecha_registro = fake.date_between(start_date="-1y", end_date="today")
        cur.execute(
            "INSERT INTO clientes (id, nombre, distrito, fecha_registro) VALUES (?, ?, ?, ?)",
            (i, nombre, distrito, fecha_registro.isoformat()),
        )

    # 3) Ventas + detalle (últimos 180 días)
    NUM_VENTAS = 700
    inicio = hoy - timedelta(days=180)
    venta_id = 0
    detalle_id = 0
    for _ in range(NUM_VENTAS):
        venta_id += 1
        cliente_id = random.randint(1, NUM_CLIENTES)
        dias = random.randint(0, 180)
        fecha = (inicio + timedelta(days=dias)).isoformat()

        # Cada venta tiene de 1 a 5 productos distintos
        n_items = random.randint(1, 5)
        items = random.sample(productos_ids, n_items)
        total = 0.0
        lineas = []
        for prod_id, precio in items:
            cantidad = random.randint(1, 6)
            subtotal = round(precio * cantidad, 2)
            total += subtotal
            detalle_id += 1
            lineas.append((detalle_id, venta_id, prod_id, cantidad, precio, subtotal))

        cur.execute(
            "INSERT INTO ventas (id, cliente_id, fecha, total) VALUES (?, ?, ?, ?)",
            (venta_id, cliente_id, fecha, round(total, 2)),
        )
        cur.executemany(
            "INSERT INTO detalle_ventas "
            "(id, venta_id, producto_id, cantidad, precio_unitario, subtotal) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            lineas,
        )


def main() -> None:
    if os.path.exists(RUTA_DB):
        os.remove(RUTA_DB)

    con = sqlite3.connect(RUTA_DB)
    try:
        cur = con.cursor()
        crear_esquema(cur)
        poblar(cur)
        con.commit()

        # Pequeño resumen para confirmar que todo salió bien
        for tabla in ("productos", "clientes", "ventas", "detalle_ventas"):
            n = cur.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
            print(f"  {tabla:<16} {n:>6} filas")
        print(f"\n✅ Base de datos creada en: {RUTA_DB}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
