from django.contrib import admin

from .models import Image, FileSetting, Gallery, GalleryImage


admin.site.register(Image)
admin.site.register(Gallery)
admin.site.register(GalleryImage)
admin.site.register(FileSetting)
