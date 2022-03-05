
import logging
import json
from datetime import date
from django.db import models
from django.urls import reverse
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MaxValueValidator
from django.utils.text import capfirst
from filemgr.models import Image
from config.mixins import TimeStampsModelMixin
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)
User = get_user_model()

__all__ = [
    'Setting', 'PageSetting', 'IndexSetting',
    'AboutSetting', 'PostSetting', 'IndexImage',
    'IndexSection'
]


class Setting(TimeStampsModelMixin):

    class Meta:
        verbose_name = _('Site Setting')
        verbose_name_plural = _('Site Setting')

    site = models.OneToOneField(
        Site, on_delete=models.CASCADE,
        related_name='settings', null=True)

    icon_url = models.CharField(
        max_length=400, blank=True, help_text=_('Site icon url'))
    logo_url = models.CharField(
        max_length=400, blank=True, help_text=_('Site logo url'))

    """
    PAGES
    """

    privacy_policy = models.TextField(blank=True)
    tos = models.TextField(
        blank=True, help_text=_('Terms of Service'))
    faq = models.TextField(
        blank=True, help_text=_('Frequently Asked Questions'))

    """
    SEO
    """

    meta_keywords = models.CharField(
        max_length=400, blank=True,
        help_text=_('Site meta keywords separated by a comma'))
    description = models.TextField(
        blank=True,
        help_text=_('Site meta description separated by a comma'))

    # APPS

    show_sidebar = models.BooleanField(
        _('show sidebar'), default=False,
        help_text='Show navigation bar on the left')
    is_live = models.BooleanField(default=False, help_text=_('open site'))
    close_site_message = models.TextField(
        blank=True,
        default=_(
            'This site is currently under construction. Please come back later!'),
        help_text=_('This message appears when the site is not live'))

    require_login = models.BooleanField(
        default=True,
        help_text=_('require login to access explicit content'))

    @property
    def online_anonymous_users(self):
        # BAAAD
        from trackr.models import Hit

        sessions = set()
        today = date.today()
        hits = Hit.objects.filter(
            updated__day=today.day,
            updated__month=today.month,
            updated__year=today.year)

        for hit in hits:
            if hit.is_online:
                sessions.add(hit.session)

        return hits.filter(session__in=sessions).values('session').distinct()

    @property
    def online_users(self):
        # BAAAD
        usrs = set()
        today = date.today()
        for usr in User.objects.filter(
                last_login__year=today.year):
            if usr.is_online:
                usrs.add(usr.pk)
        return User.objects.filter(pk__in=usrs)

    @property
    def json_ld(self):
        info = {
            "@context": "http://schema.org",
            "@type": "WebSite",
            "name": capfirst(self.site.name),
            "url": self.site.domain,
            "sameAs": [
                self.site.aboutsetting.facebook_url,
                self.site.aboutsetting.instagram_url,
                self.site.aboutsetting.pinterest_url,
                self.site.aboutsetting.youtube_url,
            ]
        }
        return json.dumps(info)

    @property
    def tos_url(self):
        return reverse(f'sitemgr:tos')

    @property
    def privacy_url(self):
        return reverse(f'sitemgr:privacy')

    @property
    def faq_url(self):
        return reverse(f'sitemgr:faq')

    @property
    def contact_email(self):
        return self.site.aboutsetting.contact_email

    @property
    def staff_edit_url(self):
        return reverse(
            f'sitemgr:staff_{self._meta.model_name}_edit',
            args=[self.id])

    def __str__(self):
        return self.site.name


class PostSetting(models.Model):
    site = models.OneToOneField(
        Site, on_delete=models.CASCADE,
        related_name='%(class)s', null=True)
    allow_user_to_post = models.BooleanField(default=False)

    @property
    def staff_edit_url(self):
        return reverse(
            f'sitemgr:staff_{self._meta.model_name}_edit',
            args=[self.id])


class PageSetting(models.Model):
    class Meta:
        abstract = True

    site = models.OneToOneField(
        Site, on_delete=models.CASCADE,
        related_name='%(class)s', null=True)

    name = models.CharField(
        max_length=400, help_text=_('Navbar label'), default='%(class)s')
    show_in_navbar = models.BooleanField(
        default=True, help_text=_('Show link in navbar'))
    show_in_footer = models.BooleanField(
        default=True, help_text=_('Show link in footer'))

    @property
    def staff_edit_url(self):
        return reverse(
            f'{self._meta.app_label}:staff_{self._meta.model_name}_edit',
            args=[self.id])

    def __str__(self):
        return f'{self.site.name}'


"""
INDEX PAGE
"""


class IndexSetting(PageSetting):
    TEMPLATE_CHOICES = (
        ('bg_slider', 'Background Slider'),
        ('masonry', 'Masonry'),
    )

    title = models.CharField(
        max_length=400, help_text=_('Page title'),
        default=_('Official Website'))
    template = models.CharField(
        max_length=50, choices=TEMPLATE_CHOICES, default='masonry')

    video_url = models.URLField(null=True, blank=True)

    @property
    def sections(self):
        return self._sections.filter(parent=None)

    @property
    def cover(self):
        return self.images.last()

    @property
    def detail_url(self):
        return reverse(f'sitemgr:index')


class IndexImage(models.Model):
    """ Carousel or video """

    setting = models.ForeignKey(
        IndexSetting, on_delete=models.CASCADE, related_name='covers')
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True)

    cta = models.CharField(
        max_length=100, null=True, blank=True,
        verbose_name=_('Call to action'))
    cta_url = models.URLField(
        blank=True, null=True,
        verbose_name=_('Call to action url'))

    images = GenericRelation(Image, related_name='cover')

    @property
    def image(self):
        return self.images.first()

    @property
    def staff_delete_url(self):
        return reverse(
            'sitemgr:staff_indeximage_delete', args=[self.pk])

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()

        super().delete(*args, **kwargs)


class IndexSection(TimeStampsModelMixin):
    class Meta:
        ordering = ('created',)
        verbose_name = _('Index Section')
        verbose_name_plural = _('Index Sections')

    page = models.ForeignKey(
        IndexSetting, related_name='_sections',
        on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    columns_count = models.PositiveIntegerField(
        default=1, validators=[MaxValueValidator(4)])

    image_url = models.CharField(max_length=500, null=True, blank=True)
    image_alt_text = models.CharField(max_length=500, null=True, blank=True)

    cta = models.CharField(max_length=500, null=True, blank=True)
    cta_url = models.URLField(null=True, blank=True)

    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE,
        related_name='sections')

    def has_items(self):
        return True

    def delete(self, *args, **kwargs):
        self.sections.all().delete()
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.page = IndexSetting.objects.first()

        super().save(*args, **kwargs)

    def staff_edit_url(self):
        return reverse('sitemgr:staff_section_edit', args=[self.id])

    def staff_delete_url(self):
        return reverse('sitemgr:staff_section_delete', args=[self.id])

    def __str__(self):
        return f'{self.page} {self.name}'


class AboutSetting(PageSetting):

    about = models.TextField(default='', blank=True)

    # CONTACT

    contact_email = models.EmailField(
        max_length=400, blank=True,
        help_text=_('preferred contact email'))

    show_contact_form = models.BooleanField(default=False)

    # SOCIAL

    patreon_url = models.CharField(
        max_length=400, blank=True,
        help_text=_('Your site\'s patreon url'))

    instagram_url = models.CharField(
        max_length=400, blank=True, help_text=_('instagram url'))

    facebook_url = models.CharField(
        max_length=400, blank=True, help_text=_('facebook url'))

    pinterest_url = models.CharField(
        max_length=400, blank=True, help_text=_('pinterest url'))

    youtube_url = models.CharField(
        max_length=400, blank=True, help_text=_('youtube url'))

    @property
    def has_social_links(self):
        return (
            self.instagram_url or self.facebook_url or
            self.pinterest_url or self.youtube_url)

    @property
    def detail_url(self):
        return reverse(f'sitemgr:about')

    @property
    def display_contact_email(self):
        if self.contact_email:
            return self.contact_email.replace('@', '[at]')
