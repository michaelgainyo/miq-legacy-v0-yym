
import logging
from django.db import models

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType


from config.utils import get_model
from config.mixins import TimeStampsModelMixin

from .post import Image, UserPost

logger = logging.getLogger(__name__)
User = get_user_model()


class Analytics(object):

    @property
    def today(self):
        Hit = get_model('trackr', 'hit')
        return Hit.today.by_path(self.detail_url)

    @property
    def views(self):
        Hit = get_model('trackr', 'hit')
        return Hit.views.by_path(self.detail_url)


class Profile(TimeStampsModelMixin):

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
        permissions = (
            ("view_staff", _("Can view the staff site")),
            ("_", _("Can view the staff site")),
        )

    TYPE_CHOICES = (
        ('blogger', _('Blogger')),
        ('artist', _('Artist')),
        ('model', _('Model')),
        ('photographer', _('Photographer')),
        ('writer', _('Writer')),
        ('curator', _('Curato')),
        ('content_creator', _('Content Creator')),
        ('videographer', _('Videographer')),
        ('mua', _('Makeup Artist')),
        ('hair', _('Hair Stylist')),
        ('stylist', _('Wardrobe Stylist')),
        ('retoucher', _('Retoucher')),
        ('director', _('Director')),
        ('designer', _('Designer')),
        ('brand', _('Brand')),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True, blank=True)

    image = models.ForeignKey(
        Image, related_name='profile',
        on_delete=models.SET_NULL, null=True, blank=True)

    type = models.CharField(
        max_length=50, choices=TYPE_CHOICES, null=True, blank=True,
        verbose_name=_('Category'))
    biography = models.TextField(blank=True, verbose_name=_('biography'))

    website = models.URLField(blank=True)
    instagram_handle = models.CharField(max_length=250, blank=True)

    is_verified = models.BooleanField(default=False)
    verification_email_sent = models.BooleanField(default=False)
    filter_explicit_content = models.BooleanField(default=True)
    ip = models.GenericIPAddressField(unpack_ipv4=True, null=True, blank=True)

    # REGISTRATION

    def send_verification_email(self):

        # imports
        from django.template import loader
        from django.contrib.sites.models import Site
        from django.utils.encoding import force_bytes
        from django.core.mail import EmailMultiAlternatives
        from django.utils.http import urlsafe_base64_encode
        from django.contrib.auth.tokens import default_token_generator

        site = Site.objects.first()
        email_template_name = 'registration/signup_email.html'
        from_email = None

        try:
            uid = urlsafe_base64_encode(force_bytes(
                self.user.pk)).decode()
        except Exception as e:
            logger.error(e)
            uid = urlsafe_base64_encode(force_bytes(self.user.pk))

        context = {
            'site': site,
            'user': self.user,
            'email': self.user.email,
            'uid': uid,
            'token': default_token_generator.make_token(self.user),
        }

        subject = f'Confirm your account, { self.user.first_name }'
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(
            subject, body, from_email, [self.user.email])

        html_email = loader.render_to_string(email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

        if email_message.send() == 1 and not self.verification_email_sent:
            self.verification_email_sent = True
            self.save()

    def add_post_perms(self, remove=False):

        perm = Permission.objects.get(
            codename='view_profile',
            content_type=ContentType.objects.get_for_model(Profile)
        )
        if remove:
            self.user.user_permissions.remove(perm)
            for post in self.user.posts.all():
                post.is_active = False
                post.was_deleted_by_user = True
                post.save()
        else:
            self.user.user_permissions.add(perm)

        for code in ['add_userpost', 'change_userpost']:

            if self.user.has_perm(f'blog.{code}'):
                continue

            perm = Permission.objects.get(
                codename=code,
                content_type=ContentType.objects.get_for_model(UserPost),
            )

            if remove:
                self.user.user_permissions.remove(perm)
            else:
                self.user.user_permissions.add(perm)
            logger.info(f'Added {perm} to {self.user} permissions')

    @property
    def contact(self):
        if self.website:
            return self.website

        if self.instagram_handle:
            return self.instagram_url

        return self.detail_url

    @property
    def detail_url(self):
        return reverse('accounts:profile', args=[self.user.username])

    @property
    def unsubscribe_url(self):
        return

    @property
    def articles_url(self):
        pass

    @property
    def edit_url(self):
        return reverse('accounts:account_edit')

    @property
    def instagram_url(self):
        if self.instagram_handle:
            return f'https://www.instagram.com/{self.instagram_handle}'

    @property
    def instagram_username(self):
        if self.instagram_handle:
            return f'@{self.instagram_handle}'

    def __str__(self):
        return '{}'.format(self.user)
