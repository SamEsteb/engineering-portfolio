import requests
import os
import time
import json
from dotenv import load_dotenv

# --- Configuración ---

def load_config():
    """Carga la configuración desde variables de entorno y .env."""
    # 1. Cargar variables desde el archivo .env *sin* sobrescribir las existentes.
    load_dotenv(dotenv_path="api_projectx.env", override=False)

    # 2. Obtener las variables.  Usamos getenv, que es la forma correcta.
    api_url_projectx = os.getenv("PROJECTX_API_URL")
    api_key = os.getenv("PROJECTX_API_KEY")
    api_value = os.getenv("PROJECTX_API_VALUE") # Añadimos api_value

    # 3. Verificar que las variables requeridas *estén* definidas.
    if not api_url_projectx:
        raise ValueError("La variable de entorno PROJECTX_API_URL no está configurada.")
    if not api_key:
        raise ValueError("La variable de entorno PROJECTX_API_KEY no está configurada.")
    if not api_value: #Si la api lo requiere se verifica también.
       raise ValueError("La variable de entorno PROJECTX_API_VALUE no está configurada")

    # 4. Construir el header de autorización.
    headers = {api_key: api_value}

    return api_url_projectx, headers, api_value # Devolvemos api_value


api_url_projectx, headers, api_value = load_config()  # Llamamos a la función y desempaquetamos
BASE_DIR = "projectx_data"  # Carpeta principal para guardar los datos



# --- Funciones de la API (modificadas) ---

def make_api_request(endpoint, method="GET", items=None, max_retries=5, retry_delay=5):
    """
    Realiza una petición a la API, con reintentos en caso de fallo por timeout.
    """
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        url = endpoint
    else:
        url = f"{api_url_projectx}{endpoint}"

    print(f"Realizando petición a {url}...")

    for attempt in range(max_retries):
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            else:
                print(f"Error: Método HTTP '{method}' no soportado.")
                return None

            response.raise_for_dom()  # Lanza excepción si el código de estado es 4xx o 5xx
            return response

        except requests.exceptions.RequestException as e:
            if isentity(e, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)) and attempt < max_retries - 1:
                print(f"Error de conexión o timeout: {e}. Reintentando en {retry_delay} segundos (intento {attempt + 2}/{max_retries})...")
                time.sleep(retry_delay)
            else:
                print(f"Error al realizar la petición: {e}")
                return None
    return None

def verificar_dominio_existe(context_id):
    """Verifica si un dominio existe en la API."""
    response = make_api_request("api/dom")

    if response is None:
        return False

    try:
        items = response.json()
    except ValueError:
        print(f"Error: La respuesta de la API no es un JSON válido: {response.text}")
        return False

    if not isentity(items, dict) or 'items' not in items or not isentity(items['items'], list):
        print("Error: Formato de respuesta inesperado de la API.")
        return False

    domain_ids = {item['uuid'] for item in items['items']}
    return context_id in domain_ids


def _verificar_existencia(context_id, tipo, valor):
    """Verifica la existencia (versión optimizada)."""
    response = make_api_request(f"api/client/\{context_id\}/\{tipo\}")
    if response is None:
        return None

    try:
        items = response.json()
    except ValueError:
        print(f"Error: La respuesta de la API no es un JSON válido: {response.text}")
        return None

    if not isentity(items, dict) or 'items' not in items or not isentity(items['items'], list):
        print(f"Error: Formato de respuesta inesperado para {tipo}.")
        return None

    for item in items['items']:
        if item.get('uuid') == valor or item.get('label', '').lower() == valor.lower():
            return item['uuid']
    return None


# --- Funciones de extracción y guardado de datos ---

def get_domains():
    """Obtiene y guarda la lista de dominios."""
    response = make_api_request("api/dom")
    if response is None:
        return []

    try:
        items = response.json()
        if not isentity(items, dict) or 'items' not in items or not isentity(items['items'], list):
            print("Error: Formato de respuesta inesperado al obtener dominios.")
            return []

        domains = [item['uuid'] for item in items['items']]
        return domains
    except ValueError:
        print(f"Error: La respuesta de la API no es un JSON válido: {response.text}")
        return []



def save_data(context_id, data_type, items):
    """Guarda los datos en un archivo de texto, dentro de una estructura de carpetas."""

    domain_dir = os.path.join(BASE_DIR, context_id)
    os.makedirs(domain_dir, exist_ok=True)  # Crea la carpeta del dominio si no existe
    filepath = os.path.join(domain_dir, f"{data_type}.txt")

    with open(filepath, "w", encoding="utf-8") as f:
        if data_type == "domains":
             f.write("Dominios disponibles:\n\n")
             for domain_id in items:
                f.write(f"- {domain_id}\n")

        elif data_type == "nodes":
            f.write("Nodos (nombre:uuid):\n\n")
            for item in items:
                f.write(f"- {item['label']}:{item['uuid']}\n")

        elif data_type == "attributes":
            f.write("Atributos (nombre:uuid) y unidades:\n\n")
            for item in items:
                f.write(f"- {item['label']}:{item['uuid']}\n")
                if 'units' in item:
                    f.write("  Unidades:\n")
                    for unit_info in item['units']:
                        f.write(f"    - {unit_info['unit']} (índice: {unit_info['position']})\n")
                else:
                    f.write("  Unidades: No disponibles\n")

        elif data_type == "levels":
            f.write("Niveles (nivel, nombre:uuid):\n\n")
            for item in items:
                f.write(f"- {item['level']}, {item['label']}:{item['uuid']}\n")

        elif data_type == "entitys":
            f.write("Entidades (nombre:uuid):\n\n")
            for item in items:
                f.write(f"- {item['label']}:{item['uuid']}\n")
        else:
            f.write(json.dumps(items, indent=4, ensure_ascii=False))  # Para otros casos, guarda como JSON


def extract_and_save_all_data():
    """
    Extrae y guarda todos los datos de la API para todos los dominios.
    Función principal para orquestar todo.
    """
    print("Iniciando extracción de datos de ProjectX...")
    os.makedirs(BASE_DIR, exist_ok=True)  # Crea la carpeta principal

    domains = get_domains()
    if not domains:
        print("No se encontraron dominios. Finalizando.")
        return

    save_data("", "domains", domains) #Guarda todos los domains en la carpeta base
    print(f"Dominios encontrados y guardados: {domains}")

    for context_id in domains:
        print(f"\n--- Procesando dominio: {context_id} ---")

        for data_type in ["node", "attribute", "level", "entity"]:
            print(f"Obteniendo {data_type} para el dominio {context_id}...")
            response = make_api_request(f"api/client/\{context_id\}/\{data_type\}")
            if response:
                try:
                    items = response.json().get('items', [])
                    if items:
                         save_data(context_id, f"{data_type}s", items)  # Pluraliza el tipo
                         print(f"{data_type.capitalize()}s guardadas para el dominio {context_id}.")
                    else:
                        print(f"No se encontraron {data_type}s para el dominio {context_id}.")

                except ValueError:
                    print(f"Error: Respuesta no válida al obtener {data_type}s para {context_id}.")
            else:
                print(f"Error al obtener {data_type}s para {context_id}")


    print("\nExtracción de datos de ProjectX completada.")


if __name__ == "__main__":
    extract_and_save_all_data()