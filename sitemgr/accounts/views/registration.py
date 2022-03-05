import logging

from django.shortcuts import redirect
from django.views import generic
from django.contrib import messages
from django.urls import reverse_lazy

from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.http import HttpResponseRedirect

from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from trackr.utils import get_ip
from sitemgr.utils import is_ajax

from ..forms import RegistrationForm


logger = logging.getLogger(__name__)
User = get_user_model()
__all__ = ['RegistrationView', 'RegistrationDoneView']

INTERNAL_RESET_URL_TOKEN = 'set-password'
INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'


class RegistrationView(generic.edit.CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('accounts:account')

    def post(self, request, *args, **kwargs):
        if is_ajax(request):
            form = self.form_class(request.POST)
            is_valid = form.is_valid()
            if not is_valid:
                print(form.errors.as_json())
                # messages.update(form.)
            data = {
                'is_valid': is_valid,
                'messages': form.errors.as_json()
            }
            return JsonResponse(data)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if form.is_valid():
            user = form.save(self.request)
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])
            user.signup_ip = get_ip(self.request)
            user.save()

            # login(self.request, user)
            try:
                user.profile.send_verification_email()
            except Exception as e:
                logger.error(e)

            msg = _("Thanks for registering. You can now log in")
            messages.info(self.request, msg)

            return HttpResponseRedirect(self.success_url)

        return self.form_invalid(form)

    def form_invalid(self, form):

        messages.error(
            self.request,
            'Something went wrong. Please try again')

        return super().form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)


class RegistrationDoneView(generic.TemplateView):
    template_name = 'registration/signup_done.html'
    token_generator = default_token_generator
    validlink = False
    user = None

    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        user = self.get_user(kwargs['uidb64'])

        if user is not None:
            token = kwargs['token']

            if self.token_generator.check_token(user, token):
                self.validlink = True
                user.profile.is_verified = True
                user.profile.save()
                self.user = user

        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (
            TypeError, ValueError, OverflowError,
                User.DoesNotExist, ValidationError):

            user = None

        return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['validlink'] = self.validlink
        context['user'] = self.user
        return context
