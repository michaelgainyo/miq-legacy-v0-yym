
import logging
import json
from collections import Counter

from django.db.models.functions import TruncMonth

from django.views import generic
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, LoginRequiredMixin)
from django.utils.translation import gettext_lazy as _

from filemgr.forms import ImageUpdateForm
from config.mixins import BootstrapModelFormMixin
from django.http import JsonResponse

from django.contrib.auth import get_user_model

from blog.models import Article
from filemgr.models import GalleryImage
from filemgr.staff.forms import GalleryImageCreateForm
from sitemgr.utils import is_ajax

logger = logging.getLogger(__name__)

__all__ = [
    'ArticleListView', 'ArticleCreateView', 'ArticleDetailView',
    'ArticleUpdateView', 'ArticleImageUploadView', 'ArticleSlidesUploadView',
    'ArticleHtmlView', 'ArticleDeleteView']

User = get_user_model()


class Mixin(LoginRequiredMixin, PermissionRequiredMixin):
    tab = 'home'
    app_name = 'blog'
    model = Article
    filter_by_user = False

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)

        if not self.request.user.is_superuser:
            if self.filter_by_user:
                qs = qs.filter(user=self.request.user)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'tab': self.tab,
            'img_update_form': ImageUpdateForm(self.request.POST or None),
            'model': self.model,
            'model_name': self.model._meta.model_name,
            'model_name_plural': self.model._meta.verbose_name_plural,
            'app_name': self.app_name})

        return context


class EditMixin(Mixin):
    update_user = False
    is_new = False
    template_name = 'blog/staff/article/edit.html'
    fields = [
        'category', 'title', 'description', 'video_url',
        'artists', 'is_explicit'
    ]

    def __init__(self, *args, **kwargs):

        try:
            self.form_class = self.get_form_class()
        except Exception:
            pass
        else:
            for field in iter(self.form_class.base_fields):
                self.form_class.base_fields[field].widget.attrs.update(
                    {'class': 'form-control'})

            self.fields = None

        finally:
            super().__init__(*args, **kwargs)

    def get_success_url(self, *args, **kwargs):

        if self.tab == 'html':
            self.success_url = self.object.staff_html_url

        if not self.success_url:
            return reverse_lazy('blog:article_edit', args=[self.object.id])

        return super().get_success_url(*args, **kwargs)

    def form_valid(self, form):

        from django.template.defaultfilters import slugify

        slug = slugify(self.request.POST.get('title'))
        article = Article.objects.filter(slug=slug)

        if article.exists() and self.is_new:
            messages.error(
                self.request,
                _('This title is already taken. '
                  'Please change the title'))

            return self.form_invalid(form)

        if self.update_user:
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.save()

        form.instance.feature = self.request.POST.get('is_featured', False)
        form.instance.publish = self.request.POST.get('is_published', False)

        return super().form_valid(form)

    def form_invalid(self, form):
        from pprint import pprint

        pprint(self.request.POST)

        return super().form_invalid(form)


class ArticleListView(Mixin, generic.ListView):
    permission_required = 'blog.view_article'
    template_name = 'blog/staff/article/list.html'
    paginate_by = 12
    filter_by_user = True

    class ArticleQuickCreateForm(BootstrapModelFormMixin):
        class Meta:
            model = Article
            fields = ('category', 'title')

    form_class = ArticleQuickCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articleform'] = self.form_class
        return context


class ArticleDetailView(Mixin, generic.DetailView):
    permission_required = 'blog.view_article'
    template_name = 'blog/staff/article/detail.html'

    def get_chart(self, queryset):
        """
        Hits per month
        Returns a tuple (labels, hits_count)
        """

        counter = Counter(queryset)
        labels = [d.strftime("%b %y") for d in counter.keys()]
        hits_count = list(counter.values())

        assert len(labels) == len(hits_count)
        return json.dumps(labels), json.dumps(hits_count)

    def get_context_data(self, **kwargs):
        from trackr.models import Hit

        context = super().get_context_data(**kwargs)

        views = self.object.views

        by_month = views.annotate(month=TruncMonth('created'))\
            .values_list('month', flat=True).order_by('created')
        labels, hits_count = self.get_chart(by_month)

        by_bots = Hit.objects.bots()\
            .by_path(self.object.detail_url)\
            .annotate(month=TruncMonth('created'))\
            .values_list('month', flat=True).order_by('created')
        _, bot_hits_count = self.get_chart(by_bots)

        context['tab'] = 'insight'
        context['articles'] = Article.objects.all

        context['data'] = {
            'labels': labels,
            'hits_count': hits_count,
            'bot_hits_count': bot_hits_count,
        }
        return context


class ArticleCreateView(EditMixin, generic.edit.CreateView):
    update_user = True
    permission_required = 'blog.add_article'


class ArticleUpdateView(EditMixin, generic.edit.UpdateView):
    is_new = False
    permission_required = 'blog.change_article'
    fields = [
        'category', 'gallery_layout', 'title', 'slug', 'description',
        'video_url', 'text_first', 'is_explicit',
    ]

    def dispatch(self, request, *args, **kwargs):

        if is_ajax(request):
            data = {'is_valid': False}
            obj = self.get_object()

            if request.method == 'POST':
                uid = request.POST.get('uid')
                action = request.POST.get('action')

                if not uid or not action:
                    return JsonResponse(data)

                usr = User.objects.filter(pk=uid)
                if action == 'add-uid' and usr.exists():
                    usr = usr.first()
                    obj.artists.add(usr)
                    data = {
                        'is_valid': True, 'pk': usr.pk,
                        'img': usr.profile.image.thumbnail.url,
                        'username': usr.username
                    }
                elif action == 'rem-uid' and usr.exists():
                    usr = usr.first()
                    obj.artists.remove(usr)
                    data = {
                        'is_valid': True,
                        'pk': usr.pk,
                        'username': usr.username
                    }

                return JsonResponse(data)

            if request.method == 'GET':

                q = request.GET.get('q')
                if q:
                    qs = User.objects.exclude(
                        pk__in=obj.artists.all())\
                        .filter(username__icontains=q, is_active=True)[:10]

                    data = {
                        'is_valid': True,
                        'qs': list(qs.values(
                            'username', 'profile__image__thumbnail', 'pk'))
                    }

                return JsonResponse(data, safe=False)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.all
        return context


class ArticleImageUploadView(ArticleUpdateView):
    tab = 'images'
    fields = ['gallery_layout']
    template_name = 'blog/staff/article/edit-images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.request.GET.get('img')
        if pk:
            context['selected'] = self.object.images.filter(pk=pk).first()

        return context


class ArticleSlidesUploadView(ArticleUpdateView):
    tab = 'slideshow'
    fields = ['gallery_layout']
    template_name = 'blog/staff/article/edit-slideshow.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.request.GET.get('img')
        if pk:
            context['selected'] = GalleryImage.objects.get(pk=pk)

        context['imageform'] = GalleryImageCreateForm
        return context


class ArticleHtmlView(ArticleUpdateView):
    tab = 'html'
    fields = ['html']


class ArticleDeleteView(Mixin, generic.DeleteView):
    permission_required = 'blog.delete_article'
    success_url = reverse_lazy('blog:article_list')
    template_name = 'staff/components/confirm-delete.html'
