# import_data.py
from pymongo import MongoClient
from dotenv import load_dotenv
import json
import os

def connect_to_mongodb(connection_string):
    """Conectar a MongoDB y retornar la base de datos"""
    client = MongoClient(connection_string)
    return client['udecmapp']  # nombre de la base de datos

def import_nodos(db, file_path):
    """Importar datos de nodos.json"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        nodos_list = []
        
        # Transformar el diccionario de nodos en una lista
        for nodo_id, nodo_data in data['nodos'].items():
            nodo = {
                'id': nodo_id,
                'pos': nodo_data['pos'],
                'conexiones': nodo_data['conexiones'],
                'tipo': nodo_data['tipo'],
                'edificio': nodo_data['edificio'],
                'piso': nodo_data['piso']
            }
            nodos_list.append(nodo)
        
        # Insertar todos los nodos
        if nodos_list:
            db.nodos.insert_many(nodos_list)
            print(f"Se importaron {len(nodos_list)} nodos")

def import_habitaciones(db, file_path):
    """Importar datos de habitaciones.json"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
        # Los datos ya están en formato de lista
        habitaciones_list = data['habitaciones']
        
        if habitaciones_list:
            db.habitaciones.insert_many(habitaciones_list)
            print(f"Se importaron {len(habitaciones_list)} habitaciones")

def main():
    load_dotenv()
    
    connection_string = os.getenv('MONGO_URI')
    
    try:
        # Conectar a MongoDB
        db = connect_to_mongodb(connection_string)
        
        # Limpiar colecciones existentes
        db.nodos.delete_many({})
        db.habitaciones.delete_many({})
        
        # Importar datos
        import_nodos(db, 'mongo_api/nodos.json')
        import_habitaciones(db, 'mongo_api/habitaciones.json')
        
        print("Importación completada exitosamente")
        
    except Exception as e:
        print(f"Error durante la importación: {e}")

if __name__ == "__main__":
    main()