# 🤖 Chatbot: AI-Powered Assistant & Integration Engine (Portfolio Showcase)

> **Nota de Privacidad y Portafolio:**  
> Este módulo forma parte de mi portafolio profesional de desarrollo de software. Para proteger la propiedad intelectual, endpoints privados y detalles de negocio específicos de la solución original, el código fuente ha sido **enmascarado y anonimizado** (estructuras de datos, variables, prompts de sistema y nombres de entidad genéricos como `ProjectX`, `Nodes`, `Records`, `Attributes`).  
>
> A pesar de la anonimización, la **arquitectura técnica, patrones de diseño, integración con LLMs, function calling y la interacción dinámica del frontend** permanecen intactos como evidencia de mis capacidades técnicas.

---

## 📌 Descripción del Proyecto

Este proyecto consiste en un **Asistente Virtual Inteligente (Chatbot)** capaz de interpretar comandos e intenciones en lenguaje natural y traducirlos en ejecuciones estructuradas contra APIs externas y bases de datos jerárquicas.

El sistema combina el procesamiento de lenguaje natural (NLP) basado en **LLMs (OpenAI)** con un motor de **Function Calling / Tool Use**, permitiendo que el chatbot no solo responda preguntas conversacionales, sino que consulte, procese, filtre y presente datos estructurados en tiempo real a través de una interfaz web interactiva.

---

## 🎯 Capacidades Demostradas

- **Orquestación de LLMs & Function Calling:** Integración avanzada con modelos de OpenAI para extracción de intenciones y parámetros desde texto no estructurado.
- **Integración y Consulta Jerárquica de APIs:** Consumo y abstracción de servicios HTTP REST para la navegación por entidades complejas (nodos, contextos, niveles y registros).
- **Validación y Capa de Datos Permitidos:** Filtrado de seguridad y validación de atributos permitidos antes de enviar consultas a la API o al LLM.
- **Motor Estático de Respaldo (Fallback):** Mecanismo resiliente para procesar consultas predeterminadas mediante reglas y árboles de decisión locales sin depender exclusivamente de un proveedor de IA externo.
- **Frontend Dinámico en JS Vanilla:** Interfaz conversacional responsiva con soporte para mensajes rich (botones dinámicos, gráficos de datos, formularios y renderizado condicional).

---

## 📂 Estructura del Código

```text
chatbot/
├── chatbot_logic/                   # Capa principal de lógica del Backend (Python / Flask)
│   ├── projectx.py                  # Endpoint Flask y orquestador principal del flujo de mensajes
│   ├── chatbot_projectx.py          # Lógica conversacional y conexión con la API del LLM
│   ├── funciones_projectx.py        # Cliente HTTP y funciones para interacción con APIs externas
│   ├── bot_estatico.py              # Motor de resolución local por reglas / fallback
│   ├── config.py                    # Configuración de entornos y variables del sistema
│   └── datos_permitidos/            # Módulo de validación y lista blanca de datos
│       └── datos_permitidos.py      # Estructuras de validación de dominios, nodos y métricas
│
└── static/                          # Recursos estáticos del Frontend
    ├── css/                         # Hojas de estilo y sistema de diseño visual
    │   ├── style.css                # Estilos generales del chat e interfaz
    │   └── style_projectx.css       # Modificadores visuales y componentes específicos
    └── js/                          # Componentes y controladores de UI (Vanilla JS)
        ├── script.js                # Manejo general del chat, envío/recepción de mensajes
        ├── projectx.js              # Controlador de estado y formateador de respuestas
        └── botones_projectx.js      # Generación dinámica de botones y widgets interactivos
```

---

## 🛠️ Tecnologías y Herramientas Demostradas

### **Backend & AI Engine**

- **Python 3.x:** Lenguaje principal de desarrollo backend.
- **Flask:** Framework web ligero para la exposición de endpoints conversacionales y gestión de solicitudes.
- **OpenAI API (GPT-4 / GPT-3.5):** Uso de LLMs para análisis conversacional y arquitectura *Function Calling*.
- **Requests / HTTP Clients:** Consumo robusto de servicios API REST con manejo de errores y timeouts.

### **Frontend & User Interface**

- **JavaScript (ES6+):** Código nativo estructurado modularmente para manipulación del DOM y asincronía (`async/await`, `fetch`).
- **HTML5 & CSS3:** Diseño responsivo, adaptado a dispositivos móviles y escritorio, con componentes modulares de chat.

### **Arquitectura & Patrones de Software**

- **Clean Architecture & Separation of Concerns:** Desacoplamiento total entre la UI, la lógica de negocio, los clientes de API y los adaptadores de IA.
- **Pattern Matching & Rule-Based Fallback:** Resiliencia operativa en la entrega de datos incluso ante fallas de conectividad externa.
- **Security & Data Sanitization:** Validación rigurosa de entradas y restricciones de alcance (*whitelisting*) antes de la ejecución de código.
