"""
Decoradores personalizados para control de acceso
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def acceso_por_app(allowed_apps):
    """
    Decorador que verifica si el usuario tiene acceso a una app específica
    
    Args:
        allowed_apps: Lista de nombres de apps permitidas (ej: ['mineria_le_stage', 'gerencia_le_stage'])
    
    Uso:
        @acceso_por_app(['mineria_le_stage'])
        def lista_equipos(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            
            # Gerencia tiene acceso a TODO
            if user.is_superuser or user.username == 'gerencia':
                return view_func(request, *args, **kwargs)
            
            # Verificar si el usuario tiene acceso a alguna de las apps permitidas
            tiene_acceso = False
            
            for app in allowed_apps:
                if app == 'mineria_le_stage':
                    # Solo usuario mineria puede acceder
                    if user.username == 'mineria' or user.groups.filter(name='Minería').exists():
                        tiene_acceso = True
                        break
                elif app == 'industria_le_stage':
                    # Solo usuario industria puede acceder
                    if user.username == 'industria' or user.groups.filter(name='Industria').exists():
                        tiene_acceso = True
                        break
                elif app == 'gerencia_le_stage':
                    # Solo gerencia puede acceder
                    if user.username == 'gerencia' or user.is_superuser:
                        tiene_acceso = True
                        break
                elif app == 'configuracion':
                    # Solo gerencia puede acceder a configuración
                    if user.username == 'gerencia' or user.is_superuser:
                        tiene_acceso = True
                        break
            
            if tiene_acceso:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'No tienes permiso para acceder a esta sección.')
                # Redirigir según el tipo de usuario
                if user.username == 'industria' or user.groups.filter(name='Industria').exists():
                    return redirect('industria_le_stage:lista_tipos_pulido_piezas')
                elif user.username == 'mineria' or user.groups.filter(name='Minería').exists():
                    return redirect('mineria_le_stage:lista_equipos')
                else:
                    return redirect('home')
        
        return wrapper
    return decorator

