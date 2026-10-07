# Descripción: Configuración de la aplicación ChatBotProjectX
CLIENT_CTX = "DOM_NAME" # Dominio de la API de ProjectX en la que trabajará el usuario.
USER = "user" # ID de usuario en el chatbot
MAX_SUMMARY_ITEMS = 10 # Número máximo de elementos abstraídos del total de la consulta, para limitar la cantidad de información que procesa el ChatBot.
MAX_JSON_SIZE_BYTES = 512 * 1024  # Tamaño máximo en bytes de la respuesta JSON generada por el ChatBot (512kb).
USER_DOMAIN_CONTEXT = True # Si se activa, el ChatBotProjectX utilizará información de niveles, atributos, entidades y nodos del dominio de usuario como contexto pasandole la información desde el prompt al chatbot (gasta más tokens).