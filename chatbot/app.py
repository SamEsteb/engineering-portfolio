from flask import Flask, render_template
import logging
from chatbot_logic.ChatBotproyectx.proyectx import proyectx_bp, inicializar_proyectx

# --- Configuración del Logging ---
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

logging.info("Aplicación iniciada")

# --- Configuración de Flask ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# --- Registro de Blueprints ---
app.register_blueprint(proyectx_bp, url_prefix='/chatbot_proyectx')

# --- Rutas principales ---
@app.route('/')
def index():
    return render_template('index.html')  # Cambia a una plantilla que muestre los enlaces

# --- Inicializar proyectx ANTES de app.run()
inicializar_proyectx()

if __name__ == '__main__':
    app.run(debug=True)