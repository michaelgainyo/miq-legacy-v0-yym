from django.contrib import admin

from .models import Hit, Path, TrackrSetting, Campaign

admin.site.register(Hit)
admin.site.register(Path)
admin.site.register(Campaign)
admin.site.register(TrackrSetting)



