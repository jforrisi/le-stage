from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.apps import apps
import pandas as pd
from io import BytesIO
from erp_demo.config import EMPRESA_NOMBRE


def obtener_tablas_disponibles():
    """Obtiene todas las tablas de la base de datos"""
    with connection.cursor() as cursor:
        if connection.vendor == 'sqlite':
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
                AND name NOT LIKE 'django_%'
                ORDER BY name
            """)
        else:
            # Para PostgreSQL, MySQL, etc.
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
        
        tablas = [row[0] for row in cursor.fetchall()]
    
    # También obtener modelos registrados para nombres más amigables
    modelos_info = {}
    for model in apps.get_models():
        if hasattr(model._meta, 'db_table'):
            tabla = model._meta.db_table
            modelos_info[tabla] = {
                'nombre': model._meta.verbose_name_plural or model.__name__,
                'modelo': model
            }
    
    return tablas, modelos_info


def lista_tablas(request):
    """Vista principal para seleccionar y ver tablas"""
    tablas, modelos_info = obtener_tablas_disponibles()
    
    # Tabla seleccionada
    tabla_seleccionada = request.GET.get('tabla', '')
    datos = None
    columnas = None
    nombre_amigable = None
    
    if tabla_seleccionada:
        try:
            # Validar que la tabla existe
            if tabla_seleccionada not in tablas:
                datos = []
                columnas = []
            else:
                # Validar nombre de tabla
                if not all(c.isalnum() or c == '_' for c in tabla_seleccionada):
                    datos = []
                    columnas = []
                else:
                    with connection.cursor() as cursor:
                        # Obtener columnas
                        if connection.vendor == 'sqlite':
                            cursor.execute(f'PRAGMA table_info("{tabla_seleccionada}")')
                            columnas_info = cursor.fetchall()
                            columnas = [col[1] for col in columnas_info]  # nombre de columna
                        else:
                            cursor.execute("""
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_name = %s
                                ORDER BY ordinal_position
                            """, [tabla_seleccionada])
                            columnas = [row[0] for row in cursor.fetchall()]
                        
                        # Obtener datos
                        cursor.execute(f'SELECT * FROM "{tabla_seleccionada}"')
                        datos = cursor.fetchall()
            
            # Nombre amigable si existe
            if tabla_seleccionada in modelos_info:
                nombre_amigable = modelos_info[tabla_seleccionada]['nombre']
            else:
                nombre_amigable = tabla_seleccionada.replace('_', ' ').title()
        except Exception as e:
            # Si hay error, mostrar mensaje
            datos = []
            columnas = []
    
    # Función para detectar módulo basado en prefijo
    def detectar_modulo(tabla):
        """Detecta el módulo basado en el prefijo de la tabla"""
        if tabla.startswith('config_'):
            return 'Configuración'
        elif tabla.startswith('compras_'):
            return 'Compras'
        elif tabla.startswith('ventas_'):
            return 'Ventas'
        elif tabla.startswith('finanzas_'):
            return 'Finanzas'
        else:
            return 'Otros'
    
    # Preparar lista de tablas con nombres amigables y módulos
    tablas_info = []
    for tabla in tablas:
        modulo = detectar_modulo(tabla)
        if tabla in modelos_info:
            tablas_info.append({
                'nombre': tabla,
                'nombre_amigable': modelos_info[tabla]['nombre'],
                'modulo': modulo
            })
        else:
            tablas_info.append({
                'nombre': tabla,
                'nombre_amigable': tabla.replace('_', ' ').title(),
                'modulo': modulo
            })
    
    # Ordenar por módulo y luego por nombre de tabla
    orden_modulos = ['Configuración', 'Compras', 'Ventas', 'Finanzas', 'Otros']
    tablas_info.sort(key=lambda x: (
        orden_modulos.index(x['modulo']) if x['modulo'] in orden_modulos else len(orden_modulos),
        x['nombre']
    ))
    
    context = {
        'tablas': tablas_info,
        'tabla_seleccionada': tabla_seleccionada,
        'datos': datos,
        'columnas': columnas,
        'nombre_amigable': nombre_amigable,
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    
    return render(request, 'tablas/lista_tablas.html', context)


def exportar_tabla_excel(request, tabla):
    """Exporta una tabla a Excel"""
    try:
        # Validar que la tabla existe en la lista de tablas disponibles
        tablas_disponibles, _ = obtener_tablas_disponibles()
        if tabla not in tablas_disponibles:
            return HttpResponse("Tabla no válida", status=400)
        
        # Validar nombre de tabla (solo letras, números y guiones bajos)
        if not all(c.isalnum() or c == '_' for c in tabla):
            return HttpResponse("Nombre de tabla inválido", status=400)
        
        with connection.cursor() as cursor:
            # Obtener datos usando parámetros seguros
            if connection.vendor == 'sqlite':
                # SQLite no soporta parámetros en nombres de tablas, pero ya validamos
                cursor.execute(f'SELECT * FROM "{tabla}"')
                datos = cursor.fetchall()
                
                # Obtener nombres de columnas
                cursor.execute(f'PRAGMA table_info("{tabla}")')
                columnas_info = cursor.fetchall()
                columnas = [col[1] for col in columnas_info]
            else:
                # Para otros SGBD usar parámetros
                cursor.execute(f'SELECT * FROM "{tabla}"')
                datos = cursor.fetchall()
                
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = %s
                    ORDER BY ordinal_position
                """, [tabla])
                columnas = [row[0] for row in cursor.fetchall()]
        
        # Crear DataFrame
        df = pd.DataFrame(datos, columns=columnas)
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos')
        
        output.seek(0)
        
        # Preparar respuesta
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{tabla}.xlsx"'
        
        return response
    
    except Exception as e:
        return HttpResponse(f"Error al exportar: {str(e)}", status=500)

