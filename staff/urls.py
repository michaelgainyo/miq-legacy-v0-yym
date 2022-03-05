
from django.urls import path

from .views import crud, index

app_name = 'staff'

urlpatterns = [
    path(
        '<str:app_name>/<str:app_model>/all/',
        crud.ListView.as_view(), name='list'),

    path(
        '<str:app_name>/<str:app_model>/<int:pk>/',
        crud.DetailView.as_view(), name='detail'),

    path(
        '<str:app_name>/<str:app_model>/edit/<int:pk>/',
        crud.UpdateView.as_view(), name='edit'),

    path('', index.IndexView.as_view(), name='index'),
]
