-- Tabla para registrar reportes descargados
CREATE TABLE reports_export (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios(id) ON DELETE CASCADE NOT NULL,
    verificacion_id UUID REFERENCES verificaciones(id) ON DELETE CASCADE NOT NULL,
    formato VARCHAR(10) NOT NULL CHECK (formato IN ('pdf', 'csv')),
    estado VARCHAR(20) DEFAULT 'generado' CHECK (estado IN ('generado', 'descargado', 'error')),
    archivo_url TEXT,
    archivo_nombre VARCHAR(255),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descargado_en TIMESTAMP,
    error_mensaje TEXT
);

-- Índices para consultas rápidas
CREATE INDEX idx_reports_usuario ON reports_export(usuario_id, creado_en DESC);
CREATE INDEX idx_reports_verificacion ON reports_export(verificacion_id);
CREATE INDEX idx_reports_estado ON reports_export(estado);
