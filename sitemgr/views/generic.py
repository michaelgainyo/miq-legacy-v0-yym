import logging

from django.views import generic

from sitemgr.mixins import SiteViewMixin


logger = logging.getLogger(__name__)


__all__ = [
    'ListView', 'DetailView',
    'TemplateView', 'View',
    'FormView', 'CreateView', 'UpdateView', 'DeleteView'
]


class ListView(SiteViewMixin, generic.list.ListView):
    pass


class DetailView(SiteViewMixin, generic.detail.DetailView):
    pass


class TemplateView(SiteViewMixin, generic.TemplateView):
    pass


class View(SiteViewMixin, generic.View):
    pass


class FormView(SiteViewMixin, generic.edit.FormView):
    pass


class CreateView(SiteViewMixin, generic.edit.CreateView):
    pass


class UpdateView(SiteViewMixin, generic.edit.UpdateView):
    pass


class DeleteView(SiteViewMixin, generic.edit.DeleteView):
    pass






































