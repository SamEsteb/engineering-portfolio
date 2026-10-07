/**
 * @fileoverview Este archivo contiene el código JavaScript para la funcionalidad del chatbot,
 * incluyendo la gestión del estado del chatbot (abierto/cerrado), la grabación de audio,
 * la subida y previsualización de imágenes, la interacción con el servidor Flask,
 * la creación de efectos visuales y el manejo de eventos del DOM.
 */

/** @constant {HTMLElement} fileInputImage - Elemento input de tipo file para seleccionar imágenes. */
const fileInputImage = document.getElementById('file-input-image');
/** @constant {HTMLElement} imagePreview - Elemento img para la previsualización de la imagen seleccionada. */
const imagePreview = document.getElementById('image-preview');
/** @constant {HTMLElement} imageDescription - Elemento para mostrar la descripción de la imagen. */
const imageDescription = document.getElementById('image-description');

/** @constant {HTMLElement} userInput - Elemento input de texto para la entrada del usuario. */
const userInput = document.getElementById('user-input');

/** @constant {HTMLElement} chatbotToggle - Botón para abrir/cerrar el chatbot. */
const chatbotToggle = document.getElementById('chatbot-toggle');
/** @constant {HTMLElement} chatbotContainer - Contenedor principal del chatbot. */
const chatbotContainer = document.getElementById('chatbot-container');

/** @constant {HTMLElement} closeChatbotButton - Botón para cerrar el chatbot. */
const closeChatbotButton = document.getElementById('close-chatbot');
/** @constant {HTMLElement} closePreviewButton - Botón para cerrar la previsualización de la imagen. */
const closePreviewButton = document.getElementById('close-preview');

/** @constant {HTMLElement} menuToggle - Botón para desplegar el menú de opciones. */
const menuToggle = document.getElementById('menu-toggle');
/** @constant {HTMLElement} menuOptions - Contenedor del menú de opciones. */
const menuOptions = document.getElementById('menu-options');
/** @constant {HTMLElement} clearHistoryButton - Botón para borrar el historial del chat. */
const clearHistoryButton = document.getElementById('clear-history-button');

/** @type {boolean} chatbotOpened - Indica si el chatbot está abierto o cerrado. */
let chatbotOpened = false; // Variable para controlar si el chatbot está abierto o no
/** @type {MediaRecorder | undefined} recorder - Almacena la entidad del MediaRecorder para grabar audio. */
let recorder; // Variable global para almacenar el objeto MediaRecorder
/** @type {MediaStream | undefined} audioStream - Almacena el stream de audio del micrófono. */
let audioStream; // Variable global para almacenar el stream de audio


/** @type {string} prefix - Prefijo de la URL para las solicitudes al servidor, obtenido dinámicamente. */
let prefix = getEndpointPrefix(); // Prefijo de la URL
console.log('Prefijo de la URL:', prefix);

/**
 * Obtiene el prefijo de la URL a partir de la ruta actual.
 *
 * @returns {string} El prefijo de la URL.
 */
function getEndpointPrefix() {
    const path = window.location.pathname;
    const parts = path.split('/');
    if (parts.length > 1) {
        return '/' + parts[1];
    } else {
        return ''; // el caso en que no haya prefijo
    }
}

/**
 * Abre el chatbot, lo muestra en la pantalla y, si es la primera vez que se abre,
 * muestra un mensaje de bienvenida y, si corresponde, inicializa el chatbot estático.
 */
function openChatbot() {
    chatbotContainer.style.display = "block";
    requestAnimationFrame(() => {
        chatbotContainer.classList.add('active');
    });

    if (!chatbotOpened) {
        let message = '';
        const prefix = window.endpointPrefix || '';

        if (prefix.endsWith('chatbot_projectx')) {
            message += '**💬 ¡Hola! Soy tu asistente ProjectX.**\n\n';
            message += 'Puedo ayudarte a consultar nodos, records de datos y análisis de datos.\n';
            message += 'Dime qué necesitas y te guiaré. 📊';
            appendMessage('chatbot', message);
            initializeStaticBot(decision_tree); // Inicializa el chatbot estático
        } else {
            message += ' Puedes preguntarme cualquier cosa.';
            appendMessage('chatbot', message);
        }

        chatbotOpened = true;
    }
}

// Agrega un listener al botón de abrir/cerrar el chatbot.
chatbotToggle.addEventListener('click', () => {
    if (chatbotContainer.style.display === "block") { // Comprueba display
        closeChatbot();
    } else {
        openChatbot();
    }
});

/**
 * Cierra el chatbot, ocultándolo de la pantalla.
 */
function closeChatbot() {
    chatbotContainer.classList.remove('active');
    // Usa un setTimeout para esperar a que termine la transición *antes* de ocultar
    setTimeout(() => {
        chatbotContainer.style.display = "none";
    }, 200); // 200ms, ajusta si tu transición CSS es más larga
}

// Evento clic para el botón de cerrar (la X)
closeChatbotButton.addEventListener('click', closeChatbot);

/**
 * Crea una partícula de efecto visual en la posición especificada.
 *
 * @param {number} x - La coordenada X de la partícula.
 * @param {number} y - La coordenada Y de la partícula.
 * @param {HTMLElement} button - El botón en el que se crea la partícula.
 */
function createParticle(x, y, button) {
    const particle = document.createElement('div');
    particle.classList.add('particle');
    particle.style.left = `${x}px`;
    particle.style.top = `${y}px`;

    // Color aleatorio (opcional)
    const colors = ['#ffcc00', '#ff9900', '#ccff00', '#00ffcc', '#00ccff', '#9900ff'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    particle.style.backgroundColor = randomColor;

    // Tamaño aleatorio (opcional)
    const size = Math.random() * 5 + 2; // Entre 2 y 7 píxeles
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;

    // --- Animación de rotación y alejamiento ---

    // Ángulo aleatorio inicial para la rotación
    const angle = Math.random() * 360;

    // Radio inicial (qué tan cerca del clic empiezan)
    const initialRadius = 0;

    // Radio final (qué tan lejos se alejan)
    const finalRadius = Math.random() * 60 + 40; // Entre 40 y 

    // Duración de la animación
    const duration = 800; // milisegundos

    // Velocidad de rotación (grados por frame)
    const rotationSpeed = Math.random() * 4 - 2; // Entre -2 y 2 grados

    let startTime = null;

    /**
     * Realiza la animación de la partícula.  Calcula la posición y opacidad
     * de la partícula en cada cuadro de animación, y la elimina cuando termina.
     * @param {number} currentTime Tiempo
     */
    function animate(currentTime) {
        if (!startTime) startTime = currentTime;
        const elapsedTime = currentTime - startTime;

        // Calcula el progreso (0 a 1)
        const progress = Math.min(elapsedTime / duration, 1);

        // Calcula el radio actual en base al progreso
        const currentRadius = initialRadius + (finalRadius - initialRadius) * progress;

        // Calcula el ángulo actual
        const currentAngle = angle + rotationSpeed * elapsedTime / 16; // Dividir por 16 para ajustar a ~60fps

        // Convierte las coordenadas polares (radio, ángulo) a cartesianas (x, y)
        const xOffset = currentRadius * Math.cos(currentAngle * Math.PI / 180);
        const yOffset = currentRadius * Math.sin(currentAngle * Math.PI / 180);

        // Aplica la nueva posición y la opacidad
        particle.style.left = `${x + xOffset}px`;
        particle.style.top = `${y + yOffset}px`;
        particle.style.opacity = 1 - progress;

        // Si la animación no ha terminado, sigue animando
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            particle.remove(); // Elimina la partícula al final
        }
    }

    // Inicia la animación
    requestAnimationFrame(animate);

    // --- Fin de la animación de rotación ---

    button.appendChild(particle);
}



/**
 * Maneja el evento de clic en los botones, creando partículas en la posición del clic.
 * @param {MouseEvent} event Evento de click
 */
function handleButtonClick(event) {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    // Crea varias partículas
    for (let i = 0; i < 10; i++) {
        createParticle(x, y, button);
    }
}

// Obtiene todos los botones a los que se quiere aplicar el efecto
const buttons = document.querySelectorAll('#chatbot-toggle, #send-message, #record-audio, #upload-image-only, #close-chatbot, #close-preview, #clear-history-button');

// Función para borrar el historial del chat
clearHistoryButton.addEventListener('click', borrarHistorial);

// Añade el listener para el evento 'click' a cada botón
buttons.forEach(button => {
    button.addEventListener('click', handleButtonClick);
});

/**
 * Muestra u oculta el menú de opciones.
 */
function toggleMenu() {
    menuOptions.classList.toggle('show');
}

// Evento clic para el botón de menú
menuToggle.addEventListener('click', toggleMenu);

//Cierra el menu si se da click afuera
document.addEventListener('click', (event) => {
    if (!menuToggle.contains(event.target) && !menuOptions.contains(event.target)) {
        menuOptions.classList.remove('show');
    }
});

// redimensionamiento de la ventana
let isResizing = false;
let startY = 0;
let startHeight = 0;
let startX = 0;
let startWidth = 0;
let edge = "";


if (chatbotContainer) {  //Buena practica.
    let isResizing = false;
    let startX = 0;
    let startWidth = 0;
    const resizableContent = document.getElementById('chatbot-resizable-content'); // Obten el nuevo contenedor

    chatbotContainer.addEventListener('mousedown', (e) => {
        const rect = chatbotContainer.getBoundingClientRect();
        const resizeBorderSize = 10;

        // Solo redimensionar desde los bordes izquierdo y derecho
        if (e.clientX < rect.left + resizeBorderSize) {
            isResizing = "left";
        } else if (e.clientX > rect.right - resizeBorderSize) {
            isResizing = "right";
        } else {
            return; // No se hizo clic en un borde válido
        }

        startX = e.clientX;
        startWidth = parseInt(window.getComputedStyle(chatbotContainer).width, 10);  //Ancho del contenedor exterior.
        e.preventDefault(); // Evita comportamiento de selección de texto
    });

    chatbotContainer.addEventListener('mousemove', (e) => {
        const rect = chatbotContainer.getBoundingClientRect();
        const resizeBorderSize = 10;

        if (!isResizing) { // Solo cambia el cursor si no se está redimensionando
            if (e.clientX < rect.left + resizeBorderSize || e.clientX > rect.right - resizeBorderSize) {
                chatbotContainer.style.cursor = 'ew-resize';
            } else {
                chatbotContainer.style.cursor = 'default';
            }
        }
    });
    chatbotContainer.addEventListener('mouseleave', () => {
        chatbotContainer.style.cursor = 'default'; // Restaura el cursor al salir
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;

        const deltaX = (isResizing === "right") ? e.clientX - startX : startX - e.clientX;
        let newWidth = startWidth + deltaX;

        // Límites de ancho
        const minWidth = 200;
        const maxWidth = window.innerWidth * 0.8;
        newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));

        chatbotContainer.style.width = `${newWidth}px`;
    });

    document.addEventListener('mouseup', () => {
        isResizing = false;
    });

    // --- Corrección para redimensionamiento de ventana ---  (Simplificado)
    window.addEventListener('resize', () => {
        if (chatbotContainer && resizableContent) { //Verificamos que existan
            //No es necesario recalcular, si la ventana se redimensiona, deja el tamaño que tiene.
        }
    });
    // --- Fin de la corrección ---
}

// --- Funciones para grabar audio y obtener transcripciones ---

/**
 * Inicia la grabación de audio utilizando el micrófono del usuario.
 * Crea una entidad de MediaRecorder, maneja los eventos `ondataavailable`
 * para enviar los datos de audio al servidor para su transcripción, y maneja
 * los errores de acceso al micrófono.
 */
async function startRecording() {
    console.log("startRecording called"); // Verifica que se llama a la función
    try {
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true }); //Obtiene el stream
        console.log("Audio stream:", audioStream); // Verifica el stream

        recorder = new MediaRecorder(audioStream); //Crea la entidad

        //Cambia el icono de record
        const recordButton = document.getElementById('record-audio');
        const icon = recordButton.querySelector('i');
        icon.classList.remove('fa-microphone');
        icon.classList.add('fa-stop');
        recordButton.title = 'Detener Grabación';

        recorder.ondataavailable = function (e) { //Al obtener datos,
            console.log("ondataavailable triggered"); // Verifica el evento
            const audioBlob = e.items; //Obtiene el audio

            const formData = new FormData(); //Crea un formdata
            formData.append('audio', audioBlob, 'audio.webm'); //Añade el audio

            for (let [key, value] of formData.entries()) { //Verifica que se guardo el audio
                console.log(key, value); // Verifica FormData
            }

            fetch(window.endpointPrefix + '/crear_transcripcion', { // Usar window.endpointPrefix , hace el request
                method: 'POST',
                body: formData
            })
                .then(response => {
                    console.log("Response:", response); // Imprime la respuesta completa
                    if (response.ok) {
                        return response.json(); //Transforma
                    }
                    throw new Error('Error al crear la transcripción.'); //Lanza un error
                })
                .then(items => {
                    userInput.value = items.transcriptionText; //Muestra la transcripcion
                })
                .catch(error => { //Maneja el error
                    console.error('Error:', error); //Log
                    alert('Error al procesar la transcripción: ' + error.message); // Muestra error al usuario
                });
        };

        recorder.onstop = function () { //Al parar la grabacion
            audioStream.getTracks().forEach(track => track.stop()); //Para el stream de audio
        };

        recorder.start(); //Empieza
        recordButton.onclick = stopRecording; //Asigna stop al boton

    } catch (err) {
        console.error('Error al acceder al dispositivo de audio:', err);
        alert('Error al acceder al micrófono: ' + err.message); // Muestra error al usuario
    }
}

/**
 * Detiene la grabación de audio.  Cambia el icono del botón de grabación
 * y restablece la función `onclick` del botón.
 */
function stopRecording() {
    recorder.stop(); //Para
    const recordButton = document.getElementById('record-audio');
    const icon = recordButton.querySelector('i');
    icon.classList.remove('fa-stop'); //Cambia icono
    icon.classList.add('fa-microphone');
    recordButton.title = 'Grabar Audio'; //Cambia el titulo
    recordButton.onclick = startRecording; //Asigna start al boton
}

// --- Funciones para subir imágenes y obtener descripciones ---

/**
 * Muestra una imagen en tamaño completo en un overlay.
 *
 * @param {string} src - La URL de la imagen a mostrar.
 */
function showExpandedImage(src) {
    const overlay = document.getElementById('overlay');
    const expandedImageContainer = document.getElementById('expanded-image-container');
    const expandedImage = document.getElementById('expanded-image');

    expandedImage.src = src; // Establece la fuente de la imagen expandida.
    overlay.style.display = 'block';         // Muestra el overlay.
    expandedImageContainer.style.display = 'block'; // Muestra el contenedor.

    // Evento para cerrar al hacer clic fuera de la imagen
    overlay.onclick = function () {
        hideExpandedImage();
    }
    // Cerrar al hacer clic en el botón de cerrar
    document.getElementById('close-expanded-image').onclick = function () {
        hideExpandedImage();
    };
}

/**
 * Oculta la imagen expandida y el overlay.
 */
function hideExpandedImage() {
    const overlay = document.getElementById('overlay');
    const expandedImageContainer = document.getElementById('expanded-image-container');

    overlay.style.display = 'none'; //Oculta
    expandedImageContainer.style.display = 'none';//Oculta
}

/**
 * Limpia la previsualización de la imagen y el input de archivos.
 * También borra la descripción de la imagen.
 */
function clearImagePreview() {
    imagePreview.src = '#';
    fileInputImage.value = '';
    document.getElementById('image-preview-container').style.display = 'none';
    imageDescription.innerHTML = ''; // También borra la descripción
}

/**
 * Maneja la selección de una imagen por el usuario.
 * Lee el archivo de imagen, muestra una previsualización,
 * muestra la imagen como un mensaje del usuario, y envía la imagen al servidor
 * para obtener una descripción.
 *
 * @param {Event} event - El evento `change` del input de archivos.
 */
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            // 1. Mostrar la imagen como mensaje del usuario.
            appendMessage('user', `<img src="${e.target.result}" alt="Imagen subida" class="user-image">`);

            // 2. enviar la imagen al servidor para la descripción.
            sendImage(file);
        };
        reader.readAsDataURL(file); // leer como Items URL.
    }
}

/**
 * Envía una imagen al servidor para obtener una descripción.
 * Muestra un indicador de "escribiendo", realiza la solicitud al servidor
 * y muestra la descripción recibida o un mensaje de error.
 *
 * @param {File} file - El archivo de imagen a enviar.
 */
function sendImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    let thinkingMessageDiv = showTypingEffect(); //Muestra el indicador

    fetch(prefix + '/describe_image', { //Solicitud al servidor
        method: 'POST',
        body: formData
    })
        .then(response => response.json()) //Transforma la respuesta
        .then(items => { //Obtiene los datos
            if (thinkingMessageDiv) { //Si existe,
                thinkingMessageDiv.remove(); //Remueve el indicador
                thinkingMessageDiv = null;
            }

            if (items.error) { //Si hay un error
                appendMessage('chatbot', `Error: ${items.error}`); //Muestra
                return;
            }

            appendMessage('chatbot', formatResponse(items.description)); //Muestra la descripcion
            fileInputImage.value = ''; //Limpia el input
        })
        .catch(error => { //Maneja error
            if (thinkingMessageDiv) {
                thinkingMessageDiv.remove();
                thinkingMessageDiv = null;
            }
            console.error('Error al enviar la imagen:', error);
            appendMessage('chatbot', 'Error al procesar la imagen.');
            fileInputImage.value = '';
        });
}


/**
 * Formatea una respuesta del servidor para su visualización en el chat.
 * Reemplaza saltos de línea con `<br>` y convierte texto en negrita
 * (delimitado por `**`) a etiquetas `<strong>`.
 *
 * @param {string} response - La respuesta del servidor.
 * @returns {string} La respuesta formateada.
 */
function formatResponse(response) {
    // Reemplaza saltos de línea con <br> para mantener el formato en HTML
    let formattedResponse = response.replace(/\n/g, '<br>');

    // Convierte **texto** a <strong>texto</strong>
    formattedResponse = formattedResponse.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    return formattedResponse;
}

/**
 * Limpia la previsualización de la imagen.
 *  Establece la fuente de la imagen de previsualización en '#'
 *  y oculta el contenedor de la previsualización.
 */
function clearImagePreview() {
    imagePreview.src = '#';
    document.getElementById('image-preview-container').style.display = 'none';
}

/**
 * Muestra la descripción de la imagen en el elemento correspondiente.
 * Utiliza `formatResponse` para formatear la descripción.
 *
 * @param {string} description - La descripción de la imagen.
 */
function showImageDescription(description) {
    imageDescription.innerHTML = formatResponse(description);
}

// Eventos para el input de texto

userInput.addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) { //Si se presiona enter y no shift
        event.preventDefault(); //Previene el salto de linea
        sendMessage(); //Envia el mensaje
    }
});

userInput.addEventListener('input', function () { //Cuando se escribe
    const lines = this.value.split('\n').length; //Cuenta las lineas
    this.rows = Math.min(lines, 4); //Ajusta el numero de lineas, maximo 4
    console.log("Líneas:", lines, "Rows:", this.rows); //Log
});

/**
 * Muestra un indicador de "escribiendo" en el chat.
 * Crea un div con tres puntos animados.
 * @returns {HTMLDivElement} Elemento que muestra la animacion
 */
function showTypingEffect() {
    let typingMessageDiv = document.createElement('div');
    typingMessageDiv.classList.add('message', 'chatbot', 'typing');

    // spans para los puntos
    typingMessageDiv.innerHTML = `
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
    `;

    let chatContainer = document.getElementById('chatbot-content');
    if (chatContainer) {
        chatContainer.appendChild(typingMessageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight; // Desplazarse al final
    } else {
        console.error("No se encontró el contenedor del chat.");
    }

    return typingMessageDiv;
}

/**
 * Oculta un indicador de "escribiendo" en el chat.
 * @param {HTMLDivElement} indicator Elemento a ocultar
 */
function hideTypingEffect(indicator) {
    if (indicator) {
        indicator.remove();
    }
}

/**
 * Expande un gráfico de Highcharts a pantalla completa.
 * Crea un clon de las opciones del gráfico original, ajusta el tamaño,
 * crea un nuevo gráfico en un contenedor superpuesto (overlay)
 * y proporciona una función para cerrar la vista expandida.
 *
 * @param {Highcharts.Chart} chart - El gráfico original de Highcharts.
 */
function toggleFullscreen(chart) {
    const overlay = document.getElementById('overlay');
    const expandedChartContainer = document.getElementById('expanded-chart');

    // 1. Clona las opciones del gráfico original *correctamente*:
    const clonedOptions = Highcharts.merge(chart.userOptions); // ¡MUY IMPORTANTE!

    // 2. Configura el contenedor para el gráfico clonado (ya está bien):
    clonedOptions.chart.renderTo = expandedChartContainer;

    // 3. Ajustar el tamaño del gráfico clonado ANTES de crearlo:
    clonedOptions.chart.width = window.innerWidth * 0.8; // 80% del ancho
    clonedOptions.chart.height = window.innerHeight * 0.8; // 80% del alto

    // 4. Limpiar el contenedor expandido (ya está bien):
    expandedChartContainer.innerHTML = '';

    // 5. Crear el gráfico clonado (usar Highcharts.chart, no new):
    const clonedChart = Highcharts.chart(clonedOptions); // Sin 'new'

    // 6. Mostrar el overlay y el contenedor expandido (ya está bien):
    overlay.style.display = 'block';
    expandedChartContainer.style.display = 'block';

    // 7.  NO es necesario redimensionar con setSize y reflow DESPUÉS de crear.
    //     Ya hemos establecido el tamaño en clonedOptions.

    // 8. Función para cerrar la vista expandida:
    const closeExpandedView = () => {
        // a. Ocultar el overlay y el contenedor expandido (ya está bien):
        overlay.style.display = 'none';
        expandedChartContainer.style.display = 'none';

        // b. Destruir el gráfico clonado (ya está bien):
        clonedChart.destroy();

        // c. NO es necesario reflow del gráfico original si no lo has tocado.
        //     Si hubieras modificado el original, entonces sí necesitarías reflow.

        // d. Eliminar el listener del overlay (ya está bien):
        overlay.removeEventListener('click', closeExpandedView);
    };

    // 9. Añadir el listener al overlay para cerrar (ya está bien):
    overlay.addEventListener('click', closeExpandedView);
}

// --- Obtener configuración de Flask ---

/**
 * Carga la configuración del chatbot desde el servidor Flask.
 * Realiza una solicitud a un endpoint específico y almacena la configuración
 * en una variable global (`window.config`).
 */
async function loadConfig() {
    try {
        const response = await fetch(prefix + "/config");  // Llama al endpoint de Flask
        const config = await response.json();    // Convierte la respuesta en JSON

        // Almacena la configuración en una variable global
        window.config = config;

        // Prueba que los datos están disponibles
        console.log("Configuración Cargada:", window.config);
    } catch (error) {
        console.error("Error al obtener la configuración:", error);
    }
}

// Llama a la función cuando se carga el script
loadConfig();

/**
 * Borra el historial del chat automáticamente al cerrar o recargar la página.
 * Envía una solicitud al servidor para borrar el historial asociado al usuario actual.
 */
function borrarHistorialAutomaticamente() {
    fetch(prefix + '/borrar_historial', { //Solicitud
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ nombre_id: window.config.USER }) //Manda el ID del usuario
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al borrar el historial'); //Lanza error si la respuesta no es OK
            }
            return response.json(); //Transforma la respuesta
        })
        .then(items => {
            console.log(items.message);
        })
        .catch(error => { //Maneja el error
            console.error('Error:', error);
        });
}

//Evento que se activa antes de cerrar la página.
window.addEventListener('beforeunload', borrarHistorialAutomaticamente);