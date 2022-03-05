
from django.urls import path
from . import views


staffpatterns = [

    path(
        'setting/edit/<int:pk>/',
        views.SettingUpdateView.as_view(), name='staff_setting_edit'),

    path(
        'setting/edit/<int:pk>/index/',
        views.IndexSettingUpdateView.as_view(),
        name='staff_indexsetting_edit'),

    path(
        'setting/edit/<int:pk>/about/',
        views.AboutSettingUpdateView.as_view(),
        name='staff_aboutsetting_edit'),

    path(
        'setting/edit/<int:pk>/users/',
        views.UserSettingUpdateView.as_view(),
        name='staff_postsetting_edit'),

    path(
        'setting/cover/add/',
        views.IndexImageCreateView.as_view(), name='staff_indeximage_add'),

    path(
        'setting/cover/delete/<int:pk>/',
        views.IndexImageDeleteView.as_view(), name='staff_indeximage_delete'),
]

staffpatterns += [
    path(
        'user/comments/',
        views.UserCommentReviewView.as_view(), name='staff_comment_review'),

    path(
        'user/posts/',
        views.UserPostsView.as_view(), name='staff_userposts'),

    path(
        'user/post/deleted/',
        views.UserPostsDeletedView.as_view(), name='staff_userpost_deleted'),

    path(
        'user/post/review/',
        views.UserPostReviewView.as_view(), name='staff_userpost_review'),
]

staffpatterns += [
    path(
        'setting/index-section/add/',
        views.SectionCreateView.as_view(), name='staff_section_create'),

    path(
        'setting/index-section/edit/<int:pk>/',
        views.SectionUpdateView.as_view(), name='staff_section_edit'),

    path(
        'setting/index-section/delete/<int:pk>/',
        views.SectionDeleteView.as_view(), name='staff_section_delete'),

]

staffpatterns += [
    path('', views.DashboardView.as_view(), name='staff_dashboard')
]
