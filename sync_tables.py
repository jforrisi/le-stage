import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from django.db import connection

sql_script = """
-- ============================================
-- ELIMINAR TABLAS EXISTENTES
-- ============================================
DROP TABLE IF EXISTS compras_devoluciones_lineas;
DROP TABLE IF EXISTS compras_devoluciones_cabezal;

-- ============================================
-- CREAR compras_devoluciones_cabezal
-- ============================================
CREATE TABLE compras_devoluciones_cabezal (
    transaccion VARCHAR(10) PRIMARY KEY,
    id_proveedor INTEGER NOT NULL,
    tipo_documento_id INTEGER NOT NULL,
    serie_documento VARCHAR(5),
    numero_documento VARCHAR(20) NOT NULL,
    forma_pago INTEGER NOT NULL,
    fecha_documento DATE NOT NULL,
    fecha_movimiento DATETIME NOT NULL,
    moneda_id INTEGER NOT NULL,
    precio_iva_inc VARCHAR(2) NOT NULL DEFAULT 'NO',
    tipo_compra VARCHAR(20) NOT NULL DEFAULT 'CONVENCIONAL',
    disponibilidad_id INTEGER,
    observaciones TEXT,
    monotributista VARCHAR(2) NOT NULL DEFAULT 'NO',
    fchhor DATETIME NOT NULL,
    usuario INTEGER,
    sub_total DECIMAL(15,2) NOT NULL DEFAULT 0,
    iva DECIMAL(15,2) NOT NULL DEFAULT 0,
    importe_total DECIMAL(15,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores_proveedor(id),
    FOREIGN KEY (tipo_documento_id) REFERENCES documentos_documento(id),
    FOREIGN KEY (forma_pago) REFERENCES config_forma_pago(id),
    FOREIGN KEY (moneda_id) REFERENCES articulos_moneda(id),
    FOREIGN KEY (disponibilidad_id) REFERENCES disponibilidades_disponibilidad(id)
);

-- ============================================
-- CREAR compras_devoluciones_lineas
-- ============================================
CREATE TABLE compras_devoluciones_lineas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaccion VARCHAR(10) NOT NULL,
    linea INTEGER NOT NULL,
    id_articulo INTEGER NOT NULL,
    id_compra_linea_id INTEGER,
    serie_doc_afectado VARCHAR(20),
    numero_doc_afectado VARCHAR(50) NOT NULL DEFAULT '',
    cantidad DECIMAL(15,2) NOT NULL,
    precio DECIMAL(15,2) NOT NULL,
    sub_total DECIMAL(15,2) NOT NULL,
    iva DECIMAL(15,2) NOT NULL,
    total DECIMAL(15,2) NOT NULL,
    FOREIGN KEY (transaccion) REFERENCES compras_devoluciones_cabezal(transaccion) ON DELETE CASCADE,
    FOREIGN KEY (id_articulo) REFERENCES articulos_articulo(id),
    FOREIGN KEY (id_compra_linea_id) REFERENCES compras_lineas(id) ON DELETE SET NULL,
    UNIQUE(transaccion, linea)
);

-- ============================================
-- CREAR ÍNDICES
-- ============================================
CREATE INDEX idx_devoluciones_cabezal_proveedor ON compras_devoluciones_cabezal(id_proveedor);
CREATE INDEX idx_devoluciones_cabezal_forma_pago ON compras_devoluciones_cabezal(forma_pago);
CREATE INDEX idx_devoluciones_cabezal_fecha ON compras_devoluciones_cabezal(fecha_documento);
CREATE INDEX idx_devoluciones_lineas_transaccion ON compras_devoluciones_lineas(transaccion);
CREATE INDEX idx_devoluciones_lineas_articulo ON compras_devoluciones_lineas(id_articulo);
CREATE INDEX idx_devoluciones_lineas_id_compra_linea ON compras_devoluciones_lineas(id_compra_linea_id);
"""

print("=" * 50)
print("Iniciando recreación de tablas...")
print("=" * 50)

try:
    with connection.cursor() as cursor:
        # Limpiar comentarios y ejecutar con executescript (mejor para SQLite)
        sql_clean = '\n'.join([line for line in sql_script.split('\n') if not line.strip().startswith('--')])
        
        print("Ejecutando comandos SQL...")
        cursor.executescript(sql_clean)
        
        print("\n✅ Tablas recreadas exitosamente!")
        print("✅ compras_devoluciones_cabezal creada")
        print("✅ compras_devoluciones_lineas creada")
        print("=" * 50)
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("=" * 50)