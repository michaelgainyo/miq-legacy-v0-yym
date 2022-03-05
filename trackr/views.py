import json
from collections import Counter
from .utils import get_referrer, get_ip
from django.db.models.functions import (TruncMonth, TruncDay, TruncHour)

from django.http import Http404
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model

from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import (
    PermissionRequiredMixin, LoginRequiredMixin)

from sitemgr.utils import is_ajax

from .models import Hit, Path, TrackrSetting
from sitemgr.views import TemplateView

User = get_user_model()


class Mixin(LoginRequiredMixin, PermissionRequiredMixin):
    app_name = 'trackr'
    back = None
    tab = None
    success_url = reverse_lazy('trackr:path_list')
    permission_required = 'sitemgr.view_staff'
    model = None

    def form_valid(self, form):
        form.instance.user = self.request.user

        if hasattr(self, 'object') and self.object:
            self.success_url = self.object.staff_edit_url

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.model:
            context['model'] = self.model
            context['model_name'] = self.model._meta.model_name
            context['model_name_plural'] = self.model._meta.verbose_name_plural

        context.update({
            'tab': self.tab,
            'back': self.back,
            'app_name': self.app_name})

        return context

    def __init__(self, *args, **kwargs):

        try:
            self.form_class = self.get_form_class()
        except Exception:
            pass
        else:
            for field in iter(self.form_class.base_fields):
                self.form_class.base_fields[field].widget.attrs.update(
                    {'class': 'form-control'})

            self.fields = None

        finally:
            super().__init__(*args, **kwargs)


#
# ANALYTICS
#

class AnalyticsView(Mixin, TemplateView):
    tab = 'index'
    template_name = 'trackr/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        labels = [
            'January', 'February', 'March',
            'April', 'May', 'June',
            'July', 'August', 'September',
            'October', 'November', 'December']

        qs = Hit.objects
        data_range = self.request.GET.get('range', 'week')
        if data_range == 'today':
            query = qs.views().today()
            bot_qs = qs.bots().today()
        elif data_range == 'yesterday':
            query = qs.views().yesterday()
            bot_qs = qs.bots().yesterday()
        elif data_range == 'month':
            query = qs.views().last_30_days()
            bot_qs = qs.bots().last_30_days()
        elif data_range == 'year':
            query = qs.views().last_year()
            bot_qs = qs.bots().last_year()
        elif data_range == 'lifetime':
            query = qs.views()
            bot_qs = qs.bots()
        else:
            query = qs.views().last_7_days()
            bot_qs = qs.bots().last_7_days()

        labels, data = self.get_chart_data(query, data_range=data_range)
        prim_data = {
            'title': data_range.replace('_', ''),
            'labels': json.dumps(labels),
            'data': json.dumps(data),
        }

        _, data = self.get_chart_data(bot_qs, data_range=data_range)
        cross_data = {
            'labels': json.dumps(_),
            'data': json.dumps(data),
        }

        context['views'] = query
        context['data'] = prim_data
        context['cross_data'] = cross_data

        return context

    def get_chart_data(self, queryset, data_range='week'):

        if data_range == 'today' or data_range == 'yesterday':
            label = "%H %p"
            queryset = queryset.annotate(hour=TruncHour('created'))\
                .values_list('hour', flat=True)
        elif data_range == 'week' or data_range == 'month':
            label = "%a %d"
            queryset = queryset.annotate(day=TruncDay('created'))\
                .values_list('day', flat=True)
        elif data_range == 'year' or data_range == 'lifetime':
            label = "%b %y"
            queryset = queryset.annotate(month=TruncMonth('created'))\
                .values_list('month', flat=True)
        else:
            return [], []

        counter = Counter(queryset.order_by('created'))
        labels = [d.strftime(label) for d in counter.keys()]
        counts = list(counter.values())

        assert len(labels) == len(counts)
        return labels, counts


class TrackrSettingUpdateView(Mixin, generic.UpdateView):
    app_name = 'trackr'
    tab = 'setting'
    model = TrackrSetting
    permission_required = 'trackr.change_trackrsetting'
    fields = ['fb_pixel_id', 'ga_tracking_id', 'filter_bot']
    template_name = 'trackr/settings.html'


#
# PATHS
#

class PathListView(Mixin, generic.ListView):
    model = Path
    permission_required = 'trackr.view_path'
    template_name = 'trackr/staff/path/list.html'
    paginate_by = 12

    def post(self, request, *args, **kwargs):
        flt = request.POST.get('filter')
        if flt:
            filters = request.session.get('filters')
            if not filters:
                request.session['filters'] = []

            request.session.get('filters').append(flt)
            request.session.modified = True

        action = request.POST.get('delete')
        if action:
            request.session.get('filters').remove(action)
            request.session.modified = True

        return HttpResponseRedirect(request.path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self.request.session.get('filters')
        context['filters'] = filters

        if filters:
            qs = None
            qs1 = None
            hits = Hit.objects.views()
            if len(filters) > 0:
                qs = hits.by_path(filters[0])
                context['qs'] = qs
                context['count'] = hits.count()
            if len(filters) > 1 and qs:
                qs1 = hits.by_path(filters[1])\
                    .filter(session__in=set(qs.values_list('session', flat=True)))
                context['qs1'] = qs1
            if len(filters) > 2 and qs1:
                context['qs2'] = hits.by_path(filters[2])\
                    .filter(session__in=set(qs1.values_list('session', flat=True)))

        return context


class PathDetailView(Mixin, generic.ListView):
    model = Path
    template_name = 'trackr/staff/path/detail.html'
    permission_required = 'trackr.view_path'
    paginate_by = 100

    def get_queryset(self, *args, **kwargs):
        self.object = Path.objects.get(pk=self.kwargs.get('pk'))
        return self.object.get_manager().order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.object
        return context


class PathDeleteView(Mixin, generic.DeleteView):
    model = Path
    permission_required = 'trackr.delete_path'
    template_name = 'staff/components/confirm-delete.html'


class PathUpdateView(Mixin, generic.edit.UpdateView):
    model = Path
    app_name = 'trackr'
    fields = ['name', 'path']
    permission_required = 'trackr.change_path'
    template_name = 'trackr/staff/path/edit.html'


class PathCreateView(Mixin, generic.edit.CreateView):
    model = Path
    app_name = 'trackr'
    fields = ['name', 'path']
    permission_required = 'trackr.add_path'
    template_name = 'trackr/staff/path/edit.html'


"""
HITS
"""


class HitListView(PathListView):
    model = Hit
    paginate_by = 10
    queryset = Hit.objects.all()
    permission_required = 'trackr.view_hit'
    template_name = 'trackr/staff/hit/list.html'

    # Date window
    date = None

    # Search
    query = None
    x = None
    exact = None

    def dispatch(self, request, *args, **kwargs):
        print(self.request.GET.get('page'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if is_ajax(request):
            data = {'is_valid': False}
            q = request.GET.get('q')
            x = request.GET.get('x')
            exact = request.GET.get('exact', False) == 'true'
            qs = self._get_queryset(Hit.objects.views, q, x, exact, 'lifetime')
            if qs.exists():
                count = qs.count()
                qs = qs.all()[:200]
                data = {
                    'is_valid': True,
                    'q': q,
                    'x': x,
                    'exact': exact,
                    'qs': list(qs.values(
                        'updated', 'created', 'pk',
                        'ip', 'path', 'user_agent')),
                    'count': count,
                }

            return JsonResponse(data)
        return super().get(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        self.query = self.request.GET.get('q')
        self.x = self.request.GET.get('x')
        self.date = date = self.request.GET.get('range', 'lifetime')

        q = self.query.split(',')[0] if self.query else self.query
        x = self.x
        exact = self.exact = self.request.GET.get('exact', False)
        sort = self.request.GET.get('sort', '-updated')

        self.query = q if q != '' else None

        return self._get_queryset(
            Hit.objects.views, q, x, exact, date).order_by(sort)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.query
        context['x'] = self.x
        context['exact'] = self.exact
        context['range'] = self.date
        return context


class HitDetailView(Mixin, generic.detail.DetailView):
    template_name = 'trackr/staff/hit/detail.html'
    permission_required = 'trackr.view_hit'
    context_object_name = 'hit'
    model = Hit


class HitDeleteView(generic.DeleteView):
    model = Hit
    permission_required = 'trackr.delete_hit'


def hit_reditect_view(request, *arg, **kwargs):
    path = request.POST.get('path')
    if not path:
        raise Http404

    hit, is_new = Hit.objects.get_or_create(
        type='btn_click', path=path,
        ip=get_ip(request), referrer=get_referrer(request))
