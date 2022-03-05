
import logging
from django.template.loader import get_template

from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.views import generic

from django.contrib.auth.mixins import (
    PermissionRequiredMixin)

from config.utils import get_model

from trackr.utils import get_referrer

from ..mixins import StaffMixin

logger = logging.getLogger(__name__)


class Mixin(StaffMixin):
    type = None
    app_name = None
    _back = None
    img_form = None

    @property
    def back(self):
        back = get_referrer(self.request)
        if back != self._back:
            self._back = back
        return self._back

    def dispatch(self, request, *args, **kwargs):

        if not self.app_name:
            self.app_name = self.kwargs.pop('app_name', None)

        app_model = self.kwargs.pop('app_model', None)

        if self.app_name:
            try:
                self.model = get_model(self.app_name, app_model)

            except Exception as e:
                logger.debug(e, exc_info=1)

        if not self.template_name:
            self.get_template(self.type)

        return super().dispatch(request, *args, **kwargs)

    def get_template(self, name):
        name = name or self.type
        if not name:
            return

        logger.info(f'getting template {name}')

        try:
            template_name = f'{self.app_name}/staff/'
            template_name += f'{self.model._meta.model_name}/{name}.html'

            get_template(template_name)
        except Exception as e:
            logger.error(f'getting template {template_name}\n{e}', exc_info=1)

            try:
                template_name = f'{self.app_name}/staff/{name}.html'
                get_template(template_name)

            except Exception as e:
                logger.error(
                    f'getting template {template_name}\n{e}', exc_info=1)
                self.template_name = f'staff/{name}.html'

            else:
                self.template_name = template_name

        else:
            self.template_name = template_name

        logger.info(f'got template {self.template_name}')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model = self.model
        context.update({
            'back': self.back,
            'model': self.model,
            'model_name': model._meta.model_name,
            'model_name_plural': model._meta.verbose_name_plural,
            'app_name': self.app_name})

        if self.img_form:
            context['img_form'] = self.img_form

        return context


class EditMixin(Mixin, PermissionRequiredMixin):
    type = 'edit'


class ListView(Mixin, ListView):
    type = 'list'
    paginate_by = 12

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)

        if hasattr(self.model, 'user'):
            queryset = queryset.filter(user=self.request.user)

        return queryset


class DetailView(Mixin, DetailView):
    type = 'detail'


class CreateView(EditMixin, generic.edit.CreateView):
    type = 'edit'
    permission_required = 'blog.add_article'


class UpdateView(EditMixin, generic.edit.UpdateView):
    type = 'edit'
    permission_required = 'blog.change_article'


class DeleteView(EditMixin, generic.edit.DeleteView):
    type = 'delete'
    template_name = 'staff/components/confirm-delete.html'
    permission_required = 'blog.delete_article'


class TemplateView(Mixin, generic.base.TemplateView):
    pass
