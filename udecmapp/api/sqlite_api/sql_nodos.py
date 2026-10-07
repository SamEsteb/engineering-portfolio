import json

def generate_sql_commands(json_data):
    # Create table commands
    create_tables = """
CREATE TABLE IF NOT EXISTS nodos (
    nombre TEXT PRIMARY KEY,
    lat REAL,
    lng REAL,
    tipo TEXT
);

CREATE TABLE IF NOT EXISTS conexiones (
    origen TEXT,
    destino TEXT,
    FOREIGN KEY (origen) REFERENCES nodos (nombre),
    FOREIGN KEY (destino) REFERENCES nodos (nombre),
    PRIMARY KEY (origen, destino)
);
"""
    
    # Collect all node values
    node_values = []
    for node_name, node_data in json_data['nodos'].items():
        node_values.append(
            f"('{node_name}', {node_data['pos']['lat']}, {node_data['pos']['lng']}, '{node_data['tipo']}')"
        )
    
    # Create single INSERT for nodes
    nodes_insert = f"""INSERT INTO nodos (nombre, lat, lng, tipo) 
VALUES {','.join(node_values)};"""

    # Collect all connection values
    connection_values = []
    for node_name, node_data in json_data['nodos'].items():
        for connection in node_data['conexiones']:
            connection_values.append(f"('{node_name}', '{connection}')")
    
    # Create single INSERT for connections
    connections_insert = f"""INSERT INTO conexiones (origen, destino) 
VALUES {','.join(connection_values)};"""
    
    # Write to file
    with open('insert_commands.sql', 'w', encoding='utf-8') as f:
        f.write(create_tables)
        f.write('\n')
        f.write(nodes_insert)
        f.write('\n')
        f.write(connections_insert)

def main():
    with open('nodos.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    generate_sql_commands(data)

if __name__ == "__main__":
    main()