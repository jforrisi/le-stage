"""
Script para crear usuarios del sistema con sus respectivos permisos
Ejecutar con: python manage.py shell < crear_usuarios.py
O mejor: python crear_usuarios.py
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp_demo.settings')
django.setup()

from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

def crear_usuarios():
    """Crea los usuarios del sistema con sus permisos"""
    
    usuarios_config = [
        {
            'username': 'gerencia',
            'password': 'gerencia.2025',
            'email': 'gerencia@empresa.com',
            'is_staff': True,
            'is_superuser': True,  # Acceso total
        },
        {
            'username': 'industria',
            'password': 'industria.2025',
            'email': 'industria@empresa.com',
            'is_staff': True,
            'is_superuser': False,
        },
        {
            'username': 'mineria',
            'password': 'mineria.2025',
            'email': 'mineria@empresa.com',
            'is_staff': True,
            'is_superuser': False,
        },
    ]
    
    with transaction.atomic():
        # Crear o actualizar usuarios
        for user_config in usuarios_config:
            username = user_config['username']
            password = user_config.pop('password')
            # Remover username de user_config para evitar duplicado
            user_config.pop('username', None)
            
            # Obtener o crear usuario
            try:
                user = User.objects.get(username=username)
                created = False
                print(f"Usuario '{username}' ya existe, actualizando...")
            except User.DoesNotExist:
                user = User.objects.create_user(username=username, **user_config)
                created = True
                print(f"Usuario '{username}' creado")
            
            # SIEMPRE actualizar todos los campos y la contraseña
            for key, value in user_config.items():
                setattr(user, key, value)
            
            # SIEMPRE establecer la contraseña (incluso si el usuario ya existía)
            user.set_password(password)
            user.save()
            print(f"✅ Contraseña establecida para '{username}'")
        
        # Crear grupos para permisos específicos
        grupo_industria, _ = Group.objects.get_or_create(name='Industria')
        grupo_mineria, _ = Group.objects.get_or_create(name='Minería')
        
        # Obtener permisos de las apps
        # Para industria_le_stage
        try:
            industria_content_types = ContentType.objects.filter(app_label='industria_le_stage')
            industria_permissions = Permission.objects.filter(content_type__in=industria_content_types)
            grupo_industria.permissions.set(industria_permissions)
            print(f"Permisos de industria asignados al grupo 'Industria' ({industria_permissions.count()} permisos)")
        except Exception as e:
            print(f"No se pudieron asignar permisos para industria_le_stage: {e}")
        
        # Para mineria_le_stage
        try:
            mineria_content_types = ContentType.objects.filter(app_label='mineria_le_stage')
            mineria_permissions = Permission.objects.filter(content_type__in=mineria_content_types)
            grupo_mineria.permissions.set(mineria_permissions)
            print(f"Permisos de minería asignados al grupo 'Minería' ({mineria_permissions.count()} permisos)")
        except Exception as e:
            print(f"No se pudieron asignar permisos para mineria_le_stage: {e}")
        
        # Asignar usuarios a grupos
        user_industria = User.objects.get(username='industria')
        user_industria.groups.add(grupo_industria)
        print(f"Usuario 'industria' asignado al grupo 'Industria'")
        
        user_mineria = User.objects.get(username='mineria')
        user_mineria.groups.add(grupo_mineria)
        print(f"Usuario 'mineria' asignado al grupo 'Minería'")
        
        print("\n✅ Usuarios creados exitosamente!")
        print("\nUsuarios:")
        print("  - gerencia (superusuario - acceso total) → contraseña: gerencia.2025")
        print("  - industria (acceso a industria) → contraseña: industria.2025")
        print("  - mineria (acceso a minería) → contraseña: mineria.2025")

if __name__ == '__main__':
    crear_usuarios()

