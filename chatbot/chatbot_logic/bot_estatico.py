from flask import jsonify, request
from chatbot_logic.ChatBotProjectX.funciones_projectx import (
    make_api_request, query_record_set,
    calculos_estadisticos, fetch_record_content_formatted
)
from chatbot_logic.ChatBotProjectX.projectx import CLIENT_CTX
import json
import datetime


decision_tree_base = {
    "uuid": "base",
    "pregunta": "¿Qué deseas hacer?",
    "opciones": [
        {"uuid": "1", "respuesta": "Ver nodos", "input_type": "button", "data_source": None, "siguiente": "1.1"},
        {"uuid": "2", "respuesta": "Consultar datos", "input_type": "button", "data_source": None, "siguiente": "2.1"},
        #{"uuid": "3", "respuesta": "Información", "input_type": "button", "data_source": None, "siguiente": "3.1"}
    ],
    "input_type": None,
    "data_source": None
}

node_1_1 = {
    "uuid": "1.1",
    "pregunta": "",
    "opciones": [
      {"uuid": "1.1", "respuesta": "Consultar", "siguiente": "2.2", "input_type": "button", "data_source": None},
      {"uuid": "1.2", "respuesta": "volver", "siguiente": "base", "input_type": "button", "data_source": None}
    ],
    "input_type": "search_select",
    "data_source": "node"
}

node_2_1 = {
    "uuid": "2.1",
    "pregunta": "Selecciona los filtros para tu consulta.",
    "opciones": [
        {"uuid": "2.1.1", "respuesta": "Nodo", "input_type": "select", "data_source": "node"},
        {"uuid": "2.1.2", "respuesta": "Atributo", "input_type": "select", "data_source": "attribute"},
        {"uuid": "2.1.3", "respuesta": "Nivel", "input_type": "select", "data_source": "level"},
        {"uuid": "2.1.4", "respuesta": "Entidad", "input_type": "select", "data_source": "entity"},
        {"uuid": "2.1.5", "respuesta": "Consultar", "siguiente": "2.2", "input_type": "button", "data_source": None},
        {"uuid": "2.1.6", "respuesta": "volver", "siguiente": "base", "input_type": "button", "data_source": None}
    ],
    "input_type": None,
    "data_source": "datos"
}

node_2_2 = {
    "uuid": "2.2",
    "pregunta": "Lista de Grupos de Datos",
    "opciones": [
      {"uuid": "2.2.1", "respuesta": "Consultar", "siguiente": "2.3", "input_type": "button", "data_source": None},
      {"uuid": "2.2.2", "respuesta": "volver", "siguiente": "2.1", "input_type": "button", "data_source": None}
    ],
    "input_type": "search_select",
    "data_source": "records"
}

node_2_3 = {
    "uuid": "2.3",
    "pregunta": "¿Cómo desea ver los datos?",
    "opciones": [
        {"uuid": "2.3.2", "respuesta": "Graficar", "siguiente": "2.4", "input_type": "button", "data_source": None},
        {"uuid": "2.3.3", "respuesta": "Descargar", "siguiente": "2.4", "input_type": "button", "data_source": None},
        {"uuid": "2.3.4", "respuesta": "volver", "siguiente": "2.1", "input_type": "button", "data_source": None}
        ],
    "input_type": "date_range",
    "data_source": None,
}

node_2_4 = {
    "uuid": "2.4",
    "pregunta": "¿Desea consultar datos estadísticos de estos datos?",
    "opciones": [
        {"uuid": "2.4.1", "respuesta": "Promedio", "siguiente": "2.5", "input_type": "button", "data_source": None},
        {"uuid": "2.4.2", "respuesta": "Desviación Estándar", "siguiente": "2.5", "input_type": "button", "data_source": None},
        {"uuid": "2.4.3", "respuesta": "Percentiles", "siguiente": "2.6", "input_type": "button", "data_source": None},
        {"uuid": "2.4.4", "respuesta": "Media Móvil", "siguiente": "2.7", "input_type": "button", "data_source": None},
        {"uuid": "2.4.5", "respuesta": "Percentil de Media Móvil", "siguiente": "2.8", "input_type": "button", "data_source": None},
        {"uuid": "2.4.6", "respuesta": "volver", "siguiente": "2.3", "input_type": "button", "data_source": None}
    ],
    "input_type": None,
    "data_source": None
}

node_2_5 = {
    "uuid": "2.5",
    "pregunta": "El resultado del cálculo estadístico es: ",
    "opciones": [
        {"uuid": "2.5.1", "respuesta": "volver", "siguiente": "2.4", "input_type": "button", "data_source": None}
    ],
    "input_type": None,
    "data_source": None
}

node_2_6 = {
    "uuid": "2.6",
    "pregunta": "¿Qué percentil desea calcular?",
    "opciones": [
        {"uuid": "2.6.1", "respuesta": "Percentil", "input_type": "select_number", "data_source": "percentile"},
        {"uuid": "2.6.2", "respuesta": "Calcular", "siguiente": "2.5", "input_type": "button", "data_source": None},
        {"uuid": "2.6.3", "respuesta": "volver", "siguiente": "2.4", "input_type": "button", "data_source": None}
    ],
    "input_type": None,
    "data_source": "percentil"
}

node_2_7 = {
    "uuid": "2.7",
    "pregunta": "Selecciona la ventana para la media móvil.",
    "opciones": [
        {"uuid": "2.7.1", "respuesta": "Ventana", "input_type": "select_number", "data_source": "window"},
        {"uuid": "2.7.2", "respuesta": "Calcular", "siguiente": "2.5", "input_type": "button", "data_source": None},
        {"uuid": "2.7.3", "respuesta": "volver", "siguiente": "2.4", "input_type": "button", "data_source": None}
    ],
    "input_type": None,
    "data_source": "ventana"
}

node_2_8 = {
    "uuid": "2.8",
    "pregunta": "Selecciona el percentil y la ventana para la media móvil.",
    "opciones": [
        {"uuid": "2.8.1", "respuesta": "Ventana", "input_type": "select_number", "data_source": "window"},
        {"uuid": "2.8.2", "respuesta": "Percentil", "input_type": "select_number", "data_source": "percentile"},
        {"uuid": "2.8.3", "respuesta": "Calcular", "siguiente": "2.5", "input_type": "button", "data_source": None},
        {"uuid": "2.8.4", "respuesta": "volver", "siguiente": "2.4", "input_type": "button", "data_source": None}
    ],
    "input_type": None,
    "data_source": "percentil y ventana"
}

decision_tree = [decision_tree_base, node_1_1, node_2_1, node_2_2, node_2_3, node_2_4, node_2_5, node_2_6, node_2_7, node_2_8]

def get_node_flask(node_id, tree):
    """
    Obtiene un nodo del árbol de decisión dado su ID.

    :param node_id: El ID del nodo a buscar.
    :param tree: El árbol de decisión en el que buscar.
    :return: El nodo encontrado, o None si no se encuentra.
    """
    for node in tree:
        if node["uuid"] == node_id:
            return node
    return None


def process_static_bot_request(node_id):
    """
    Procesa una petición para el bot estático, devolviendo el nodo correspondiente del árbol de decisión.

    :param node_id: El ID del nodo solicitado.
    :return: Un diccionario con la información del nodo, o un mensaje de error si no se encuentra.
    """
    node = get_node_flask(node_id, decision_tree)
    if not node:
        return {"error": "Nodo no encontrado"}
    return node

def get_data_for_select(data_source):
    """
    Obtiene datos para poblar un menú desplegable del bot estático.

    :param data_source: El tipo de datos a obtener ('node', 'attribute', 'level', 'entity', 'records').
    :return: Una lista de strings con los datos, o una lista vacía si hay un error.
    """
    if data_source == "node":
        response = make_api_request(f"api/list")
        if response and response.status_code == 200:
            items = response.json()
            return [item["label"] for item in items.get("items", [])]
        else:
            return []

    elif data_source == "attribute":
        response = make_api_request(f"api/attributes")
        if response and response.status_code == 200:
            items = response.json()
            return [item["label"] for item in items.get("items", [])]
        else:
            return []

    elif data_source == "level":
        response = make_api_request(f"api/levels")
        if response and response.status_code == 200:
            items = response.json()
            return [item["label"] for item in items.get("items", [])]
        else:
            return []

    elif data_source == "entity":
        response = make_api_request(f"api/nodes")
        if response and response.status_code == 200:
            items = response.json()
            return [item["label"] for item in items.get("items", [])]
        else:
            return []
    elif data_source == "records":
        return []

    else:
        return []



def static_bot():
    """
    Maneja las peticiones al bot estático, procesando la solicitud y devolviendo el nodo correspondiente.

    :return: Una respuesta JSON con la información del nodo actual del árbol de decisión.
    """
    items = request.get_json()
    node_id = items.get('node_id', 'base')
    response_data = process_static_bot_request(node_id)
    return jsonify(response_data)

def static_data(data_source):
    """
    Obtiene datos estáticos para poblar los menús desplegables del bot estático.

    :param data_source: El tipo de datos a obtener ('node', 'attribute', etc.).
    :return: Una respuesta JSON con los datos solicitados.
    """
    items = get_data_for_select(data_source)
    return jsonify(items)

def consultar():
    """
    Consulta records de datos basadas en los filtros seleccionados por el usuario en el bot estático.

    :return: Una respuesta JSON con las records de datos encontradas, o un mensaje de error.
    """
    items = request.get_json()
    print(f"Items: {items}")
    query_type = items.get('query_type')
    query_value = items.get('query_value')
    additional_filters = items.get('additional_filters')
    result = query_record_set(query_type, query_value, additional_filters)

    try:
        result_json = json.loads(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Respuesta inválida de query_record_set"}), 500

    if "records" not in result_json:
        return jsonify({"error": "No se encontraron records de datos"}), 404

    processed_records = []
    for ts in result_json["records"]:
        try:
            begin_date = datetime.datetime.fromtimestamp(ts.get('begin', 0)).strftime('%d-%m-%Y') if ts.get('begin') else ''
            end_date = datetime.datetime.fromtimestamp(ts.get('end', 0)).strftime('%d-%m-%Y') if ts.get('end') else ''
            processed_records.append({
                "uuid": ts.get('uuid', ''),
                "date_range": f"{begin_date} a {end_date}"
            })
        except (TypeError, ValueError):
          return jsonify({"error": "Error al procesar las fechas de una record de datos"}), 500

    result_json["records"] = processed_records

    return jsonify(result_json)


def process_records():
    """
    Procesa una record de datos seleccionada por el usuario para graficarla o descargarla.

    :return: Una respuesta JSON con los datos de la record de datos en el formato solicitado (Highcharts o CSV), o un mensaje de error.
    """
    items = request.get_json()
    record_uuid = items.get('record_uuid')
    start_date = items.get('start_date')
    end_date = items.get('end_date')
    action = items.get('action')

    if not all([record_uuid, start_date, end_date, action]):
        return jsonify({"error": "Faltan atributos"}), 400

    if action == 'graficar':
        formatted_data = fetch_record_content_formatted(record_uuid, "highcharts", start_date, end_date)
    elif action == 'descargar':
        formatted_data = fetch_record_content_formatted(record_uuid, "csv", start_date, end_date)
    else:
        return jsonify({"error": f"Acción desconocida: {action}"}), 400

    try:
        formatted_data_json = json.loads(formatted_data)
    except json.JSONDecodeError:
        return jsonify({"error": "Respuesta inválida de fetch_record_content_formatted"}), 500

    return jsonify(formatted_data_json)


def calcular():
    """
    Realiza cálculos estadísticos sobre una record de datos seleccionada por el usuario.

    :return: Una respuesta JSON con el resultado del cálculo, o un mensaje de error.
    """
    items = request.get_json()
    record_uuid = items.get('record_uuid')
    start_date = items.get('start_date')
    end_date = items.get('end_date')
    tipo_calculo = items.get('tipo_calculo')
    params = items.get('params', {})

    if not all([record_uuid, start_date, end_date, tipo_calculo]):
        return jsonify({"error": "Faltan atributos obligatorios."}), 400

    result = calculos_estadisticos(record_uuid, start_date, end_date, tipo_calculo, params)

    try:
        result_json = json.loads(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Respuesta inválida de calculos_estadisticos"}), 500
    return jsonify(result_json)


def process_statistics():
    """
    Procesa cálculos estadísticos sobre una record de datos (duplicado de 'calcular', podría eliminarse).

    :return: Una respuesta JSON con el resultado del cálculo, o un mensaje de error.
    """
    items = request.get_json()
    record_uuid = items.get('record_uuid')
    start_date = items.get('start_date')
    end_date = items.get('end_date')
    tipo_calculo = items.get('tipo_calculo')
    params = items.get('params', {})

    if not all([record_uuid, start_date, end_date, tipo_calculo]):
        return jsonify({"error": "Faltan atributos obligatorios."}), 400

    result = calculos_estadisticos(record_uuid, start_date, end_date, tipo_calculo, params)
    try:
        result_json = json.loads(result)
    except json.JSONDecodeError:
        return jsonify({"error": "Respuesta inválida de calculos_estadisticos"}), 500
    return jsonify(result_json)