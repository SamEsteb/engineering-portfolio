from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory, url_for
import os
import logging
import re
from dotenv import load_dotenv
import openai
from openai import OpenAI
from werkzeug.utils import secure_filename
import uuid
import filetype
import requests
from chatbot_logic.ChatBotProjectX import config

print("Iniciando la aplicación - ChatBotProjectX")

log = logging.getLogger(__name__)

def log_message(log_func, message, *args, **kwargs):
    """
    Registra un mensaje, manejando posibles errores de codificación Unicode.

    :param log_func: La función de registro a utilizar (ej. log.info, log.error).
    :param message: El mensaje a registrar.
    :param args: Argumentos posicionales adicionales para la función de registro.
    :param kwargs: Argumentos de palabra clave adicionales para la función de registro.
    """
    try:
        log_func(message, *args, **kwargs)
    except UnicodeEncodeError:
        try:
            if isentity(message, str):
                sanitized_message = message.encode('cp1252', errors='ignore').decode('cp1252', errors='ignore')
            else:
                sanitized_message = str(message).encode('utf-8', 'replace').decode('utf-8', 'ignore')
            log_func(sanitized_message, *args, **kwargs)
        except Exception as e:
            log_func(f"Error al registrar el mensaje: {e}")

projectx_bp = Blueprint('chatbot_projectx', __name__, template_folder='templates', static_folder='static')

client = None
api_key = None
api_key_projectx = None
api_value_projectx = None
api_url_projectx = None
headers = None
CLIENT_CTX = None
USER = None
MAX_JSON_SIZE_BYTES = None
MAX_SUMMARY_ITEMS = None
conversation_histories = {}
INSTRUCTIONS = ""
USER_DOMAIN_CONTEXT = None

def inicializar_projectx():
    """
    Inicializa la aplicación ProjectX, cargando variables de entorno y configurando el cliente de OpenAI.

    Esta función carga las claves de API desde archivos .env, configura el cliente de OpenAI,
    y define las instrucciones para el modelo de lenguaje.
    También verifica la existencia del dominio del usuario en la API de ProjectX.

    :raises ValueError: Si alguna de las variables de entorno requeridas no está configurada.
    :raises Exception: Si ocurre algún otro error durante la inicialización.
    """
    print("inicializar_projectx - Iniciando función")
    global client, api_key, api_key_projectx, api_value_projectx, api_url_projectx, headers, CLIENT_CTX, USER, INSTRUCTIONS, MAX_JSON_SIZE_BYTES, MAX_SUMMARY_ITEMS, USER_DOMAIN_CONTEXT

    try:
        load_dotenv(dotenv_path="api.env")
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada.")
        client = OpenAI(api_key=api_key)
        openai.api_key = api_key

        load_dotenv(dotenv_path="api_projectx.env")
        api_key_projectx = os.getenv("PROJECTX_API_KEY")
        api_value_projectx = os.getenv("PROJECTX_API_VALUE")
        api_url_projectx = os.getenv("PROJECTX_API_URL")
        if not all([api_key_projectx, api_value_projectx, api_url_projectx]):
            raise ValueError("Faltan variables de entorno de ProjectX (PROJECTX_API_KEY, PROJECTX_API_VALUE, PROJECTX_API_URL).")

        CLIENT_CTX = config.CLIENT_CTX
        USER = config.USER
        MAX_JSON_SIZE_BYTES = config.MAX_JSON_SIZE_BYTES
        MAX_SUMMARY_ITEMS = config.MAX_SUMMARY_ITEMS
        USER_DOMAIN_CONTEXT = config.USER_DOMAIN_CONTEXT
        headers = {api_key_projectx: api_value_projectx}

        from chatbot_logic.ChatBotProjectX.funciones_projectx import verificar_dominio_existe
        if not verificar_dominio_existe(CLIENT_CTX):
            log.error(f"El dominio del usuario '{CLIENT_CTX}' no existe.")
            #raise ValueError(f"El dominio del usuario '{CLIENT_CTX}' no existe.")

        INSTRUCTIONS = (
            "Eres un asistente experto en manejar datos de la API ProjectX.\n"
            f"**IMPORTANTE:** Tu contexto de trabajo es: **{config.CLIENT_CTX}**. TODAS tus respuestas deben estar relacionadas con este contexto.\n"
            "**Funciones principales:**\n"
            "- Interpretar mensajes del usuario para determinar la acción correcta.\n"
            "- Extraer y reformatear fechas al formato **DD-MM-YYYY** (si el usuario usa otro formato, conviértelo).\n"
            "- Identificar y construir correctamente los **IDs de records de datos** en el formato **SRTPL** "
            "(SSS = Nodo, R = Nivel, T = Tipo, PPPP = Atributo, LLL = Entidad). "
            " Debes entender cómo se construyen estos IDs y cómo se relacionan con los datos de la API.\n"
            "*Si no se especifica el tipo, asume que es procesado (M).*\n"
            "- **No asumas valores** si el usuario no proporciona toda la información necesaria (fechas, IDs, etc.), "
            "No te inventes los nombres ni identificadores de nodos, atributos, entidades, niveles, etc.\n"
            f"Si **{config.USER_DOMAIN_CONTEXT}** es True, entonces SIEMPRE debes usar la información de contexto para identificar nombres e identificadores de nodos, atributos, entidades, niveles, etc. Por ejemplo, un usuario te puede pedir una nivel horaria y tu debes buscar cual es la forma correcta de llamar a esa nivel dentro de la información, en vez de simplemente asumir que quizás será 'hourly' encontrarás que en realidad es 'hour' gracias al contexto. Si es False, continua solo con la información que te de el usuario o que obtengas de tus consultas.\n"
            "pregunta por la información faltante antes de continuar.\n"
            "- Utilizar **Markdown** para estructurar bien las respuestas.\n"
            "**Consultas Disponibles:**\n"
            "Puedes realizar las siguientes acciones en la API ProjectX:\n"
            "- Obtener nodos por contexto.\n"
            "- Obtener records de datos de un contexto o de una nodo específica.\n"
            "- Consultar datos con nivel, atributo e entidad específicos.\n"
            "- Obtener **uniones e intersecciones** de records de datos con distintos valores de nodo, nivel, atributo o entidad.\n"
            "- Obtener una record de datos por ID con un rango de fechas.\n"
            "- Calcular el **promedio** de valores de un ID de serie entre 2 fechas.\n"
            "- Obtener datos para gráficos Highcharts o archivos CSV.\n"
            "**Gráficos y CSV:**\n"
            "- Si el usuario solicita un gráfico, explica brevemente cómo se debe interpretar.\n"
            "- **NO generes ni muestres imágenes.** Los gráficos deben ser interpretados en Highcharts usando `get_record_with_highcharts`.\n"
            "- **Si obtienes datos CSV, NO los incluyas en tu respuesta.** Solo indica si la obtención fue exitosa o no.\n"
            "**Restricciones y Seguridad:**\n"
            "- **NO respondas preguntas ajenas a la API ProjectX.** Si el usuario pregunta algo fuera de este contexto, indícale que no puedes ayudar con eso.\n"
            "- **NO accedas a archivos externos ni recursos fuera de las funciones proporcionadas.**\n"
            "- **NO generes ni devuelvas imágenes o URLs de imágenes** (especialmente de `cdn.openai.com`).\n"
            "- **Si el usuario solicita información sobre las herramientas disponibles, proporciona una lista de las funciones que puedes usar.**\n"
            "- **Si el usuario solicita información sobre una herramienta específica, proporciona detalles sobre ella.**\n"
            "**Soporte y Ejemplos:**\n"
            "Si el usuario necesita ayuda, proporciona ejemplos de consultas válidas para que entienda cómo interactuar contigo.\n"
            "Si no puedes completar una tarea, notifícalo y ofrece orientación sobre qué información falta.\n"
            "Asegúrate de haber entendido correctamente la solicitud antes de responder.\n"
            "Si el usuario solicita información sobre una herramienta específica, proporciona detalles sobre ella sin revelar información confidencial.\n"
            "Además del chatbot, el chatbot tiene asociado una serie de botones que funcionan a modo de arbol de decisiones, para facilitar la interacción con el usuario.\n"
            "**Objetivo:**\n"
            "Tu prioridad es ser **claro, preciso y eficiente**, estructurando la información de forma clara y consistente.\n"
            "**Usa emojis cuando sea apropiado** para mejorar la comprensión."
        )
        log.info("Variables de entorno cargadas y cliente de OpenAI inicializado.")

    except Exception as e:
        log.exception(f"Error al cargar variables/inicializar: {e}")
        raise

@projectx_bp.route('/')
def projectx_index():
    """
    Renderiza la plantilla principal del chatbot ProjectX.

    :return: La plantilla HTML renderizada.
    """
    print("projectx_index - Iniciando función")
    from chatbot_logic.ChatBotProjectX.bot_estatico import decision_tree

    return render_template('chatbot_projectx.html', endpoint_prefix='/chatbot_projectx', decision_tree=decision_tree)

@projectx_bp.route('/config')
def projectx_config():
    """
    Devuelve la configuración del chatbot en formato JSON.

    :return: Un objeto JSON con la configuración del chatbot.
    """
    print("projectx_config - Iniciando función")
    return jsonify({
        'CLIENT_CTX': CLIENT_CTX,
        'USER': USER,
        'MAX_JSON_SIZE_BYTES': MAX_JSON_SIZE_BYTES,
        'MAX_SUMMARY_ITEMS': MAX_SUMMARY_ITEMS
    })

@projectx_bp.route('/enviar_mensaje', methods=['POST'])
def projectx_send_message():
    """
    Procesa los mensajes enviados por el usuario al chatbot.

    :return: Una respuesta JSON con el resultado del procesamiento del mensaje.
    :raises:
        - ValueError: Si el mensaje esta vacio, si excede los 500 caracteres.
    """
    print("projectx_send_message - Iniciando función")
    from chatbot_logic.ChatBotProjectX.chatbot_projectx import process_conversation, get_conversation_history

    log.info("Mensaje recibido en /projectx/enviar_mensaje")
    items = request.get_json()
    user_message = items.get('message')

    if not user_message or len(user_message) > 500:
        log.warning("Mensaje inválido o demasiado largo.")
        return jsonify({'error': 'Mensaje inválido o demasiado largo.'}), 400

    user_message = user_message.replace("<", "<").replace(">", ">")
    log.info(f"Mensaje del usuario: {user_message}")

    if user_message:
        try:
            conversation_history = get_conversation_history(USER)
            result = process_conversation(user_message, conversation_history, USER, USER_DOMAIN_CONTEXT)

            response_text = result["response"]
            response_data = {
                'response': response_text,
                'status': result["status"],
                'arguments': {},
            }

            if result["chart_data"]:
                response_data['chart_data'] = result["chart_data"]
                if "message" in result["chart_data"]:
                    response_data['incomplete_data_message'] = result["chart_data"]['message']

            if result["usage"]:
                usage_data = {
                    "completion_tokens": result['usage'].completion_tokens,
                    "prompt_tokens": result['usage'].prompt_tokens,
                    "total_tokens": result['usage'].total_tokens,
                }
                response_data['usage'] = usage_data

            log.debug(f"Datos a enviar desde Flask: {response_data}".encode('utf-8', 'replace'))
            return jsonify(response_data), 200

        except Exception as e:
            log.exception(f"Error capturado en projectx_send_message: {e}")
            return jsonify({'error': 'Error al procesar el mensaje.'}), 500
    else:
        log.warning("No se proporcionó ningún mensaje.")
        return jsonify({'error': 'No se proporcionó ningún mensaje.'}), 400

@projectx_bp.route('/borrar_historial', methods=['POST'])
def borrar_historial():
    """
    Borra el historial de conversación del usuario actual.

    :return: Una respuesta JSON indicando el éxito o fracaso de la operación.
    """
    print("borrar_historial - Iniciando función")
    from chatbot_logic.ChatBotProjectX.chatbot_projectx import clear_conversation_history

    log.info("Solicitud recibida para borrar historial")
    items = request.get_json()
    nombre_id = items.get('nombre_id')

    if not nombre_id:
        return jsonify({'error': 'nombre_id no proporcionado'}), 400

    try:
        clear_conversation_history(nombre_id)
        log.info(f"Historial borrado para {nombre_id}")
        return jsonify({'message': 'Historial borrado correctamente'}), 200
    except Exception as e:
        log.exception(f"Error al borrar el historial para {nombre_id}: {e}")
        return jsonify({'error': 'Error al borrar el historial'}), 500

@projectx_bp.route('/guardar_audio', methods=['POST'])
def projectx_guardar_audio():
    """
    Guarda un archivo de audio enviado por el usuario.

    :return: Una respuesta JSON indicando el éxito o fracaso de la operación.
    """
    print("projectx_guardar_audio - Iniciando función")
    if 'audio' in request.files:
        audio_file = request.files['audio']

        kind = filetype.guess(audio_file)
        if kind is None or kind.mime not in ['audio/mpeg', 'audio/wav', 'audio/ogg']:
            return jsonify({'error': 'Tipo de archivo no permitido.'}), 400

        if audio_file.content_length > 5 * 1024 * 1024:
            return jsonify({'error': 'Archivo demasiado grande.'}), 400

        filename = str(uuid.uuid4()) + '.' + kind.extension
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'archivos_audio', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        audio_file.save(filepath)
        return jsonify({'message': 'Archivo de audio guardado correctamente.'}), 200
    else:
        return jsonify({'error': 'No se proporcionó ningún archivo de audio.'}), 400

@projectx_bp.route('/crear_transcripcion', methods=['POST'])
def projectx_crear_transcripcion():
    """
    Crea una transcripción de un archivo de audio enviado por el usuario.

    :return: Una respuesta JSON con la transcripción o un mensaje de error.
    """
    print("projectx_crear_transcripcion - Iniciando función")
    if 'audio' not in request.files:
        return jsonify({'error': 'No se proporcionó ningún archivo de audio.'}), 400

    audio_file = request.files['audio']
    filename = secure_filename(audio_file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'archivos_audio', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    audio_file.save(filepath)

    try:
        with open(filepath, "rb") as audio_file_to_api:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                language="es",
                file=audio_file_to_api,
                response_format="text"
            )
    except Exception as e:
        log.exception(f"Error durante la transcripción: {e}")
        return jsonify({'error': 'Error al procesar la transcripción.'}), 500
    finally:
        os.remove(filepath)

    transcript_text = transcript
    if not transcript_text or len(transcript_text) > 1000:
        return jsonify({'error': 'Transcripción inválida o demasiado larga.'}), 400

    if not re.fullmatch(r"[\s\da-zA-ZáéíóúÁÉÍÓÚñÑ.,;:'\"¿?¡!]+", transcript_text):
        return jsonify({'error': 'La transcripción contiene caracteres no permitidos.'}), 400

    transcript_text = transcript_text.replace("<", "<").replace(">", ">")
    return jsonify({'message': 'Transcripción creada correctamente.', 'transcriptionText': transcript_text}), 200

@projectx_bp.route('/describe_image', methods=['POST'])
def projectx_describe_image():
    """
    Describe una imagen enviada por el usuario utilizando el modelo GPT-4 Vision de OpenAI.

    :return: Una respuesta JSON con la descripción de la imagen o un mensaje de error.
    """
    print("projectx_describe_image - Iniciando función")
    from chatbot_logic.ChatBotProjectX.chatbot_projectx import encode_image, limpiar_descripcion

    if 'image' in request.files:
        image_file = request.files['image']

        kind = filetype.guess(image_file)
        if kind is None or kind.mime not in ['image/jpeg', 'image/png', 'image/gif']:
            return jsonify({'error': 'Tipo de archivo no permitido.'}), 400

        if image_file.content_length > 1 * 1024 * 1024:
            return jsonify({'error': 'Archivo demasiado grande.'}), 400

        filename = str(uuid.uuid4()) + '.' + (kind.extension if kind else 'jpg')
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        image_file.save(filepath)

        base64_image = encode_image(filepath)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe el problema si es que hay en la imagen y dame posibles soluciones, de manera bastante resumida. Los problemas que encuentres deben estar relacionados con X. Sobre todo, con mediciones de X, Y, Z. Si no encuentras problemas, puedes describir la imagen de manera general, siempre que tenga que ver con X."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"items:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            json_data = response.json()
            description = json_data['choices'][0]['message']['content']
            description = limpiar_descripcion(description)

            if not description.strip() or len(description.split()) < 5 or len(description) > 1500:
                return jsonify({'error': 'Descripción inválida o demasiado larga.'}), 400

            return jsonify({
                'description': description,
                'image_url': url_for('chatbot_projectx.uploaded_file', filename=filename)
            })
        else:
            log.error(f"Error de OpenAI: {response.status_code} - {response.text}")
            return jsonify({'error': f'Error de OpenAI: {response.status_code} - {response.text}'}), response.status_code
    else:
        return jsonify({'error': 'No se proporcionó ninguna imagen'}), 400

@projectx_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Sirve un archivo estático desde la carpeta de uploads.

    :param filename: El nombre del archivo a servir.
    :return: El archivo solicitado.
    """
    print("uploaded_file - Iniciando función")
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@projectx_bp.route('/static_bot', methods=['POST'])
def static_bot():
    """
    Maneja las peticiones al bot estático.

    :return: Una respuesta JSON con la información del nodo actual del árbol de decisión.
    """
    print("static_bot - Iniciando función")
    from chatbot_logic.ChatBotProjectX.bot_estatico import static_bot as static_bot_logic
    return static_bot_logic()

@projectx_bp.route('/static_data/<data_source>', methods=['GET'])
def static_data(data_source):
    """
    Obtiene datos estáticos para poblar los menús desplegables del bot estático.

    :param data_source: El tipo de datos a obtener ('node', 'attribute', etc.).
    :return: Una respuesta JSON con los datos solicitados.
    """
    print("static_data - Iniciando función")
    from chatbot_logic.ChatBotProjectX.bot_estatico import static_data as static_data_logic
    return static_data_logic(data_source)

@projectx_bp.route('/static_data/consultar', methods=['POST'])
def consultar():
    """
    Consulta records de datos basadas en los filtros seleccionados por el usuario.

    :return: Una respuesta JSON con las records de datos encontradas.
    """
    print("consultar - Iniciando función")
    from chatbot_logic.ChatBotProjectX.bot_estatico import consultar as consultar_logic
    return consultar_logic()

@projectx_bp.route('/static_data/process_records', methods=['POST'])
def process_records():
    """
    Procesa una record de datos para graficarla o descargarla.

    :return: Una respuesta JSON con los datos de la record de datos en el formato solicitado.
    """
    print("process_records - Iniciando función")
    from chatbot_logic.ChatBotProjectX.bot_estatico import process_records as process_records_logic
    return process_records_logic()

@projectx_bp.route('/static_data/calcular', methods=['POST'])
def calcular():
    """
    Realiza cálculos estadísticos sobre una record de datos.

    :return: Una respuesta JSON con el resultado del cálculo.
    """
    print("calcular - Iniciando función")
    from chatbot_logic.ChatBotProjectX.bot_estatico import calcular as calcular_logic
    return calcular_logic()

@projectx_bp.route('/static_data/process_statistics', methods=['POST'])
def process_statistics():
    """
    Procesa cálculos estadísticos sobre una record de datos.

    :return: Una respuesta JSON con los datos de la record de datos en el formato solicitado.
    """
    print("process_statistics - Iniciando función")
    from chatbot_logic.ChatBotProjectX.bot_estatico import process_statistics as process_statistics_logic
    return process_statistics_logic()