import logging

from django.template.loader import render_to_string
from django.template import Context, Template
from django.contrib.auth import get_user_model


from django.core.exceptions import PermissionDenied


logger = logging.getLogger(__name__)
User = get_user_model()


class SiteViewMixin(object):

    def __init__(self, *args, **kwargs):
        if hasattr(self, 'form_class') and not self.form_class:
            self.form_class = self.get_form_class()
            for field in iter(self.form_class.base_fields):
                self.form_class.base_fields[field].widget.attrs.update(
                    {'class': 'form-control'})

        self.fields = None
        super().__init__(*args, **kwargs)

    def visitor(self, request=None):
        request = getattr(self, 'request', request)

        if request.user.is_authenticated:
            uuid = request.user.uuid
        else:
            uuid = request.session.get('uuid')

        logger.debug(f'visitor uuid: {uuid}')

        try:
            if uuid:
                return User.objects.get(uuid=uuid)
        except LookupError:
            pass


class GroupRequiredMixin(object):
    """
        group_required - list of strings, required param
    """

    group_required = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        else:
            user_groups = []
            for group in request.user.groups.values_list('name', flat=True):
                user_groups.append(group)

            count = len(set(user_groups).intersection(self.group_required))
            if not request.user.is_superuser and count <= 0:
                raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class ObjectRenderMixin(object):
    def render(self, template_name, context={}):
        # context.update(site_dict)

        if '.html' in template_name:
            return render_to_string(template_name, context)

        t = Template(str(template_name))
        return t.render(Context(context))

    def staff_btn(self, url, text, **kwargs):
        style_class = 'btn-0 btn btn-sm'

        return self.render(
            f'<a class="{style_class}" href="{url}">{text}</a>', {})

    def staff_detail_btn(self, *args, **kwargs):
        return self.staff_btn(self.staff_detail_url, 'detail')

    def staff_edit_btn(self, *args, **kwargs):
        return self.staff_btn(
            self.staff_edit_url, f'edit {self._meta.model_name}')


#
