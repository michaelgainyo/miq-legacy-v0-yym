from django.urls import path
from . import views


staffpatterns = [

    path(
        'images/',
        views.ImageListView.as_view(), name='staff_img_list'),

    path(
        'image/edit/<int:pk>/',
        views.ImgUpdateView.as_view(), name='staff_img_update'),

    path(
        'image/delete/<int:pk>/',
        views.ImageDeleteView.as_view(), name='staff_img_delete'),

]

staffpatterns += [
    path(
        'gallery-img/',
        views.GalleryImageCreateView.as_view(), name='staff_gimg_create'),

    path(
        'gallery-image/edit/<int:pk>/',
        views.GalleryImageUpdateView.as_view(), name='staff_gimg_update'),

    path(
        'gallery-image/delete/<int:pk>/',
        views.GalleryImageDeleteView.as_view(), name='staff_gimg_delete'),
]

staffpatterns += [
    path(
        'galleries/',
        views.FileListView.as_view(), name='files'),

    path(
        'gallery/add/',
        views.GalleryCreateView.as_view(), name='staff_gallery_create'),

    path(
        'gallery/edit/<int:pk>/',
        views.GalleryUpdateView.as_view(), name='staff_gallery_edit'),

    path(
        'gallery/delete/<int:pk>/',
        views.GalleryDeleteView.as_view(), name='staff_gallery_delete'),
]

staffpatterns += [
    path(
        'files/',
        views.FileListView.as_view(), name='files'),

    path(
        'file/upload/',
        views.FileUploadView.as_view(), name='file_upload'),

    path(
        'file/edit/<int:pk>/',
        views.FileUpdateView.as_view(), name='file_edit'),

    path(
        'file/delete/<int:pk>/',
        views.FileDeleteView.as_view(), name='file_delete'),
]


staffpatterns += [
    path(
        'setting/edit/<int:pk>/file/',
        views.FileSettingUpdateView.as_view(), name='setting_edit'),
]
