import logging

from sitemgr.views import generic
from django.http import HttpResponseRedirect

from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, LoginRequiredMixin)

from sitemgr.models import UserPost, Comment


logger = logging.getLogger(__name__)
__all__ = [
    'UserPostReviewView', 'UserPostsView', 'UserPostsDeletedView',
    'UserCommentReviewView'
]


class Mixin(LoginRequiredMixin, PermissionRequiredMixin):
    model = UserPost
    tab = 'pending'
    permission_required = 'sitemgr.view_staff'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tab'] = self.tab
        return context


class UserPostReviewView(Mixin, MultipleObjectMixin, generic.TemplateView):
    paginate_by = 12
    object_list = UserPost.staff.filter(
        is_active=False, was_deleted_by_user=False).order_by('created')
    ordering = ('-created',)
    context_object_name = 'posts'
    permission_required = 'sitemgr.change_userpost'
    success_url = reverse_lazy('sitemgr:staff_userpost_review')

    template_name = 'sitemgr/staff/userpost/edit.html'

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action', 'update')
        pk = request.POST.get('pk')
        userpost = UserPost.staff.get(pk=pk)

        if action == 'update':
            userpost.is_active = request.POST.get('is_active', False)

            is_explicit = request.POST.get('is_explicit', False)
            if not userpost.is_explicit == is_explicit:
                userpost.is_explicit = is_explicit

            userpost.save()

            if not userpost.is_explicit == userpost.image.is_explicit:
                userpost.image.is_explicit = userpost.is_explicit
                userpost.image.save()

        elif action == 'delete':
            userpost.delete()

        self.success_url = request.POST.get('next', self.success_url)
        return HttpResponseRedirect(self.success_url)


class UserPostsDeletedView(UserPostReviewView):
    tab = 'deleted'
    object_list = object_list = UserPost.staff.filter(was_deleted_by_user=True)
    success_url = reverse_lazy('sitemgr:staff_userposts_deleted')


class UserPostsView(UserPostReviewView):
    tab = 'all'
    object_list = UserPost.staff.all()
    success_url = reverse_lazy('sitemgr:staff_userposts')


class UserCommentReviewView(UserPostReviewView):
    paginate_by = 100
    object_list = Comment.objects.all()
    context_object_name = 'comments'
    permission_required = 'sitemgr.change_comment'
    success_url = reverse_lazy('sitemgr:staff_comment_review')
    template_name = 'sitemgr/staff/comment/edit.html'
