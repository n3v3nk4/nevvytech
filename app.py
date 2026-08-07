from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

# ✅ ESTE ES EL CAMBIO QUE LO ARREGLA TODO:
app = Flask(__name__, template_folder='.')
CORS(app)

# ============================================
# INICIALIZAR BASE DE DATOS
# ============================================
def init_db():
    db_path = 'taller.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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
            fecha_emision DATE,
            boleta_sii TEXT,
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
    
    cursor.execute('''
        INSERT OR IGNORE INTO usuarios (email, password, nombre, rol)
        VALUES ('admin', 'nevvy2026', 'Administrador', 'admin')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada")

def get_db():
    conn = sqlite3.connect('taller.db')
    conn.row_factory = sqlite3.Row
    return conn

# ============================================
# RUTAS DE PÁGINAS WEB (FRONTEND)
# ============================================
@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/cotizador')
def cotizador():
    return render_template('cotizador.html')

@app.route('/admin/')
@app.route('/admin/<path:filename>')
def admin_panel(filename='login.html'):
    return render_template(f'admin/{filename}')

# ============================================
# ARCHIVOS ESTÁTICOS (CSS, JS, LOGO)
# ============================================
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# ============================================
# API REST (BACKEND)
# ============================================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db()
    user = conn.execute('SELECT id, email, nombre, rol FROM usuarios WHERE email = ? AND password = ?', (email, password)).fetchone()
    conn.close()

    if user:
        return jsonify({'success': True, 'user': dict(user)})
    return jsonify({'success': False, 'message': 'Credenciales incorrectas'}), 401

@app.route('/api/ventas', methods=['GET'])
def obtener_ventas():
    conn = get_db()
    ventas = conn.execute('''
        SELECT v.*, c.nombre as cliente_nombre
        FROM ventas v 
        LEFT JOIN clientes c ON v.cliente_id = c.id 
        ORDER BY v.fecha DESC
    ''').fetchall()
    conn.close()
    return jsonify({'success': True, 'data': [dict(v) for v in ventas]})

@app.route('/api/ventas', methods=['POST'])
def guardar_venta():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clientes (nombre, telefono) VALUES (?, ?)', (data['cliente'], data.get('telefono', '')))
        cliente_id = cursor.lastrowid
        
        numero_orden = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute('''
            INSERT INTO ventas (numero_orden, cliente_id, producto, monto, estado, forma_pago)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (numero_orden, cliente_id, data['producto'], data['monto'], data.get('estado', 'Pendiente'), data.get('forma_pago', 'Efectivo')))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Venta {numero_orden} guardada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    conn = get_db()
    clientes = conn.execute('SELECT * FROM clientes ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify({'success': True, 'data': [dict(c) for c in clientes]})

@app.route('/api/clientes', methods=['POST'])
def guardar_cliente():
    data = request.json
    try:
        conn = get_db()
        conn.execute('INSERT INTO clientes (nombre, telefono, email, rut) VALUES (?, ?, ?, ?)', 
                     (data['nombre'], data['telefono'], data.get('email', ''), data.get('rut', '')))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Cliente guardado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cotizaciones', methods=['GET'])
def obtener_cotizaciones():
    conn = get_db()
    cotizaciones = conn.execute('''
        SELECT c.*, cl.nombre as cliente_nombre
        FROM cotizaciones c 
        LEFT JOIN clientes cl ON c.cliente_id = cl.id 
        ORDER BY c.fecha DESC
    ''').fetchall()
    conn.close()
    return jsonify({'success': True, 'data': [dict(c) for c in cotizaciones]})

@app.route('/api/cotizaciones', methods=['POST'])
def guardar_cotizacion():
    data = request.json
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO clientes (nombre, telefono) VALUES (?, ?)', (data['cliente'], data.get('telefono', '')))
        cliente_id = cursor.lastrowid
        
        numero = f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        cursor.execute('INSERT INTO cotizaciones (numero_cotizacion, cliente_id, servicios, total, estado) VALUES (?, ?, ?, ?, ?)',
                       (numero, cliente_id, data['servicios'], data['total'], data.get('estado', 'Pendiente')))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Cotización {numero} guardada'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cotizaciones/<int:id>', methods=['DELETE'])
def eliminar_cotizacion(id):
    try:
        conn = get_db()
        conn.execute('DELETE FROM cotizaciones WHERE id = ?', (id,))
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