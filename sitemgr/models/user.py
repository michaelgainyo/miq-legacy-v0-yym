
import uuid
import logging
import datetime
from django.db import models
from django.core.cache import cache

from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.contrib.auth.validators import UnicodeUsernameValidator


logger = logging.getLogger(__name__)


@deconstructible
class CustomUnicodeUsernameValidator(UnicodeUsernameValidator):
    # regex = r'^[\w.@+-]+$'

    # only updated the message
    message = _('Enter a valid username.')


class User(AbstractUser):

    class Meta:
        # ordering = ('-created',)
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        permissions = (
            ("view_staff", _("Can view the staff site")),
        )

    # overrides
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits '
            'and ./_ only.'),
        validators=[MinLengthValidator(4), CustomUnicodeUsernameValidator()],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(
        _('first name'), max_length=30,
        validators=[
            MinLengthValidator(2, message='Enter your first name.')
        ])

    # added fields
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False)
    signup_ip = models.GenericIPAddressField(
        unpack_ipv4=True, null=True, blank=True)

    last_login_ip = models.GenericIPAddressField(
        unpack_ipv4=True, null=True, blank=True)

    @property
    def is_online(self):

        now = datetime.datetime.now()
        online_timeout = 300  # in seconds

        if self.last_seen and now < self.last_seen + datetime.timedelta(
                seconds=online_timeout):
            return True

        return False

    @property
    def last_seen(self):
        return cache.get('seen_%s' % self.username)

    def clean(self, *args, **kwargs):
        u = self.username
        if u.replace('.', '').isdigit() or '@' in u or '+' in u or '-' in u:
            raise ValidationError({
                'username': _('Enter a valid username.')})

        super().clean(*args, **kwargs)

    @property
    def detail_url(self):
        return reverse('accounts:account')

    def __str__(self):
        return self.username
