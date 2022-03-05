
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.conf.urls.i18n import i18n_patterns

from .sitemaps import sitemaps

# I18N
urlpatterns = [path('i18n/', include('django.conf.urls.i18n'))]

# APPS
urlpatterns += i18n_patterns(

    path('admin/', admin.site.urls),
    path('accounts/', include('sitemgr.accounts.urls', namespace="accounts")),

    # blog
    path('', include('blog.urls', namespace="blog")),

    # trackr
    path('', include('trackr.urls', namespace="analytics")),
    prefix_default_language=False

)

# ESSENTIALS
urlpatterns += i18n_patterns(
    path('', include('sitemgr.urls', namespace="sitemgr")),
    path('', include('filemgr.urls', namespace="filemgr")),
    prefix_default_language=False
)

urlpatterns += [
    path(
        'sitemap.xml', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),

    path('robots.txt', TemplateView.as_view(
        template_name="robots.txt",
        content_type="text/plain"), name="robots_file"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
