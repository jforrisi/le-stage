from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from decimal import Decimal
from erp_demo.decorators import acceso_por_app
from mineria_le_stage.models import PiezasCorteCantera
from erp_demo.config import EMPRESA_NOMBRE


@acceso_por_app(['gerencia_le_stage'])
def control_produccion_piezas_corte(request):
    """Vista de control de producción - Piezas de Corte con columnas calculadas"""
    piezas = PiezasCorteCantera.objects.all().select_related(
        'equipo_minero', 'equipo_corte'
    ).order_by('-fecha_creacion')
    
    # Búsqueda
    busqueda = request.GET.get('busqueda', '')
    if busqueda:
        piezas = piezas.filter(
            Q(nombre_piedra__icontains=busqueda) |
            Q(numero__icontains=busqueda) |
            Q(equipo_minero__nombre__icontains=busqueda) |
            Q(equipo_corte__nombre__icontains=busqueda)
        )
    
    # Paginación
    paginator = Paginator(piezas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calcular columnas para cada pieza
    piezas_con_calculos = []
    for pieza in page_obj:
        # Costo Tallado = kilos_despues_tallado * precio_por_kilo_tallado
        costo_tallado = pieza.kilos_despues_tallado * pieza.precio_por_kilo_tallado
        
        # Extra Carlos (convertir de CharField a Decimal)
        extra_carlos_decimal = Decimal('0')
        if pieza.extra_carlos:
            try:
                extra_carlos_decimal = Decimal(str(pieza.extra_carlos).replace(',', '.'))
            except (ValueError, TypeError):
                extra_carlos_decimal = Decimal('0')
        
        # Costo Pulido = pulido_por_kilo * kilos_despues_tallado (sin extra_carlos)
        costo_pulido = pieza.pulido_por_kilo * pieza.kilos_despues_tallado
        
        # Costos Industrialización = Costo Tallado + Costo Pulido + Extra Carlos
        costos_industrializacion = costo_tallado + costo_pulido + extra_carlos_decimal
        
        piezas_con_calculos.append({
            'pieza': pieza,
            'costo_tallado': costo_tallado,
            'costo_pulido': costo_pulido,
            'extra_carlos_decimal': extra_carlos_decimal,
            'costos_industrializacion': costos_industrializacion,
        })
    
    context = {
        'piezas_con_calculos': piezas_con_calculos,
        'piezas': page_obj,
        'busqueda': busqueda,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': 'Control de Producción - Piezas de Corte',
    }
    return render(request, 'gerencia_le_stage/control_produccion/piezas_corte.html', context)


@acceso_por_app(['gerencia_le_stage'])
def detalle_pieza_corte(request, id):
    """Vista de detalle completo de una pieza de corte (minería + industria)"""
    pieza = get_object_or_404(
        PiezasCorteCantera.objects.select_related('equipo_minero', 'equipo_corte', 'tipo_proceso'),
        id=id
    )
    
    # Calcular costos
    costo_tallado = pieza.kilos_despues_tallado * pieza.precio_por_kilo_tallado
    
    extra_carlos_decimal = Decimal('0')
    if pieza.extra_carlos:
        try:
            extra_carlos_decimal = Decimal(str(pieza.extra_carlos).replace(',', '.'))
        except (ValueError, TypeError):
            extra_carlos_decimal = Decimal('0')
    
    # Costo Pulido sin extra_carlos
    costo_pulido = pieza.pulido_por_kilo * pieza.kilos_despues_tallado
    
    # Costo Total = Costo Tallado + Costo Pulido + Extra Carlos
    costo_total = costo_tallado + costo_pulido + extra_carlos_decimal
    
    context = {
        'pieza': pieza,
        'costo_tallado': costo_tallado,
        'costo_pulido': costo_pulido,
        'extra_carlos_decimal': extra_carlos_decimal,
        'costo_total': costo_total,
        'empresa_nombre': EMPRESA_NOMBRE,
        'titulo': f'Detalle Pieza de Corte - {pieza.nombre_piedra or pieza.id}',
    }
    return render(request, 'gerencia_le_stage/control_produccion/detalle_pieza_corte.html', context)
