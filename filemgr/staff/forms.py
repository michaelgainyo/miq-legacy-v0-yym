
from config.mixins import BootstrapModelFormMixin
from ..models import Image, GalleryImage


class ImageInfoUpdateForm(BootstrapModelFormMixin):
    class Meta:
        model = Image
        fields = ('order', 'alt_text', 'external_url', 'is_explicit')


class ImageUpdateForm(BootstrapModelFormMixin):
    class Meta:
        model = Image
        fields = (
            'order',
            'file', 'thumbnail',
            'm_file', 'm_thumbnail',
            'alt_text', 'external_url',
            'is_explicit')


class GalleryImageCreateForm(BootstrapModelFormMixin):
    class Meta:
        model = GalleryImage
        fields = ('title', 'description', 'file')


class GalleryImageUpdateForm(BootstrapModelFormMixin):
    class Meta:
        model = GalleryImage
        fields = (
            'title', 'description',
            'alt_text', 'external_url', 'order',
            'is_explicit')
