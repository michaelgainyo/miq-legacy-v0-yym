

from django.contrib.sites.models import Site

from sitemgr import views


class IndexView(views.DetailView):
    template_name = 'sitemgr/pages/index.html'

    def get_object(self, *args, **kwargs):
        return Site.objects.first().indexsetting
