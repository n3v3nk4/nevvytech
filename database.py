import sqlite3
import os

def crear_bd():
    # Si el archivo existe, lo borramos para forzar la creación desde cero
    if os.path.exists('taller.db'):
        os.remove('taller.db')
        print("🗑️ Base de datos anterior eliminada")

    conn = sqlite3.connect('taller.db')
    cursor = conn.cursor()
    
    # 1. TABLA CLIENTES
    cursor.execute('''
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT NOT NULL,
            email TEXT,
            rut TEXT,
            direccion TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. TABLA VENTAS (CON LAS NUEVAS COLUMNAS)
    cursor.execute('''
        CREATE TABLE ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_orden TEXT UNIQUE NOT NULL,
            cliente_id INTEGER,
            producto TEXT NOT NULL,
            monto REAL NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
            forma_pago TEXT DEFAULT 'Efectivo',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_emision DATE,
            boleta_sii TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
    ''')
    
    # 3. TABLA COTIZACIONES
    cursor.execute('''
        CREATE TABLE cotizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_cotizacion TEXT UNIQUE NOT NULL,
            cliente_id INTEGER,
            servicios TEXT NOT NULL,
            subtotal REAL,
            iva REAL,
            total REAL NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )
    ''')
    
    # 4. TABLA USUARIOS
    cursor.execute('''
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre TEXT,
            rol TEXT DEFAULT 'usuario',
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 5. Insertar usuario admin
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (email, password, nombre, rol)
        VALUES ('admin', 'nevvy2026', 'Administrador', 'admin')
    ''')
    
    conn.commit()
    conn.close()
    print('✅ Base de datos SQLite creada exitosamente con las nuevas columnas')

if __name__ == '__main__':
    crear_bd()