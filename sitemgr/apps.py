from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SitemgrConfig(AppConfig):
    name = 'sitemgr'
    verbose_name = _('Site Manager')

    def ready(self):
        from . import signals
