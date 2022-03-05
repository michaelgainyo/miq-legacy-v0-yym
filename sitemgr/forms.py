
import logging
from django import forms
from django.utils.translation import gettext_lazy as _
from config.mixins import BootstrapModelFormMixin, BootstrapFormMixin

from .models import Comment


logger = logging.getLogger(__name__)


class CommentAddForm(BootstrapModelFormMixin):
    class Meta:
        model = Comment
        fields = ['body']

    body = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={'class': 'form-control'}))


class ContactForm(BootstrapFormMixin):
    first_name = forms.CharField(label=_("First Name"), max_length=30)
    last_name = forms.CharField(label=_("Last Name"), max_length=30)
    email = forms.EmailField()

    order_number = forms.CharField(
        label=_("Order Number"), max_length=30, required=False,
        help_text=_('This field is not required'))
    subject = forms.CharField(max_length=250)
    message = forms.CharField(widget=forms.Textarea())
