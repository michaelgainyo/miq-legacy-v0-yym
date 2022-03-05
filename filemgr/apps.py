from django.apps import AppConfig


class FilemgrConfig(AppConfig):
    name = 'filemgr'
    verbose_name = 'File Manager'

    def ready(self, *args, **kwargs):
        from . import signals
