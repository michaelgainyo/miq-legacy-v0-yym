
from config.mixins import BootstrapModelFormMixin
from .models import Image


class ImageUpdateForm(BootstrapModelFormMixin):
    class Meta:
        model = Image
        fields = ('is_explicit', 'external_url')


class ImageUploadForm(BootstrapModelFormMixin):
    class Meta:
        model = Image
        fields = ('file',)
