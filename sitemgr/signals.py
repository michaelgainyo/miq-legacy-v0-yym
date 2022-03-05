
import logging

from django.dispatch import receiver
from django.db.models import signals
from django.contrib.auth.signals import (
    user_logged_in, user_logged_out, user_login_failed
)
from django.contrib.auth import get_user_model

from django.contrib.sites.models import Site

from trackr.utils import get_ip

from . import models


logger = logging.getLogger(__name__)
User = get_user_model()


def after_login(sender, user, request, **kwargs):
    logger.debug(f'New login: {user}')
    ip = get_ip(request)

    try:
        assert user.last_login_ip == ip
    except Exception as e:
        logger.error(e, exc_info=1)
        logger.info(f'User[{user}] IP Change: {user.last_login_ip} > {ip}')
        user.last_login_ip = ip
        user.save()


user_logged_in.connect(after_login)


def after_logout(sender, request, user, **kwargs):
    logger.debug('Logout')


user_logged_out.connect(after_logout)


def login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username')

    # TODO: send admin email
    logger.error(f'Login failed: {username}')


user_login_failed.connect(login_failed)


@receiver(signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    prof, new = models.Profile.objects.get_or_create(user=instance)
    if new:
        logger.info(f'Created new profile for user: {prof.user.username}')


@receiver(signals.post_save, sender=Site)
def auto_create_site_settings(sender, **kwargs):
    Setting = models.Setting

    instance = kwargs.get('instance')
    if not Setting.objects.filter(site=instance).exists():
        Setting.objects.create(site=instance)

    model = models.IndexSetting
    if not model.objects.filter(site=instance).exists():
        model.objects.create(site=instance, name='Home')

    model = models.AboutSetting
    if not model.objects.filter(site=instance).exists():
        model.objects.create(site=instance, name='About')

    model = models.PostSetting
    if not model.objects.filter(site=instance).exists():
        model.objects.create(site=instance)

    from blog.models import BlogSetting
    if not BlogSetting.objects.filter(site=instance).exists():
        BlogSetting.objects.create(site=instance, name='Blog')
