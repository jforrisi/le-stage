"""
Vistas de autenticación personalizadas
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from erp_demo.config import EMPRESA_NOMBRE


def login_view(request):
    """Vista de login personalizada"""
    if request.user.is_authenticated:
        # Si ya está logueado, redirigir según su tipo de usuario
        return redirect_home(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}!')
            return redirect_home(user)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    context = {
        'empresa_nombre': EMPRESA_NOMBRE,
    }
    return render(request, 'auth/login.html', context)


@login_required
def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')


def redirect_home(user):
    """Redirige al usuario a su página de inicio según su tipo"""
    if user.is_superuser or user.username == 'gerencia':
        # Gerencia va a la página principal
        return redirect('home')
    elif user.username == 'industria' or user.groups.filter(name='Industria').exists():
        # Industria va a su módulo
        return redirect('industria_le_stage:lista_tipos_pulido_piezas')
    elif user.username == 'mineria' or user.groups.filter(name='Minería').exists():
        # Minería va a su módulo
        return redirect('mineria_le_stage:lista_equipos')
    else:
        # Por defecto, página principal
        return redirect('home')

