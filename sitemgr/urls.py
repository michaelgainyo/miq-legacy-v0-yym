
from django.urls import path, include
from . import views

from .staff.urls import staffpatterns


app_name = 'sitemgr'


comments = [
    path(
        'create/',
        views.comment.CommentCreateView.as_view(), name='comment_create'),

    path(
        'delete/<int:pk>/',
        views.comment.CommentDeactivateView.as_view(),
        name='comment_deactivate'),
]

urlpatterns = [
    path('comments/', include((comments))),

    path('staff/', include((staffpatterns))),

    path('stat/', views.log_activity, name='log_status'),
    path('about/', views.pages.about.AboutView.as_view(), name='about'),
    path(
        'privacy-policy',
        views.pages.page.PrivacyView.as_view(), name='privacy'),
    path('tos', views.pages.page.TosView.as_view(), name='tos'),
    path('faq', views.pages.page.FaqView.as_view(), name='faq'),

    path('', views.pages.index.IndexView.as_view(), name='index'),

]
