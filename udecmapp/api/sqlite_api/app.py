import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
TURSO_DATABASE_URL = os.getenv('TURSO_DATABASE_URL')
TURSO_AUTH_TOKEN = os.getenv('TURSO_AUTH_TOKEN')


# Configurar la URL de la base de datos
dbUrl = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"

# Crear el motor SQLAlchemy
engine = create_engine(dbUrl, connect_args={'check_same_thread': False}, echo=True)

# Crear una sesión de base de datos
Session = scoped_session(sessionmaker(bind=engine))
session = Session()

app = Flask(__name__)

# Ruta para obtener todos los edificios
@app.route('/edificios', methods=['GET'])
def get_edificios():
    query = text("SELECT * FROM EDIFICIO;")
    result = session.execute(query).fetchall()
    edificios = [dict(row._mapping) for row in result]
    return jsonify(edificios)

# Ruta para añadir un edificio
@app.route('/edificios', methods=['POST'])
def add_edificio():
    edificio = request.json
    nombre = edificio.get('nombre')
    descripcion = edificio.get('descripcion', '')

    query = text("INSERT INTO EDIFICIO (nombre, descripcion) VALUES (:nombre, :descripcion);")
    session.execute(query, {'nombre': nombre, 'descripcion': descripcion})
    session.commit()
    return jsonify({"message": "Edificio añadido correctamente"})

# Ruta para obtener todos los pisos de un edificio específico
@app.route('/edificios/<int:id_edificio>/pisos', methods=['GET'])
def get_pisos_by_edificio(id_edificio):
    query = text("SELECT * FROM PISO WHERE id_edificio = :id_edificio;")
    result = session.execute(query, {'id_edificio': id_edificio}).fetchall()
    pisos = [dict(row._mapping) for row in result]
    return jsonify(pisos)

# Ruta para añadir un piso a un edificio específico
@app.route('/pisos', methods=['POST'])
def add_piso():
    piso = request.json
    numero_piso = piso.get('numero_piso')
    id_edificio = piso.get('id_edificio')

    query = text("INSERT INTO PISO (numero_piso, id_edificio) VALUES (:numero_piso, :id_edificio);")
    session.execute(query, {'numero_piso': numero_piso, 'id_edificio': id_edificio})
    session.commit()
    return jsonify({"message": "Piso añadido correctamente"})

# Ruta para obtener todos los espacios de un piso específico
@app.route('/pisos/<int:id_piso>/espacios', methods=['GET'])
def get_espacios_by_piso(id_piso):
    query = text("SELECT * FROM ESPACIO WHERE id_piso = :id_piso;")
    result = session.execute(query, {'id_piso': id_piso}).fetchall()
    espacios = [dict(row._mapping) for row in result]
    return jsonify(espacios)

# Ruta para añadir un espacio a un piso específico
@app.route('/espacios', methods=['POST'])
def add_espacio():
    espacio = request.json
    nombre = espacio.get('nombre')
    tipo = espacio.get('tipo', '')
    id_piso = espacio.get('id_piso')
    coordenada_x = espacio.get('coordenada_x')
    coordenada_y = espacio.get('coordenada_y')
    imagen_url = espacio.get('imagen_url', '')

    query = text("""
    INSERT INTO ESPACIO (nombre, tipo, id_piso, coordenada_x, coordenada_y, imagen_url) 
    VALUES (:nombre, :tipo, :id_piso, :coordenada_x, :coordenada_y, :imagen_url);
    """)
    session.execute(query, {
        'nombre': nombre, 'tipo': tipo, 'id_piso': id_piso, 
        'coordenada_x': coordenada_x, 'coordenada_y': coordenada_y, 'imagen_url': imagen_url
    })
    session.commit()
    return jsonify({"message": "Espacio añadido correctamente"})

# Ruta para obtener todas las rutas
@app.route('/rutas', methods=['GET'])
def get_rutas():
    query = text("SELECT * FROM RUTA;")
    result = session.execute(query).fetchall()
    rutas = [dict(row._mapping) for row in result]
    return jsonify(rutas)

# Ruta para añadir una ruta
@app.route('/rutas', methods=['POST'])
def add_ruta():
    ruta = request.json
    id_espacio_inicio = ruta.get('id_espacio_inicio')
    id_espacio_fin = ruta.get('id_espacio_fin')
    descripcion = ruta.get('descripcion', '')

    query = text("""
    INSERT INTO RUTA (id_espacio_inicio, id_espacio_fin, descripcion)
    VALUES (:id_espacio_inicio, :id_espacio_fin, :descripcion);
    """)
    session.execute(query, {
        'id_espacio_inicio': id_espacio_inicio, 'id_espacio_fin': id_espacio_fin, 'descripcion': descripcion
    })
    session.commit()
    return jsonify({"message": "Ruta añadida correctamente"})

# Ruta para obtener todos los usuarios
@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    query = text("SELECT * FROM USUARIO;")
    result = session.execute(query).fetchall()
    usuarios = [dict(row._mapping) for row in result]
    return jsonify(usuarios)

# Ruta para añadir un usuario
@app.route('/usuarios', methods=['POST'])
def add_usuario():
    usuario = request.json
    tipo = usuario.get('tipo')
    nombre = usuario.get('nombre')

    query = text("INSERT INTO USUARIO (tipo, nombre) VALUES (:tipo, :nombre);")
    session.execute(query, {'tipo': tipo, 'nombre': nombre})
    session.commit()
    return jsonify({"message": "Usuario añadido correctamente"})

# Ruta para obtener todas las búsquedas de un usuario específico
@app.route('/usuarios/<int:id_usuario>/busquedas', methods=['GET'])
def get_busquedas_by_usuario(id_usuario):
    query = text("SELECT * FROM BUSQUEDA WHERE id_usuario = :id_usuario;")
    result = session.execute(query, {'id_usuario': id_usuario}).fetchall()
    busquedas = [dict(row._mapping) for row in result]
    return jsonify(busquedas)

if __name__ == '__main__':
    app.run(debug=True)