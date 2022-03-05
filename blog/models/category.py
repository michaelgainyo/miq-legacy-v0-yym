
from django.db import models
from django.urls import reverse
from django.utils.text import capfirst
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _

from config.mixins import TimeStampsModelMixin


class Category(TimeStampsModelMixin):
    class Meta:
        ordering = ('name',)
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    description = models.TextField(blank=True)

    @property
    def detail_url(self):
        return reverse('blog:category', args=[self.slug])

    @property
    def staff_create_url(self):
        return reverse(f'blog:{self._meta.model_name}_create')

    @property
    def staff_edit_url(self):
        return reverse(f'blog:{self._meta.model_name}_edit', args=[self.id])

    @property
    def staff_delete_url(self):
        return reverse(f'blog:{self._meta.model_name}_delete', args=[self.id])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        if not self.name:
            self.name = capfirst(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return capfirst(self.name)
