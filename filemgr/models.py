
import logging

from datetime import date
from PIL import Image as PImage

from django.db import models
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


from config.mixins import TimeStampsModelMixin
from sitemgr.mixins import ObjectRenderMixin


IMG_SIZE = (800, 1200)
THUMB_SIZE = (500, 500)

User = get_user_model()
logger = logging.getLogger(__name__)
__all__ = ['File', 'Image', 'Gallery', 'GalleryImage', 'FileSetting']


def minimum_size(image):
    errors = []
    width = IMG_SIZE[0]
    height = IMG_SIZE[1]

    if image.width < width or image.height < height:
        errors.append(
            'Width/Height should be at least {}x{} px.'.format(width, height))

    if image.width > 3999 or image.height > 4000:
        errors.append('This image is too big.')

    raise ValidationError(errors)


class BaseFile(TimeStampsModelMixin):
    class Meta:
        ordering = ('-created',)
        abstract = True

    is_explicit = models.BooleanField(default=False)

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)

    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True)

    @property
    def url(self):
        return self.file.url

    @property
    def full_url(self):
        from django.contrib.sites.models import Site

        url = Site.objects.first().domain
        if self.file:
            url += self.file.url
        return url

    def __str__(self):
        return '{}'.format(self.file.name)


class File(BaseFile):
    class Meta:
        ordering = ('-created', 'name')
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    name = models.CharField(max_length=400)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='content/files/')

    @property
    def download_url(self):
        return self.file.url

    @property
    def staff_edit_url(self):
        return reverse('filemgr:file_edit', args=[self.id])

    @property
    def staff_delete_url(self):
        return reverse('filemgr:file_delete', args=[self.id])

    def delete(self, *args, **kwargs):
        pk = self.pk
        name = self.name

        self.file.delete(save=False)
        super().delete(*args, **kwargs)
        logger.info(f'Deleted file[{pk}]: {name}')


class BaseImage(ObjectRenderMixin):

    def crop_to_square(self, file):
        """
        Crops a given image file to square
        """

        if not file:
            return

        img = PImage.open(file)
        width, height = img.size
        if width > IMG_SIZE[0] and height > IMG_SIZE[1]:
            # keep ratio but shrink down
            img.thumbnail((width, height))
            # img.show()

        # check which one is smaller
        if height < width:
            # make square by cutting off equal amounts left and right
            left = (width - height) / 2
            right = (width + height) / 2
            top = 0
            bottom = height
            cropped = img.crop((left, top, right, bottom))

        elif width < height:
            # make square by cutting off bottom
            left = 0
            right = width
            top = 0
            bottom = width
            cropped = img.crop((left, top, right, bottom))
        else:
            cropped = img

        return cropped

    def get_thumbnail(self, file, width=THUMB_SIZE[0], height=THUMB_SIZE[1]):

        if not file:
            logger.warn('No file to resize')
            return

        thumb = PImage.open(file)
        th_width, th_height = thumb.size
        if th_width > width and th_height > height:
            thumb.thumbnail((width, height))
            logger.info(f'Resized file[{file}]')

        return thumb

    @property
    def render_thumb(self):
        template_name = 'filemgr/image/img-widget.html'
        protect_img = FileSetting.objects.first().protect_image
        if protect_img:
            template_name = 'filemgr/image/img-widget-hidden.html'

        context = {
            'img': self,
            'alt': self.get_alt_text,
            'cls': 'img-fluid',
            'width': self.thumbnail.width,
            'height': self.thumbnail.height,
        }

        return super().render(template_name, context)

    def render(self, url=None, width=None, height=None, alt=None):
        template_name = 'filemgr/image/img-widget.html'
        protect_img = FileSetting.objects.first().protect_image
        if protect_img:
            template_name = 'filemgr/image/img-widget-hidden.html'

        context = {
            'img': self,
            'url': url or self.url,
            'alt': alt,
            'width': width or self.file.width,
            'height': height or self.file.height
        }

        return super().render(template_name, context)


class Image(BaseImage, BaseFile):

    def get_path(self, filename):
        year = date.today().year
        path = f'content/images/{year}/'

        return f'{path}/{filename}'

    class Meta:
        ordering = ('order', 'created')
        verbose_name = 'Image'
        verbose_name_plural = 'Images'

    file = models.ImageField(
        upload_to=get_path,
        verbose_name='Desktop Image Default'
    )

    m_file = models.ImageField(
        upload_to=get_path,
        null=True, blank=True,
        verbose_name='Mobile Image Default',

    )

    thumbnail = models.ImageField(
        upload_to=get_path, max_length=500,
        null=True,
        verbose_name='Desktop Thumbnail',)
    m_thumbnail = models.ImageField(
        upload_to=get_path, max_length=500,
        null=True, blank=True,
        verbose_name='Mobile Thumbnail',
    )

    order = models.PositiveIntegerField(default=0, blank=True)

    alt_text = models.CharField(max_length=400, blank=True)
    external_url = models.URLField(null=True, blank=True)

    @property
    def get_alt_text(self):
        txt = ''
        if self.alt_text:
            txt = self.alt_text

        if self.content_object:
            txt = getattr(
                self.content_object, 'title',
                getattr(self.content_object, 'name', ''))
        return txt

    @property
    def edit_info_form(self):
        from .staff.forms import ImageInfoUpdateForm
        return ImageInfoUpdateForm(initial=self.__dict__)

    @property
    def edit_form(self):
        from .staff.forms import ImageUpdateForm
        return ImageUpdateForm(initial=self.__dict__)

    def delete(self, *args, **kwargs):
        pk = self.pk

        # no need to save if its gon be deleted anyways
        if self.m_file:
            self.m_file.delete(save=False)
        if self.m_thumbnail:
            self.m_thumbnail.delete(save=False)

        if self.thumbnail:
            self.thumbnail.delete(save=False)

        self.file.delete(save=False)

        super().delete(*args, **kwargs)
        logger.info(f'Deleted image[{pk}]')

    @property
    def staff_edit_url(self):
        return reverse('filemgr:staff_img_update', args=[self.id])

    @property
    def staff_delete_url(self):
        return reverse('filemgr:staff_img_delete', args=[self.id])

    def save(self, *args, **kwargs):
        new = False
        if not self.pk:
            super().save(*args, **kwargs)
            new = True

            # Generate thumbnail
            if not self.thumbnail:
                # duplicate file first
                self.thumbnail.save(
                    self.file.url.split('/')[-1],
                    self.file.file, save=False)

        super().save(*args, **kwargs)

        if new:
            self.get_thumbnail(file=self.thumbnail).save(self.thumbnail.path)

            # # Resize uploaded image
            # self.get_thumbnail(
            #     file=self.file, width=IMG_SIZE[0],
            #     height=IMG_SIZE[1]).save(self.file.path)

        logger.info(f'Saved Image[{self.pk}]')

    def crop_file_to_square(self):
        """
        Crops main file and thumbnail to square
        """

        if self.file:
            self.crop_to_square(file=self.file).save(self.file.path)
            logger.info(f'Cropped file[{self.file}] to square')

        if self.thumbnail:
            self.crop_to_square(file=self.thumbnail).save(self.thumbnail.path)
            logger.info(f'Cropped thumb[{self.thumbnail}] to square')


"""
GALLERY
"""


class Gallery(TimeStampsModelMixin):

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Gallery'
        verbose_name_plural = 'Galleries'

    # user

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_slider = models.BooleanField(default=False)

    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True)

    @property
    def staff_create_url(self):
        return reverse('filemgr:staff_gallery_create')

    @property
    def staff_edit_url(self):
        return reverse('filemgr:staff_gallery_edit', args=[self.id])

    @property
    def staff_delete_url(self):
        return reverse('filemgr:staff_gallery_delete', args=[self.id])

    def delete(self, *args, **kwargs):
        pk = self.pk
        name = self.name

        logger.debug(f'Deleting gallery[{pk}]: {name}')

        imgs = self.images.all()
        if imgs.exists():
            count = imgs.count()

            for img in imgs:
                img.delete()

            logger.info(f'Deleted gallery[{pk}] images: count {count}')

        super().delete(*args, **kwargs)
        logger.info(f'Deleted gallery[{pk}]: {name}')

    def __str__(self):
        return f'{self.name}'


class GalleryImage(Image):
    class Meta:
        ordering = ('order', 'created')
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    gallery = models.ForeignKey(
        Gallery, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(
        blank=True, help_text='Supports HTML')

    @property
    def edit_form(self):
        from .staff.forms import GalleryImageUpdateForm
        return GalleryImageUpdateForm(initial=self.__dict__)

    @property
    def staff_create_url(self):
        return reverse('filemgr:staff_gimg_create')

    @property
    def staff_edit_url(self):
        return reverse('filemgr:staff_gimg_update', args=[self.id])

    @property
    def staff_delete_url(self):
        return reverse('filemgr:staff_gimg_delete', args=[self.id])

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = self.gallery.images.count() + 1

        super().save(*args, **kwargs)


"""
SETTINGS
"""


class FileSetting(models.Model):
    site = models.OneToOneField(
        Site, on_delete=models.CASCADE,
        related_name='%(class)s', null=True)

    # TODO
    protect_image = models.BooleanField(
        default=True, help_text='Hide image\'s url')

    @property
    def staff_edit_url(self):
        return reverse('filemgr:setting_edit', args=[self.id])
