
from django.views.generic import TemplateView

from ..mixins import StaffMixin


class IndexView(StaffMixin, TemplateView):
    template_name = 'staff/index.html'






