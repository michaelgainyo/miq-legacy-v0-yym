
from django.db import models
from django import forms


class TimeStampsModelMixin(models.Model):
    """
    Abstract class with creation and modification date and time
    ['created', 'updated']
    """

    created = models.DateTimeField(
        ("creation date and time"),
        editable=False,
        auto_now_add=True,)

    updated = models.DateTimeField(
        ("update date and time"),
        auto_now=True,
        editable=False
    )

    class Meta:
        abstract = True

    def get_absolute_url(self):
        if hasattr(self, 'detail_url'):
            return self.detail_url


class BootstrapFormMixin(forms.Form):
    """
    Adds 'form control' class to form fields
    """

    def __init__(self, *args, **kwargs):
        super(BootstrapFormMixin, self).__init__(*args, **kwargs)

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'})


class BootstrapModelFormMixin(forms.ModelForm):
    """
    Adds 'form control' class to form fields
    """

    def __init__(self, *args, **kwargs):
        super(BootstrapModelFormMixin, self).__init__(*args, **kwargs)

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'})





