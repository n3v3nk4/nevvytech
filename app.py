from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os
import hashlib

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ============================================
# INICIALIZAR BASE DE DATOS
# ============================================
def init_db():
    db_path = 'taller.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear todas las tablas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre TEXT NOT NULL,
            rol TEXT DEFAULT 'usuario'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            telefono TEXT,
            email TEXT,
            rut TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_orden TEXT UNIQUE NOT NULL,
            cliente_id INTEGER,
            producto TEXT NOT NULL,
            monto REAL NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
            forma_pago TEXT DEFAULT 'Efectivo',
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cotizaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_cotizacion TEXT UNIQUE NOT NULL,
            cliente_id INTEGER,
            servicios TEXT,
            total REAL NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
            fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    # Crear usuario admin (con email 'admin' para login simple)
    cursor.execute('''
        INSERT OR REPLACE INTO usuarios (id, email, password, nombre, rol)
        VALUES (1, 'admin', 'nevvy2026', 'Administrador', 'admin')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada con usuario admin")

# ============================================
# CONEXIÓN A SQLITE
# ============================================
def get_db():
    conn = sqlite3.connect('taller.db')
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# RUTAS
# ============================================
@app.route('/')
def inicio():
    return '🚀 NEVVY TECH API funcionando correctamente'

# ============================================
# 🔐 LOGIN - VERSIÓN MEJORADA
# ============================================
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        print(f"🔍 Intento de login: {email}")
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Buscar por email O nombre (para permitir 'admin' o 'admin@nevvytech.cl')
        cursor.execute('''
            SELECT id, email, nombre, password, rol 
            FROM usuarios 
            WHERE email = ? OR nombre = ?
        ''', (email, email))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            print(f"❌ Usuario no encontrado: {email}")
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 401
        
        # Verificar contraseña
        if user['password'] != password:
            print(f"❌ Contraseña incorrecta para: {email}")
            return jsonify({
                'success': False,
                'message': 'Contraseña incorrecta'
            }), 401
        
        print(f"✅ Login exitoso: {email}")
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'nombre': user['nombre'],
                'rol': user['rol']
            }
        })
        
    except Exception as e:
        print(f"❌ ERROR en login: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

# ============================================
# RUTAS DE DEBUG
# ============================================
@app.route('/crear-admin')
def crear_admin():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO usuarios (id, email, password, nombre, rol)
            VALUES (1, 'admin', 'nevvy2026', 'Administrador', 'admin')
        ''')
        conn.commit()
        conn.close()
        return '✅ Usuario admin creado correctamente<br>👤 Usuario: admin<br>🔑 Contraseña: nevvy2026'
    except Exception as e:
        return f'❌ Error: {e}', 500

@app.route('/ver-usuarios')
def ver_usuarios():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, nombre, rol FROM usuarios")
        usuarios = cursor.fetchall()
        conn.close()
        return jsonify({
            'total': len(usuarios),
            'usuarios': [dict(u) for u in usuarios]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# 🧹 RUTA DE LIMPIEZA (NUEVO)
# ============================================
@app.route('/limpiar-datos')
def limpiar_datos():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Eliminar todos los datos de las tablas
        cursor.execute("DELETE FROM ventas")
        cursor.execute("DELETE FROM cotizaciones")
        cursor.execute("DELETE FROM clientes")
        
        # Reiniciar los contadores de ID
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='ventas'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='cotizaciones'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='clientes'")
        
        conn.commit()
        conn.close()
        return '''
        <html>
            <head>
                <title>Datos limpiados</title>
                <style>
                    body { background: #0a1628; color: white; font-family: Arial; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
                    .card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 40px; max-width: 500px; text-align: center; }
                    h1 { color: #34d399; }
                    p { color: #94a3b8; }
                    a { color: #60a5fa; text-decoration: none; border: 1px solid #60a5fa; padding: 8px 16px; border-radius: 8px; display: inline-block; margin: 5px; }
                    a:hover { background: rgba(96,165,250,0.1); }
                </style>
            </head>
            <body>
                <div class="card">
                    <h1>✅ Datos eliminados</h1>
                    <p>Todos los datos de prueba han sido eliminados correctamente.</p>
                    <p>📊 Las tablas están vacías.</p>
                    <br>
                    <a href="/api/ventas">Ver ventas</a>
                    <a href="/api/clientes">Ver clientes</a>
                    <a href="/admin/dashboard.html">Dashboard</a>
                </div>
            </body>
        </html>
        '''
    except Exception as e:
        return f'❌ Error: {e}', 500

# ============================================
# API REST - VENTAS
# ============================================
@app.route('/api/ventas', methods=['GET'])
def obtener_ventas():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, c.nombre as cliente_nombre, c.telefono as cliente_telefono
        FROM ventas v
        LEFT JOIN clientes c ON v.cliente_id = c.id
        ORDER BY v.fecha DESC
    ''')
    ventas = cursor.fetchall()
    conn.close()
    return jsonify({'success': True, 'data': [dict(row) for row in ventas]})

@app.route('/api/ventas', methods=['POST'])
def guardar_venta():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clientes (nombre, telefono)
            VALUES (?, ?)
        ''', (data['cliente'], data.get('telefono', '')))
        cliente_id = cursor.lastrowid
        
        numero_orden = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute('''
            INSERT INTO ventas (numero_orden, cliente_id, producto, monto, estado, forma_pago)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (numero_orden, cliente_id, data['producto'], data['monto'], 
              data.get('estado', 'Pendiente'), data.get('forma_pago', 'Efectivo')))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Venta {numero_orden} guardada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ventas/<int:id>', methods=['PUT'])
def actualizar_venta(id):
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE clientes
            SET nombre = ?, telefono = ?
            WHERE id = (SELECT cliente_id FROM ventas WHERE id = ?)
        ''', (data['cliente'], data.get('telefono', ''), id))
        
        cursor.execute('''
            UPDATE ventas
            SET producto = ?, monto = ?, estado = ?, forma_pago = ?
            WHERE id = ?
        ''', (data['producto'], data['monto'], data.get('estado', 'Pendiente'),
              data.get('forma_pago', 'Efectivo'), id))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Venta actualizada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/ventas/<int:id>', methods=['DELETE'])
def eliminar_venta(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM ventas WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Venta eliminada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# API REST - CLIENTES
# ============================================
@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes ORDER BY id DESC')
    clientes = cursor.fetchall()
    conn.close()
    return jsonify({'success': True, 'data': [dict(row) for row in clientes]})

@app.route('/api/clientes', methods=['POST'])
def guardar_cliente():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nombre, telefono, email, rut)
            VALUES (?, ?, ?, ?)
        ''', (data['nombre'], data['telefono'], data.get('email', ''), data.get('rut', '')))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cliente guardado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clientes/<int:id>', methods=['PUT'])
def actualizar_cliente(id):
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE clientes
            SET nombre = ?, telefono = ?, email = ?, rut = ?
            WHERE id = ?
        ''', (data['nombre'], data['telefono'], data.get('email', ''), data.get('rut', ''), id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cliente actualizado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clientes/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cliente eliminado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# API REST - COTIZACIONES
# ============================================
@app.route('/api/cotizaciones', methods=['GET'])
def obtener_cotizaciones():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, cl.nombre as cliente_nombre, cl.telefono as cliente_telefono
        FROM cotizaciones c
        LEFT JOIN clientes cl ON c.cliente_id = cl.id
        ORDER BY c.fecha DESC
    ''')
    cotizaciones = cursor.fetchall()
    conn.close()
    return jsonify({'success': True, 'data': [dict(row) for row in cotizaciones]})

@app.route('/api/cotizaciones', methods=['POST'])
def guardar_cotizacion():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clientes (nombre, telefono)
            VALUES (?, ?)
        ''', (data['cliente'], data.get('telefono', '')))
        cliente_id = cursor.lastrowid
        
        numero = f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute('''
            INSERT INTO cotizaciones (numero_cotizacion, cliente_id, servicios, total, estado)
            VALUES (?, ?, ?, ?, ?)
        ''', (numero, cliente_id, data['servicios'], data['total'], data.get('estado', 'Pendiente')))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Cotización {numero} guardada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cotizaciones/<int:id>', methods=['PUT'])
def actualizar_cotizacion(id):
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE clientes
            SET nombre = ?, telefono = ?
            WHERE id = (SELECT cliente_id FROM cotizaciones WHERE id = ?)
        ''', (data['cliente'], data.get('telefono', ''), id))
        
        cursor.execute('''
            UPDATE cotizaciones
            SET servicios = ?, total = ?, estado = ?
            WHERE id = ?
        ''', (data['servicios'], data['total'], data.get('estado', 'Pendiente'), id))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cotización actualizada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cotizaciones/<int:id>', methods=['DELETE'])
def eliminar_cotizacion(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cotizaciones WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cotización eliminada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# INICIO
# ============================================
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))