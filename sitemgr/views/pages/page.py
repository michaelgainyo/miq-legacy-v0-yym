
from sitemgr import views


__all__ = ['PrivacyView', 'TosView', 'FaqView']


class PrivacyView(views.TemplateView):
    template_name = 'sitemgr/pages/privacy.html'


class TosView(views.TemplateView):
    template_name = 'sitemgr/pages/tos.html'


class FaqView(views.TemplateView):
    template_name = 'sitemgr/pages/faq.html'
