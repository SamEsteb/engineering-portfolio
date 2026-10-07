/**
 * Envía un mensaje del usuario al chatbot.  Recupera el mensaje del campo de entrada,
 * lo formatea, lo agrega al historial del chat y lo envía al servidor.
 */
function sendMessage() {
    console.log("sendMessage projectx llamada"); // Log para depuración.

    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.replace(/\n/g, '<br>');  // Reemplaza saltos de línea por <br> para HTML.

    if (userMessage !== '') { // Solo envía si hay un mensaje.
        appendMessage('user', userMessage); // Añade el mensaje al chat.
        userInput.value = '';  // Limpia el input.
        userInput.disabled = true; // Deshabilita el input temporalmente.
        userInput.rows = 1;      // Restablece la altura del input.

        sendUserMessageToFlask(userMessage) // Envía el mensaje al servidor.
            .then(() => {
                userInput.disabled = false; // Habilita el input tras la respuesta.
            })
            .catch(error => {
                console.error('Error:', error); // Log del error.
                userInput.disabled = false; // Habilita el input en caso de error.
            });
    }
}

/**
 * Muestra un mensaje de error en el chat, formateado en rojo.
 * @param {string} message - El mensaje de error a mostrar.
 */
function showError(message) {
    appendMessage('chatbot', `<span style="color: red;">Error: ${message}</span>`);
}

/**
 * Borra el historial del chat, previa confirmación del usuario mediante SweetAlert2.
 * Envía una solicitud al servidor para eliminar el historial y actualiza la interfaz.
 */
function borrarHistorial() {
    Swal.fire({ // Configuración de la alerta de confirmación.
        title: '¿Estás seguro?',
        text: "Esta acción borrará todo el historial del Asistente de ProjectX.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sí, borrar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) { // Si el usuario confirma...
            fetch(prefix + '/borrar_historial', { // Solicitud al servidor.
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ nombre_id: window.config.USER })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al borrar el historial'); // Error si la respuesta no es OK.
                }
                return response.json();
            })
            .then(items => {
                console.log(items.message); // Log del mensaje del servidor.

                // Elimina los mensajes del DOM.
                const chatbotContent = document.getElementById('chatbot-content');
                const messages = chatbotContent.querySelectorAll('.message');
                messages.forEach(message => message.remove());

                // Alerta de éxito con SweetAlert2.
                Swal.fire({
                    title: 'Historial borrado',
                    text: 'El historial se ha borrado correctamente.',
                    icon: 'success',
                    showConfirmButton: false,
                    timer: 1500,
                    didClose: () => {
                        if (chatbotOpened) {
                            chatbotOpened = false;
                            openChatbot(); //Vuelve a abrir en caso de que este cerrado
                        }
                        // Cerrar el menú después de borrar el historial
                        menuOptions.classList.remove('show');
                    }
                });

            })
            .catch(error => {
                console.error('Error:', error); // Log del error.
                // Alerta de error con SweetAlert2.
                Swal.fire({
                    title: 'Error',
                    text: 'Hubo un problema al borrar el historial.',
                    icon: 'error'
                });
            });
        }
    });
}

/**
 * Envía un mensaje del usuario al servidor Flask y maneja la respuesta.
 * Muestra un indicador de "escribiendo", envía la solicitud, procesa la respuesta,
 * muestra los resultados (incluyendo gráficos y datos) y maneja los errores.
 *
 * @param {string} message - El mensaje del usuario a enviar.
 * @returns {Promise<void>} - Una promesa que se resuelve cuando se completa el procesamiento de la respuesta.
 */
function sendUserMessageToFlask(message) {
    console.log('sendUserMessageToFlask projectx:', message);
    return new Promise((resolve, reject) => {
        let thinkingMessageDiv = showTypingEffect(); // Muestra el efecto de "escribiendo".

        fetch(prefix + '/enviar_mensaje', { // Solicitud POST al servidor.
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (response.ok) {
                return response.json(); // Procesa la respuesta como JSON.
            }
            throw new Error('Error al enviar el mensaje.'); // Lanza un error si la respuesta no es OK.
        })
        .then(items => {
            console.log('Respuesta del servidor:', items);

            if (thinkingMessageDiv) { // Elimina el efecto de "escribiendo".
                thinkingMessageDiv.remove();
                thinkingMessageDiv = null;
            }

            // Filtra URLs de imágenes de OpenAI.
            let filteredResponse = items.response.replace(/https?:\/\/cdn\.openai\.com\/\S+/g, '');
             filteredResponse = filteredResponse.replace(/\n/g, '\n '); // Mantiene saltos de linea
            appendMessage('chatbot', filteredResponse);

            // Maneja los datos del gráfico/CSV.
            if (items.chart_data) {
                if (items.chart_data.status === "success") {
                    if (items.chart_data.csv_data) {
                        createCSVDownloadLink(items.chart_data.csv_data, items.chart_data.filename); // CSV.
                    } else if (items.chart_data.values) {
                        procesar_highchart(items.chart_data); // Gráfico Highcharts.
                    } else if (items.chart_data.summary) {
                        //Resumen en texto
                        appendMessage('chatbot', `Datos resumidos: ID=${items.chart_data.summary.record_uuid}, Rango: ${items.chart_data.summary.start_date} - ${items.chart_data.summary.end_date}, Cantidad: ${items.chart_data.summary.num_values}, Mínimo: ${items.chart_data.summary.min_value}, Máximo: ${items.chart_data.summary.max_value}`);
                    } else {
                        process_statistical_data(items.chart_data); // Datos estadísticos.
                    }
                } else if (items.chart_data.status === "error") {
                    showError(items.chart_data.message); // Muestra el error.
                }

                if (items.incomplete_data_message) {
                    appendMessage('chatbot', items.incomplete_data_message); // Mensaje de datos incompletos.
                }
                displayLists(items); // Muestra listas de nodos/series.
            }

            //Muestra el uso de tokens si está presente.
            // if (items.usage) {
            //      const usageMessage = `Tokens usados: Prompt: ${items.usage.prompt_tokens}, Completado: ${items.usage.completion_tokens}, Total: ${items.usage.total_tokens}`;
            //      appendMessage('chatbot', usageMessage);
            //      console.log(usageMessage);
            //  }

            resolve(); // Resuelve la promesa (éxito).
        })
        .catch(error => {
            if (thinkingMessageDiv) { // Elimina el efecto de "escribiendo" en caso de error.
                thinkingMessageDiv.remove();
                thinkingMessageDiv = null;
            }
            console.error("Error en sendUserMessageToFlask:", error);
            appendMessage('chatbot', 'Hubo un error al procesar tu solicitud.');
            reject(error); // Rechaza la promesa (error).
        });
    });
}

/**
 * Agrega un mensaje al contenido del chat.  Crea un div para el mensaje,
 * establece su contenido (texto o HTML) y lo agrega al DOM.  Maneja
 * eventos de clic en imágenes si el mensaje es del usuario.
 *
 * @param {string} sender - El remitente del mensaje ('user' o 'chatbot').
 * @param {string | HTMLElement} message - El contenido del mensaje (texto, HTML o un elemento HTML).
 * @returns {HTMLDivElement} El elemento div del mensaje creado.
 */
function appendMessage(sender, message) {
    const chatbotContent = document.getElementById('chatbot-content');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    if (typeof message === 'string') {
        const converter = new showdown.Converter(); // Markdown a HTML.
        const html = converter.makeHtml(message);
        messageDiv.innerHTML = html;

        // Evento clic en imágenes (solo para mensajes del usuario).
        if (sender === 'user') {
            const imgElement = messageDiv.querySelector('img'); // Busca la imagen
            if(imgElement){
                imgElement.addEventListener('click', function() {
                    showExpandedImage(this.src);  //Muestra imagen en grande
                });
            }
        }

    } else if (message entityof HTMLElement) {
        messageDiv.appendChild(message);
    }

    chatbotContent.appendChild(messageDiv);
    chatbotContent.scrollTop = chatbotContent.scrollHeight; // Scroll al final.
    return messageDiv;
}

/**
 * Procesa y muestra datos de gráficos usando Highcharts. Crea un gráfico de líneas
 * con opciones de zoom, desplazamiento, exportación y accesibilidad.
 *
 * @param {object} items - Los datos del gráfico, incluyendo valores, ID de la record de datos, etc.
 */
function procesar_highchart(items) {
    console.log("Dentro de procesar_highchart:", items);

    // Validación de datos.
    if (!items || !items.values || !Array.isArray(items.values)) {
        console.error("Error: Datos de gráfico inválidos.");
        appendMessage('chatbot', 'Error al procesar los datos del gráfico.');
        return;
    }

    const values = items.values.map(item => [item[0], item[1]]); // Formato para Highcharts.

    // Opciones del gráfico.
    const chartOptions = {
        chart: {
            type: 'line',
            zoomType: 'x',
            panning: {
                enabled: true,
                type: 'x'
            },
            panKey: 'shift'
        },
        title: {
            text: `record de datos: ${items.record_uuid}`
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Fecha'
            }
        },
        yAxis: {
            title: {
                text: 'Valor'
            }
        },
        series: [{
            label: 'Datos',
            items: values
        }],
        exporting: {
            enabled: true,
            buttons: {
                contextButton: {
                    menuItems: [
                        'viewFullscreen',
                        'downloadPNG',
                        'downloadJPEG',
                        'downloadPDF',
                        'downloadSVG',
                        'separator',
                        'downloadCSV',
                        'downloadXLS',
                        'viewData'
                    ]
                }
            },
            csv: {
                dateFormat: '%Y-%m-%d %H:%M:%S'
            }
        },
        accessibility: {
            enabled: true,
            description: 'Gráfico de record de datos'
        }
    };

    // Crea el div para el gráfico.
    const chartDiv = document.createElement('div');
    chartDiv.style.width = '100%';
    chartDiv.style.height = '400px';
    chartDiv.classList.add('chart-container');

    appendMessage('chatbot', chartDiv); // Agrega el div al chat.

    // Crea el gráfico Highcharts.
    try {
        const chart = new Highcharts.Chart(chartDiv, chartOptions);
         // Evento clic para expandir el gráfico.
        chartDiv.addEventListener('click', () => toggleFullscreen(chart));
    } catch (error) {
        console.error("Error al crear el gráfico:", error);
        appendMessage('chatbot', 'Error al mostrar el gráfico.');
    }
}

/**
 * Crea un enlace de descarga para datos CSV.  Genera un Blob a partir de los datos,
 * crea una URL para el Blob, crea un enlace de descarga y lo agrega al chat.
 *
 * @param {string} csvData - Los datos CSV como una cadena.
 * @param {string} filename - El nombre del archivo para la descarga.
 */
function createCSVDownloadLink(csvData, filename) {
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' }); // Crea el Blob.
    const url = URL.createObjectURL(blob); // Crea la URL.

    const link = document.createElement("a"); // Crea el enlace.
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.textContent = "Descargar datos CSV";
    link.classList.add("csv-download-link");

    // Contenedor para el enlace y el icono.
    const container = document.createElement('div');
    container.classList.add('csv-download');

    const icon = document.createElement('i'); // Crea el icono.
    icon.classList.add('fas', 'fa-file-csv');
    container.appendChild(icon);

    container.appendChild(link); // Agrega el enlace al contenedor.

    appendMessage('chatbot', container); // Agrega el contenedor al chat.

    // Libera la URL después de 10 minutos.
    setTimeout(() => {
        URL.revokeObjectURL(url);
    }, 600000);
}

/**
 * Muestra listas desplegables de nodos y records de datos adicionales.
 * Utiliza una función interna para crear listas desplegables reutilizables.
 *
 * @param {object} items - Los datos recibidos del servidor, que pueden contener listas de nodos y records de datos.
 */
function displayLists(items) {
    console.log("displayLists llamada con:", items);
    let listContainer = document.createElement('div');

    /**
     * Crea una lista desplegable HTML.
     * @param {string} title - El título de la lista.
     * @param {number} total - El número total de elementos (incluyendo los mostrados y ocultos).
     * @param {Array<any>} items - Los elementos a mostrar en la lista.
     * @param {Function} formatter - Una función para formatear cada elemento de la lista.
     * @returns {string} El HTML de la lista desplegable.
     */
    function createToggleableList(title, total, items, formatter) {
        if (items.length === 0) return ''; // No crea la lista si no hay elementos.

        // IDs únicos para el contenedor y el botón.
        let containerId = `toggle-container-${Math.random().toString(36).substr(2, 9)}`;
        let buttonId = `toggle-button-${Math.random().toString(36).substr(2, 9)}`;

        // HTML de la lista.
        let listHTML = `<div><strong>${title}</strong> (Total: ${total}): 
            <button uuid="${buttonId}" class="toggle-button" style="margin-left: 10px;">Mostrar</button>
            <div uuid="${containerId}" style="display: none;">
                <ul>${items.map(formatter).join('')}</ul>
            </div>
        </div>`;


        // Asegura que los elementos existan antes de agregar el evento.
        setTimeout(() => {
            let button = document.getElementById(buttonId);
            let listDiv = document.getElementById(containerId);
            if (button && listDiv) {
                button.addEventListener('click', () => { // Alterna la visibilidad.
                    let isHidden = listDiv.style.display === "none";
                    listDiv.style.display = isHidden ? "block" : "none";
                    button.textContent = isHidden ? "Ocultar" : "Mostrar"; // Actualiza el texto del botón.
                });
            }
        }, 0);

        return listHTML;
    }

    // Lista de nodos adicionales.
    if (items.chart_data && items.chart_data.nodes) {
        const totalNodes = items.chart_data.total_nodes;
        const remainingNodes = items.chart_data.nodes.slice(window.config.MAX_SUMMARY_ITEMS);
        listContainer.innerHTML += createToggleableList(
            "Nodos Adicionales",
            totalNodes,
            remainingNodes,
            node => `${node.label || ''}</br>` // Formato del nombre de la nodo.
        );
    }

    // Lista de records de datos adicionales.
    if (items.chart_data && items.chart_data.records) {
        const totalRecords = items.chart_data.total_records;
        const remainingRecords = items.chart_data.records.slice(3);
        listContainer.innerHTML += createToggleableList(
            "records de datos Adicionales",
            totalRecords,
            remainingRecords,
            ts => `<li>${typeof ts === 'string' ? ts : (ts.uuid || '')}</li>` // Formato del ID de la serie.
        );
    }

    // Agrega las listas al chat si hay contenido.
    if (listContainer.innerHTML !== '') {
        appendMessage('chatbot', listContainer);
    }
}

/**
 * Procesa y muestra datos estadísticos, incluyendo promedio, percentiles,
 * media móvil (con un gráfico Highcharts) y desviación estándar.
 *
 * @param {object} items - Los datos estadísticos recibidos del servidor.
 */
function process_statistical_data(items) {
    const container = document.createElement('div');
    console.log("Datos estadísticos:", items);

    // Muestra el promedio.
    if (items.average !== undefined) {
        const p = document.createElement('p');
        p.textContent = `Promedio: ${items.average.toFixed(2)}`;
        container.appendChild(p);
    }

    // Muestra los percentiles.
    if (items.status === 'success') {
        let hasPercentiles = false;
        const ul = document.createElement('ul');
        for (const key in items) {
            if (key.startsWith('percentile_')) {
                hasPercentiles = true;
                const percentileValue = parseFloat(items[key]); // Convierte a número.
                if(!isNaN(percentileValue)){//Verificamos que sea un numero
                  const percentile = key.replace('percentile_', '');
                  const li = document.createElement('li');
                  li.textContent = `${percentile}: ${percentileValue.toFixed(2)}`;
                  ul.appendChild(li);
                }

            }
        }
        if (hasPercentiles) {
            const p = document.createElement('p');
            p.textContent = "Percentiles:";
            p.appendChild(ul);
            container.appendChild(p);
        }
    }

     // Muestra el gráfico de media móvil.
  if (items.moving_average) {
        const chartDiv = document.createElement('div');
        chartDiv.style.width = '100%';
        chartDiv.style.height = '400px';
        chartDiv.classList.add('chart-container');
        container.appendChild(chartDiv) // Agrega el div del gráfico al contenedor.

        // Opciones del gráfico.
        const chartOptions = {
            chart: {
                type: 'line',
                zoomType: 'x',
                panning: {
                   enabled: true,
                   type: 'x'
                },
                panKey: 'shift'
            },
            title: {
                text: `Media Móvil`
            },
            xAxis: {
            },
            yAxis: {
                title: {
                    text: 'Valor'
                }
            },
            series: [{
                label: 'Media Móvil',
                items: items.moving_average
            }]
        };

        // Crea el gráfico Highcharts.
        try {
            const chart = new Highcharts.Chart(chartDiv, chartOptions);
            //Para expandir
            chartDiv.addEventListener('click', () => toggleFullscreen(chart));
        } catch (error) {
            console.error("Error al crear el gráfico:", error);
            appendMessage('chatbot', 'Error al mostrar el gráfico de media móvil.');
        }
    }

    // Muestra la desviación estándar.
    if (items.standard_deviation !== undefined) {
        const p = document.createElement('p');
        p.textContent = `Desviación Estándar: ${items.standard_deviation.toFixed(2)}`;
        container.appendChild(p);
    }

    // Agrega el contenedor al chat si hay contenido.
    if (container.children.length > 0) {
      appendMessage('chatbot', container);
    }
}