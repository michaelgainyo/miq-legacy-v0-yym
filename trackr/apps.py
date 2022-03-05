from django.apps import AppConfig


class TrackrConfig(AppConfig):
    name = 'trackr'
    verbose_name = 'Trackr'

    def ready(self):
        from . import signals
