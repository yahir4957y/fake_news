-- Tabla para tracking global de tokens de Gemini
CREATE TABLE token_usage_global (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_tokens_used BIGINT DEFAULT 0,
    total_requests INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar fila inicial
INSERT INTO token_usage_global (id) VALUES (gen_random_uuid());

-- Tabla para uso de tokens por usuario
CREATE TABLE token_usage_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id VARCHAR(255) UNIQUE NOT NULL,  -- ID de Clerk
    email VARCHAR(255),
    tokens_used BIGINT DEFAULT 0,
    requests_count INT DEFAULT 0,
    last_request TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);