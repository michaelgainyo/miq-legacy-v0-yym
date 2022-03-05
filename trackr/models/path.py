import logging

from django.db import models
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from config.mixins import TimeStampsModelMixin
from .hit import Hit

__all__ = ['Path', 'TrackrSetting']

logger = logging.getLogger(__name__)
User = get_user_model()


class Path(TimeStampsModelMixin):
    class Meta:
        ordering = ('-created', )
        verbose_name = "User Path"
        verbose_name_plural = "User Paths"

    name = models.CharField(max_length=100, null=True)
    path = models.CharField(max_length=300)

    @property
    def staff_detail_url(self):
        return reverse('trackr:path_detail', args=[self.id])

    @property
    def staff_create_url(self):
        return reverse('trackr:path_create')

    @property
    def staff_edit_url(self):
        return reverse('trackr:path_edit', args=[self.id])

    @property
    def staff_delete_url(self):
        return reverse('trackr:path_delete', args=[self.id])

    def get_manager(self):
        return Hit.views.filter(path__exact=self.path)

    def get_today_manager(self):
        return Hit.today.filter(path__exact=self.path)

    def __str__(self):
        return self.name


class TrackrSetting(models.Model):

    site = models.OneToOneField(
        Site, on_delete=models.CASCADE,
        related_name='%(class)s', null=True)

    ga_tracking_id = models.CharField(
        max_length=400, blank=True, null=True,
        verbose_name='Google Analytics Tracking ID',
        help_text='Google Analytics Measurement ID')

    fb_pixel_id = models.CharField(
        max_length=400, blank=True, null=True,
        verbose_name='Facebook Pixel ID',
        help_text='Facebook Pixel ID')

    filter_bot = models.BooleanField(
        default=True,
        verbose_name='Filter known bots traffic')

    class Meta:
        verbose_name = "Trackr Settings"
        verbose_name_plural = "Trackr Settings"

    @property
    def staff_edit_url(self):
        return reverse(
            f'trackr:staff_{self._meta.model_name}_edit',
            args=[self.id])

    @property
    def staff_index_url(self):
        return reverse('trackr:staff_index')

    def __str__(self):
        return f'{self.site} Trackr Settings'
