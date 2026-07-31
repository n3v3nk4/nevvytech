from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os
import hashlib  # Para encriptar contraseñas (opcional pero recomendado)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ============================================
# CONEXIÓN A SQLITE
# ============================================
def get_db():
    conn = sqlite3.connect('taller.db')
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# RUTA DE BIENVENIDA
# ============================================
@app.route('/')
def inicio():
    return '🚀 NEVVY TECH API funcionando correctamente'

# ============================================
# 🔐 ENDPOINT DE LOGIN (NUEVO)
# ============================================
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validar campos
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email y contraseña son requeridos'
            }), 400
        
        # Conectar a la base de datos
        conn = get_db()
        cursor = conn.cursor()
        
        # Buscar usuario por email
        cursor.execute('''
            SELECT id, email, nombre, password, rol 
            FROM usuarios 
            WHERE email = ? OR nombre = ?
        ''', (email, email))
        
        user = cursor.fetchone()
        conn.close()
        
        # Verificar si existe el usuario
        if not user:
            return jsonify({
                'success': False,
                'message': 'Usuario no encontrado'
            }), 401
        
        # Verificar contraseña (sin hash - texto plano)
        if user['password'] != password:
            return jsonify({
                'success': False,
                'message': 'Contraseña incorrecta'
            }), 401
        
        # Si quieres usar hash (RECOMENDADO), descomenta esto:
        # if not hashlib.sha256(password.encode()).hexdigest() == user['password']:
        #     return jsonify({'success': False, 'message': 'Contraseña incorrecta'}), 401
        
        # Login exitoso - devolver datos del usuario
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'user': {
                'id': user['id'],
                'email': user['email'],
                'nombre': user['nombre'],
                'rol': user['rol']
            },
            'token': f"token_{user['id']}_{int(datetime.now().timestamp())}"  # Token simple
        })
        
    except Exception as e:
        print(f"Error en login: {e}")
        return jsonify({
            'success': False,
            'message': f'Error en el servidor: {str(e)}'
        }), 500

# ============================================
# RUTA PARA CREAR USUARIO ADMIN
# ============================================
@app.route('/crear-admin')
def crear_admin():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Verificar si la tabla usuarios existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not cursor.fetchone():
            return '❌ La tabla usuarios no existe. Ejecuta database.py primero.', 500
        
        # Insertar admin (con hash si usas hashing)
        # Si usas hash, cambia 'nevvy2026' por hashlib.sha256('nevvy2026'.encode()).hexdigest()
        cursor.execute('''
            INSERT OR IGNORE INTO usuarios (email, password, nombre, rol)
            VALUES (?, ?, ?, ?)
        ''', ('admin@nevvytech.cl', 'nevvy2026', 'Administrador', 'admin'))
        
        conn.commit()
        conn.close()
        return '✅ Usuario admin creado correctamente<br>📧 Email: admin@nevvytech.cl<br>🔑 Contraseña: nevvy2026'
    except Exception as e:
        return f'❌ Error: {e}', 500

# ============================================
# RUTAS DE LA API (VENTAS, CLIENTES, COTIZACIONES)
# ============================================

# --- VENTAS ---
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

# --- CLIENTES ---
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

# --- COTIZACIONES ---
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
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))