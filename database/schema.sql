-- extensiones
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- usuarios
CREATE TABLE usuarios (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nombre VARCHAR(150),
    foto_url TEXT,
    proveedor_auth VARCHAR(50),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado BOOLEAN DEFAULT TRUE
);

-- roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);

INSERT INTO roles (nombre, descripcion) VALUES
('ADMIN', 'Administrador'),
('USUARIO', 'Usuario normal');

-- usuario_roles
CREATE TABLE usuario_roles (
    id SERIAL PRIMARY KEY,
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    rol_id INT REFERENCES roles(id),
    UNIQUE(usuario_id, rol_id)
);

-- contenidos
CREATE TABLE contenidos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    tipo VARCHAR(20) NOT NULL,
    url TEXT,
    texto TEXT,
    hash_contenido TEXT,
    estado VARCHAR(20) DEFAULT 'pendiente',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_tipo_contenido CHECK (tipo IN ('texto', 'imagen', 'video', 'url'))
);

-- verificaciones
CREATE TABLE verificaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    contenido_id UUID REFERENCES contenidos(id) ON DELETE CASCADE,
    tipo_verificacion VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'en_proceso',
    score_credibilidad DECIMAL(5,2),
    nivel_credibilidad VARCHAR(20),
    version INT DEFAULT 1,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP,
    ip_usuario INET,
    dispositivo TEXT
);

-- analisis
CREATE TABLE analisis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verificacion_id UUID REFERENCES verificaciones(id) ON DELETE CASCADE,
    tipo_analisis VARCHAR(50),
    herramienta VARCHAR(100),
    score_credibilidad DECIMAL(5,2),
    peso DECIMAL(3,2),
    detalles JSONB,
    insights JSONB,
    tiempo_respuesta_ms INT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- retroalimentacion ia
CREATE TABLE retroalimentacion_ia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verificacion_id UUID REFERENCES verificaciones(id) ON DELETE CASCADE,
    resumen TEXT,
    recomendacion TEXT,
    fuentes_sugeridas JSONB,
    mostrar_recomendacion BOOLEAN DEFAULT FALSE,
    modelo_ia VARCHAR(100),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- etiquetas
CREATE TABLE etiquetas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL
);

-- contenido_etiquetas
CREATE TABLE contenido_etiquetas (
    id SERIAL PRIMARY KEY,
    contenido_id UUID REFERENCES contenidos(id) ON DELETE CASCADE,
    etiqueta_id INT REFERENCES etiquetas(id),
    UNIQUE(contenido_id, etiqueta_id)
);

-- reportes
CREATE TABLE reportes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contenido_id UUID REFERENCES contenidos(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    motivo TEXT,
    estado VARCHAR(20) DEFAULT 'pendiente',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- historial_consultas
CREATE TABLE historial_consultas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE,
    contenido_id UUID REFERENCES contenidos(id),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- logs_sistema
CREATE TABLE logs_sistema (
    id BIGSERIAL PRIMARY KEY,
    usuario_id UUID,
    accion VARCHAR(100),
    tabla_afectada VARCHAR(50),
    registro_id UUID,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- indices
CREATE INDEX idx_usuario_email ON usuarios(email);
CREATE INDEX idx_contenido_usuario ON contenidos(usuario_id);
CREATE INDEX idx_contenido_tipo ON contenidos(tipo);
CREATE INDEX idx_hash_contenido ON contenidos(hash_contenido);
CREATE INDEX idx_verificacion_usuario ON verificaciones(usuario_id);
CREATE INDEX idx_verificacion_fecha ON verificaciones(fecha_inicio DESC);
CREATE INDEX idx_analisis_verificacion ON analisis(verificacion_id);
CREATE INDEX idx_json_detalles ON analisis USING GIN(detalles);
CREATE INDEX idx_json_insights ON analisis USING GIN(insights);
CREATE INDEX idx_reporte_estado ON reportes(estado);

-- funcion nivel credibilidad
CREATE OR REPLACE FUNCTION calcular_nivel(score DECIMAL)
RETURNS VARCHAR AS $$
BEGIN
    IF score IS NULL THEN
        RETURN NULL;
    ELSIF score <= 30 THEN
        RETURN 'baja';
    ELSIF score <= 70 THEN
        RETURN 'media';
    ELSE
        RETURN 'alta';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- trigger nivel credibilidad
CREATE OR REPLACE FUNCTION set_nivel_credibilidad()
RETURNS TRIGGER AS $$
BEGIN
    NEW.nivel_credibilidad := calcular_nivel(NEW.score_credibilidad);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_nivel_credibilidad
BEFORE INSERT OR UPDATE ON verificaciones
FOR EACH ROW
EXECUTE FUNCTION set_nivel_credibilidad();
