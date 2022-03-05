import logging

from django.db.models import Count
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.views.generic.list import MultipleObjectMixin
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, LoginRequiredMixin)
from sitemgr.utils import is_ajax

from sitemgr.views import generic
from config.utils import get_model
from trackr.utils import get_ip
from config.mixins import BootstrapModelFormMixin
from sitemgr.models import Profile, UserPost, View

from ..forms import AccountEditForm, PostUploadForm


logger = logging.getLogger(__name__)
User = get_user_model()
__all__ = [
    'AccountView', 'AccountUpdateView', 'AccountNotificationView',
    'AccountProfileView', 'AccountPostView', 'AccountPostDeactivateView',
]


class Mixin(LoginRequiredMixin):
    pass


# POST CREATE VIEW
class AccountView(Mixin, MultipleObjectMixin, generic.CreateView):
    tab = 'posts'
    form_class = PostUploadForm
    object_list = UserPost.objects.order_by('-updated')
    context_object_name = 'feed'
    paginate_by = 8
    template_name = 'sitemgr/account/index.html'

    def get_context_data(self, **kwargs):

        if not self.request.user.profile.is_verified:
            messages.info(
                self.request,
                _('Please check your email to complete your registration'))

        if self.request.user.profile.filter_explicit_content:
            self.object_list = self.object_list.exclude(is_explicit=True)

        context = super().get_context_data(**kwargs)
        context.update({
            'tab': self.tab,

        })
        return context

    def form_valid(self, form):
        form = PostUploadForm(self.request.POST, self.request.FILES)

        if form.is_valid():

            is_explicit = self.request.POST.get('is_explicit', False)
            is_active = False
            msg = 'Thank you! Your post is pending review'

            if self.request.user.has_perm('sitemgr.view_staff'):
                is_active = True
                msg = None

            new_post = UserPost.objects.create(
                user=self.request.user,
                description=form.cleaned_data.get('description'),
                is_explicit=is_explicit, is_active=is_active)

            form.instance.object_id = new_post.pk
            form.instance.content_object = new_post
            form.instance.user = new_post.user

            img = form.save()

            # Generate square profile images
            try:
                if not img.m_file:
                    img.m_file.save(
                        img.file.url.split('/')[-1],
                        img.file.file, save=False)
            except Exception as e:
                logger.error(e)
            else:
                img.crop_to_square(file=img.m_file).save(img.m_file.path)
            finally:
                img.save()

            url = self.request.POST.get('next')
            if not url:
                url = self.request.user.detail_url

            if msg:
                messages.success(self.request, msg)

            return HttpResponseRedirect(url)

        return self.form_invalid(form)

    def form_invalid(self, form):
        # messages.error(self.request, 'Oops something went wrong!')
        return super().form_invalid(form)


class AccountNotificationView(Mixin, PermissionRequiredMixin, generic.ListView):
    paginate_by = 8
    permission_required = 'sitemgr.add_userpost'
    template_name = 'sitemgr/account/notifications.html'

    def get_queryset(self):
        return View.objects.exclude(viewer=self.request.user).filter(
            post__user=self.request.user,
            post__is_active=True).order_by('-created')[:100]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = 'notif'

        # count and order by viewers
        context['most_popular'] = self.request.user.posts\
            .annotate(views_count=Count('viewers'))\
            .order_by('-views_count')[:6]
        return context


class AccountUpdateView(Mixin, generic.UpdateView):
    model = Profile
    fields = ['filter_explicit_content']
    success_url = reverse_lazy('accounts:account_edit')
    template_name = 'sitemgr/account/edit.html'

    class CreatorForm(BootstrapModelFormMixin):
        class Meta:
            model = Profile
            fields = ['type', 'biography', 'website', 'instagram_handle']
    creator_form = CreatorForm

    def get_object(self):
        return self.request.user.profile

    def post(self, request, *args, **kwargs):
        if is_ajax(request):
            data = {'is_valid': False}

            from filemgr.forms import ImageUploadForm

            form = ImageUploadForm(request.POST, request.FILES)

            if form.is_valid():

                form.instance.user = request.user
                img = form.save()
                img.crop_file_to_square()

                profile = request.user.profile
                profile.image = img
                profile.save()

                data = {
                    'is_valid': True, 'url': img.url, 'pk': img.pk,
                    'thumb': img.thumbnail.url
                }
            return JsonResponse(data)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):

        msg = False

        is_creator = self.request.POST.get('is_creator')
        if is_creator:
            if is_creator == 'add':
                self.request.user.profile.add_post_perms()
            elif is_creator == 'remove':
                self.request.user.profile.add_post_perms(remove=True)

            messages.success(self.request, 'Your profile has been updated!')
            return HttpResponseRedirect(self.success_url)

        user_form = AccountEditForm(
            self.request.POST, instance=self.request.user)

        creator_form = self.creator_form(
            self.request.POST, instance=self.request.user.profile)

        if user_form.has_changed() and user_form.is_valid():
            user_form.save()
            msg = True

        if creator_form.has_changed() and creator_form.is_valid():
            creator_form.save()
            msg = True

        if user_form.has_changed() or form.has_changed():
            msg = True

        if msg:
            messages.success(self.request, 'Your profile has been updated!')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Something went wrong')

        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data = {
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
        }
        context.update({
            'user_form': AccountEditForm(data),
            'creator_form': self.creator_form(instance=self.object),
        })
        return context


class AccountProfileView(generic.ListView):
    tab = 'posts'
    model = UserPost
    paginate_by = 9
    template_name = 'sitemgr/account/profile.html'

    def get_queryset(self, *args, **kwargs):
        return self.get_object().posts.all()

    def get_object(self):
        return get_object_or_404(
            User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = self.tab
        context['user'] = self.get_object()

        return context


class AccountPostView(Mixin, generic.DetailView):
    model = UserPost
    template_name = 'sitemgr/account/post.html'
    context_object_name = 'post'

    def get_object(self):
        return get_object_or_404(
            UserPost, user__username=self.kwargs.get('username'),
            short_code=self.kwargs.get('short_code'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        user = self.request.user
        if user.is_authenticated:
            view, new = View.objects.get_or_create(post=obj, viewer=user)
            if new:
                view.ip = get_ip(self.request)
                view.user_agent = self.request.META.get('HTTP_USER_AGENT')
                view.save()

        related = obj.user.posts.exclude(pk=obj.pk).order_by('?')
        if user.profile.filter_explicit_content:
            related = related.exclude(is_explicit=True)

        context['related'] = related[:4]
        return context


class AccountPostDeactivateView(Mixin, generic.UpdateView):
    model = UserPost
    fields = ['is_active']
    template_name = 'components/confirm-delete.html'

    def get_object(self, *args, **kwargs):
        if self.request.user.is_superuser:
            obj = super().get_object(*args, **kwargs)

        else:
            obj = get_object_or_404(
                UserPost, user=self.request.user,
                is_active=True,
                pk=self.kwargs.get('pk'))

        self.success_url = obj.user.profile.detail_url
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back'] = self.object.detail_url
        return context

    def form_valid(self, form):
        next = self.request.POST.get('next')
        if next:
            self.success_url = next

        form.instance.is_active = False
        form.instance.was_deleted_by_user = True

        return super().form_valid(form)
