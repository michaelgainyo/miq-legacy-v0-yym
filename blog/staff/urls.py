

from django.urls import path
from . import views


staffpatterns = [
    path(
        'articles/',
        views.ArticleListView.as_view(), name='article_list'),

    path(
        'article/create/',
        views.ArticleCreateView.as_view(), name='article_create'),

    path(
        'article/<int:pk>/',
        views.ArticleDetailView.as_view(), name='staff_article_detail'),

    path(
        'article/edit/<int:pk>/',
        views.ArticleUpdateView.as_view(), name='article_edit'),

    path(
        'article/edit-html/<int:pk>/',
        views.ArticleHtmlView.as_view(), name='article_edit_html'),

    path(
        'article/images/<int:pk>/',
        views.ArticleImageUploadView.as_view(), name='article_images'),

    path(
        'article/slideshow/<int:pk>/',
        views.ArticleSlidesUploadView.as_view(),
        name='staff_article_slideshow'),

    path(
        'article/delete/<int:pk>/',
        views.ArticleDeleteView.as_view(), name='article_delete'),

]

staffpatterns += [
    path(
        'categories/',
        views.CategoryListView.as_view(), name='category_list'),

    path(
        'category/create/',
        views.CategoryCreateView.as_view(), name='category_create'),

    path(
        'category/edit/<int:pk>/',
        views.CategoryUpdateView.as_view(), name='category_edit'),

    path(
        'category/delete/<int:pk>/',
        views.CategoryDeleteView.as_view(), name='category_delete'),

]





