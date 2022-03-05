
from django.urls import path, include

from .staff.urls import staffpatterns
from . import views

app_name = 'blog'

articles = [
    path(
        '<slug:category__slug>/<slug:slug>',
        views.ArticleView.as_view(), name='article'),

    path('', views.ArticlesView.as_view(), name='articles'),
]

category = [

    path(
        '<slug:slug>/',
        views.CategoryView.as_view(), name='category'),
]

urlpatterns = [
    path('articles/', include((articles))),
    path('articles/', include((category))),

    path('staff/blog/', include((staffpatterns))),

]
