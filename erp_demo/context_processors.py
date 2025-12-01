from erp_demo.config import EMPRESA_NOMBRE
from pathlib import Path
import os
import pandas as pd


def empresa_context(request):
    """Context processor para agregar variables globales a todos los templates"""
    return {
        'empresa_nombre': EMPRESA_NOMBRE,
    }


def menu_context(request):
    """Context processor para generar el menú lateral desde el Excel"""
    menu_data = []
    
    # Determinar qué secciones puede ver el usuario
    user = getattr(request, 'user', None)
    usuario_username = user.username if user and user.is_authenticated else None
    
    # Definir permisos por usuario
    secciones_permitidas = []
    if usuario_username == 'gerencia' or (user and user.is_superuser):
        # Gerencia ve todo
        secciones_permitidas = None  # None significa todas las secciones
    elif usuario_username == 'mineria':
        # Mineria solo ve Minería Le Stage
        secciones_permitidas = ['Minería Le Stage']
    elif usuario_username == 'industria':
        # Industria solo ve Industria Le Stage
        secciones_permitidas = ['Industria Le Stage']
    else:
        # Usuario no autenticado o sin permisos específicos - no ve nada
        secciones_permitidas = []
    
    try:
        # Ruta al archivo Excel
        excel_path = Path(__file__).parent.parent / 'config.xlsx'
        
        if excel_path.exists():
            # Leer el Excel
            df = pd.read_excel(excel_path, sheet_name='menu')
            
            # Mapear nivel 2 a URLs
            url_map = {
                'Clientes': 'lista_clientes',
                'Proveedores': 'lista_proveedores',
                'Artículos': 'lista_articulos',
                'Disponibilidades': 'lista_disponibilidades',
                'Transacciones': 'lista_transacciones',
                'IVA': 'lista_ivas',
                'Forma de pago': 'lista_formas_pago',
                'Formas de pago': 'lista_formas_pago',
                'Formas de Pago': 'lista_formas_pago',
                'Ingresos compras': 'compras_ingreso:lista_compras',
                'Devoluciones compras': 'compras_devoluciones:lista_compras_devoluciones',
                'Devoluciones Compras': 'compras_devoluciones:lista_compras_devoluciones',
                'Ingresos ventas': 'ventas_ingreso:lista_ventas',
                'Ventas': 'ventas_ingreso:lista_ventas',
                'Devoluciones ventas': 'ventas_devoluciones:lista_ventas_devoluciones',
                'Devoluciones Ventas': 'ventas_devoluciones:lista_ventas_devoluciones',
                'Minería Le Stage': 'mineria_le_stage:lista_equipos',
                'Mineria Le Stage': 'mineria_le_stage:lista_equipos',
                'Tablas': 'lista_tablas',
                'Depósitos': 'lista_depositos',
            }
            
            # Agrupar por nivel 1 y evitar duplicados
            menu_structure = {}
            seen_items = set()  # Para evitar duplicados
            
            for _, row in df.iterrows():
                nivel1 = str(row['nivel 1']).strip() if pd.notna(row['nivel 1']) else ''
                nivel2 = str(row['nivel 2']).strip() if pd.notna(row['nivel 2']) else ''
                
                if not nivel1 or not nivel2:
                    continue
                
                # Ignorar "Minería Le Stage" si aparece como nivel 2 (se agregará como nivel 1 después)
                # Comparación flexible para capturar variaciones
                nivel2_lower = nivel2.lower().strip()
                if 'mineria' in nivel2_lower and 'stage' in nivel2_lower:
                    continue
                
                if nivel1 not in menu_structure:
                    menu_structure[nivel1] = []
                
                # Crear clave única para evitar duplicados
                item_key = (nivel1, nivel2)
                if item_key not in seen_items:
                    seen_items.add(item_key)
                    
                    item = {
                        'nombre': nivel2,
                        'url': url_map.get(nivel2, '#'),
                        'hijos': []
                    }
                    
                    # Agregar nivel 3 para Clientes -> Lista + Nuevo + Canales Comerciales
                    if nivel2 == 'Clientes':
                        item['hijos'].append({
                            'nombre': 'Lista de Clientes',
                            'url': 'lista_clientes'
                        })
                        item['hijos'].append({
                            'nombre': 'Nuevo Cliente',
                            'url': 'crear_cliente'
                        })
                        item['hijos'].append({
                            'nombre': 'Canales Comerciales',
                            'url': 'lista_canales'
                        })
                    
                    # Agregar nivel 3 para Artículos -> Tipos, Familias, SubFamilias
                    if nivel2 == 'Artículos':
                        item['hijos'] = [
                            {'nombre': 'Lista de Artículos', 'url': 'lista_articulos'},
                            {'nombre': 'Tipos de Artículo', 'url': 'lista_tipos_articulo'},
                            {'nombre': 'Familias', 'url': 'lista_familias'},
                            {'nombre': 'Sub Familias', 'url': 'lista_subfamilias'},
                        ]
                    
                    # Agregar nivel 3 para Ingresos compras -> Lista + Nueva
                    if nivel2 == 'Ingresos compras':
                        item['hijos'] = [
                            {'nombre': 'Lista de Compras', 'url': 'compras_ingreso:lista_compras'},
                            {'nombre': 'Nueva Compra', 'url': 'compras_ingreso:crear_compra'},
                        ]
                    
                    # Agregar nivel 3 para Devoluciones compras -> Lista + Nueva
                    if nivel2 == 'Devoluciones compras' or nivel2 == 'Devoluciones Compras':
                        item['hijos'] = [
                            {'nombre': 'Lista de Devoluciones', 'url': 'compras_devoluciones:lista_compras_devoluciones'},
                            {'nombre': 'Nueva Devolución', 'url': 'compras_devoluciones:crear_compra_devolucion'},
                        ]
                    
                    # Agregar nivel 3 para Ingresos ventas -> Lista + Nueva
                    if nivel2 == 'Ingresos ventas' or nivel2 == 'Ventas':
                        item['hijos'] = [
                            {'nombre': 'Lista de Ventas', 'url': 'ventas_ingreso:lista_ventas'},
                            {'nombre': 'Nueva Venta', 'url': 'ventas_ingreso:crear_venta'},
                        ]
                    
                    # Agregar nivel 3 para Devoluciones ventas -> Lista + Nueva
                    if nivel2 == 'Devoluciones ventas' or nivel2 == 'Devoluciones Ventas':
                        item['hijos'] = [
                            {'nombre': 'Lista de Devoluciones', 'url': 'ventas_devoluciones:lista_ventas_devoluciones'},
                            {'nombre': 'Nueva Devolución', 'url': 'ventas_devoluciones:crear_venta_devolucion'},
                        ]
                    
                    menu_structure[nivel1].append(item)
            
            # Agregar "Tablas" a la sección Configuración si existe
            if 'Configuración' in menu_structure:
                # Verificar si ya existe "Tablas" en Configuración
                existe_tablas = any(item['nombre'] == 'Tablas' for item in menu_structure['Configuración'])
                if not existe_tablas:
                    menu_structure['Configuración'].append({
                        'nombre': 'Tablas',
                        'url': 'lista_tablas',
                        'hijos': []
                    })
            
            # Eliminar "Minería Le Stage" de cualquier nivel 1 donde aparezca como nivel 2
            # Usar comparación flexible para capturar variaciones
            for nivel1_key in list(menu_structure.keys()):
                menu_structure[nivel1_key] = [
                    item for item in menu_structure[nivel1_key]
                    if not ('mineria' in item['nombre'].lower() and 'stage' in item['nombre'].lower())
                ]
            
            # Agregar "Minería Le Stage" como nivel 1 (al mismo nivel que Configuración y Compras)
            menu_structure['Minería Le Stage'] = [
                {'nombre': 'Equipos', 'url': 'mineria_le_stage:lista_equipos'},
                {'nombre': 'Equipos Corte', 'url': 'mineria_le_stage:lista_equipos_corte'},
                {'nombre': 'Piedras/Canteras', 'url': 'mineria_le_stage:lista_piedras_canteras'},
                {'nombre': 'Producción Equipos', 'url': 'mineria_le_stage:lista_produccion_equipos'},
                {'nombre': 'Costos Equipos', 'url': 'mineria_le_stage:lista_costos'},
                {'nombre': 'Piezas de Corte en Cantera', 'url': 'mineria_le_stage:lista_piezas_corte_cantera'},
            ]
            
            # Agregar "Industria Le Stage" como nivel 1
            menu_structure['Industria Le Stage'] = [
                {'nombre': 'Tipos de Pulido Piezas', 'url': 'industria_le_stage:lista_tipos_pulido_piezas'},
                {'nombre': 'Piezas de Corte en Industria', 'url': 'industria_le_stage:lista_piezas_corte_cantera_industria'},
            ]
            
            # Agregar "Gerencia" como nivel 1
            menu_structure['Gerencia'] = [
                {
                    'nombre': 'Control de Producción',
                    'url': '#',
                    'hijos': [
                        {'nombre': 'Piezas de Corte', 'url': 'gerencia_le_stage:control_produccion_piezas_corte'},
                    ]
                }
            ]
            
            # Filtrar menú según permisos del usuario
            # Si secciones_permitidas es None, mostrar todo (gerencia)
            # Si es una lista, filtrar solo esas secciones
            if secciones_permitidas is not None and len(secciones_permitidas) > 0:
                menu_structure = {
                    nivel1: hijos 
                    for nivel1, hijos in menu_structure.items() 
                    if nivel1 in secciones_permitidas
                }
            
            # Convertir a lista para el template
            menu_data = [
                {
                    'nombre': nivel1,
                    'hijos': hijos
                }
                for nivel1, hijos in menu_structure.items()
            ]
    except Exception as e:
        # Si hay error, usar menú por defecto (filtrar según usuario)
        menu_default = [
            {
                'nombre': 'Configuración',
                'hijos': [
                    {'nombre': 'Clientes', 'url': 'lista_clientes', 'hijos': [
                        {'nombre': 'Canales Comerciales', 'url': 'lista_canales'}
                    ]},
                    {'nombre': 'Proveedores', 'url': 'lista_proveedores', 'hijos': []},
                    {'nombre': 'Artículos', 'url': 'lista_articulos', 'hijos': [
                        {'nombre': 'Lista de Artículos', 'url': 'lista_articulos'},
                        {'nombre': 'Tipos de Artículo', 'url': 'lista_tipos_articulo'},
                        {'nombre': 'Familias', 'url': 'lista_familias'},
                        {'nombre': 'Sub Familias', 'url': 'lista_subfamilias'},
                    ]},
                    {'nombre': 'Tablas', 'url': 'lista_tablas', 'hijos': []},
                ]
            },
            {
                'nombre': 'Operaciones',
                'hijos': [
                    {'nombre': 'Compras', 'url': 'compras_ingreso:lista_compras', 'hijos': [
                        {'nombre': 'Lista de Compras', 'url': 'compras_ingreso:lista_compras'},
                        {'nombre': 'Nueva Compra', 'url': 'compras_ingreso:crear_compra'},
                    ]},
                    {'nombre': 'Devoluciones Compras', 'url': 'compras_devoluciones:lista_compras_devoluciones', 'hijos': [
                        {'nombre': 'Lista de Devoluciones', 'url': 'compras_devoluciones:lista_compras_devoluciones'},
                        {'nombre': 'Nueva Devolución', 'url': 'compras_devoluciones:crear_compra_devolucion'},
                    ]},
                    {'nombre': 'Ventas', 'url': 'ventas_ingreso:lista_ventas', 'hijos': [
                        {'nombre': 'Lista de Ventas', 'url': 'ventas_ingreso:lista_ventas'},
                        {'nombre': 'Nueva Venta', 'url': 'ventas_ingreso:crear_venta'},
                    ]},
                    {'nombre': 'Devoluciones Ventas', 'url': 'ventas_devoluciones:lista_ventas_devoluciones', 'hijos': [
                        {'nombre': 'Lista de Devoluciones', 'url': 'ventas_devoluciones:lista_ventas_devoluciones'},
                        {'nombre': 'Nueva Devolución', 'url': 'ventas_devoluciones:crear_venta_devolucion'},
                    ]},
                ]
            },
            {
                'nombre': 'Minería Le Stage',
                'hijos': [
                    {'nombre': 'Equipos', 'url': 'mineria_le_stage:lista_equipos'},
                    {'nombre': 'Equipos Corte', 'url': 'mineria_le_stage:lista_equipos_corte'},
                    {'nombre': 'Piedras/Canteras', 'url': 'mineria_le_stage:lista_piedras_canteras'},
                    {'nombre': 'Producción Equipos', 'url': 'mineria_le_stage:lista_produccion_equipos'},
                    {'nombre': 'Costos Equipos', 'url': 'mineria_le_stage:lista_costos'},
                    {'nombre': 'Piezas de Corte en Cantera', 'url': 'mineria_le_stage:lista_piezas_corte_cantera'},
                ]
            },
            {
                'nombre': 'Industria Le Stage',
                'hijos': [
                    {'nombre': 'Tipos de Pulido Piezas', 'url': 'industria_le_stage:lista_tipos_pulido_piezas'},
                    {'nombre': 'Piezas de Corte en Industria', 'url': 'industria_le_stage:lista_piezas_corte_cantera_industria'},
                ]
            },
            {
                'nombre': 'Gerencia',
                'hijos': [
                    {
                        'nombre': 'Control de Producción',
                        'url': '#',
                        'hijos': [
                            {'nombre': 'Piezas de Corte', 'url': 'gerencia_le_stage:control_produccion_piezas_corte'},
                        ]
                    }
                ]
            }
        ]
        
        # Filtrar menú por defecto según permisos del usuario
        if secciones_permitidas is not None:
            if len(secciones_permitidas) > 0:
                menu_data = [
                    seccion for seccion in menu_default 
                    if seccion['nombre'] in secciones_permitidas
                ]
            else:
                menu_data = []
        else:
            # Gerencia ve todo
            menu_data = menu_default
    
    return {
        'menu_lateral': menu_data,
    }

