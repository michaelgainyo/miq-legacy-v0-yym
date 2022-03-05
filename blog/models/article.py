
import logging
import json

from django.db import models
from django.urls import reverse

from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import striptags, wordcount, truncatewords
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from django.contrib.sites.models import Site
from config.utils import get_content_type
from config.mixins import TimeStampsModelMixin

from trackr.mixins import AnalyticsModelMixin
from sitemgr.models.comment import Comment
from sitemgr.models.post import Image
from filemgr.models import Gallery

from .category import Category


User = get_user_model()
logger = logging.getLogger(__name__)


class Analytics(AnalyticsModelMixin):
    pass


class ArticleImageMgr(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            content_type=get_content_type(Article))


class ArticleImage(Image):
    class Meta:
        proxy = True

    objects = ArticleImageMgr()


class PublishedMngr(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(publish=True)


class UnpublishedMngr(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(publish=False)


class Article(Analytics, TimeStampsModelMixin):
    LAYOUT_CHOICES = (
        ('one_column', _('One Column')),
        ('two_column', _('Two Column')),
    )

    GALLERY_LAYOUT_CHOICES = (
        ('one_column', _('One Column')),
        ('two_column', _('Two Column')),
        ('slideshow', _('Slideshow')),
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        permissions = (
            ("publish_article", _("Can publish an article")),
        )

    category = models.ForeignKey(
        Category, related_name='articles',
        null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    description = models.TextField(blank=True)

    # Allow user to enter html
    html = models.TextField(blank=True)

    publish = models.BooleanField(
        default=False, help_text=_('Publish this article'))
    feature = models.BooleanField(
        default=False, help_text=_('Feature this article'))

    artists = models.ManyToManyField(
        User, related_name='articles', blank=True)

    is_explicit = models.BooleanField(
        default=False,
        help_text=_('All images will be tagged explicit'))

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)

    # Content
    video_url = models.URLField(null=True, blank=True)
    images = GenericRelation(ArticleImage, related_name='article')
    galleries = GenericRelation(Gallery, related_name='galleries')
    _comments = GenericRelation(Comment, related_name='post')

    text_first = models.BooleanField(default=False)
    gallery_layout = models.CharField(
        max_length=50, choices=GALLERY_LAYOUT_CHOICES,
        default='one_column', null=True)

    objects = models.Manager()
    published = PublishedMngr()
    unpublished = UnpublishedMngr()

    """
    SEO
    """

    @property
    def json_ld(self):
        site = Site.objects.first()
        is_explicit = self.is_explicit\
            or self.images.filter(is_explicit=True).exists()
        desc = self.html or self.description
        if desc:
            desc = striptags(desc)

        info = {
            "@context": "http://schema.org",
            "@type": "BlogPosting",
            "articleSection": capfirst(self.category),
            "headline": capfirst(self.title),
            "thumbnailUrl": f'http://{self.image.full_url}'
            if self.image else '',
            "image": [
                f'http://{img.full_url}' for img in self.images.all()
            ],
            "keywords": "",
            "wordcount": wordcount(desc),
            "url": f'http://{site.domain}{self.detail_url}',
            "datePublished": f'{self.created}',
            "dateCreated": f'{self.created}',
            "dateModified": f'{self.updated}',
            "description": truncatewords(desc, 50),
            "articleBody": desc,
            "author": {
                "@type": "Person",
                "name": capfirst(site.name)
            },
            "isFamilyFriendly": not is_explicit,
            "mainEntityOfPage": True,
            "publisher": {
                "@type": "Organization",
                "name": capfirst(site.name),
                "url": f'http://{site.domain}',
                "logo": {
                    "@type": "ImageObject",
                    "url": f'http://{site.domain}{site.settings.logo_url}'
                }
            }
        }
        return json.dumps(info)

    @property
    def meta(self):
        """ Open graph info """
        desc = self.html or self.description
        if desc:
            desc = striptags(desc)

        return {
            'type': 'article',
            'description': truncatewords(desc, 50),
            'image': f'http://{self.image.full_url}',
        }

    @property
    def comments(self):
        return self._comments.filter(active=True)

    @property
    def image_landscape(self):
        images = self.images
        if self.gallery_layout == 'slideshow' and self.gallery\
                and self.gallery.images.count() > 0:
            images = self.gallery.images

        for image in images.order_by('order'):
            if image.file.height < image.file.width:
                return image

        return self.image

    @property
    def image_portrait(self):
        images = self.images
        if self.gallery_layout == 'slideshow' and self.gallery\
                and self.gallery.images.count() > 0:
            images = self.gallery.images

        for image in images.order_by('order'):
            if image.file.height > image.file.width:
                return image

        return self.image

    @property
    def image(self):
        """ Returns article first image """
        if self.gallery_layout == 'slideshow' and self.gallery\
                and self.gallery.images.count() > 0:
            return self.gallery.images.first()

        return self.images.first()

    @property
    def gallery(self):
        """ Returns article first image """

        return self.galleries.first()

    def save(self, *args, **kwargs):
        logger.debug(f'Saving article[{self.pk}]: {self.title}')

        if not self.slug:
            self.slug = self.title

        self.slug = slugify(self.slug)

        if self.feature:
            featured = Article.objects.filter(feature=True)
            if featured.exists():
                for article in featured:
                    article.feature = False
                    article.save()

        if self.is_explicit:
            images = self.images.filter(is_explicit=False)
            if images.exists():
                for image in images:
                    image.is_explicit = True
                    image.save()

        super().save(*args, **kwargs)
        logger.info(f'Saved article[{self.pk}]: {self.title}')

    def delete(self, *args, **kwargs):
        pk = self.pk
        title = self.title

        logger.debug(f'Deleting article[{pk}]: {title}')

        imgs = self.images.all()
        if imgs.exists():
            count = imgs.count()

            for img in imgs:
                img.delete()

            logger.info(f'Deleted article[{pk}] images: count {count}')

        comments = self._comments.all()
        if comments.exists():
            count = comments.count()

            for comment in comments:
                comment.delete()

            logger.info(f'Deleted article[{pk}] comments: count {count}')

        super().delete(*args, **kwargs)
        logger.info(f'Deleted article[{pk}]: {title}')

    @property
    def detail_url(self):
        return reverse(
            'blog:article', args=[self.category.slug, self.slug])

    @property
    def staff_create_url(self):
        return reverse(f'blog:{self._meta.model_name}_create')

    @property
    def staff_detail_url(self):
        return reverse('blog:staff_article_detail', args=[self.id])

    @property
    def staff_edit_url(self):
        return reverse(f'blog:{self._meta.model_name}_edit', args=[self.id])

    @property
    def staff_html_url(self):
        return reverse(f'blog:{self._meta.model_name}_edit_html', args=[self.id])

    @property
    def staff_images_upload_url(self):
        if self.gallery_layout == 'slideshow':
            return self.staff_slideshow_url

        return reverse(f'blog:{self._meta.model_name}_images', args=[self.id])

    @property
    def staff_slideshow_url(self):
        return reverse('blog:staff_article_slideshow', args=[self.id])

    @property
    def staff_delete_url(self):
        return reverse(f'blog:{self._meta.model_name}_delete', args=[self.id])

    def __str__(self):
        return f'{self.title}'
