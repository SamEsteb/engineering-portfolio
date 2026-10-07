# 🗺️ UdeCMapp — Campus & Indoor Navigation System

> **Portfolio Showcase**: Este repositorio udecmapp es un prototipo que contiene el código fuente, diseño de arquitectura y lógica de negocio del sistema **UdeCMapp**. Está preparado como muestra de ingeniería de software, patrones de desarrollo y diseño de sistemas distribuidos.

---

## 📐 Arquitectura del Sistema

El proyecto está diseñado bajo un desacoplamiento entre el cliente móvil y los servicios backend de soporte:

```
udecmapp/
├── app/                        # Cliente Móvil (Flutter / Dart)
│   ├── lib/
│   │   ├── config/             # Configuración centralizada y variables de entorno (ApiConfig)
│   │   ├── pages/              # Vistas principales, Mapa interactivo, Gestor de Nodos (Grafos)
│   │   ├── screens/            # Pantallas secundarias: Asistente IA (Gemini), Contactos, Historial
│   │   └── main.dart           # Punto de entrada de la aplicación
│   └── pubspec.yaml            # Especificación de dependencias y librerías
│
└── api/                        # Servicios Backend (Python / Flask)
    ├── mongo_api/              # Microservicio REST con persistencia en MongoDB (Document-based)
    │   ├── app.py              # Endpoints para edificios, pisos, habitaciones y nodos
    │   └── script.py           # Script de migración y estructuración de grafos
    └── sqlite_api/             # Microservicio REST alternativo con SQLite (Relational)
        ├── app.py              # API Flask relacional
        ├── sql_habitaciones.py # Operaciones CRUD de habitaciones
        ├── sql_nodos.py        # Operaciones de grafos y conexiones
        └── tablas.sql          # Esquema DDL de bases de datos
```

---

## 🚀 Tecnologías y Habilidades Demostradas

### 📱 Frontend (Mobile)

- **Framework:** Flutter & Dart (Null-safety)
- **Mapas y Geolocalización:** `flutter_map` (OpenStreetMap), `latlong2`, `geolocator`
- **Enrutamiento por Grafos:** Algoritmos para cálculo de rutas y navegación entre pisos y habitaciones (`nodos_manager.dart`)
- **Inteligencia Artificial Generativa:** Integración directa con Google Generative AI (Gemini Pro) para asistencia contextual en campus
- **Persistencia Local:** `shared_preferences` para historial de búsquedas
- **Buenas Prácticas:** Configuración centralizada (`ApiConfig`), inyección de variables de entorno (`flutter_dotenv`) y diseño modular de widgets

### 🐍 Backend & Bases de Datos

- **Framework Web:** Python 3 + Flask + Flask-CORS
- **NoSQL:** MongoDB con PyMongo para almacenamiento flexible de topologías y grafos
- **SQL:** SQLite3 con diseño relacional estructurado (`tablas.sql`)
- **Diseño de APIs:** Endpoints RESTful JSON optimizados para consumo móvil
- **Seguridad y Configuración:** Manejo seguro de secretos mediante `python-dotenv` y archivos `.env`

---
