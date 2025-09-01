from django.apps import AppConfig


class OnlinestoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'onlineStore'

   
    def ready(self):
        # This line is crucial. It imports your signals file and
        # connects the receivers (the functions you just wrote).
        import onlineStore.signals        