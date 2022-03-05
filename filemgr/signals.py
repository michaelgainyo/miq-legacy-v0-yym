# filemgr/signals.py

import logging
import random
import string

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from sitemgr.models.setting import Site

from . import models


THUMBNAIL_SIZE = (800, 800)

logger = logging.getLogger(__name__)


def code_generator(
        size=6,
        chars=string.ascii_lowercase + string.digits):
    """ Rando code generator """

    return ''.join(random.choice(chars) for _ in range(size))


@receiver(pre_save, sender=models.Image)
def delete_previous_profile_picture(sender, instance, **kwargs):
    from sitemgr.models import Profile

    if isinstance(instance.content_object, Profile):
        try:
            instance.content_object.images.all().delete()
        except Exception as e:
            logger.error(f'Error deleting profile pictures:\n{e}')
        else:
            logger.info(
                f'Deleted all previous profile pictures by'
                f' {instance.content_object}')


@receiver(post_save, sender=Site)
def auto_create_file_settings(sender, **kwargs):
    instance = kwargs.get('instance')
    model = models.FileSetting

    if not model.objects.filter(site=instance).exists():
        model.objects.create(site=instance)
