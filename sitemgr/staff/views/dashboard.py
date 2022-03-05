import logging

from django.db.models.functions import TruncHour

from sitemgr.views import generic
from collections import Counter

from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect

from django.contrib.auth.mixins import (
    PermissionRequiredMixin, LoginRequiredMixin)


logger = logging.getLogger(__name__)
User = get_user_model()


class Mixin(LoginRequiredMixin, PermissionRequiredMixin):
    app_name = 'sitemgr'
    model = None


class DashboardView(Mixin, generic.TemplateView):
    template_name = 'sitemgr/staff/dashboard.html'
    permission_required = 'sitemgr.view_staff'

    def get_chart_data(self, queryset):
        queryset = queryset.annotate(hour=TruncHour('created'))\
            .values_list('hour', flat=True)

        counter = Counter(queryset.order_by('created'))
        labels = [d.strftime("%H %p") for d in counter.keys()]
        counts = list(counter.values())

        assert len(labels) == len(counts)
        return labels, counts

    def get_context_data(self, **kwargs):
        from trackr.models import Hit

        context = super().get_context_data(**kwargs)
        context['todo_list'] = self.request.session.get('todo')

        hits = Hit.objects.views()
        today = hits.today()
        yesterday = hits.yesterday()

        labels, counts = self.get_chart_data(today)
        _, cross_counts = self.get_chart_data(yesterday)
        if not labels:
            labels = _ or []

        data = {
            'labels': labels, 'today': counts, 'yesterday': cross_counts
        }

        context.update({
            'hits': hits,
            'today': today,
            'yesterday': yesterday,
            'chart_data': data
        })

        return context

    def post(self, request, *args, **kwargs):
        if request.session.get('todo', None) is None:
            request.session['todo'] = []

        data = request.POST
        action = data.get('action')
        if action == 'delete':
            pk = data.get('pk')
            del request.session['todo'][int(pk)]

        item = data.get('item')
        if item:
            request.session['todo'].append(item)

        request.session.save()
        return HttpResponseRedirect(request.path_info)
