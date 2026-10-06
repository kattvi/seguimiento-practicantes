-- =============================================================================
-- Sistema web para el control y seguimiento de practicantes
-- Esquema de base de datos (MySQL 8.0.16 o superior) - versión 1.0
--
-- Tablas: usuario, practicante, actividad
-- Vista:  v_progreso_practicante (horas acumuladas, restantes y % de avance)
--
-- Las restricciones CHECK solo se aplican desde MySQL 8.0.16.
--
-- Reglas que se validan en la aplicación (no se pueden expresar como CHECK
-- de una sola fila):
--   * Un practicante no puede registrar más de 8 horas en total por día.
--   * La fecha de una actividad debe estar entre fecha_inicio y fecha_termino.
-- =============================================================================

CREATE TABLE usuario (
    id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    correo          VARCHAR(120) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol             VARCHAR(15)  NOT NULL DEFAULT 'practicante',
    activo          BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT ck_usuario_rol CHECK (rol IN ('administrador', 'practicante'))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE practicante (
    id_practicante   INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario       INT          NOT NULL UNIQUE,
    matricula        VARCHAR(30)  NOT NULL UNIQUE,
    universidad      VARCHAR(100) NOT NULL,
    carrera          VARCHAR(100) NOT NULL,
    telefono         VARCHAR(20),
    supervisor       VARCHAR(100) NOT NULL,
    fecha_inicio     DATE         NOT NULL,
    fecha_termino    DATE         NOT NULL,
    horas_requeridas SMALLINT     NOT NULL DEFAULT 480,
    estado           VARCHAR(10)  NOT NULL DEFAULT 'activo',
    CONSTRAINT fk_practicante_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario),
    CONSTRAINT ck_practicante_horas   CHECK (horas_requeridas > 0),
    CONSTRAINT ck_practicante_fechas  CHECK (fecha_termino >= fecha_inicio),
    CONSTRAINT ck_practicante_estado  CHECK (estado IN ('activo', 'terminado', 'baja'))
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE TABLE actividad (
    id_actividad   INT AUTO_INCREMENT PRIMARY KEY,
    id_practicante INT           NOT NULL,
    fecha          DATE          NOT NULL,
    descripcion    VARCHAR(300)  NOT NULL,
    horas          DECIMAL(3, 1) NOT NULL,
    CONSTRAINT fk_actividad_practicante FOREIGN KEY (id_practicante) REFERENCES practicante (id_practicante),
    CONSTRAINT ck_actividad_horas       CHECK (horas > 0 AND horas <= 8)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

CREATE INDEX idx_actividad_practicante ON actividad (id_practicante, fecha);

-- Progreso de cada practicante (RN-02 y RN-03)
CREATE VIEW v_progreso_practicante AS
SELECT
    p.id_practicante,
    u.nombre AS practicante,
    p.horas_requeridas,
    COALESCE(SUM(a.horas), 0) AS horas_acumuladas,
    GREATEST(p.horas_requeridas - COALESCE(SUM(a.horas), 0), 0) AS horas_restantes,
    LEAST(ROUND(COALESCE(SUM(a.horas), 0) * 100.0 / p.horas_requeridas, 1), 100) AS porcentaje_avance
FROM practicante p
JOIN usuario u ON u.id_usuario = p.id_usuario
LEFT JOIN actividad a ON a.id_practicante = p.id_practicante
GROUP BY p.id_practicante, u.nombre, p.horas_requeridas;
