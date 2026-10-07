/**
 * @fileoverview Este archivo contiene funciones para la interacción con el chatbot estático,
 * incluyendo la obtención y visualización de datos, la creación de elementos de interfaz
 * (selectores, inputs de fecha, inputs numéricos, botones) y el manejo de las interacciones del usuario.
 */

/**
 * @type {Array<any>} previousSelections - Almacena las selecciones previas del usuario para referencia.
 */
let previousSelections = [];
/**
 * @type {Object.<string, any>} fetchDataCache - Caché para almacenar los datos obtenidos de las solicitudes,
 * evitando peticiones repetidas al servidor.  La clave es el `data_source`.
 */
let fetchDataCache = {}; // Objeto para almacenar la caché

/**
 * Busca un nodo específico en un árbol de nodos por su ID.
 *
 * @param {string} node_id - El ID del nodo a buscar.
 * @param {Array<object> | object} tree - El árbol de nodos (o un nodo raíz) donde se busca.
 * @returns {object | null} El nodo encontrado, o null si no se encuentra.
 */
function get_node(node_id, tree) {
    /**
     * Función recursiva interna para buscar el nodo.
     * @param {Array<object>} nodes - Array de nodos donde se busca
     * @param {string} target_id - ID que se busca
     * @returns {object | null} El nodo encontrado, o null si no existe.
     */
    function find_node(nodes, target_id) {
        if (!nodes) return null;
        for (const node of nodes) {
            if (node.uuid === target_id) return node;
            if (node.opciones) { // Busca recursivamente en los subnodos.
                const found = find_node(node.opciones, target_id);
                if (found) return found;
            }
        }
        return null;
    }
    // Permite pasar un solo nodo como árbol.
    return find_node(Array.isArray(tree) ? tree : [tree], node_id);
}

/**
 * Muestra una respuesta estática del bot.  Crea el contenedor principal,
 * agrega una pregunta (si la hay), crea los elementos de entrada
 * (selectores, inputs de fecha, inputs numéricos) según el `input_type` del nodo,
 * y crea los botones de opciones.  Maneja las interacciones del usuario y
 * las acciones correspondientes (consultar, graficar, descargar, cálculos estadísticos).
 *
 * @param {object} items - Los datos del nodo actual, incluyendo pregunta, input_type, opciones, etc.
 * @param {string} nodeId - El ID del nodo actual.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 */
function displayStaticBotResponse(items, nodeId, tree) {
    const container = document.createElement('div');
    container.classList.add('chatbot-response');
    container.dataset.nodeId = nodeId; // Guarda el ID del nodo en el contenedor.
    console.log(previousSelections);

    // Agrega la pregunta si existe.
    if (items.pregunta) {
        const questionElement = document.createElement('p');
        questionElement.innerHTML = items.pregunta;
        questionElement.classList.add('chatbot-question');
        container.appendChild(questionElement);
    }

    const selectedValues = {}; // Almacena los valores seleccionados por el usuario en este nodo.
    const promises = []; // Almacena promesas para operaciones asíncronas (como la creación de selects).

    // Crea los elementos de entrada según el tipo.
    if (items.input_type === 'search_select') {
        promises.push(createSearchSelect(container, items, nodeId, tree, selectedValues));
    } else if (items.input_type === 'select') {
        promises.push(createInlineSearchSelect(container, items, nodeId, tree, selectedValues));
    } else if (items.input_type === 'date_range') {
        createDateRangeSelector(container, items, nodeId, tree, selectedValues);
    } else if (items.input_type === 'select_number') {
        createNumberInput(container, items, nodeId, selectedValues);
    }

    // Crea elementos de entrada adicionales definidos en 'opciones'.
    if (items.opciones && items.opciones.length > 0) {
        items.opciones.forEach(option => {
            if (option.input_type === 'select') {
                promises.push(createInlineSearchSelect(container, option, nodeId, tree, selectedValues));
            } else if (option.input_type === 'select_number') {
                createNumberInput(container, option, nodeId, selectedValues);
            }
        });
        createOptionElements(container, items, nodeId, tree, selectedValues); // Crea los botones de opciones.
    }

    const typingIndicator = showTypingEffect(); // Muestra el indicador de "escribiendo".

    // Espera a que todas las promesas (creación de selects) se resuelvan.
    Promise.all(promises)
        .then(() => {
            appendMessage("chatbot", container); // Agrega el contenedor al chat.
            hideTypingEffect(typingIndicator); // Oculta el indicador.
            disablePreviousInteractions(nodeId); // Deshabilita interacciones en nodos anteriores.
        })
        .catch(error => { // Maneja cualquier error.
            hideTypingEffect(typingIndicator);
            console.error("Error general en la carga de datos:", error);
            appendMessage('chatbot', "Error al cargar la interfaz.");
        });
}

/**
 * Crea un input de tipo número para percentiles o ventanas de media móvil.
 *
 * @param {HTMLElement} container - El contenedor donde se agrega el input.
 * @param {object} items - Los datos del nodo, incluyendo data_source (percentile o window).
 * @param {string} nodeId - El ID del nodo actual.
 * @param {object} selectedValues - Objeto para almacenar los valores seleccionados.
 */
function createNumberInput(container, items, nodeId, selectedValues) {
    const numberContainer = document.createElement('div');
    numberContainer.classList.add('number-input-container');

    const label = document.createElement('label');
    label.textContent = `${items.respuesta}: `;
    label.htmlFor = `number-${items.uuid}`;
    numberContainer.appendChild(label);

    const input = document.createElement('input');
    input.type = 'number';
    input.uuid = `number-${items.uuid}`;
    input.classList.add('number-input');
    input.dataset.nodeId = items.uuid; // Guarda el ID del nodo.

    // Establece min, max y placeholder según el tipo (percentil o ventana).
    if (items.data_source === 'percentile') {
        input.min = 1;
        input.max = 100;
        input.placeholder = "Ingrese un número (1-100)";
    } else if (items.data_source === 'window') {
        input.min = 1;
        input.placeholder = "Ingrese un número (>0)";
    }

    // Maneja el evento 'input' para validar y guardar el valor.
    input.addEventListener('input', () => {
        if (items.data_source === 'percentile') {
            let num = parseInt(input.value, 10);
            if (isNaN(num)) { //Validacion
                input.value = '';
                return;
            }
            if (num < 1) { //Valida min
                input.value = 1;
            } else if (num > 100) { //Valida max
                input.value = 100;
            }
            selectedValues[items.data_source] = input.value; // Guarda el valor.
        } else if (items.data_source === 'window') {
            let num = parseInt(input.value, 10);
            if (isNaN(num)) { //Validacion
                input.value = '';
                return;
            }
            if (num < 1) {  //Valida min
                input.value = 1;
            }
            selectedValues[items.data_source] = input.value; // Guarda el valor.
        } else if (items.data_source) { //Si hay un items source que no sea percentile o windor
            selectedValues[items.data_source] = input.value;
        }
        previousSelections.push({ type: items.data_source, value: input.value }); // Guarda en el historial.
    });

    numberContainer.appendChild(input);
    container.appendChild(numberContainer);
}

/**
 * Crea los botones de opciones para un nodo del chatbot estático.
 * Maneja las acciones de los botones (consultar, graficar, descargar, cálculos estadísticos, volver).
 *
 * @param {HTMLElement} container - El contenedor donde se agregan los botones.
 * @param {object} items - Los datos del nodo actual.
 * @param {string} nodeId - El ID del nodo actual.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 * @param {object} selectedValues - Objeto para almacenar los valores seleccionados.
 */
function createOptionElements(container, items, nodeId, tree, selectedValues) {
    const optionsContainer = document.createElement('div');
    optionsContainer.classList.add('options-container');
    let hasBackButton = false; // Flag para verificar si ya se agregó un botón de "Volver".

    /**
     * Maneja el evento click de un botón de opción.
     * Realiza diferentes acciones según la respuesta del botón.
     *
     * @param {Event} event - El evento click.
     * @param {object} option - La opción asociada al botón.
     * @param {Array<object> | object} tree - El árbol de nodos completo.
     * @param {object} items - Los datos del nodo actual.
     */
    function handleOptionButtonClick(event, option, tree, items) {
        // Acción: Consultar.
        if (option.respuesta.toLowerCase() === 'consultar') {
             //Verifica si se hizo una seleccion
            let selectionCount = 0;
            if (items.input_type === 'search_select') { //Para search select
                const resultsList = container.querySelector('.search-results-list');
                if (resultsList) {
                    selectionCount = resultsList.querySelectorAll('.selected').length; //Elementos seleccionados
                }
            } else if (items.input_type === 'select' || (items.opciones && items.opciones.some(opt => opt.input_type === 'select'))) { //Para selects
                const selects = container.querySelectorAll('.inline-search-select');
                selects.forEach(select => {
                    if (select.value && select.value !== "") {
                        selectionCount++; //Aumenta si hay valor
                    }
                });
            } else if (items.input_type === 'select_number' || (items.opciones && items.opciones.some(opt => opt.input_type === 'select_number'))) {
                const numberInputs = container.querySelectorAll('.number-input');
                numberInputs.forEach(input => {
                    if (input.value && input.value !== "") {
                        selectionCount++; //Aumenta si hay valor
                    }
                });
            }

            if (selectionCount === 0) {
                appendMessage('chatbot', 'Debe seleccionar al menos un elemento');
                return; // No continúa si no hay selección.
            }

            //Prepara el mensaje del usuario.
            let nombre_data_source;
            switch (items.data_source) {
                case 'node': nombre_data_source = 'nodo'; break;
                case 'attribute': nombre_data_source = 'atributo'; break;
                case 'level': nombre_data_source = 'nivel'; break;
                default: nombre_data_source = items.data_source;
            }

            let valores = []; //Valores seleccionados
            if (selectedValues && typeof selectedValues === 'object' && Object.keys(selectedValues).length > 0) {
                valores = Object.values(selectedValues); //Obtiene valores si existen
            } else {
                valores = ["No se seleccionaron valores"]; //Si no hay, mensaje
            }
            //Mensaje al usuario.
            appendMessage("user", `${option.respuesta} ${nombre_data_source}: ${valores.join(', ')}`);


            const currentNode = get_node(nodeId, tree); //Obtiene nodo actual
            if (currentNode && currentNode.opciones) { //Verifica opciones
                const nextNodeOption = currentNode.opciones.find(opt => opt.respuesta.toLowerCase() === 'consultar'); //Busca siguiente nodo con consultar
                if (nextNodeOption && nextNodeOption.siguiente) { //Verifica que exista.
                    const nextNode = get_node(nextNodeOption.siguiente, tree); //Busca el nodo
                    if (nextNode && nextNode.input_type === 'search_select') {  //Si es search select
                        const queryData = buildQueryData(items, selectedValues, tree);  //Construye datos
                        if (queryData) { //Si existen los datos,
                            const typingIndicator = showTypingEffect();
                            //Hace la consulta con los datos obtenidos.
                            fetch('/chatbot_projectx/static_data/consultar', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify(queryData)
                            })
                                .then(response => response.json()) //Transforma la respuesta a json.
                                .then(result => {
                                    hideTypingEffect(typingIndicator); //Oculta typing
                                    if (result.error) { //Muestra el error si existe.
                                        appendMessage('chatbot', 'Error: ' + result.error);
                                    } else {
                                        handleQueryResults(result, nextNodeOption.siguiente, tree); //Muestra resultados
                                    }
                                })
                                .catch(error => { //Maneja error
                                    hideTypingEffect(typingIndicator); //Oculta typing
                                    console.error('Error:', error); //Log
                                    appendMessage('chatbot', 'Error al realizar la consulta.'); //Mensaje
                                });
                            return;
                        }
                    }
                }
            }
        } else if (option.respuesta.toLowerCase() === 'graficar' || option.respuesta.toLowerCase() === 'descargar') { //Accion: Graficar o Descargar.
            appendMessage('user', option.respuesta); // Agrega la respuesta del usuario.

            // Obtiene la record de datos y el rango de fechas de las selecciones previas.
            let record_uuid = null;
            let start_date = null;
            let end_date = null;

            // Busca la record de datos (último string con longitud >= 12).
            for (let i = previousSelections.length - 1; i >= 0; i--) {
                if (typeof previousSelections[i] === 'string' && previousSelections[i].length >= 12) {
                    record_uuid = previousSelections[i].substring(0, 12); //Asumimos que los primeros 12 caracteres son el record_uuid
                    break;
                }
            }

            // Busca el rango de fechas (último objeto con tipo 'date').
            for (let i = previousSelections.length - 1; i >= 0; i--) {
                if (typeof previousSelections[i] === 'object' && previousSelections[i].type === "date") {
                    start_date = previousSelections[i].start_date;
                    end_date = previousSelections[i].end_date;
                    break;
                }
            }

            // Validación: Si no hay record de datos o fechas, muestra un mensaje y retorna.
            if (!record_uuid || !start_date || !end_date) {
                appendMessage('chatbot', 'Por favor, selecciona una record de datos y un rango de fechas.');
                return;
            }

            // Prepara los datos de la solicitud.
            const action = option.respuesta.toLowerCase(); // 'graficar' o 'descargar'.
            const requestData = {
                record_uuid: record_uuid,
                start_date: start_date,
                end_date: end_date,
                action: action
            };

            const typingIndicator = showTypingEffect();
            // Realiza la solicitud al servidor.
            fetch('/chatbot_projectx/static_data/process_records', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })
                .then(response => response.json())
                .then(result => {
                    hideTypingEffect(typingIndicator); //Oculta typing
                    if (result.error) { //Muestra el error si existe
                        appendMessage('chatbot', 'Error: ' + result.error);
                    } else {
                        // Procesa la respuesta (crea el gráfico o el enlace de descarga).
                        if (action === 'graficar') {
                            procesar_highchart(result); // Llama a la función que crea el gráfico.
                        } else if (action === 'descargar') {
                            createCSVDownloadLink(result.csv_data, `${record_uuid}_data.csv`); // Crea el enlace de descarga.
                        }
                    }
                })
                .catch(error => { //Maneja error
                    hideTypingEffect(typingIndicator); //Oculta
                    console.error('Error:', error); //Log
                    appendMessage('chatbot', `Error al ${action} la record de datos.`);
                });
        } else if (['promedio', 'desviación estándar'].includes(option.respuesta.toLowerCase())) { //Accion promedio o desviacion estandar
            appendMessage('user', option.respuesta); //Mensaje de usuario
              // Obtiene la record de datos y el rango de fechas de las selecciones previas.
            let record_uuid = null;
            let start_date = null;
            let end_date = null;
            let params = {};

            // Busca la record de datos (último string con longitud >= 12).
            for (let i = previousSelections.length - 1; i >= 0; i--) {
                if (typeof previousSelections[i] === 'string' && previousSelections[i].length >= 12) {
                    record_uuid = previousSelections[i].substring(0, 12);
                    break;
                }
            }

            // Busca el rango de fechas (último objeto con tipo 'date').
            for (let i = previousSelections.length - 1; i >= 0; i--) {
                if (typeof previousSelections[i] === 'object' && previousSelections[i].type === "date") {
                    start_date = previousSelections[i].start_date;
                    end_date = previousSelections[i].end_date;
                    break;
                }
            }

            // Validación: Si no hay record de datos o fechas, muestra un mensaje y retorna.
            if (!record_uuid || !start_date || !end_date) {
                appendMessage('chatbot', 'Por favor, selecciona una record de datos y un rango de fechas.');
                return;
            }

             //Tipo de calculo
            let tipo_calculo = option.respuesta.toLowerCase();
            if (tipo_calculo === 'desviación estándar') {
                tipo_calculo = 'desviacion_estandar'; //Para el request
            }

            //Prepara datos
            const requestData = {
                record_uuid: record_uuid,
                start_date: start_date,
                end_date: end_date,
                tipo_calculo: tipo_calculo,
                params: params
            };
            const typingIndicator = showTypingEffect();

            //Hace el request
            fetch('/chatbot_projectx/static_data/process_statistics', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })
                .then(response => response.json())
                .then(result => {
                    hideTypingEffect(typingIndicator); //Oculta typing
                    if (result.error) {  //Muestra el error si existe
                        appendMessage('chatbot', 'Error: ' + result.error);
                    } else {
                        process_statistical_data(result); //Procesa los datos estadisticos.
                    }
                })
                .catch(error => { //Maneja error
                    hideTypingEffect(typingIndicator); //Oculta
                    console.error('Error:', error); //Log
                    appendMessage('chatbot', 'Error al realizar el cálculo estadístico.'); //Mensaje
                });

        } else if (['percentiles', 'media móvil', 'percentil de media móvil'].includes(option.respuesta.toLowerCase())) { //Accion: percentiles, media movil o percentil de media movil
            appendMessage('user', option.respuesta); //Mensaje
            if (option.siguiente) { //Si hay un nodo siguiente, muestra la respuesta
                fetchStaticBotResponse(option.siguiente, tree);
            }
            return;

        } else if (option.respuesta.toLowerCase() === 'calcular') { //Accion: Calcular
            //Resetea los valores
            let record_uuid = null;
            let start_date = null;
            let end_date = null;
            let tipo_calculo = null;
            let params = {};

             // Busca la record de datos (último string con longitud >= 12).
            for (let i = previousSelections.length - 1; i >= 0; i--) {
                if (typeof previousSelections[i] === 'string' && previousSelections[i].length >= 12) {
                    record_uuid = previousSelections[i].substring(0, 12);
                    break;
                }
            }

            // Busca el rango de fechas (último objeto con tipo 'date').
            for (let i = previousSelections.length - 1; i >= 0; i--) {
                if (typeof previousSelections[i] === 'object' && previousSelections[i].type === "date") {
                    start_date = previousSelections[i].start_date;
                    end_date = previousSelections[i].end_date;
                    break;
                }
            }

             // Validación: Si no hay record de datos o fechas, muestra un mensaje y retorna.
            if (!record_uuid || !start_date || !end_date) {
                appendMessage('chatbot', 'Por favor, selecciona una record de datos y un rango de fechas.');
                return;
            }

            //Encuentra nodo previo para determinar el tipo de calculo
            const previousNode = findPreviousNode(tree, nodeId);
            if (!previousNode) {
                appendMessage('chatbot', 'No se pudo determinar el tipo de cálculo.');
                return;
            }

            //Busca en las opciones del nodo anterior para ver que tipo se selecciono
            if (previousNode.opciones) {
                const previousOption = previousNode.opciones.find(opt => opt.siguiente === nodeId); //Encuentra la opcion
                if (previousOption) { //Si existe,
                    tipo_calculo = previousOption.respuesta.toLowerCase(); //Obtiene respuesta
                    if (tipo_calculo === 'desviación estándar') { //Lo mismo que arriba, para el request
                        tipo_calculo = 'desviacion_estandar';
                    } else if (tipo_calculo === 'media móvil') {
                        tipo_calculo = 'media_movil';
                    } else if (tipo_calculo === 'percentil de media móvil') {
                        tipo_calculo = 'percentil_media_movil';
                    }
                } else {
                    appendMessage('chatbot', 'No se pudo determinar el tipo de cálculo (opción previa no encontrada).');
                    return;
                }
            } else {
                appendMessage('chatbot', "No se pudo determinar el tipo de cálculo(sin opciones).");
                return;
            }

            //Obtiene los atributos si existen.
            if (tipo_calculo === 'percentiles' && selectedValues['percentile']) {
                params.percentiles = [parseInt(selectedValues['percentile'], 10)];
            } else if (tipo_calculo === 'media_movil' && selectedValues['window']) {
                params.window = parseInt(selectedValues['window'], 10);
            } else if (tipo_calculo === 'percentil_media_movil') {
                if (selectedValues['window']) {
                    params.window = parseInt(selectedValues['window'], 10);
                }
                if (selectedValues['percentile']) {
                    params.percentiles = [parseInt(selectedValues['percentile'], 10)];
                }
            }

            //Prepara datos
            const requestData = {
                record_uuid: record_uuid,
                start_date: start_date,
                end_date: end_date,
                tipo_calculo: tipo_calculo,
                params: params
            };

            const typingIndicator = showTypingEffect();
            //Hace el request
            fetch('/chatbot_projectx/static_data/calcular', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            })
                .then(response => response.json())
                .then(result => {
                    hideTypingEffect(typingIndicator); //Oculta typing
                    if (result.error) { //Muestra el error si existe.
                        appendMessage('chatbot', 'Error: ' + result.error);
                    } else {
                        process_statistical_data(result); //Procesa los datos
                    }
                })
                .catch(error => { //Maneja error.
                    hideTypingEffect(typingIndicator);
                    console.error('Error:', error);
                    appendMessage('chatbot', 'Error al realizar el cálculo.');
                });
        } else {
            appendMessage("user", option.respuesta); // Agrega mensaje del usuario por defecto.
        }

        // Si la opción tiene un nodo siguiente, muestra la respuesta correspondiente.
        if (option.siguiente) {
            fetchStaticBotResponse(option.siguiente, tree);
        }
    }

    // Crea los botones a partir de las opciones del nodo.
    items.opciones.forEach(option => {
        if (option.input_type === 'button') {
            const button = document.createElement('button');
            button.classList.add('static-bot-button');

            //Personaliza el boton, dependiendo de la respuesta.
            if (option.respuesta.toLowerCase() === "Información") {
                button.innerHTML = '<i class="fas fa-info-circle"></i>';
                button.classList.add('icon-button');
            } else if (option.respuesta.toLowerCase() === "consultar") {
                button.innerHTML = '<i class="fas fa-search"></i> Consultar';
                button.classList.add('icon-button');
            } else if (option.respuesta.toLowerCase() === "volver") {
                button.innerHTML = '<i class="fas fa-arrow-left"></i> Volver';
                button.classList.add('icon-button');
                hasBackButton = true; //Indica que existe el boton de volver.
            } else if (option.respuesta.toLowerCase() === "calcular") {
                button.innerHTML = '<i class="fas fa-calculator"></i> Calcular';
                button.classList.add('icon-button');
            } else { //Caso estandar
                button.textContent = option.respuesta;
            }

            button.dataset.nodeId = option.uuid;  //Guarda el ID del nodo en el boton.
            if (option.siguiente) { //Lo mismo si existe un nodo siguiente
                button.dataset.siguiente = option.siguiente;
            }
            //Asigna el evento al boton.
            button.addEventListener('click', (event) => handleOptionButtonClick(event, option, tree, items));
            optionsContainer.appendChild(button);

        }
    });

    // Agrega un botón de "Volver" si no existe ya y no es el nodo base.
    if (!hasBackButton && nodeId !== 'base') {
        addBackButton(optionsContainer, nodeId, tree);
    }

    container.appendChild(optionsContainer); // Agrega los botones al contenedor.

    // Para input de tipo search_select, este bloque maneja los eventos al dar click a las opciones.
    if (items.input_type === 'search_select') {
        const resultsList = container.querySelector('.search-results-list');
        if (resultsList) {
            resultsList.addEventListener('click', (event) => {
                if (event.target.tagName === 'LI') {
                    const listItem = event.target;

                    //Permite solamente una opcion seleccioanda.
                    if (listItem.classList.contains('selected')) {
                        listItem.classList.remove('selected'); //Remueve seleccion
                    } else {
                        resultsList.querySelectorAll('li').forEach(li => li.classList.remove('selected')); //Remueve otras
                        listItem.classList.add('selected'); //Agrega seleccion
                        if (items.data_source) { //Si hay un items source
                            selectedValues[items.data_source] = listItem.textContent; //Guardamos el texto del elemento
                            previousSelections.push(listItem.textContent); //Guardamos como string
                        }
                    }
                }
            });
        }
    }
}
/**
 * Deshabilita las interacciones (botones, selects, inputs) en los nodos anteriores
 * del chatbot para evitar modificaciones en respuestas ya dadas.
 *
 * @param {string} currentNodeId - El ID del nodo actual.  Los nodos anteriores a este serán deshabilitados.
 */
function disablePreviousInteractions(currentNodeId) {
    /**
     * Funcion que deshabilita los elementos
     * @param {HTMLElement} container Contenedor a deshabilitar
     */
    function disableElements(container) {
        if (!container) return;
        //Selecciona todos los elementos que interactuan con el usuario.
        const buttons = container.querySelectorAll('.static-bot-button');
        const selects = container.querySelectorAll('.inline-search-select');
        const listItems = container.querySelectorAll('.search-results-list li');
        const dateInputs = container.querySelectorAll('.date-input');
        const searchInputs = container.querySelectorAll('.search-input');
        const numberInputs = container.querySelectorAll('.number-input');
        //Los deshabilita.
        buttons.forEach(el => el.disabled = true);
        selects.forEach(el => el.disabled = true);
        listItems.forEach(el => {
            el.style.pointerEvents = 'none'; //Para que no se pueda interactuar con el
            el.style.opacity = '0.6';//Opacidad
        });
        dateInputs.forEach(el => el.disabled = true);
        searchInputs.forEach(el => el.disabled = true);
        numberInputs.forEach(el => el.disabled = true);
    }
    //Selecciona todas las respuestas del chatbot
    const allResponseContainers = document.querySelectorAll('.chatbot-response');
    allResponseContainers.forEach(container => { //Por cada una
        if (container.dataset.nodeId !== currentNodeId) { //Si el uuid es diferente al del nodo actual,
            disableElements(container); //Deshabilita
        }
    });
}

/**
 * Maneja los resultados de una consulta (para el flujo de "Consultar").
 * Si hay resultados (records de datos), crea un nodo temporal para mostrarlos
 * y los muestra usando `displayStaticBotResponse`.  Si no hay resultados,
 * muestra un mensaje al usuario.
 *
 * @param {object} results - Los resultados de la consulta.
 * @param {string} nextNodeId - El ID del siguiente nodo (después de mostrar los resultados).
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 */
function handleQueryResults(results, nextNodeId, tree) {
    console.log(results);
    //Si hay datos
    if (results.records && results.records.length > 0) {
        //Crea un nuevo nodo con los resultados.
        const resultsNode = {
            uuid: 'temp-results', //Nodo temporal
            input_type: 'search_select', //Tipo search select
            data_source: 'datos', //Datasource
            records: results.records, //Datos
            opciones: [], //Opciones vacias, se agregaran mas abajo.
            tree: tree,
        };
        const nextNode = get_node(nextNodeId, tree); //Obtiene el nodo siguiente.
        if (nextNode && nextNode.opciones) {
            resultsNode.opciones = nextNode.opciones; //Se le agrega las opciones.
        }
        displayStaticBotResponse(resultsNode, resultsNode.uuid, tree); //Muestra la respuesta, con las records de datos.
    } else {
        appendMessage('chatbot', "No se encontraron datos para la consulta realizada.");
    }
}

/**
 * Crea un elemento de selección con búsqueda (search-select) para nodos, atributos, etc.
 * Obtiene los datos de forma asíncrona (usando `fetchDataAndPopulateList`),
 * los muestra en una lista y permite al usuario filtrar las opciones escribiendo.
 *
 * @param {HTMLElement} container - El contenedor donde se agrega el selector.
 * @param {object} items - Los datos del nodo, incluyendo data_source.
 * @param {string} nodeId - El ID del nodo actual.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 * @param {object} selectedValues - Objeto para almacenar los valores seleccionados.
 * @returns {Promise<void>} Una promesa que se resuelve cuando el selector se ha creado y poblado.
 */
function createSearchSelect(container, items, nodeId, tree, selectedValues) {
    return new Promise((resolve, reject) => {
        //Pone un nombre a items source para presentarlo al usuario
        let nombre_data_source = items.data_source;
        if (items.data_source === 'node') {
            nombre_data_source = 'nodo';
        } else if (items.data_source === 'attribute') {
            nombre_data_source = 'atributo';
        } else if (items.data_source === 'level') {
            nombre_data_source = 'nivel';
        } else if (items.data_source === 'query_result' || items.data_source === 'query_results') {
            nombre_data_source = "serie de tiempo"
        }
        //Creacion de los elementos
        const searchContainer = document.createElement('div');
        searchContainer.classList.add('search-select-container');
        const inputContainer = document.createElement('div');
        inputContainer.classList.add('search-input-container');
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = items.data_source ? `Buscar ${nombre_data_source}...` : 'Buscar...'; // Placeholder.
        searchInput.classList.add('search-input');
        inputContainer.appendChild(searchInput);
        searchContainer.appendChild(inputContainer);
        const resultsList = document.createElement('ul');
        resultsList.uuid = `${items.data_source || 'results'}-list`; // ID para la lista.
        resultsList.classList.add('search-results-list');
        resultsList.dataset.nodeId = nodeId; // Guarda el ID del nodo.
        searchContainer.appendChild(resultsList);

        // Obtiene los datos (de la caché o del servidor) y los muestra en la lista.
        const fetchDataPromise = items.records
            ? Promise.resolve(items.records) // Si ya están los datos, resuelve inmediatamente.
            : fetchDataAndPopulateList(resultsList, items, tree);  // Si no, los obtiene.

        fetchDataPromise
            .then(items => {
                if (items) {
                    populateListWithRecords(resultsList, items); // Muestra las records de datos.
                }
                resolve(); // Resuelve la promesa (éxito).
            })
            .catch(error => {
                reject(error); // Rechaza la promesa (error).
            });

        // Filtra la lista al escribir en el input.
        searchInput.addEventListener('input', () => {
            filterListOptions(resultsList, searchInput.value.toLowerCase());
        });

        container.appendChild(searchContainer); // Agrega el selector al contenedor.
    });
}

/**
 * Rellena una lista (ul) con elementos de lista (li) a partir de un array de records de datos.
 * Cada elemento de la lista muestra el ID y el rango de fechas de la record de datos, o simplemente el item si no es un objeto.
 *
 * @param {HTMLUListElement} listElement - La lista (ul) que se rellena.
 * @param {Array<object | string>} records - El array de records de datos.  Cada elemento puede ser un objeto
 *  con propiedades `uuid` y `date_range`, o simplemente un string.
 */
function populateListWithRecords(listElement, records) {
    listElement.innerHTML = ''; // Limpia la lista.
    records.forEach(item => {
        const listItem = document.createElement('li');
        //Muestra de esta manera si es un objeto, si no, muestra solo item
        listItem.textContent = item.uuid ? `${item.uuid} (${item.date_range})` : item;
        listItem.classList.add('search-result-item');
        listElement.appendChild(listItem);
    });
}

/**
 * Crea un selector desplegable (select) con búsqueda *inline* (dentro del mismo elemento, sin un input separado).
 * Obtiene los datos de forma asíncrona, los muestra como opciones en el select y permite al usuario seleccionar una opción.
 *
 * @param {HTMLElement} container - El contenedor donde se agrega el selector.
 * @param {object} items - Los datos del nodo, incluyendo `respuesta` (para el label) y `data_source`.
 * @param {string} nodeId - El ID del nodo actual.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 * @param {object} selectedValues - Objeto para almacenar los valores seleccionados.
 * @returns {Promise<void>} Una promesa que se resuelve cuando el selector se ha creado y poblado.
 */
function createInlineSearchSelect(container, items, nodeId, tree, selectedValues) {
    return new Promise((resolve, reject) => {
        const selectContainer = document.createElement('div');
        selectContainer.classList.add('inline-search-select-container');

        //Crea el label
        const label = document.createElement('label');
        label.textContent = `${items.respuesta}: `;
        label.setAttribute('for', `select-${items.uuid}`);
        label.classList.add('select-label');
        selectContainer.appendChild(label);

        //Crea el select
        const select = document.createElement('select');
        select.uuid = `select-${items.uuid}`;
        select.classList.add('inline-search-select');
        select.dataset.nodeId = items.uuid; //Guarda ID
        if (items.siguiente) { //Guarda siguiente si existe
            select.dataset.siguiente = items.siguiente;
        }
        selectContainer.appendChild(select);

        //Obtiene los datos
        fetchDataAndPopulateList(select, items, tree)
            .then(items => {
                //Crea opcion vacia
                const emptyOption = document.createElement('option');
                emptyOption.value = "";
                emptyOption.textContent = `Seleccione ${items.respuesta}`;
                emptyOption.selected = true;
                select.appendChild(emptyOption);

                //Agrega las opciones
                items.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item;
                    option.textContent = item;
                    select.appendChild(option);
                });

                //Guarda el valor seleccionado.
                select.addEventListener('change', (event) => {
                    const selectedValue = event.target.value;
                    if (items.data_source) { //Si hay un items source
                        if (selectedValue !== "") { //Y la seleccion no esta vacia
                            selectedValues[items.data_source] = selectedValue; //Guarda
                            previousSelections.push(selectedValue);
                        } else {
                            delete selectedValues[items.data_source]; //Si esta vacio, borra si existe
                        }
                    }
                });
                resolve(); //Resuelve
            })
            .catch(error => {
                reject(error); //Rechaza
            });

        container.appendChild(selectContainer);
    });
}

/**
 * Crea un selector de rango de fechas (dos inputs de tipo 'date').
 *
 * @param {HTMLElement} container - El contenedor donde se agregan los inputs.
 * @param {object} items - Los datos del nodo.
 * @param {string} nodeId - El ID del nodo actual.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 * @param {object} selectedValues - Objeto para almacenar los valores seleccionados.
 */
function createDateRangeSelector(container, items, nodeId, tree, selectedValues) {
    const dateRangeContainer = document.createElement('div');
    dateRangeContainer.classList.add('date-range-container');

    // Crea los elementos HTML (labels e inputs) para el rango de fechas.
    const startDateLabel = document.createElement('label');
    startDateLabel.textContent = 'Desde: ';
    startDateLabel.htmlFor = 'start-date-' + nodeId;
    const startDateInput = document.createElement('input');
    startDateInput.type = 'date';
    startDateInput.uuid = 'start-date-' + nodeId;
    startDateInput.classList.add('date-input');
    const endDateLabel = document.createElement('label');
    endDateLabel.textContent = 'Hasta: ';
    endDateLabel.htmlFor = 'end-date-' + nodeId;
    const endDateInput = document.createElement('input');
    endDateInput.type = 'date';
    endDateInput.uuid = 'end-date-' + nodeId;
    endDateInput.classList.add('date-input');

    //Agrupa cada label con su input
    const startGroup = document.createElement('div');
    startGroup.classList.add('date-group');
    startGroup.appendChild(startDateLabel);
    startGroup.appendChild(startDateInput);
    const endGroup = document.createElement('div');
    endGroup.classList.add('date-group');
    endGroup.appendChild(endDateLabel);
    endGroup.appendChild(endDateInput);

    //Agrega al contenedor
    dateRangeContainer.appendChild(startGroup);
    dateRangeContainer.appendChild(endGroup);
    container.appendChild(dateRangeContainer);


    /**
     * Maneja los cambios en los inputs de fecha.  Guarda las fechas seleccionadas
     * en `selectedValues` y en `previousSelections`.
     */
    function handleDateChange() {
        const startDate = formatDateToDDMMYYYY(startDateInput.value); // Formato DD-MM-YYYY.
        const endDate = formatDateToDDMMYYYY(endDateInput.value);

        if (startDate && endDate) {  //Si hay fechas,
            selectedValues['Fecha inicio'] = startDate; //Guarda como Fecha inicio
            selectedValues['Fecha fin'] = endDate;

            // Elimina cualquier selección de fecha anterior *para este nodo*.
            previousSelections = previousSelections.filter(selection => !(selection.type === 'date' && selection.nodeId === nodeId));

            // Agrega la nueva selección.
            previousSelections.push({ type: 'date', start_date: startDate, end_date: endDate, nodeId: nodeId });
        }
    }

    // Eventos para detectar cambios en las fechas.
    startDateInput.addEventListener('change', handleDateChange);
    endDateInput.addEventListener('change', handleDateChange);

     //Precargar fechas si hay una seleccion previa, con el mismo nodeId
     let previousDateSelection = previousSelections.find(ps => ps.type === "date" && ps.nodeId === nodeId)
     if(previousDateSelection){
        //Separa
         let [day, month, year] = previousDateSelection.start_date.split("-");
         startDateInput.value = `${year}-${month}-${day}`; //Formato para el input

         [day, month, year] = previousDateSelection.end_date.split("-");
         endDateInput.value = `${year}-${month}-${day}`; //Formato para el input

        handleDateChange(); //Llama para que se guarden
     }
}

/**
 * Formatea una fecha de YYYY-MM-DD a DD-MM-YYYY.
 *
 * @param {string} dateString - La fecha en formato YYYY-MM-DD.
 * @returns {string} La fecha en formato DD-MM-YYYY, o una cadena vacía si la entrada es inválida.
 */
function formatDateToDDMMYYYY(dateString) {
    if (!dateString) return '';
    const [year, month, day] = dateString.split('-');
    if (year && month && day) {
        return `${day}-${month}-${year}`; //Formato
    }
    return ''; //Inválido
}

/**
 * Agrega un botón "Volver" al contenedor.  El botón permite al usuario
 * regresar al nodo anterior en el árbol de conversación.
 *
 * @param {HTMLElement} container - El contenedor donde se agrega el botón.
 * @param {string} nodeId - El ID del nodo actual.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 */
function addBackButton(container, nodeId, tree) {
    const backButton = document.createElement('button');
    backButton.innerHTML = '<i class="fas fa-arrow-left"></i> Volver'; // Icono y texto.
    backButton.classList.add('icon-button', 'static-bot-button'); // Clases CSS.
    backButton.title = "Volver"; // Tooltip.
    backButton.addEventListener('click', () => {
        // Encuentra el nodo anterior.
        const previousNode = findPreviousNode(tree, nodeId) || { uuid: 'base' }; //Si no lo encuentra, vuelve a base
        fetchStaticBotResponse(previousNode.uuid, tree); // Muestra la respuesta del nodo anterior.
    });
    container.appendChild(backButton); // Agrega el botón al contenedor.
}

/**
 * Encuentra el nodo anterior a un nodo dado en el árbol de conversación.
 *
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 * @param {string} nodeId - El ID del nodo actual.
 * @returns {object | null} El nodo anterior, o null si no se encuentra (o si el nodo actual es la raíz).
 */
function findPreviousNode(tree, nodeId) {
    /**
     * Busca recursivamente el nodo anterior.
     * @param {Array<object>} nodes Nodos donde se busca
     * @param {string} targetId ID del nodo actual
     * @returns {object | null} Nodo anterior, o null si no se encuentra
     */
    function search(nodes, targetId) {
        if (!nodes) return null;
        for (const node of nodes) { //Busca
            if (node.opciones) {
                for (const option of node.opciones) {
                    if (option.siguiente === targetId) return node; //Si el nodo actual es el siguiente de una opcion, lo retorna
                }
            }
            //Busca recursivamente
            const found = search(node.opciones, targetId);
            if (found) return found;
        }
        return null;
    }
    const searchNodes = Array.isArray(tree) ? tree : [tree]; //Para aceptar un solo nodo
    return search(searchNodes, nodeId); //Llama
}

/**
 * Inicializa el chatbot estático, comenzando en el nodo 'base'.
 *
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 */
function initializeStaticBot(tree) {
    fetchStaticBotResponse('base', tree); // Comienza en el nodo base.
}

/**
 * Obtiene y muestra la respuesta de un nodo del chatbot estático.
 * Realiza una solicitud al servidor para obtener los datos del nodo y luego
 * llama a `displayStaticBotResponse` para mostrar la respuesta.
 *
 * @param {string} nodeId - El ID del nodo a mostrar.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 */
function fetchStaticBotResponse(nodeId, tree) {
    const typingIndicator = showTypingEffect(); // Muestra el indicador de "escribiendo".
    fetch('/chatbot_projectx/static_bot', { //Solicitud
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_id: nodeId }) //Envia el ID del nodo.
    })
        .then(response => response.json()) //Transforma
        .then(items => {
            hideTypingEffect(typingIndicator); //Oculta
            if (items.error) { //Si hay error,
                console.error(items.error); //Log
                appendMessage('chatbot', 'Error: ' + items.error); //Mensaje
                return;
            }
            displayStaticBotResponse(items, nodeId, tree); //Si no, llama a mostrar la respuesta.
        })
        .catch(error => { //Maneja error
            hideTypingEffect(typingIndicator);
            console.error('Error:', error);
            appendMessage('chatbot', 'Error al comunicarse con el bot estático.');
        });
}


/**
 * Obtiene datos de forma asíncrona (de la caché o del servidor) y los usa para rellenar un elemento de lista (ul o select).
 * Utiliza una caché (`fetchDataCache`) para evitar solicitudes repetidas al servidor.
 *
 * @param {HTMLElement} listElement - El elemento de lista (ul o select) que se rellena.
 * @param {object} items - Los datos del nodo, incluyendo `data_source`.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 * @returns {Promise<Array<any>>} Una promesa que se resuelve con los datos obtenidos.
 */
function fetchDataAndPopulateList(listElement, items, tree) {
    console.log('fetchDataAndPopulateList');
    return new Promise((resolve, reject) => {
        const dataSource = items.data_source;
        const cacheKey = dataSource; // Usamos data_source como clave para la caché.
        console.log(`Obteniendo datos para ${dataSource}`);

        // Verificar si los datos ya están en la caché.
        if (fetchDataCache[cacheKey]) {
            console.log(`Usando caché para ${dataSource}`);
            resolve(fetchDataCache[cacheKey]); // Resolver con los datos de la caché.
            return;
        }

        // Si no están en la caché, realizar la solicitud al servidor.
        const url = `/chatbot_projectx/static_data/${dataSource}`; //Construye url
        const method = 'GET';
        const headers = { 'Content-Type': 'application/json' };
        fetch(url, { method, headers })  //Solicitud
            .then(response => response.json())  //Transforma
            .then(responseData => {
                listElement.innerHTML = ''; //Limpia la lista
                if (Array.isArray(responseData)) {
                    // Guardar en caché antes de resolver.
                    fetchDataCache[cacheKey] = responseData;
                    resolve(responseData); //Resuelve con los datos
                } else {
                    console.error(`No se pudieron obtener los datos para ${dataSource}:`, responseData);
                    appendMessage('chatbot', `Error al cargar la lista de ${dataSource}.`);
                    reject(`No se pudieron obtener los datos para ${dataSource}`); //Rechaza
                }
            })
            .catch(error => { //Maneja error
                console.error(`Error al obtener los datos para ${dataSource}:`, error);
                appendMessage('chatbot', `Error al cargar la lista de ${dataSource}.`);
                reject(error); //Rechaza
            });
    });
}

/**
 * Filtra las opciones de una lista (ul) según un texto de búsqueda.
 * Muestra solo los elementos de la lista que contienen el texto de búsqueda (sin distinción entre mayúsculas y minúsculas).
 *
 * @param {HTMLUListElement} listElement - La lista (ul) que se filtra.
 * @param {string} searchText - El texto de búsqueda.
 */
function filterListOptions(listElement, searchText) {
    const items = listElement.querySelectorAll('li'); //Obtiene todos los li
    items.forEach(item => {
        //Muestra el elemento si incluye el texto, si no, lo oculta
        item.style.display = item.textContent.toLowerCase().includes(searchText) ? '' : 'none';
    });
}

/**
 * Marca un elemento de una lista como seleccionado (agrega la clase 'selected')
 * y desmarca los demás elementos de la misma lista.
 *
 * @deprecated Esta función no se utiliza en el código actual, pero podría usarse en el futuro
 * si se necesita una selección *múltiple* en las listas.  El código actual solo permite *una* selección.
 * @param {Event} event - El evento click en el elemento de la lista.
 */
function selectItem(event) {
    const listItem = event.target; //Obtiene el elemento
    const list = listItem.parentNode; //Obtiene la lista
    list.querySelectorAll('li').forEach(item => item.classList.remove('selected')); //Remueve la clase selected de los otros
    listItem.classList.add('selected'); //Agrega la clase al elemento
    previousSelections.push(listItem.textContent); //Agrega la seleccion a previousSelections
}

/**
 * Construye un objeto con los datos de la consulta para enviarlo al servidor (para el flujo de "Consultar").
 * Recopila el tipo de consulta (nodo, atributo, nivel), el valor de la consulta y los filtros adicionales
 * (fechas, otros selects) a partir de `selectedValues` y la estructura del árbol de nodos.
 *
 * @param {object} items - Los datos del nodo actual.
 * @param {object} selectedValues - Objeto con los valores seleccionados por el usuario.
 * @param {Array<object> | object} tree - El árbol de nodos completo.
 * @returns {object | null} El objeto con los datos de la consulta, o null si faltan datos esenciales.
 */
function buildQueryData(items, selectedValues, tree) {
    const currentNode = get_node(items.uuid, tree); //Busca el nodo actual
    if (!currentNode) { //Si no existe,
        appendMessage('chatbot', 'Error: Nodo actual no encontrado.'); //Mensaje
        return null; //Retorna
    }
    let query_type = null; //Inicializa
    let query_value = null; //Inicializa
    const additional_filters = {}; //Filtros adicionales

    //Recorre las opciones para buscar filtros
    for (const option of currentNode.opciones) {
        if (option.input_type === 'select' && selectedValues[option.data_source]) { //Selects
            additional_filters[option.data_source] = selectedValues[option.data_source]; //Guarda
        } else if (option.input_type === "date_range") { //Fechas
            additional_filters['Fecha inicio'] = selectedValues['Fecha inicio'];
            additional_filters['Fecha fin'] = selectedValues['Fecha fin'];
        }
    }

    //Determina el tipo de consulta y el valor.
    if (selectedValues.node) {
        query_type = "node";
        query_value = selectedValues.node;
    } else if (selectedValues.attribute) {
        query_type = "attribute";
        query_value = selectedValues.attribute;
    } else if (selectedValues.level) {
        query_type = "level";
        query_value = selectedValues.level;
    }

    //Crea objeto
    const queryData = {
        query_type: query_type,
        query_value: query_value,
        additional_filters: additional_filters
    };

    //Valida que exista el tipo de consulta y el valor
    if (!queryData.query_type || !queryData.query_value) {
        return null;
    }
    return queryData; //Retorna
}