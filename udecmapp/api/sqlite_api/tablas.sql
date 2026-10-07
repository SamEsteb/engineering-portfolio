-- Tabla para EDIFICIO
CREATE TABLE EDIFICIO (
    id_edificio INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT
);

-- Tabla para PISO
CREATE TABLE PISO (
    id_piso INTEGER PRIMARY KEY,
    numero_piso INTEGER NOT NULL,
    id_edificio INTEGER NOT NULL,
    FOREIGN KEY (id_edificio) REFERENCES EDIFICIO(id_edificio)
);

-- Tabla para ESPACIO
CREATE TABLE ESPACIO (
    id_espacio INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    tipo TEXT,
    id_piso INTEGER NOT NULL,
    coordenada_x REAL NOT NULL,
    coordenada_y REAL NOT NULL,
    imagen_url TEXT,
    FOREIGN KEY (id_piso) REFERENCES PISO(id_piso)
);

-- Tabla para RUTA
CREATE TABLE RUTA (
    id_ruta INTEGER PRIMARY KEY,
    id_espacio_inicio INTEGER NOT NULL,
    id_espacio_fin INTEGER NOT NULL,
    descripcion TEXT,
    FOREIGN KEY (id_espacio_inicio) REFERENCES ESPACIO(id_espacio),
    FOREIGN KEY (id_espacio_fin) REFERENCES ESPACIO(id_espacio)
);

-- Tabla para USUARIO
CREATE TABLE USUARIO (
    id_usuario INTEGER PRIMARY KEY,
    tipo TEXT NOT NULL,
    nombre TEXT NOT NULL
);

-- Tabla para BUSQUEDA
CREATE TABLE BUSQUEDA (
    id_busqueda INTEGER PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    consulta TEXT NOT NULL,
    fecha_hora DATETIME NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
);

-- Tabla para CODIGO_QR
CREATE TABLE CODIGO_QR (
    id_codigo_qr INTEGER PRIMARY KEY,
    id_espacio INTEGER NOT NULL,
    contenido TEXT NOT NULL,
    FOREIGN KEY (id_espacio) REFERENCES ESPACIO(id_espacio)
);

-- Tabla para CHATBOT
CREATE TABLE CHATBOT (
    id_chatbot INTEGER PRIMARY KEY
);
