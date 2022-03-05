
import logging

from django.contrib.sites.models import Site
from .mixins import SiteViewMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class SiteMgrMiddleware(SiteViewMixin):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):

        site = Site.objects.first()
        logger.debug(f'Processing site[{site.name}] template response')

        title = None
        meta_keywords = site.settings.meta_keywords
        meta_description = site.settings.description
        obj = response.context_data.get(
            'object', response.context_data.get('product'))

        filter_explicit = True
        try:
            if request.user.is_authenticated:
                filter_explicit = request.user.profile.filter_explicit_content
        except Exception as e:
            logger.error(f'{e}')

        if obj:
            if hasattr(obj, 'meta') and obj.meta:
                response.context_data['meta'] = obj.meta

            if hasattr(obj, 'title') and obj.title:
                title = f'{obj.title}'

            if hasattr(obj, 'meta_keywords') and obj.meta_keywords:
                meta_keywords = obj.meta_keywords

            if hasattr(obj, 'description') and obj.description:
                meta_description = obj.description

        if title:
            response.context_data['title'] = title

        response.context_data.update({
            'site': site,
            'meta_keywords': meta_keywords,
            'meta_description': meta_description,

            'visitor': self.visitor(request),
            'filter_explicit': filter_explicit,
            'is_live': False,
        })

        if hasattr(site, 'settings'):
            response.context_data.update({
                'is_live': site.settings.is_live,
            })
        return response


class StaffMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):
        from_settings = []

        for app in settings.INSTALLED_APPS:
            if 'django' not in app:
                _app = app.split('.')
                if len(_app) > 1:
                    from_settings.append(_app[1])
                else:
                    from_settings.append(app)

        response.context_data.update({
            'apps': from_settings,
        })
        return response
