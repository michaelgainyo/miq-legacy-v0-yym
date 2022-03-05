
import uuid
from django.db import models
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.fields import GenericRelation

from sitemgr.models.comment import Comment
from filemgr.models import Image

from config.mixins import TimeStampsModelMixin

User = get_user_model()


class UserPostMgr(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(is_active=True)


class UserPost(TimeStampsModelMixin):

    class Meta:
        ordering = ('-created',)
        verbose_name = _("User Post")
        verbose_name_plural = _("User Posts")

    Hit = None

    description = models.TextField(blank=True)
    short_code = models.UUIDField(
        unique=True, default=uuid.uuid4, editable=False)  # Auto Generated

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='posts')

    is_active = models.BooleanField(default=False)
    was_deleted_by_user = models.BooleanField(default=False)
    is_explicit = models.BooleanField(default=False)

    viewers = models.ManyToManyField(
        User, related_name='viewed', through='View', blank=True)

    _comments = GenericRelation(Comment, related_name='post')
    images = GenericRelation(Image, related_name='post')

    objects = UserPostMgr()
    staff = models.Manager()

    # ANALYTICS
    @property
    def today(self):
        if not self.Hit:
            from trackr.models import Hit
            self.Hit = Hit
        return self.Hit.today.by_path(self.detail_url)

    @property
    def thumbnail_is_cropped(self):
        img = self.image
        if img and img.file.height != img.file.width:
            return True
        return False

    @property
    def image(self):
        return self.images.first()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def comments(self):
        return self._comments.filter(active=True)

    @property
    def render_description(self):
        tokens = [i for i in self.description.split()]

        i = 0
        for token in tokens:
            if token.startswith("@"):
                user = User.objects.filter(username=slugify(token)).first()
                if user:
                    tokens[i] = f'<a href="{user.profile.detail_url}">{token}</a>'

            i += 1

        return ' '.join(tokens)

    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()

        super().delete(*args, **kwargs)

    @property
    def detail_url(self):
        return reverse(
            'accounts:post',
            args=[self.user.username, self.short_code])

    @property
    def delete_url(self):
        return reverse('accounts:post_deactivate', args=[self.pk])

    @property
    def edit_url(self):
        return reverse(
            f'account:{self._meta.model_name}_edit', args=[self.short_code])

    @property
    def staff_delet_url(self):
        return reverse(f'accounts:staff_userpost_review')

    @property
    def staff_delete_url(self):
        return reverse(
            f'account:{self._meta.model_name}_delete', args=[self.id])

    def __str__(self):
        return f'{self.user.username}: {self.short_code}'


class View(models.Model):

    class Meta:
        ordering = ('-created',)
        verbose_name = _('View')
        verbose_name_plural = _('Views')

    post = models.ForeignKey(
        UserPost, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='views')

    ip = models.GenericIPAddressField(
        unpack_ipv4=True, null=True, verbose_name='ip address')
    user_agent = models.TextField(null=True)

    created = models.DateTimeField(
        verbose_name=_('date created'), auto_now_add=True)
