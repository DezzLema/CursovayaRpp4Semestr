from django.apps import AppConfig


class GraphsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'graphs'
    label = 'graphs'  # Убедитесь, что это уникальное значение
