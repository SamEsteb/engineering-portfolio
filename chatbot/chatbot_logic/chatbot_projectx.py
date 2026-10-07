import openai
import json
import re
import base64
import concurrent.futures
import os  # Importa el módulo os
from chatbot_logic.ChatBotProjectX.funciones_projectx import (
    fetch_context_items, query_record_set, calculos_estadisticos,
    get_record_uuid, fetch_record_content_formatted
)
from chatbot_logic.ChatBotProjectX.projectx import client, INSTRUCTIONS, CLIENT_CTX


def verificar_api_key():
    """
    Verifica que la clave de API de OpenAI esté configurada.

    :raises ValueError: Si la clave de API no está configurada.
    :return: api_key: La clave de la API de OpenAI
    """
    print("verificar_api_key - Iniciando función")
    api_key = openai.api_key
    if not api_key:
        raise ValueError("La API key de OpenAI no está configurada.  Configura la variable de entorno OPENAI_API_KEY.")
    return api_key

def create_system_message(additional_context=None):
    """
    Crea el mensaje del sistema, manejando correctamente el contexto.

    :param additional_context:  Contexto adicional (str) a incluir.
    :return: Un diccionario con el rol y el contenido del mensaje del sistema.
    """
    print("create_system_message - Iniciando función")

    # Construye el contenido base (instrucciones)
    content = [{"type": "text", "text": INSTRUCTIONS}]

    # Agrega el contexto adicional si existe
    if additional_context:
        content.append({"type": "text", "text": additional_context})

    return {"role": "system", "content": content}


def load_domain_context(client_ctx):
    """
    Carga el contexto específico del dominio desde archivos .txt.

    :param client_ctx: El dominio del usuario (nombre de la subcarpeta).
    :return: Una cadena con el contenido concatenado de los archivos, o None si no hay archivos.
    """
    print(f"load_domain_context - Iniciando función para el dominio: {client_ctx}")
    context_dir = os.path.join("projectx_data", client_ctx)
    context_texts = []

    if os.path.exists(context_dir) and os.path.isdir(context_dir):
        for filename in os.listdir(context_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(context_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        context_texts.append(f.read())
                except Exception as e:
                    print(f"Error al leer el archivo {filepath}: {e}")
    else:
        print(f"load_domain_context - No se encontró la carpeta: {context_dir}")
        return None  # No existe la carpeta

    if not context_texts:
        print(f"load_domain_context - No se encontraron archivos .txt en: {context_dir}")
        return None  # No hay archivos .txt

    return "\n\n".join(context_texts)

def generate_chat_completion(messages, tool_calls=None):
    """
    Genera una respuesta del modelo de lenguaje a partir de una lista de mensajes.

    :param messages: Una lista de diccionarios que representan la conversación hasta el momento.
    :param tool_calls: Una lista de herramientas (funciones) que el modelo puede utilizar (opcional).
    :return: Una tupla con el mensaje de respuesta y los datos de uso de la API, o (None, None) si hay un error.
    """
    print("generate_chat_completion - Iniciando función")
    try:
        kwargs = {
            "model": "gpt-4-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
        }
        if tool_calls:
            kwargs["tools"] = tool_calls
            kwargs["tool_choice"] = "auto"

        response = client.chat.completions.create(**kwargs)

        response_message = response.choices[0].message
        usage_data = response.usage

        return response_message, usage_data

    except openai.APIError as e:
        print(f"Error de la API de OpenAI: {e}")
        return None, None
    except Exception as e:
        print(f"Error inesperado en generate_chat_completion: {e}")
        return None, None

def execute_function(func_name, arguments):
    """
    Ejecuta una función de la API de ProjectX dado su nombre y argumentos.

    :param func_name: El nombre de la función a ejecutar.
    :param arguments: Un diccionario con los argumentos de la función.
    :return: El resultado de la función, o un mensaje de error si la función no existe.
    """
    print("execute_function - Iniciando función")
    if func_name == "fetch_context_items":
        return fetch_context_items(arguments.get("data_type"))
    elif func_name == "query_record_set":
        return query_record_set(
            arguments.get("query_type"),
            arguments.get("query_value"),
            arguments.get("additional_filters"),
            arguments.get("combination_type", "intersection")
        )
    elif func_name == "calculos_estadisticos":
        return calculos_estadisticos(
            arguments.get("uuid"),
            arguments.get("start_date"),
            arguments.get("end_date"),
            arguments.get("tipo_calculo"),
            arguments.get("params"),
        )
    elif func_name == "get_record_uuid":
        return get_record_uuid(
            arguments.get("node"),
            arguments.get("attribute"),
            arguments.get("level"),
            arguments.get("type"),
            arguments.get("entity"),
        )
    elif func_name == "fetch_record_content":
        return fetch_record_content_formatted(
            arguments.get("uuid"),
            arguments.get("output_format"),
            start_date=arguments.get("start_date"),
            end_date=arguments.get("end_date"),
            date=arguments.get("date"),
        )
    else:
        print(f"Función desconocida: {func_name}")
        return f"Error: Función desconocida '{func_name}'"

def process_tool_calls(tool_calls):
    """
    Procesa las llamadas a herramientas (funciones) realizadas por el modelo de lenguaje.

    :param tool_calls: Una lista de objetos ToolCall del mensaje de respuesta del modelo.
    :return: Una tupla con:
        - Una lista de resultados de las llamadas a herramientas.
        - Un diccionario con los datos de la API obtenidos por las herramientas.
        - None (reservado para futuros usos).
    """
    print("process_tool_calls - Iniciando función")
    results = []
    api_data = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                execute_function, action.function.label, json.loads(action.function.arguments)
            ): action
            for action in tool_calls
        }

        for future in concurrent.futures.as_completed(futures):
            action = futures[future]
            try:
                result = future.result()
                arguments = json.loads(action.function.arguments)
                try:
                    result_json = json.loads(result)
                except json.JSONDecodeError:
                    result_json = result

                if isentity(result_json, dict):
                    api_data.update(result_json)

                if action.function.label == "fetch_record_content":
                    if arguments.get("output_format") == "csv":
                        output_for_openai = {
                            "status": result_json.get("status", "error"),
                        }
                    elif isentity(result_json, dict) and ("values" in result_json or "summary" in result_json or "csv_data" in result_json):
                        output_for_openai = {
                            "status": result_json.get("status", "success"),
                            "record_uuid": result_json.get("record_uuid", ""),
                            "message": result_json.get("message", "Datos del gráfico enviados directamente.")
                        }
                    else:
                        output_for_openai = {"status": "error", "message": "Error interno."}

                elif action.function.label == "calculos_estadisticos":
                    if isentity(result_json, dict) and "status" in result_json:
                        if result_json["status"] == "success":
                            tipo_calculo = arguments.get("tipo_calculo")
                            if tipo_calculo == "promedio":
                                message = f"El promedio calculado es: {result_json.get('average')}"
                            elif tipo_calculo == "percentiles":
                                message = "Percentiles calculados: " + ", ".join(
                                    [f"{p}: {result_json.get(f'percentile_{p}')}" for p in arguments.get("params", {}).get("percentiles", [])]
                                )
                            elif tipo_calculo == "desviacion_estandar":
                                 message = f"La desviación estándar calculada es: {result_json.get('standard_deviation')}"
                            elif tipo_calculo == "media_movil":
                                message = "Media móvil calculada (datos enviados directamente para graficación)."
                            elif tipo_calculo == "percentil_media_movil":
                                percentiles = arguments.get("params", {}).get("percentiles", [])
                                message = "Percentiles de la media móvil calculados: " + ", ".join([f"{p}: {result_json.get(f'percentile_{p}')}" for p in percentiles])
                            else:
                                message = "Cálculo estadístico realizado."
                        else:
                            message = result_json.get("message", "Error en el cálculo.")
                        output_for_openai = {
                            "status": result_json["status"],
                            "message": message,
                        }
                    else:
                        output_for_openai = {"status": "error", "message": "Error interno."}

                else:
                    output_for_openai = {}
                    for key, value in result_json.items():
                        if key.endswith('_summary'):
                            output_for_openai[key] = value
                    if not output_for_openai:
                        output_for_openai = result_json
                results.append(
                    {
                        "tool_call_id": action.uuid,
                        "output": json.dumps(output_for_openai),
                    }
                )

            except Exception as e:
                print(f"Error al ejecutar la función: {e}")
                results.append(
                    {
                        "tool_call_id": action.uuid,
                        "output": json.dumps({"status": "error", "message": "Error al ejecutar la función"}),
                    }
                )

    return results, api_data, None

tools_list = [
     {
        "type": "function",
        "function": {
            "label": "fetch_context_items",
            "description": "Obtiene nodos o records de datos.",
            "attributes": {
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "enum": ["nodes", "records"],
                        "description": "Tipo de datos: 'nodes' o 'records'."
                    }
                },
                "required": ["data_type"]
            }
        }
    },
     {
        "type": "function",
        "function": {
            "label": "query_record_set",
            "description": "Obtiene records de datos filtradas por tipo de consulta y valor.  Opcionalmente, se pueden agregar filtros adicionales. También, sirve de acercamiento a los datos, si un usuario quiere los datos, pero no sabe que ID tiene la record de datos, entonces se debe usar esta función para entregarles estas records de datos.",
            "attributes": {
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": ["node", "level", "attribute", "entity"],
                        "description": "Tipo de consulta principal (obligatorio)."
                    },
                    "query_value": {
                        "type": "string",
                        "description": "Valor para el tipo de consulta principal (obligatorio)."
                    },
                    "additional_filters": {
                        "type": "object",
                        "description": "Filtros adicionales (opcional).",
                        "properties": {
                            "node": {"type": "string", "description": "Nodo."},
                            "level": {"type": "string", "description": "Nivel."},
                            "attribute": {"type": "string", "description": "Atributo."},
                            "entity": {"type": "string", "description": "Entidad."},
                             "type": {
                                "type": "string",
                                "enum": ["bruto", "procesado"],
                                "description": "Tipo de dato: 'bruto' o 'procesado'."
                            }
                        }
                    }
                },
                "required": ["query_type", "query_value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "label": "calculos_estadisticos",
            "description": "Realiza cálculos estadísticos sobre una record de datos.",
            "attributes": {
                "type": "object",
                "properties": {
                    "uuid": {"type": "string", "description": "ID de la record de datos."},
                    "start_date": {"type": "string", "description": "Fecha de inicio."},
                    "end_date": {"type": "string", "description": "Fecha de fin."},
                    "tipo_calculo": {
                        "type": "string",
                        "enum": ["promedio", "percentiles", "media_movil", "desviacion_estandar", "percentil_media_movil"],
                        "description": "Tipo de cálculo estadístico a realizar."
                    },
                    "params": {
                        "type": "object",
                        "description": "Atributos adicionales para el cálculo (opcional).",
                        "properties": {
                            "percentiles": {
                                "type": "array",
                                "items": {"type": "integer"},
                                "description": "Lista de percentiles (ej. [25, 50, 75])."
                            },
                            "window": {
                                "type": "integer",
                                "description": "Tamaño de la ventana para la media móvil."
                            }
                        }
                    }
                },
                "required": ["uuid", "start_date", "end_date", "tipo_calculo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "label": "get_record_uuid",
            "description": "Obtiene el ID de una record de datos (formato SSSRTPPPPLLL) a partir de nodo, atributo, nivel, tipo e entidad.",
            "attributes": {
                "type": "object",
                "properties": {
                    "node": {"type": "string", "description": "Nodo."},
                    "attribute": {"type": "string", "description": "Atributo."},
                    "level": {"type": "string", "description": "Nivel."},
                    "type": {"type": "string", "description": "Tipo ('bruto' o 'procesado')."},
                    "entity": {"type": "string", "description": "Entidad."},
                },
                "required": ["node", "attribute", "level", "type", "entity"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "label": "fetch_record_content",
            "description": "Obtiene datos de records de datos para un rango de fechas o una fecha específica, en formato Highcharts o CSV.",
            "attributes": {
                "type": "object",
                "properties": {
                    "uuid": {
                        "type": "string",
                        "description": "ID de la record de datos (obligatorio). Formato: SSSRTPPPPLLL."
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Fecha de inicio (ignorada si se usa 'date')."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Fecha de fin (ignorada si se usa 'date')."
                    },
                    "date": {
                        "type": "string",
                        "description": "Fecha específica (si se usa, se ignoran 'start_date' y 'end_date')."
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["highcharts", "csv"],
                        "description": "Formato de salida ('highcharts' o 'csv')."
                    }
                },
                "required": [
                    "uuid",
                    "output_format"
                ]
            }
        }
    }
]

def process_conversation(user_message, conversation_history, nombre_id, use_domain_context=False):
    """
    Procesa una conversación con el modelo de lenguaje, incluyendo llamadas a herramientas.

    :param user_message: El mensaje del usuario.
    :param conversation_history: El historial de conversación.
    :param nombre_id: El identificador del usuario.
    :param use_domain_context:  Indica si se debe usar el contexto del dominio (True/False).
    :return: Un diccionario con el resultado del procesamiento.
    """
    print("process_conversation - Iniciando función")
    conversation_history.append({"role": "user", "content": user_message})

    while True:
        # Carga el contexto del dominio *antes* de crear el mensaje del sistema
        print("use_domain_context:", use_domain_context)
        additional_context = load_domain_context(CLIENT_CTX) if use_domain_context else None
        messages = [create_system_message(additional_context)] + conversation_history
        chat_response, usage_data = generate_chat_completion(messages, tool_calls=tools_list)

        if chat_response is None:
            return {
                "status": False,
                "response": "Hubo un error al comunicarse con OpenAI.",
                "chart_data": None,
                "conversation_history": conversation_history,
                "usage": None,
            }

        if chat_response.tool_calls:
            tool_outputs, api_data, _ = process_tool_calls(chat_response.tool_calls)
            conversation_history.append(chat_response)
            messages.append(chat_response)

            for tool_output in tool_outputs:
                 conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_output["tool_call_id"],
                    "content": tool_output["output"],
                })
                 messages.append({
                    "role": "tool",
                    "tool_call_id": tool_output["tool_call_id"],
                    "content": tool_output["output"],
                })

            final_response, final_usage_data = generate_chat_completion(messages)
            if final_response is None:
                return {
                    "status": False,
                    "response": "Hubo un error al obtener la respuesta final.",
                    "chart_data": api_data,
                    "conversation_history": conversation_history,
                    "usage": usage_data
                }

            conversation_history.append(final_response)
            final_response_text = final_response.content
            combined_usage_data = usage_data
            if final_usage_data:
                combined_usage_data.completion_tokens += final_usage_data.completion_tokens
                combined_usage_data.prompt_tokens += final_usage_data.prompt_tokens
                combined_usage_data.total_tokens += final_usage_data.total_tokens

            return {
                "status": True,
                "response": final_response_text,
                "chart_data": api_data,
                "conversation_history": conversation_history,
                "usage": combined_usage_data,
            }

        else:
            response_text = chat_response.content
            conversation_history.append({"role": "assistant", "content": response_text})
            return {
                "status": True,
                "response": response_text,
                "chart_data": None,
                "conversation_history": conversation_history,
                "usage": usage_data,
            }

def get_conversation_history(nombre_id):
    """
    Obtiene el historial de conversación de un usuario.

    :param nombre_id: El identificador del usuario.
    :return: Una lista con los mensajes del historial de conversación.
    """
    print("get_conversation_history - Iniciando función")
    from chatbot_logic.ChatBotProjectX.projectx import conversation_histories

    if nombre_id not in conversation_histories:
        conversation_histories[nombre_id] = []
    return conversation_histories[nombre_id]


def clear_conversation_history(nombre_id):
    """
    Borra el historial de conversación de un usuario.

    :param nombre_id: El identificador del usuario.
    """
    print("clear_conversation_history - Iniciando función")
    from chatbot_logic.ChatBotProjectX.projectx import conversation_histories

    if nombre_id in conversation_histories:
        del conversation_histories[nombre_id]



def encode_image(image_path):
    """
    Codifica una imagen en base64.

    :param image_path: La ruta a la imagen.
    :return: La imagen codificada en base64 como una cadena de texto.
    """
    print("encode_image - Iniciando función")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def limpiar_descripcion(descripcion):
    """
    Limpia una descripción de texto eliminando URLs, caracteres especiales y espacios extra.

    :param descripcion: La descripción a limpiar.
    :return: La descripción limpia.
    """
    print("limpiar_descripcion - Iniciando función")
    descripcion = re.sub(r'http\S+', '', descripcion)
    replacements = {
        '“': '"', '”': '"', '‘': "'", '’': "'", '…': '...',
        '—': '-', '\xa0': ' ', '«': '"', '»': '"',
    }
    for char, replacement in replacements.items():
        descripcion = descripcion.replace(char, replacement)
    descripcion = re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ.,;:'\"¿?¡! *()\n\-]", "", descripcion)
    descripcion = re.sub(r' +', ' ', descripcion).strip()
    return descripcion