from django.apps import AppConfig


class ArticulosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'configuracion.articulos'
    label = 'articulos'  # Mantener el label original para compatibilidad con migraciones
    verbose_name = 'Artículos'

