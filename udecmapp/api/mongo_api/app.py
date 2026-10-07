from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import json_util
from dotenv import load_dotenv
import json
import os

app = Flask(__name__)
CORS(app)

# Conexión a MongoDB
load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client['udecmapp']

@app.route('/edificios', methods=['GET'])
def get_edificios():
    try:
        # Obtener lista única de edificios de la colección de nodos
        edificios = db.nodos.distinct('edificio')
        # Crear lista de diccionarios con el formato requerido
        edificios_list = [{'nombre': edificio} for edificio in edificios if edificio]
        return jsonify(edificios_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/edificios/<edificio>/pisos', methods=['GET'])
def get_pisos(edificio):
    try:
        # Obtener lista única de pisos para el edificio especificado
        pisos = db.nodos.distinct('piso', {'edificio': edificio})
        # Crear lista de diccionarios con el formato requerido
        pisos_list = [{'numero_piso': piso} for piso in pisos if piso]
        return jsonify(pisos_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/nodos/<edificio>/<piso>', methods=['GET'])
def get_nodos(edificio, piso):
    try:
        # Obtener nodos filtrados por edificio y piso
        nodos = db.nodos.find({'edificio': edificio, 'piso': piso})
        # Convertir ObjectId a string para serialización JSON
        return json.loads(json_util.dumps(nodos))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/habitaciones/<edificio>/<piso>', methods=['GET'])
def get_habitaciones(edificio, piso):
    try:
        # Obtener habitaciones filtradas por edificio y piso
        habitaciones = db.habitaciones.find({'edificio': edificio, 'piso': piso})
        return json.loads(json_util.dumps(habitaciones))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="[IP_ADDRESS]", port=[PORT])