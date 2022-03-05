from django.urls import path, include

from . import views
from .staff.urls import staffpatterns

app_name = 'filemgr'

images = [
    path('upload/', views.ImageUploadView.as_view(), name='img_upload'),
]

urlpatterns = [
    path('image/', include((images))),
    path('staff/', include((staffpatterns))),
]
