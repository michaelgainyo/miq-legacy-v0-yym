
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

from trackr.utils import get_ip

from . import views


app_name = 'accounts'


class AuthForm(AuthenticationForm):
    def clean(self):
        self.cleaned_data['username'] = self.cleaned_data.get(
            'username').lower()

        return super().clean()


class LoginView(auth_views.LoginView):
    authentication_form = AuthForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        done = super().form_valid(form)
        user = self.request.user

        if user.is_authenticated:
            ip = get_ip(self.request)

            if not user.profile.ip:
                user.profile.ip = ip
                user.profile.save()

            if user.last_login_ip != ip:
                user.last_login_ip = ip
                user.save()

            if not self.request.session.get('uuid'):
                self.request.session['uuid'] = f'{user.uuid}'

        return done


class PasswordResetView(auth_views.PasswordResetView):
    def form_valid(self, form):
        if self.request.user.is_authenticated:
            logout(self.request)

        return super().form_valid(form)


urlpatterns = [

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]

urlpatterns += [

    path(
        'register/',
        views.RegistrationView.as_view(), name='register'),

    path(
        'register/done/<str:uidb64>/<str:token>/',
        views.RegistrationDoneView.as_view(),
        name='register_done'),
]

urlpatterns += [
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done'),

    path(
        'password-reset/',
        PasswordResetView.as_view(
            html_email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('accounts:password_reset_done'),
        ),
        name='password_reset'),

    path(
        'password-confirm/<str:uidb64>/<str:token>/',
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy('accounts:password_reset_complete')
        ),
        name='password_reset_confirm'),

    path(
        'password-reset/complete/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete'),
]

urlpatterns += [
    path(
        'account/edit/',
        views.AccountUpdateView.as_view(), name='account_edit'),

    path(
        'account/notifications/',
        views.AccountNotificationView.as_view(), name='notifications'),

    path(
        'account/',
        views.AccountView.as_view(), name='account'),
    path(
        '<str:username>/',
        views.AccountProfileView.as_view(), name='profile'),

    path(
        '<str:username>/<str:short_code>/',
        views.AccountPostView.as_view(), name='post'),
    path(
        'post/delete/<int:pk>/',
        views.AccountPostDeactivateView.as_view(), name='post_deactivate'),
]
