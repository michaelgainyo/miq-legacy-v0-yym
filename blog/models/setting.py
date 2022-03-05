import logging
from django.db import models
from django.urls import reverse
from sitemgr.models.setting import PageSetting
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

__all__ = ['BlogSetting']


class BlogSetting(PageSetting):
    class Meta:
        ordering = ('site',)
        verbose_name = _('Blog Settings')
        verbose_name_plural = _('Blog Settings')

    TEMP_CHOICES = (
        ('one_column', _('One Column')),
        ('masonry', _('Masonry')),
    )

    article_list_template = models.CharField(
        max_length=20, choices=TEMP_CHOICES, default='one_column',
        verbose_name=_('article list template'))

    featured_text_hex = models.CharField(
        _('featured article hex color'), default='#000',
        max_length=7,
        help_text=_(
            'The color in which to display the featured article\'s '
            'text on the articles list page'))

    accept_submissions = models.BooleanField(default=False)
    submission_terms = models.TextField(blank=True)

    @property
    def categories(self):
        from . import Category
        return Category.objects.all()[:5]

    @property
    def detail_url(self):
        return reverse('blog:articles')

    def __str__(self):
        return f'{self.site} Blog Settings'
