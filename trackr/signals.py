import logging
from django.dispatch import receiver
from django.db.models import signals
from django.core.signals import got_request_exception
from django.contrib.auth import get_user_model

from django.contrib.sites.models import Site

from .models import TrackrSetting
from .utils import *

logger = logging.getLogger(__name__)
User = get_user_model()


def log_request_exception(sender, request, **kwargs):
    logger.error(f'Request Exception.\n{request}')


got_request_exception.connect(log_request_exception)


@receiver(signals.post_save, sender=Site)
def auto_create_site_trackrsettings(sender, **kwargs):
    instance = kwargs.get('instance')
    if not TrackrSetting.objects.filter(site=instance).exists():
        TrackrSetting.objects.create(site=instance)
