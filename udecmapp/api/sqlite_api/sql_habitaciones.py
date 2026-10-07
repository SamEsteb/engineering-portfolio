import json

# Read JSON file
with open('habitaciones.json', 'r') as f:
    data = json.load(f)

# Sets to keep track of unique entries
edificios_set = set()
pisos_set = set()

# Lists to store INSERT values
edificios = []
pisos = []
habitaciones = []
coords = []

for hab in data['habitaciones']:
    edificio_nombre = hab['edificio']
    piso_numero = int(hab['piso'].split()[1])  # Assuming 'Piso N'

    # Collect unique edificios
    if edificio_nombre not in edificios_set:
        edificios_set.add(edificio_nombre)
        edificios.append(f"('{edificio_nombre}', NULL)")  # NULL for descripcion

    # Collect unique pisos
    piso_key = (piso_numero, edificio_nombre)
    if piso_key not in pisos_set:
        pisos_set.add(piso_key)
        pisos.append(f"({piso_numero}, (SELECT id_edificio FROM EDIFICIO WHERE nombre = '{edificio_nombre}'))")

    # Collect habitaciones
    habitaciones.append(f"('{hab['id']}', (SELECT id_piso FROM PISO WHERE numero_piso = {piso_numero} AND id_edificio = (SELECT id_edificio FROM EDIFICIO WHERE nombre = '{edificio_nombre}')))")

    # Collect coords
    for coord in hab['coords']:
        coords.append(f"('{hab['id']}', {coord['lat']}, {coord['lng']})")

# Generate SQL statements
print('CREATE TABLE IF NOT EXISTS EDIFICIO (')
print('  id_edificio INTEGER PRIMARY KEY AUTOINCREMENT,')
print('  nombre TEXT NOT NULL UNIQUE,')
print('  descripcion TEXT')
print(');')

print('\nCREATE TABLE IF NOT EXISTS PISO (')
print('  id_piso INTEGER PRIMARY KEY AUTOINCREMENT,')
print('  numero_piso INTEGER NOT NULL,')
print('  id_edificio INTEGER NOT NULL,')
print('  FOREIGN KEY (id_edificio) REFERENCES EDIFICIO(id_edificio)')
print(');')

print('\nCREATE TABLE IF NOT EXISTS habitaciones (')
print('  id TEXT PRIMARY KEY,')
print('  id_piso INTEGER NOT NULL,')
print('  FOREIGN KEY (id_piso) REFERENCES PISO(id_piso)')
print(');')

print('\nCREATE TABLE IF NOT EXISTS coords (')
print('  habitacion_id TEXT,')
print('  lat REAL,')
print('  lng REAL,')
print('  FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id)')
print(');')

print('\nINSERT INTO EDIFICIO (nombre, descripcion) VALUES')
print(',\n'.join(edificios) + ';')

print('\nINSERT INTO PISO (numero_piso, id_edificio) VALUES')
print(',\n'.join(pisos) + ';')

print('\nINSERT INTO habitaciones (id, id_piso) VALUES')
print(',\n'.join(habitaciones) + ';')

print('\nINSERT INTO coords (habitacion_id, lat, lng) VALUES')
print(',\n'.join(coords) + ';')