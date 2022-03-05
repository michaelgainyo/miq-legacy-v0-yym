# models/comment.py

import logging

from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import striptags, slugify

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth import get_user_model

from config.mixins import TimeStampsModelMixin

logger = logging.getLogger(__name__)
User = get_user_model()


class CommentMgr(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(active=True)

    def active(self, *args, **kwargs):
        return self.get_queryset(*args, **kwargs)

    def posted(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs)


class Comment(TimeStampsModelMixin):
    class Meta:
        ordering = ('-created',)
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    body = models.TextField()
    active = models.BooleanField(default=True)

    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='children')

    user = models.ForeignKey(
        User, related_name='comments', on_delete=models.CASCADE)

    objects = CommentMgr()

    @property
    def render_body(self):
        tokens = [i for i in self.body.split()]

        i = 0
        txt = '<a class="text-muted mr-2" href="'\
            f'{self.parent.user.profile.detail_url}">@{self.parent.user}</a>'\
            if self.parent and self.parent.user is not self.user\
            else ' '

        for token in tokens:
            if token.startswith("@"):
                user = User.objects.filter(username=slugify(token)).first()
                if user:
                    tokens[i] = f'<a class="text-muted"'\
                        f' href="{user.profile.detail_url}">{token}</a>'

            i += 1

        return txt + ' '.join(tokens)

    @property
    def deactivate_url(self):
        return reverse('sitemgr:comment_deactivate', args=[self.id])

    def save(self, *args, **kwargs):
        self.body = striptags(self.body)

        super().save(*args, **kwargs)
