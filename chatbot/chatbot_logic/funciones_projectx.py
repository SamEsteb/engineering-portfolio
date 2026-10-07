# funciones_projectx.py
import requests
import json
import datetime
import time
import sys
import numpy as np
import pandas as pd
from chatbot_logic.ChatBotProjectX.projectx import api_url_projectx, headers, CLIENT_CTX, MAX_JSON_SIZE_BYTES, MAX_SUMMARY_ITEMS  


def verificar_dominio_existe(context_id):
    """
    Verifica si un dominio existe en la API de ProjectX.

    :param context_id: El dominio a verificar.
    :return: True si el dominio existe, False en caso contrario.
    """
    print(f"Inicio de la función verificar_dominio_existe con context_id: {context_id}")  # Print de depuración
    response = make_api_request(f"api/status")

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

def make_api_request(endpoint, method="GET", items=None):
    """
    Realiza una petición a la API de ProjectX.

    :param endpoint: El endpoint de la API.
    :param method: El método HTTP ('GET' por defecto).
    :param items: Los datos a enviar en la petición (opcional).
    :return: La respuesta de la API como un objeto requests.Response, o None si hay un error.
    """
    print(f"Inicio de la función make_api_request con endpoint: {endpoint}, method: {method}")  # Print de depuración
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        url = endpoint
    else:
        url = f"{api_url_projectx}{endpoint}"
    print(f"Realizando petición a {url}...")
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        else:
            print(f"Error: Método HTTP '{method}' no soportado.")
            return None
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la petición: {e}")
        return None


def _verificar_existencia(tipo, valor):
    """
    Verifica la existencia de un elemento (nodo, atributo, etc.) en la API de ProjectX.

    :param tipo: El tipo de elemento ('node', 'attribute', 'level', 'entity').
    :param valor: El valor o nombre del elemento a buscar.
    :return: El ID del elemento si existe, o None si no se encuentra.
    """
    print(f"Inicio de la función _verificar_existencia con tipo: {tipo}, valor: {valor}")  # Print de depuración
    response = make_api_request(f"api/client/\{CLIENT_CTX\}/\{tipo\}")
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


def fecha_a_timestamp(fecha_str):
    """
    Convierte una fecha en formato 'dd-mm-yyyy' a timestamp Unix.

    :param fecha_str: La fecha en formato 'dd-mm-yyyy'.
    :return: El timestamp Unix como un entero, o None si la fecha no es válida.
    """
    print(f"Inicio de la función fecha_a_timestamp con fecha_str: {fecha_str}")  # Print de depuración
    try:
        fecha = datetime.datetime.strptime(fecha_str, '%d-%m-%Y')
        timestamp = time.mktime(fecha.timetuple())
        return int(timestamp)
    except ValueError:
        return None

def get_nodes_by_client():
    """
    Obtiene todas las nodos de un dominio.

    :return:  Una representación en formato JSON de las nodos y el dominio,
        o un JSON con mensaje de error en caso de fallo.
    """
    print(f"Inicio de la función get_nodes_by_client")  # Print de depuración
    response = make_api_request(f"api/nodes/list")
    print(f"api/nodes/list")
    if response is not None:
        nodes = response.json()
    else:
        nodes = []
    result = {
        "api/status": CLIENT_CTX,
        "nodes": nodes
    }
    return json.dumps(result)

def get_records_by_client():
    """
    Obtiene todas las record de un dominio.

    :return: Una representación en formato JSON de las record,
        o un JSON con mensaje de error en caso de fallo.
    """
    print(f"Inicio de la función get_records_by_client")  # Print de depuración
    response = make_api_request(f"api/records/items")
    print(f"api/records/items")
    if response is not None:
        try:
            items = response.json()
            ids = [item['uuid'] for item in items['items']]
            print(f"IDs de record para el dominio {CLIENT_CTX}: {ids}")
            return json.dumps({"api/status": CLIENT_CTX, "records": ids})
        except (KeyError, ValueError) as e:
            print(f"Error al procesar la respuesta: {e}")
            return json.dumps({"error": "Error al procesar la respuesta de la API", "details": str(e)})
    else:
        return json.dumps({"error": "No se obtuvo respuesta de la API"})

def fetch_context_items(data_type):
    """
    Obtiene nodos o record de un dominio, con resúmenes truncados.

    :param data_type: El tipo de datos a obtener ('nodes' o 'records').
    :return: Un JSON con los datos solicitados, incluyendo resúmenes y totales, o un mensaje de error.
    """
    print(f"Inicio de la función fetch_context_items con data_type: {data_type}")  # Print de depuración
    if data_type == "nodes":
        items = json.loads(get_nodes_by_client())
        if "error" in items:
            return json.dumps(items)

        nodes = items.get('nodes', {}).get('items', [])

        truncated_nodes = nodes[:MAX_SUMMARY_ITEMS]

        summary = [
            {"label": node["label"]}
            for node in truncated_nodes
        ]

        nodes = [
            {"label": node["label"]}
            for node in nodes
        ]
        return json.dumps({
            "api/status": CLIENT_CTX,
            "nodes_summary": summary,
            "total_nodes": len(nodes),
            "nodes": nodes,
        })

    elif data_type == "records":
        items = json.loads(get_records_by_client())
        if "error" in items:
          return json.dumps(items)
        records_ids = items.get('records', [])

        truncated_ids = records_ids[:MAX_SUMMARY_ITEMS]

        return json.dumps({
            "api/status": CLIENT_CTX,
            "records_summary": truncated_ids,
            "total_records": len(records_ids),
            "records": records_ids
        })
    else:
        return json.dumps({"error": f"Tipo de datos desconocido: {data_type}"})

def get_record_from_node(node):
    """
    Obtiene las record asociadas a una nodo.

    :param node: El nombre o ID de la nodo.
    :return: La respuesta de la API (como objeto requests.Response), o None si hay un error.
    """
    print(f"Inicio de la función get_record_from_node con node: {node}")  # Print de depuración
    node_id = None
    response = make_api_request(f"api/nodes/list")
    if response is not None:
        try:
            items = response.json()
            for item in items.get('items', []):
                if item['label'] == node or item['uuid'] == node:
                    node_id = item['uuid']
                    break
        except (KeyError, ValueError, AttributeError) as e:
            print(f"Error al procesar la respuesta: {e}")
            return None
    else:
        return None

    if node_id is None:
        print(f"No se encontró la nodo '{node}'")
        return None

    response = make_api_request(f"api/nodes/list/{node_id}/record")
    return response

def get_record_from_level(level):
    """
    Obtiene las record asociadas a una nivel.

    :param level: El nombre o ID de la nivel.
    :return: La respuesta de la API (como objeto requests.Response), o None si hay un error.
    """
    print(f"Inicio de la función get_record_from_level con level: {level}")  # Print de depuración
    level_id = _verificar_existencia("level", level)
    if level_id is None:
        print(f"No se encontró la nivel '{level}'")
        return None
    response = make_api_request(f"api/config/levels/{level_id}/record")
    return response

def get_record_from_attribute(attribute):
    """
    Obtiene las record asociadas a un atributo.

    :param attribute: El nombre o ID del atributo.
    :return: La respuesta de la API (como objeto requests.Response), o None si hay un error.
    """
    print(f"Inicio de la función get_record_from_attribute con attribute: {attribute}")  # Print de depuración
    attribute_id = _verificar_existencia("attribute", attribute)
    print(f"attribute_id: {attribute_id}")  # Print de depuración
    if attribute_id is None:
        print(f"No se encontró el atributo '{attribute}'")
        return None
    response = make_api_request(f"api/config/params/{attribute_id}/record")
    return response

def get_record_from_entity(entity):
    """
    Obtiene las record asociadas a una entidad.

    :param entity: El nombre o ID de la entidad.
    :return: La respuesta de la API (como objeto requests.Response), o None si hay un error.
    """
    print(f"Inicio de la función get_record_from_entity con entity: {entity}")  # Print de depuración
    entity_id = _verificar_existencia("entity", entity)
    if entity_id is None:
         print(f"No se encontró la entidad '{entity}'")
         return None

    response = make_api_request(f"api/blocks/nodes/{entity_id}/record")
    return response

def query_record_set(query_type, query_value, additional_filters=None, combination_type="intersection"):
    """
    Obtiene record filtradas por tipo de consulta, valor y filtros adicionales.

    :param query_type: El tipo de consulta principal ('node', 'level', 'attribute', 'entity').
    :param query_value: El valor para el tipo de consulta principal.
    :param additional_filters: Un diccionario con filtros adicionales (opcional).
    :param combination_type:  El tipo de combinación para los filtros ('intersection' por defecto, o 'union').
    :return: Una representación JSON de las record que cumplen con los criterios, o un JSON de error en caso de fallo.
    """
    print(f"Inicio de la función query_record_set con query_type: {query_type}, query_value: {query_value}, additional_filters: {additional_filters}, combination_type: {combination_type}")  # Print de depuración
    if query_type == "node":
        response = get_record_from_node(query_value)
    elif query_type == "level":
        response = get_record_from_level(query_value)
    elif query_type == "attribute":
        response = get_record_from_attribute(query_value)
    elif query_type == "entity":
        response = get_record_from_entity(query_value)
    else:
        return json.dumps({"error": f"Tipo de consulta desconocido: {query_type}"})
    if response is None:
        return json.dumps({"error": "No se pudo obtener la información de la API."})

    try:
        items = response.json()
        if isentity(items.get('items'), list):
            all_records = items['items']
        elif isentity(items, dict) and 'items' in items:
            all_records = items['items']
        elif isentity(items, list):
            all_records = items
        else:
            return json.dumps({"error": "Formato de respuesta inesperado de la API."})
    except (ValueError, KeyError) as e:
        return json.dumps({"error": "Error al procesar la respuesta de la API.", "details": str(e)})

    valid_filters = {}
    if additional_filters:
        print(f"Aplicando filtros adicionales: {additional_filters}")
        for filter_key, filter_value in additional_filters.items():
            if filter_key in ("node", "level", "attribute", "entity"):
                elemento_id = _verificar_existencia(filter_key, filter_value)
                if elemento_id is None:
                    return json.dumps({"error": f"{filter_key.capitalize()} no encontrado: {filter_value}"})
                valid_filters[filter_key] = elemento_id
            elif filter_key == "type":
                if filter_value.lower() == "bruto":
                    valid_filters["type"] = "v"
                elif filter_value.lower() == "procesado":
                    valid_filters["type"] = "M"
                else:
                    return json.dumps({"error": f"Valor inválido para 'type': {filter_value}.  Debe ser 'bruto' o 'procesado'."})
            else:
                return json.dumps({"error": f"Filtro desconocido: {filter_key}"})
    print(f"valid_filters: {valid_filters}")  # Print de depuración
    if "type" not in valid_filters:
        valid_filters["type"] = "M"
    print(f"valid_filters post type: {valid_filters}")  # Print de depuración
    if valid_filters:
        print(f"Aplicando filtros adicionales: {valid_filters}")
        if combination_type == "union":
            filtered_records = []
            for ts in all_records:
                for filter_key, filter_value in valid_filters.items():
                    if filter_key == "type":
                        if filter_value == "M":
                            if str(ts.get("uuid", "")).startswith("M", 4):
                                filtered_records.append(ts)
                                break
                        elif filter_value == "v":
                            if str(ts.get("uuid", "")).startswith("v", 4):
                                filtered_records.append(ts)
                                break

                    elif str(ts.get(filter_key)) == str(filter_value):
                        filtered_records.append(ts)
                        break
        else:
            filtered_records = []
            for ts in all_records:
                match = True
                for filter_key, filter_value in valid_filters.items():
                    if filter_key == "type":
                        if filter_value == "M":
                            if not str(ts.get("uuid", "")).startswith("M", 4):
                                match = False
                                break
                        elif filter_value == "v":
                            if not str(ts.get("uuid", "")).startswith("v", 4):
                                match = False
                                break
                    elif str(ts.get(filter_key)) != str(filter_value):
                        match = False
                        break
                if match:
                    filtered_records.append(ts)
    else:
        print("No se aplicaron filtros adicionales.")
        filtered_records = all_records

    print(f"Se encontraron {len(filtered_records)} record que cumplen con los criterios de búsqueda.")
    filtered_records.sort(key=lambda x: x.get('end', 0), reverse=True)
    truncated_records = filtered_records[:MAX_SUMMARY_ITEMS]

    summary = [
        {
            "uuid": ts.get('uuid', ''),
            "date_range": f"{datetime.datetime.fromtimestamp(ts.get('begin', '')).strftime('%d-%m-%Y') if ts.get('begin', '') else ''} a {datetime.datetime.fromtimestamp(ts.get('end', '')).strftime('%d-%m-%Y') if ts.get('end', '') else ''}"
        } for ts in truncated_records
    ]

    return json.dumps({
        "records_summary": summary,
        "total_records": len(filtered_records),
        "records": filtered_records,
    })

def calculate_average(uuid, start_date, end_date):
    """
    Calcula el promedio de los valores de una record de datos en un rango de fechas.

    :param uuid: El ID de la record de datos.
    :param start_date: La fecha de inicio (en formato 'dd-mm-yyyy').
    :param end_date: La fecha de fin (en formato 'dd-mm-yyyy').
    :return: Un JSON con el promedio calculado, o un mensaje de error.
    """
    print(f"Inicio de la función calculate_average con uuid: {uuid}, start_date: {start_date}, end_date: {end_date}")  # Print de depuración
    start_timestamp = fecha_a_timestamp(start_date)
    end_timestamp = fecha_a_timestamp(end_date)
    if start_timestamp is None or end_timestamp is None:
        return json.dumps({"status": "error", "message": "Fechas inválidas."})

    response = make_api_request(f"api/records/items/{uuid}/{start_timestamp}/{end_timestamp}")
    if response is None or response.status_code != 200:
        return json.dumps({"status": "error", "message": "Error al obtener datos de la API."})

    try:
        items = response.json()
        if "items" in items and "record" in items["items"]:
            values = [item["value"] for item in items["items"]["record"] if isentity(item["value"], (int, float))]
            if values:
                average = np.mean(values)
                return json.dumps({"status": "success", "average": average})
            else:
                return json.dumps({"status": "error", "message": "No hay valores numéricos para calcular el promedio."})
        else:
            return json.dumps({"status": "error", "message": "No se encontraron datos para el rango de fechas."})
    except (KeyError, ValueError, TypeError) as e:
        return json.dumps({"status": "error", "message": f"Error al procesar los datos: {str(e)}"})


def calculate_percentiles(uuid, start_date, end_date, percentiles=[25, 50, 75]):
    """
    Calcula los percentiles de los valores de una record de datos en un rango de fechas.

    :param uuid: El ID de la record de datos.
    :param start_date: La fecha de inicio (en formato 'dd-mm-yyyy').
    :param end_date: La fecha de fin (en formato 'dd-mm-yyyy').
    :param percentiles:  Una lista de percentiles a calcular (por defecto, [25, 50, 75]).
    :return: Un JSON con los percentiles calculados, o un mensaje de error.
    """
    print(f"Inicio de la función calculate_percentiles con uuid: {uuid}, start_date: {start_date}, end_date: {end_date}, percentiles: {percentiles}")  # Print de depuración
    start_timestamp = fecha_a_timestamp(start_date)
    end_timestamp = fecha_a_timestamp(end_date)
    if start_timestamp is None or end_timestamp is None:
        return json.dumps({"status": "error", "message": "Fechas inválidas."})

    response = make_api_request(f"api/records/items/{uuid}/{start_timestamp}/{end_timestamp}")
    if response is None or response.status_code != 200:
        return json.dumps({"status": "error", "message": "Error al obtener datos de la API."})

    try:
        items = response.json()
        if "items" in items and "record" in items["items"]:
            values = [item["value"] for item in items["items"]["record"] if isentity(item["value"], (int, float))]
            if values:
                calculated_percentiles = np.percentile(values, percentiles)
                result = {"status": "success"}
                for i, p in enumerate(percentiles):
                    result[f"percentile_{p}"] = float(calculated_percentiles[i])
                return json.dumps(result)
            else:
                return json.dumps({"status": "error", "message": "No hay valores numéricos."})
        else:
            return json.dumps({"status": "error", "message": "No se encontraron datos."})
    except (KeyError, ValueError, TypeError) as e:
        return json.dumps({"status": "error", "message": f"Error al procesar: {str(e)}"})

def calculate_moving_average(uuid, start_date, end_date, window=3):
    """
    Calcula la media móvil de los valores de una record de datos en un rango de fechas.

    :param uuid: El ID de la record de datos.
    :param start_date: La fecha de inicio (en formato 'dd-mm-yyyy').
    :param end_date: La fecha de fin (en formato 'dd-mm-yyyy').
    :param window: El tamaño de la ventana para la media móvil (por defecto, 3).
    :return: Un JSON con la media móvil calculada, o un mensaje de error.
    """
    print(f"Inicio de la función calculate_moving_average con uuid: {uuid}, start_date: {start_date}, end_date: {end_date}, window: {window}")  # Print de depuración
    start_timestamp = fecha_a_timestamp(start_date)
    end_timestamp = fecha_a_timestamp(end_date)
    if start_timestamp is None or end_timestamp is None:
        return json.dumps({"status": "error", "message": "Fechas inválidas."})

    response = make_api_request(f"api/records/items/{uuid}/{start_timestamp}/{end_timestamp}")
    if response is None or response.status_code != 200:
        return json.dumps({"status": "error", "message": "Error al obtener datos."})

    try:
        items = response.json()
        if "items" in items and "record" in items["items"]:
            values = [item["value"] for item in items["items"]["record"] if isentity(item["value"], (int, float))]
            if values:
                series = pd.Series(values)
                moving_average = series.rolling(window=window, min_periods=1).mean()
                return json.dumps({"status": "success", "moving_average": moving_average.tolist()})
            else:
                return json.dumps({"status": "error", "message": "No hay valores numéricos."})
        else:
            return json.dumps({"status": "error", "message": "No se encontraron datos."})
    except (KeyError, ValueError, TypeError) as e:
         return json.dumps({"status": "error", "message": f"Error al procesar: {str(e)}"})

def calculate_std_deviation(uuid, start_date, end_date):
    """
    Calcula la desviación estándar de los valores de una record de datos en un rango de fechas.

    :param uuid: El ID de la record de datos.
    :param start_date: La fecha de inicio (en formato 'dd-mm-yyyy').
    :param end_date: La fecha de fin (en formato 'dd-mm-yyyy').
    :return: Un JSON con la desviación estándar calculada, o un mensaje de error.
    """
    print(f"Inicio de la función calculate_std_deviation con uuid: {uuid}, start_date: {start_date}, end_date: {end_date}")  # Print de depuración
    start_timestamp = fecha_a_timestamp(start_date)
    end_timestamp = fecha_a_timestamp(end_date)
    if start_timestamp is None or end_timestamp is None:
        return json.dumps({"status": "error", "message": "Fechas inválidas."})

    response = make_api_request(f"api/records/items/{uuid}/{start_timestamp}/{end_timestamp}")
    if response is None or response.status_code != 200:
        return json.dumps({"status": "error", "message": "Error al obtener datos de la API."})

    try:
        items = response.json()
        if "items" in items and "record" in items["items"]:
            values = [item["value"] for item in items["items"]["record"] if isentity(item["value"], (int, float))]
            if values:
                std_dev = np.std(values)
                return json.dumps({"status": "success", "standard_deviation": std_dev})
            else:
                return json.dumps({"status": "error", "message": "No hay valores numéricos para calcular la desviación estándar."})
        else:
            return json.dumps({"status": "error", "message": "No se encontraron datos para el rango de fechas."})
    except (KeyError, ValueError, TypeError) as e:
        return json.dumps({"status": "error", "message": f"Error al procesar los datos: {str(e)}"})

def calculate_percentiles_from_data(items, percentiles=[25, 50, 75]):
    """
    Calcula los percentiles de un conjunto de datos dado.

    :param items: Una lista de valores numéricos.
    :param percentiles: Una lista de percentiles a calcular.
    :return: Un JSON con los percentiles calculados, o un mensaje de error.
    """
    print(f"Inicio de la función calculate_percentiles_from_data con items: {items}, percentiles: {percentiles}")  # Print de depuración
    if not items:
        return json.dumps({"status": "error", "message": "No hay datos para calcular percentiles."})

    try:
        calculated_percentiles = np.percentile(items, percentiles)
        result = {"status": "success"}
        for i, p in enumerate(percentiles):
            result[f"percentile_{p}"] = float(calculated_percentiles[i])
        return json.dumps(result)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error al calcular percentiles: {str(e)}"})

def calculos_estadisticos(uuid, start_date, end_date, tipo_calculo, params=None):
    """
    Realiza cálculos estadísticos sobre una record de datos.

    :param uuid: El ID de la record de datos.
    :param start_date: La fecha de inicio (en formato 'dd-mm-yyyy').
    :param end_date: La fecha de fin (en formato 'dd-mm-yyyy').
    :param tipo_calculo: El tipo de cálculo ('promedio', 'percentiles', 'media_movil', 'desviacion_estandar', 'percentil_media_movil').
    :param params: Atributos adicionales para el cálculo (opcional, depende del tipo de cálculo).
    :return: Un JSON con el resultado del cálculo, o un mensaje de error.
    """
    print(f"Inicio de la función calculos_estadisticos con uuid: {uuid}, start_date: {start_date}, end_date: {end_date}, tipo_calculo: {tipo_calculo}, params: {params}")  # Print de depuración
    start_timestamp = fecha_a_timestamp(start_date)
    end_timestamp = fecha_a_timestamp(end_date)
    if start_timestamp is None or end_timestamp is None:
        return json.dumps({"status": "error", "message": "Fechas inválidas."})

    if tipo_calculo == "promedio":
        return calculate_average(uuid, start_date, end_date)
    elif tipo_calculo == "percentiles":
        percentiles = params.get("percentiles", [25, 50, 75]) if params else [25, 50, 75]
        return calculate_percentiles(uuid, start_date, end_date, percentiles)
    elif tipo_calculo == "media_movil":
        window = params.get("window", 3) if params else 3
        return calculate_moving_average(uuid, start_date, end_date, window)
    elif tipo_calculo == "desviacion_estandar":
        return calculate_std_deviation(uuid, start_date, end_date)
    elif tipo_calculo == "percentil_media_movil":
        window = params.get("window", 3) if params else 3
        ma_result = calculate_moving_average(uuid, start_date, end_date, window)

        if ma_result is None:
            return json.dumps({"status": "error", "message": "Error al calcular la media móvil (resultado None)."})

        try:
            ma_result_json = json.loads(ma_result)
        except json.JSONDecodeError:
            return json.dumps({"status": "error", "message": "Error al decodificar el resultado de la media móvil."})

        if ma_result_json.get("status") != "success":
            return ma_result

        percentiles = params.get("percentiles", [25, 50, 75]) if params else [25, 50, 75]

        moving_average_data = ma_result_json.get("moving_average")

        if not isentity(moving_average_data, list):
            return json.dumps({"status": "error", "message": "El resultado de la media móvil no es una lista."})

        percentiles_result = calculate_percentiles_from_data(moving_average_data, percentiles)
        return percentiles_result

    else:
        return json.dumps({"status": "error", "message": f"Tipo de cálculo desconocido: {tipo_calculo}"})

def get_record_uuid(node, attribute, level, type, entity):
    """
    Construye el ID de una record de datos a partir de sus componentes.

    :param node: El nombre o ID de la nodo.
    :param attribute: El nombre o ID del atributo.
    :param level: El nombre o ID de la nivel.
    :param type: El tipo de dato ('bruto' o 'procesado').
    :param entity: El nombre o ID de la entidad.
    :return: Un JSON con el ID de la record de datos, o un mensaje de error.
    """
    print(f"Inicio de la función get_record_uuid con node: {node}, attribute: {attribute}, level: {level}, type: {type}, entity: {entity}")  # Print de depuración
    node_id = _verificar_existencia("node", node)
    if node_id is None:
        return json.dumps({"error": f"No se encontró la nodo '{node}'"})
    attribute_id = _verificar_existencia("attribute", attribute)
    if attribute_id is None:
        return json.dumps({"error": f"No se encontró el atributo '{attribute}'"})
    level_id = _verificar_existencia("level", level)
    if level_id is None:
        return json.dumps({"error": f"No se encontró la nivel '{level}'"})
    entity_id = _verificar_existencia("entity", entity)
    if entity_id is None:
        return json.dumps({"error": f"No se encontró la entidad '{entity}'"})

    type_id = None
    if type == "bruto":
        type_id = "v"
    elif type == "procesado":
        type_id = "M"
    else:
        return json.dumps({"error": f"Tipo desconocido: '{type}'. Debe ser 'bruto' o 'procesado'."})

    record_uuid = f"{node_id:03}{level_id}{type_id}{attribute_id:04}{entity_id:03}"
    return json.dumps({"record_uuid": record_uuid})

def get_record_with_highcharts(uuid, start_date, end_date):
    """
    Obtiene los datos de una record de datos en formato Highcharts.

    :param uuid: El ID de la record de datos.
    :param start_date: La fecha de inicio (en formato 'dd-mm-yyyy').
    :param end_date: La fecha de fin (en formato 'dd-mm-yyyy').
    :return: Un JSON con los datos de la record de datos en formato Highcharts, o un mensaje de error.  Incluye manejo de truncamiento de datos.
    """
    print(f"Inicio de la función get_record_with_highcharts con uuid: {uuid}, start_date: {start_date}, end_date: {end_date}")  # Print de depuración
    start_timestamp = fecha_a_timestamp(start_date)
    end_timestamp = fecha_a_timestamp(end_date)

    if start_timestamp is None or end_timestamp is None:
        error_message = "Error: Las fechas proporcionadas no son válidas."
        print(error_message)
        return json.dumps({"status": "error", "message": error_message})

    base_url = f"api/records/items/{uuid}/{start_timestamp}/{end_timestamp}?format=highcharts"
    current_url = base_url
    all_values = []
    truncated = False

    while current_url:
        response = make_api_request(current_url)

        if response is None:
            return json.dumps({"status": "error", "message": "No se obtuvo respuesta de la API"})

        try:
            items = response.json()
            if "items" in items and "record" in items["items"]:
                values = [(item["x"], item["y"]) for item in items["items"]["record"]]
                all_values.extend(values)

                if "links" in items and "next" in items["links"]:
                    current_url = items["links"]["next"]
                else:
                    current_url = None
            else:
                return json.dumps({"status": "error", "message": "No se encontraron valores para el rango de fechas especificado"})
        except (KeyError, ValueError) as e:
            return json.dumps({"status": "error", "message": f"Error al procesar la respuesta de la API: {str(e)}"})

    original_values = all_values[:]
    if all_values:
        message = None
        truncated_values = all_values
        while True:
            json_size = sys.getsizeof(truncated_values)
            if json_size <= MAX_JSON_SIZE_BYTES:
                break
            truncated = True
            if len(truncated_values) <= 0:
                return json.dumps({
                    "status": "success",
                    "record_uuid": uuid,
                    "summary": {
                        "record_uuid": uuid,
                        "start_date": start_date,
                        "end_date": end_date,
                        "num_values": len(original_values),
                        "min_value": min(item[1] for item in original_values),
                        "max_value": max(item[1] for item in original_values)
                    },
                    "message": "La información para el gráfico es extensa y no pudo ser incluida en su totalidad. Solo se muestra un resumen."
                })
            truncated_values = truncated_values[:len(truncated_values) // 2]


        if truncated:
            message = "La información para el gráfico es extensa y no pudo ser incluida en su totalidad, solo se muestra una parte."
        else:
            message = ""

        return json.dumps({
            "status": "success",
            "record_uuid": uuid,
            "start_date": start_date,
            "end_date": end_date,
            "values": truncated_values,
            "message": message
        })

    else:
        return json.dumps({"status": "error", "message": "No se encontraron valores para el rango de fechas especificado"})

def get_record_with_csv(uuid, start_date, end_date):
    """
    Obtiene los datos de una record de datos en formato CSV.

    :param uuid: El ID de la record de datos.
    :param start_date: La fecha de inicio (en formato 'dd-mm-yyyy').
    :param end_date: La fecha de fin (en formato 'dd-mm-yyyy').
    :return: Un JSON con los datos de la record de datos en formato CSV, o un mensaje de error.
    """
    print(f"Inicio de la función get_record_with_csv con uuid: {uuid}, start_date: {start_date}, end_date: {end_date}")  # Print de depuración
    start_timestamp = fecha_a_timestamp(start_date)
    end_timestamp = fecha_a_timestamp(end_date)

    if start_timestamp is None or end_timestamp is None:
        return json.dumps({"status": "error", "message": "Error: Las fechas proporcionadas no son válidas."})

    url = f"api/records/items/{uuid}/{start_timestamp}/{end_timestamp}?format=csv"
    response = make_api_request(url)

    if response is None:
        return json.dumps({"status": "error", "message": "No se obtuvo respuesta de la API"})

    if response.status_code != 200:
        return json.dumps({"status": "error", "message": f"Error en la API: {response.status_code} - {response.text}"})

    try:
        csv_content = response.content.decode('utf-8')

        return json.dumps({
            "status": "success",
            "record_uuid": uuid,
            "filename": f"record_{uuid}_{start_date}_{end_date}.csv",
            "csv_data": csv_content,
        })

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error al procesar el CSV: {str(e)}"})


def fetch_record_content_formatted(uuid, output_format, start_date=None, end_date=None, date=None):
    """
    Obtiene los datos de una record de datos en el formato especificado (Highcharts o CSV).

    :param uuid: El ID de la record de datos.
    :param output_format: El formato de salida ('highcharts' o 'csv').
    :param start_date: La fecha de inicio (en formato 'dd-mm-yyyy', opcional si se usa 'date').
    :param end_date: La fecha de fin (en formato 'dd-mm-yyyy', opcional si se usa 'date').
    :param date:  Una fecha específica (en formato 'dd-mm-yyyy', si se usa, se ignoran 'start_date' y 'end_date').
    :return: Un JSON con los datos de la record de datos en el formato solicitado, o un mensaje de error.
    """
    print(f"Inicio de la función fetch_record_content_formatted con uuid: {uuid}, output_format: {output_format}, start_date: {start_date}, end_date: {end_date}, date: {date}")  # Print de depuración
    if date:
        start_date = date
        end_date = date
    if output_format == "highcharts":
        return get_record_with_highcharts(uuid, start_date, end_date)
    elif output_format == "csv":
        return get_record_with_csv(uuid, start_date, end_date)
    else:
        return json.dumps({"error": f"Formato de salida desconocido: {output_format}"})