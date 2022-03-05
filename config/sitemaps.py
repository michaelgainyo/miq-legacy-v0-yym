
from django.contrib.sitemaps import Sitemap

from blog.models import Article


class SiteMap(Sitemap):
    model = None
    filter = {}

    def items(self):
        if self.model is not None:
            return self.model.objects.all()

    def lastmod(self, obj):
        return obj.updated


class Blog(SiteMap):
    changefreq = 'monthly'

    def items(self):
        return Article.published.all()


sitemaps = {'blog': Blog}
