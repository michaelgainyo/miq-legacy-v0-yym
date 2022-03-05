
from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from config.mixins import BootstrapModelFormMixin

from filemgr.models import Image

User = get_user_model()


class IndexImageCreateForm(BootstrapModelFormMixin):
    class Meta:
        model = Image
        fields = ('file', 'is_explicit')

    title = forms.CharField(
        max_length=200, required=False, help_text=_('Title'))
    description = forms.CharField(
        widget=forms.Textarea, required=False, help_text=_('Description'))

    cta = forms.CharField(
        max_length=100, required=False,
        help_text=_('Call to action'))
    cta_url = forms.URLField(required=False, help_text=_('Call to action url'))
