import logging

from sitemgr.views import generic
from django.contrib import messages
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect

from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, LoginRequiredMixin)

from sitemgr.models import (
    Setting, IndexSetting, AboutSetting, PostSetting,
    IndexImage, IndexSection)

from ..forms import IndexImageCreateForm


logger = logging.getLogger(__name__)
__all__ = [
    'SettingUpdateView', 'IndexSettingUpdateView', 'AboutSettingUpdateView',
    'IndexImageCreateView', 'IndexImageDeleteView', 'UserSettingUpdateView',
    'SectionCreateView', 'SectionUpdateView', 'SectionDeleteView'
]


class Mixin(LoginRequiredMixin, PermissionRequiredMixin):
    app_name = 'sitemgr'
    model = None

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)

        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'model': self.model,
            'app_name': self.app_name})

        if self.model:
            context['model_name'] = self.model._meta.model_name

        return context


class SettingUpdateView(Mixin, generic.UpdateView):
    tab = 'general'
    model = Setting
    permission_required = 'sitemgr.change_setting'
    fields = [
        # 'site',
        'icon_url', 'logo_url',
        'meta_keywords', 'description',

        'privacy_policy', 'tos', 'faq',
        'show_sidebar',

        'require_login', 'is_live', 'close_site_message'
    ]

    template_name = 'sitemgr/staff/setting/edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = self.tab

        return context

    def form_valid(self, form):
        success_url = '{}:{}_edit'.format(
            self.model._meta.app_label,
            self.model._meta.model_name)

        self.success_url = reverse_lazy(success_url, args=[self.object.pk])
        self.success_url = self.object.staff_edit_url

        return super().form_valid(form)

    def form_invalid(self, form):
        self.success_url = self.object.staff_edit_url
        return super().form_invalid(form)


class IndexSettingUpdateView(SettingUpdateView):
    tab = 'index'
    model = IndexSetting
    permission_required = 'sitemgr.change_setting'
    fields = [
        'name', 'title', 'template', 'video_url',
        'show_in_navbar', 'show_in_footer']
    template_name = 'sitemgr/staff/setting/edit-index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cover_form'] = IndexImageCreateForm
        return context


class UserSettingUpdateView(SettingUpdateView):
    tab = 'users'
    model = PostSetting
    permission_required = 'sitemgr.change_postsetting'
    fields = ['allow_user_to_post']


class IndexImageCreateView(Mixin, generic.CreateView):
    form_class = IndexImageCreateForm
    permission_required = 'sitemgr.change_setting'
    template_name = 'sitemgr/staff/setting/edit-index.html'

    def form_valid(self, form):

        obj = IndexImage.objects.create(
            setting=Site.objects.first().indexsetting,
            title=form.cleaned_data.get('title'),
            description=form.cleaned_data.get('description'),
            cta=form.cleaned_data.get('cta'),
            cta_url=form.cleaned_data.get('cta_url'))

        form.instance.object_id = obj.pk
        form.instance.content_object = obj
        form.instance.user = self.request.user

        form.save()

        url = self.request.POST.get('next')
        if not url:
            url = self.request.user.detail_url

        return HttpResponseRedirect(url)


class IndexImageDeleteView(Mixin, generic.DeleteView):
    model = IndexImage
    permission_required = 'sitemgr.delete_indeximage'
    success_url = reverse_lazy('sitemgr:staff_indexsetting_edit', args=[1])
    template_name = 'staff/components/confirm-delete.html'


class AboutSettingUpdateView(SettingUpdateView):
    tab = 'about'
    model = AboutSetting
    permission_required = 'sitemgr.change_setting'
    fields = [
        'name', 'about',
        'contact_email', 'show_contact_form',
        'show_in_navbar', 'show_in_footer',
        'patreon_url',
        'instagram_url', 'facebook_url',
        'pinterest_url', 'youtube_url',
    ]

    template_name = 'sitemgr/staff/setting/edit-index.html'


"""
SECTION
"""


class SectionMixin(Mixin):
    model = IndexSection
    template_name = 'sitemgr/staff/setting/edit-index.html'
    permission_required = 'sitemgr.change_indexsection'
    tab = None
    success_url = reverse_lazy('sitemgr:staff_indexsetting_edit', args=[1])


class SectionCreateView(SectionMixin, generic.CreateView):
    fields = ['name', 'columns_count', ]
    permission_required = 'sitemgr.add_indexsection'

    def form_valid(self, form):
        count = form.cleaned_data.get('columns_count')

        if count > 1:
            parent = form.save()

            for i in range(count):
                IndexSection.objects.create(
                    name=f'{i}', parent=parent)

            return HttpResponseRedirect(self.success_url)

        return super().form_valid(form)


class SectionUpdateView(SectionMixin, generic.UpdateView):
    permission_required = 'sitemgr.change_indexsection'
    fields = [
        'name',
        'title', 'text',
        'image_url', 'image_alt_text', 'cta', 'cta_url'
    ]

    def get_success_url(self):
        return super().get_success_url() + f'#pills-{self.object.pk}-tab'

    def form_invalid(self, form):
        messages.error(self.request, _('Something went wrong!'))
        return HttpResponseRedirect(self.success_url)


class SectionDeleteView(SectionMixin, generic.DeleteView):
    template_name = 'staff/components/confirm-delete.html'
    permission_required = 'sitemgr.delete_indexsection'
