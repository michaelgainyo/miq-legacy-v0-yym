
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from . import models

CustomUser = get_user_model()


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'username', 'first_name', 'signup_ip', 'last_login_ip', 'email'
    ]


admin.site.register(models.User, CustomUserAdmin)
admin.site.register(models.Profile)

admin.site.register(models.UserPost)
admin.site.register(models.View)
admin.site.register(models.Comment)
admin.site.register(models.IndexImage)

admin.site.register(models.Setting)
admin.site.register(models.IndexSetting)

admin.site.register(models.PostSetting)
admin.site.register(models.AboutSetting)
