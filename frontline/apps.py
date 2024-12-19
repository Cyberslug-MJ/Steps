from django.apps import AppConfig


class FrontlineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'frontline'

    def ready(self):
        import frontline.signals