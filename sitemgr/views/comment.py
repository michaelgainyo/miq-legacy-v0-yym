
import logging
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from config.utils import get_model
from sitemgr.utils import is_ajax

from ..models import Comment
from ..forms import CommentAddForm

from . import generic


logger = logging.getLogger(__name__)


class Mixin(LoginRequiredMixin):
    model = Comment


class CommentCreateView(Mixin, generic.CreateView):
    form_class = CommentAddForm
    template_name = 'sitemgr/account/articles.html'

    def form_valid(self, form):

        model = self.request.POST.get('model')
        app = self.request.POST.get('app')
        pk = self.request.POST.get('pk')
        ppk = self.request.POST.get('ppk')
        url = self.request.POST.get('next')

        if model and pk and app:
            obj = get_model(app, model).objects.get(pk=pk)

            form.instance.user = self.request.user
            form.instance.object_id = pk
            form.instance.content_object = obj

            if ppk:
                parent = Comment.objects.filter(pk=ppk)
                if parent.exists():
                    form.instance.parent = parent.first()

            if not url:
                url = obj.detail_url

            self.success_url = url

            if is_ajax(self.request):
                comment = form.save()
                return JsonResponse({
                    'is_valid': True, 'pk': comment.pk,
                    'obj_pk': comment.content_object.pk,
                    'user_url': comment.user.profile.image.thumbnail.url,
                    'usr_detail_url': comment.user.profile.detail_url,
                    'username': comment.user.username,
                    'body': comment.render_body,
                    'count': comment.content_object.comments.count()
                })

            return super().form_valid(form)

        return redirect(self.success_url)


class CommentDeactivateView(Mixin, generic.UpdateView):
    fields = ['active']
    template_name = 'sitemgr/comment.html'

    def form_valid(self, form):
        if self.request.user == self.object.user or\
                self.request.user == self.object.content_object.user\
                or self.request.user.is_superuser:

            form.instance.active = False
            # TODO CHILDREN

            if is_ajax(self.request):
                comment = form.save()
                return JsonResponse({
                    'is_valid': True,
                    'obj_pk': comment.content_object.pk,
                    'count': comment.content_object.comments.count()
                })

            self.success_url = self.request.POST.get(
                'next', self.object.content_object.detail_url)
            return super().form_valid(form)

        return self.form_invalid(form)

    def form_invalid(self, form):
        print(self.request.POST)
        return redirect(self.object.content_object.detail_url)
