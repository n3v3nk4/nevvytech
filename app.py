from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

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
# RUTAS DE LA API
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