
from django.urls import path, include
from . import views

app_name = 'trackr'

analytics = [
    path(
        'settings/<int:pk>/',
        views.TrackrSettingUpdateView.as_view(),
        name='staff_trackrsetting_edit'),

    path('', views.AnalyticsView.as_view(), name='staff_index'),
]

hits = [
    path('hits/', views.HitListView.as_view(), name='hit_list'),

    path(
        'hit/<int:pk>/',
        views.HitDetailView.as_view(), name='hit_detail'),

    path(
        'hit/delete/<int:pk>/',
        views.HitDeleteView.as_view(), name='hit_delete'),
]

paths = [

    path('paths/', views.PathListView.as_view(), name='path_list'),

    path(
        'path/<int:pk>/',
        views.PathDetailView.as_view(), name='path_detail'),

    path(
        'path/create/',
        views.PathCreateView.as_view(), name='path_create'),

    path(
        'path/edit/<int:pk>/',
        views.PathUpdateView.as_view(), name='path_edit'),

    path(
        'path/delete/<int:pk>/',
        views.PathDeleteView.as_view(), name='path_delete'),
]

urlpatterns = [
    path('staff/analytics/', include((analytics))),
    path('staff/analytics/', include((hits))),
    path('staff/analytics/', include((paths))),
]






