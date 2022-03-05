
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    PasswordChangeForm, UserCreationForm,
    PasswordResetForm, SetPasswordForm)
from django.utils.translation import gettext_lazy as _

from filemgr.models import Image
from config.mixins import BootstrapModelFormMixin


User = get_user_model()


class PostUploadForm(BootstrapModelFormMixin):
    class Meta:
        model = Image
        fields = ('file', 'is_explicit')

    description = forms.CharField(widget=forms.Textarea, required=False)


class AccountEditForm(BootstrapModelFormMixin):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class RegistrationForm(BootstrapModelFormMixin, UserCreationForm):

    username = forms.CharField(min_length=4)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields["first_name"].required = True
        self.fields["email"].required = True
        self.fields["email"].help_text = _(
            'We will send you a verification email here')

    def clean_username(self):
        return self.cleaned_data['username'].lower()

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_('This user already exists.'))
        return email


class PasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'})


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'})


class SetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {'class': 'form-control'})
