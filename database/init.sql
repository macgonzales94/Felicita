-- ==============================================
-- ESQUEMA BASE DE DATOS FELICITA
-- Sistema de Facturación Electrónica para Perú
-- PostgreSQL 15+ con collation español Perú
-- ==============================================

-- Configurar encoding y collation para Perú
ALTER DATABASE felicita_db SET datestyle TO "ISO, DMY";
ALTER DATABASE felicita_db SET timezone TO 'America/Lima';

-- ==============================================
-- EXTENSIONES NECESARIAS
-- ==============================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- ==============================================
-- TIPOS DE DATOS PERSONALIZADOS
-- ==============================================

-- Tipo de comprobante SUNAT
CREATE TYPE tipo_comprobante_enum AS ENUM (
    '01', -- Factura
    '03', -- Boleta de Venta
    '07', -- Nota de Crédito
    '08', -- Nota de Débito
    '09'  -- Guía de Remisión
);

-- Estado de comprobante
CREATE TYPE estado_comprobante_enum AS ENUM (
    'PENDIENTE',
    'ENVIADO',
    'ACEPTADO',
    'RECHAZADO',
    'ANULADO'
);

-- Tipo de documento de identidad
CREATE TYPE tipo_documento_enum AS ENUM (
    '1', -- DNI
    '4', -- Carnet de extranjería
    '6', -- RUC
    '7', -- Pasaporte
    '0'  -- Otros
);

-- Tipo de moneda
CREATE TYPE tipo_moneda_enum AS ENUM (
    'PEN', -- Sol Peruano
    'USD', -- Dólar Americano
    'EUR'  -- Euro
);

-- Estados de movimiento de inventario
CREATE TYPE tipo_movimiento_inventario_enum AS ENUM (
    'ENTRADA',
    'SALIDA',
    'TRANSFERENCIA',
    'AJUSTE'
);

-- ==============================================
-- TABLA: EMPRESAS
-- ==============================================

CREATE TABLE empresas (
    id SERIAL PRIMARY KEY,
    ruc VARCHAR(11) NOT NULL UNIQUE,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    direccion TEXT NOT NULL,
    ubigeo VARCHAR(6),
    telefono VARCHAR(20),
    email VARCHAR(100),
    pagina_web VARCHAR(255),
    representante_legal VARCHAR(255),
    estado BOOLEAN DEFAULT TRUE,
    
    -- Configuración SUNAT
    usuario_sol VARCHAR(50),
    clave_sol VARCHAR(50),
    certificado_digital TEXT,
    
    -- Configuración contable
    plan_cuentas_id INTEGER,
    ejercicio_fiscal_inicio DATE DEFAULT '2024-01-01',
    
    -- Auditoria
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER,
    usuario_actualizacion INTEGER
);

-- Índices para empresas
CREATE INDEX idx_empresas_ruc ON empresas(ruc);
CREATE INDEX idx_empresas_estado ON empresas(estado);

-- ==============================================
-- TABLA: USUARIOS
-- ==============================================

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    
    -- Campos específicos FELICITA
    empresa_id INTEGER REFERENCES empresas(id),
    numero_documento VARCHAR(20),
    tipo_documento tipo_documento_enum DEFAULT '1',
    telefono VARCHAR(20),
    direccion TEXT,
    avatar VARCHAR(255),
    
    -- Permisos y roles
    rol VARCHAR(50) DEFAULT 'VENDEDOR', -- ADMIN, CONTADOR, VENDEDOR, CLIENTE
    permisos_especiales JSONB DEFAULT '{}',
    
    -- Configuraciones usuario
    configuraciones JSONB DEFAULT '{}',
    tema_preferido VARCHAR(20) DEFAULT 'claro',
    idioma VARCHAR(5) DEFAULT 'es-pe',
    
    -- Auditoria
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para usuarios
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_id);
CREATE INDEX idx_usuarios_activo ON usuarios(is_active);

-- ==============================================
-- TABLA: CLIENTES
-- ==============================================

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    
    -- Identificación
    numero_documento VARCHAR(20) NOT NULL,
    tipo_documento tipo_documento_enum NOT NULL,
    razon_social VARCHAR(255) NOT NULL,
    nombre_comercial VARCHAR(255),
    
    -- Contacto
    direccion TEXT,
    ubigeo VARCHAR(6),
    telefono VARCHAR(20),
    email VARCHAR(100),
    pagina_web VARCHAR(255),
    
    -- Información comercial
    condicion_pago VARCHAR(50) DEFAULT 'CONTADO',
    limite_credito DECIMAL(12,2) DEFAULT 0.00,
    vendedor_asignado_id INTEGER REFERENCES usuarios(id),
    
    -- Configuración fiscal
    exonerado_igv BOOLEAN DEFAULT FALSE,
    retencion_agente BOOLEAN DEFAULT FALSE,
    percepcion_agente BOOLEAN DEFAULT FALSE,
    
    -- Estado y auditoria
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER REFERENCES usuarios(id),
    usuario_actualizacion INTEGER REFERENCES usuarios(id),
    
    UNIQUE(empresa_id, numero_documento)
);

-- Índices para clientes
CREATE INDEX idx_clientes_empresa ON clientes(empresa_id);
CREATE INDEX idx_clientes_documento ON clientes(numero_documento);
CREATE INDEX idx_clientes_razon_social ON clientes USING gin(to_tsvector('spanish', razon_social));
CREATE INDEX idx_clientes_estado ON clientes(estado);

-- ==============================================
-- TABLA: CATEGORIAS_PRODUCTOS
-- ==============================================

CREATE TABLE categorias_productos (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria_padre_id INTEGER REFERENCES categorias_productos(id),
    estado BOOLEAN DEFAULT TRUE,
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(empresa_id, codigo)
);

-- ==============================================
-- TABLA: PRODUCTOS
-- ==============================================

CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    
    -- Identificación
    codigo VARCHAR(50) NOT NULL,
    codigo_barra VARCHAR(50),
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    categoria_id INTEGER REFERENCES categorias_productos(id),
    
    -- Clasificación SUNAT
    codigo_sunat VARCHAR(20), -- Código de producto SUNAT
    tipo_producto VARCHAR(20) DEFAULT 'BIEN', -- BIEN, SERVICIO
    unidad_medida VARCHAR(10) DEFAULT 'NIU', -- Código SUNAT
    
    -- Precios
    precio_compra DECIMAL(12,4) DEFAULT 0.0000,
    precio_venta DECIMAL(12,4) NOT NULL,
    precio_venta_min DECIMAL(12,4),
    margen_ganancia DECIMAL(5,2) DEFAULT 0.00,
    
    -- Configuración impuestos
    afecto_igv BOOLEAN DEFAULT TRUE,
    codigo_impuesto VARCHAR(10) DEFAULT '1000', -- Código SUNAT
    
    -- Control de inventario
    maneja_stock BOOLEAN DEFAULT TRUE,
    stock_minimo DECIMAL(12,4) DEFAULT 0.0000,
    stock_maximo DECIMAL(12,4),
    
    -- Configuraciones adicionales
    peso DECIMAL(8,4),
    volumen DECIMAL(8,4),
    imagen VARCHAR(255),
    observaciones TEXT,
    
    -- Estado y auditoria
    estado BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER REFERENCES usuarios(id),
    usuario_actualizacion INTEGER REFERENCES usuarios(id),
    
    UNIQUE(empresa_id, codigo)
);

-- Índices para productos
CREATE INDEX idx_productos_empresa ON productos(empresa_id);
CREATE INDEX idx_productos_codigo ON productos(codigo);
CREATE INDEX idx_productos_codigo_barra ON productos(codigo_barra);
CREATE INDEX idx_productos_nombre ON productos USING gin(to_tsvector('spanish', nombre));
CREATE INDEX idx_productos_categoria ON productos(categoria_id);
CREATE INDEX idx_productos_estado ON productos(estado);

-- ==============================================
-- TABLA: ALMACENES
-- ==============================================

CREATE TABLE almacenes (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    direccion TEXT,
    responsable_id INTEGER REFERENCES usuarios(id),
    es_principal BOOLEAN DEFAULT FALSE,
    estado BOOLEAN DEFAULT TRUE,
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(empresa_id, codigo)
);

-- ==============================================
-- TABLA: STOCKS
-- ==============================================

CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos(id) ON DELETE CASCADE,
    almacen_id INTEGER REFERENCES almacenes(id) ON DELETE CASCADE,
    
    cantidad_disponible DECIMAL(12,4) DEFAULT 0.0000,
    cantidad_reservada DECIMAL(12,4) DEFAULT 0.0000,
    cantidad_total DECIMAL(12,4) GENERATED ALWAYS AS (cantidad_disponible + cantidad_reservada) STORED,
    
    costo_promedio DECIMAL(12,4) DEFAULT 0.0000,
    valor_total DECIMAL(12,2) GENERATED ALWAYS AS (cantidad_total * costo_promedio) STORED,
    
    fecha_ultimo_movimiento TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(producto_id, almacen_id)
);

-- Índices para stocks
CREATE INDEX idx_stocks_producto ON stocks(producto_id);
CREATE INDEX idx_stocks_almacen ON stocks(almacen_id);
CREATE INDEX idx_stocks_cantidad ON stocks(cantidad_disponible);

-- ==============================================
-- TABLA: SERIES_COMPROBANTES
-- ==============================================

CREATE TABLE series_comprobantes (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    tipo_comprobante tipo_comprobante_enum NOT NULL,
    serie VARCHAR(4) NOT NULL,
    numero_actual INTEGER DEFAULT 0,
    numero_maximo INTEGER DEFAULT 99999999,
    
    -- Configuración
    activo BOOLEAN DEFAULT TRUE,
    electronico BOOLEAN DEFAULT TRUE,
    por_defecto BOOLEAN DEFAULT FALSE,
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(empresa_id, tipo_comprobante, serie)
);

-- ==============================================
-- TABLA: COMPROBANTES
-- ==============================================

CREATE TABLE comprobantes (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    
    -- Identificación del comprobante
    tipo_comprobante tipo_comprobante_enum NOT NULL,
    serie VARCHAR(4) NOT NULL,
    numero INTEGER NOT NULL,
    numero_completo VARCHAR(20) GENERATED ALWAYS AS (serie || '-' || LPAD(numero::text, 8, '0')) STORED,
    
    -- Cliente
    cliente_id INTEGER REFERENCES clientes(id),
    cliente_numero_documento VARCHAR(20) NOT NULL,
    cliente_tipo_documento tipo_documento_enum NOT NULL,
    cliente_razon_social VARCHAR(255) NOT NULL,
    cliente_direccion TEXT,
    cliente_email VARCHAR(100),
    
    -- Fechas
    fecha_emision DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_vencimiento DATE,
    
    -- Montos
    moneda tipo_moneda_enum DEFAULT 'PEN',
    tipo_cambio DECIMAL(6,4) DEFAULT 1.0000,
    
    subtotal DECIMAL(12,2) DEFAULT 0.00,
    total_descuentos DECIMAL(12,2) DEFAULT 0.00,
    base_imponible DECIMAL(12,2) DEFAULT 0.00,
    total_igv DECIMAL(12,2) DEFAULT 0.00,
    total_otros_impuestos DECIMAL(12,2) DEFAULT 0.00,
    total_gratuito DECIMAL(12,2) DEFAULT 0.00,
    total_sin_impuestos DECIMAL(12,2) DEFAULT 0.00,
    total_con_impuestos DECIMAL(12,2) DEFAULT 0.00,
    
    -- Configuración
    forma_pago VARCHAR(50) DEFAULT 'CONTADO',
    condicion_pago VARCHAR(100),
    observaciones TEXT,
    
    -- Estado SUNAT
    estado_sunat estado_comprobante_enum DEFAULT 'PENDIENTE',
    codigo_hash VARCHAR(100),
    codigo_qr TEXT,
    xml_enviado TEXT,
    xml_respuesta TEXT,
    pdf_url VARCHAR(255),
    
    -- Referencia (para notas de crédito/débito)
    comprobante_referencia_id INTEGER REFERENCES comprobantes(id),
    motivo_nota TEXT,
    
    -- Auditoria
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER REFERENCES usuarios(id),
    usuario_actualizacion INTEGER REFERENCES usuarios(id),
    
    UNIQUE(empresa_id, tipo_comprobante, serie, numero)
);

-- Índices para comprobantes
CREATE INDEX idx_comprobantes_empresa ON comprobantes(empresa_id);
CREATE INDEX idx_comprobantes_cliente ON comprobantes(cliente_id);
CREATE INDEX idx_comprobantes_fecha_emision ON comprobantes(fecha_emision);
CREATE INDEX idx_comprobantes_numero_completo ON comprobantes(numero_completo);
CREATE INDEX idx_comprobantes_estado_sunat ON comprobantes(estado_sunat);
CREATE INDEX idx_comprobantes_tipo ON comprobantes(tipo_comprobante);

-- ==============================================
-- TABLA: ITEMS_COMPROBANTES
-- ==============================================

CREATE TABLE items_comprobantes (
    id SERIAL PRIMARY KEY,
    comprobante_id INTEGER REFERENCES comprobantes(id) ON DELETE CASCADE,
    producto_id INTEGER REFERENCES productos(id),
    
    -- Identificación del item
    numero_item INTEGER NOT NULL,
    codigo_producto VARCHAR(50),
    descripcion VARCHAR(255) NOT NULL,
    unidad_medida VARCHAR(10) DEFAULT 'NIU',
    
    -- Cantidades y precios
    cantidad DECIMAL(12,4) NOT NULL,
    precio_unitario DECIMAL(12,4) NOT NULL,
    descuento_unitario DECIMAL(12,4) DEFAULT 0.0000,
    precio_unitario_con_descuento DECIMAL(12,4) GENERATED ALWAYS AS (precio_unitario - descuento_unitario) STORED,
    
    -- Valores
    valor_venta DECIMAL(12,2) GENERATED ALWAYS AS (cantidad * precio_unitario_con_descuento) STORED,
    descuento_total DECIMAL(12,2) GENERATED ALWAYS AS (cantidad * descuento_unitario) STORED,
    
    -- Impuestos
    base_imponible DECIMAL(12,2) DEFAULT 0.00,
    igv_unitario DECIMAL(12,4) DEFAULT 0.0000,
    igv_total DECIMAL(12,2) DEFAULT 0.00,
    codigo_impuesto VARCHAR(10) DEFAULT '1000',
    
    -- Totales
    precio_total DECIMAL(12,2) GENERATED ALWAYS AS (valor_venta + igv_total) STORED,
    
    UNIQUE(comprobante_id, numero_item)
);

-- Índices para items
CREATE INDEX idx_items_comprobante ON items_comprobantes(comprobante_id);
CREATE INDEX idx_items_producto ON items_comprobantes(producto_id);

-- ==============================================
-- TABLA: MOVIMIENTOS_INVENTARIO
-- ==============================================

CREATE TABLE movimientos_inventario (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    
    -- Referencia
    tipo_movimiento tipo_movimiento_inventario_enum NOT NULL,
    numero_documento VARCHAR(50),
    referencia_tabla VARCHAR(50), -- comprobantes, transferencias, ajustes
    referencia_id INTEGER,
    
    -- Producto y almacén
    producto_id INTEGER REFERENCES productos(id),
    almacen_id INTEGER REFERENCES almacenes(id),
    
    -- Movimiento
    cantidad DECIMAL(12,4) NOT NULL,
    costo_unitario DECIMAL(12,4) DEFAULT 0.0000,
    costo_total DECIMAL(12,2) GENERATED ALWAYS AS (cantidad * costo_unitario) STORED,
    
    -- Stock resultante (para PEPS)
    stock_anterior DECIMAL(12,4) DEFAULT 0.0000,
    stock_actual DECIMAL(12,4) DEFAULT 0.0000,
    
    -- Metadatos
    observaciones TEXT,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER REFERENCES usuarios(id),
    
    -- Para control PEPS
    lote_numero VARCHAR(50),
    fecha_vencimiento DATE
);

-- Índices para movimientos
CREATE INDEX idx_movimientos_producto ON movimientos_inventario(producto_id);
CREATE INDEX idx_movimientos_almacen ON movimientos_inventario(almacen_id);
CREATE INDEX idx_movimientos_fecha ON movimientos_inventario(fecha_movimiento);
CREATE INDEX idx_movimientos_tipo ON movimientos_inventario(tipo_movimiento);
CREATE INDEX idx_movimientos_referencia ON movimientos_inventario(referencia_tabla, referencia_id);

-- ==============================================
-- TABLA: PLAN_CUENTAS (PCGE)
-- ==============================================

CREATE TABLE plan_cuentas (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    
    codigo VARCHAR(20) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    
    -- Jerarquía
    cuenta_padre_id INTEGER REFERENCES plan_cuentas(id),
    nivel INTEGER NOT NULL,
    
    -- Configuración
    tipo_cuenta VARCHAR(50), -- ACTIVO, PASIVO, PATRIMONIO, INGRESOS, GASTOS
    naturaleza VARCHAR(20) DEFAULT 'DEUDOR', -- DEUDOR, ACREEDOR
    acepta_movimientos BOOLEAN DEFAULT TRUE,
    
    -- Estado
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(empresa_id, codigo)
);

-- ==============================================
-- TABLA: ASIENTOS_CONTABLES
-- ==============================================

CREATE TABLE asientos_contables (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    
    numero_asiento INTEGER NOT NULL,
    fecha_asiento DATE NOT NULL DEFAULT CURRENT_DATE,
    periodo VARCHAR(7) GENERATED ALWAYS AS (TO_CHAR(fecha_asiento, 'YYYY-MM')) STORED,
    
    concepto TEXT NOT NULL,
    referencia_tabla VARCHAR(50), -- comprobantes, pagos, etc.
    referencia_id INTEGER,
    
    total_debe DECIMAL(12,2) DEFAULT 0.00,
    total_haber DECIMAL(12,2) DEFAULT 0.00,
    
    estado VARCHAR(20) DEFAULT 'BORRADOR', -- BORRADOR, CONFIRMADO, ANULADO
    automatico BOOLEAN DEFAULT FALSE,
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_creacion INTEGER REFERENCES usuarios(id),
    
    UNIQUE(empresa_id, numero_asiento)
);

-- ==============================================
-- TABLA: DETALLES_ASIENTOS
-- ==============================================

CREATE TABLE detalles_asientos (
    id SERIAL PRIMARY KEY,
    asiento_id INTEGER REFERENCES asientos_contables(id) ON DELETE CASCADE,
    cuenta_id INTEGER REFERENCES plan_cuentas(id),
    
    numero_detalle INTEGER NOT NULL,
    descripcion TEXT,
    
    debe DECIMAL(12,2) DEFAULT 0.00,
    haber DECIMAL(12,2) DEFAULT 0.00,
    
    UNIQUE(asiento_id, numero_detalle)
);

-- ==============================================
-- TABLA: CONFIGURACIONES
-- ==============================================

CREATE TABLE configuraciones (
    id SERIAL PRIMARY KEY,
    empresa_id INTEGER REFERENCES empresas(id) ON DELETE CASCADE,
    
    clave VARCHAR(100) NOT NULL,
    valor TEXT,
    descripcion TEXT,
    tipo VARCHAR(20) DEFAULT 'TEXT', -- TEXT, NUMBER, BOOLEAN, JSON
    
    categoria VARCHAR(50) DEFAULT 'GENERAL',
    editable BOOLEAN DEFAULT TRUE,
    
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(empresa_id, clave)
);

-- ==============================================
-- FUNCIONES Y TRIGGERS
-- ==============================================

-- Función para actualizar fecha_actualizacion automáticamente
CREATE OR REPLACE FUNCTION actualizar_fecha_modificacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a tablas principales
CREATE TRIGGER trigger_empresas_fecha_actualizacion
    BEFORE UPDATE ON empresas
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_usuarios_fecha_actualizacion
    BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_clientes_fecha_actualizacion
    BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_productos_fecha_actualizacion
    BEFORE UPDATE ON productos
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_stocks_fecha_actualizacion
    BEFORE UPDATE ON stocks
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();

CREATE TRIGGER trigger_comprobantes_fecha_actualizacion
    BEFORE UPDATE ON comprobantes
    FOR EACH ROW EXECUTE FUNCTION actualizar_fecha_modificacion();

-- Función para auto-incrementar series de comprobantes
CREATE OR REPLACE FUNCTION obtener_siguiente_numero_serie(
    p_empresa_id INTEGER,
    p_tipo_comprobante tipo_comprobante_enum,
    p_serie VARCHAR(4)
) RETURNS INTEGER AS $$
DECLARE
    v_numero_actual INTEGER;
BEGIN
    UPDATE series_comprobantes 
    SET numero_actual = numero_actual + 1
    WHERE empresa_id = p_empresa_id 
      AND tipo_comprobante = p_tipo_comprobante 
      AND serie = p_serie
    RETURNING numero_actual INTO v_numero_actual;
    
    RETURN v_numero_actual;
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- COMENTARIOS EN TABLAS
-- ==============================================

COMMENT ON TABLE empresas IS 'Información de las empresas que usan el sistema';
COMMENT ON TABLE usuarios IS 'Usuarios del sistema con roles y permisos';
COMMENT ON TABLE clientes IS 'Clientes y proveedores de las empresas';
COMMENT ON TABLE productos IS 'Catálogo de productos y servicios';
COMMENT ON TABLE stocks IS 'Control de inventarios por almacén';
COMMENT ON TABLE comprobantes IS 'Comprobantes electrónicos SUNAT';
COMMENT ON TABLE items_comprobantes IS 'Detalles de items en comprobantes';
COMMENT ON TABLE movimientos_inventario IS 'Historial de movimientos de stock (PEPS)';
COMMENT ON TABLE plan_cuentas IS 'Plan Contable General Empresarial (PCGE)';
COMMENT ON TABLE asientos_contables IS 'Asientos contables del sistema';

-- ==============================================
-- DATOS INICIALES BÁSICOS
-- ==============================================

-- Insertar configuraciones por defecto
INSERT INTO configuraciones (empresa_id, clave, valor, descripcion, categoria) VALUES
(1, 'IGV_RATE', '0.18', 'Tasa de IGV en Perú', 'IMPUESTOS'),
(1, 'MONEDA_PRINCIPAL', 'PEN', 'Moneda principal del sistema', 'GENERAL'),
(1, 'METODO_COSTEO', 'PEPS', 'Método de costeo de inventarios', 'INVENTARIO'),
(1, 'NUMERACION_AUTOMATICA', 'true', 'Numeración automática de comprobantes', 'FACTURACION'),
(1, 'BACKUP_AUTOMATICO', 'true', 'Backup automático de base de datos', 'SISTEMA');

COMMIT;

-- ==============================================
-- MENSAJE FINAL
-- ==============================================

SELECT 'Base de datos FELICITA inicializada correctamente ✅' AS resultado;