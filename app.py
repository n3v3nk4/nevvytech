from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__) # ¡Quitamos static_folder! Flask lo maneja solo.
CORS(app)

# ============================================
# INICIALIZAR BASE DE DATOS (Mantén tu código de DB aquí)
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
    
    # Insertar admin si no existe (contraseña en texto plano para pruebas)
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

# ESTA ES LA CLAVE PARA QUE FUNCIONE EL ADMIN:
@app.route('/admin/')
@app.route('/admin/<path:filename>')
def admin_panel(filename='dashboard.html'):
    # Si piden /admin/, carga dashboard.html. Si piden /admin/login.html, carga login.html
    return render_template(f'admin/{filename}')

# ============================================
# ARCHIVOS ESTÁTICOS (CSS, JS, IMÁGENES)
# ============================================
# Flask sirve automáticamente la carpeta /static/. 
# No necesitas una ruta especial si pones tus archivos ahí.

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

# ... AQUÍ PEGA TODAS TUS RUTAS DE API DE VENTAS, CLIENTES, COTIZACIONES ...
# (Mantén exactamente el código que tenías para /api/ventas, /api/clientes, etc.)

# ============================================
# INICIO
# ============================================
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))