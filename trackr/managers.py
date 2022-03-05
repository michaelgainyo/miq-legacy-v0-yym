
import logging
import datetime
from datetime import date

from django.db import models
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site


__all__ = ['ViewsManager']
User = get_user_model()
logger = logging.getLogger(__name__)


class ViewsManagerMixin(object):

    @property
    def sessions(self):
        return self.get_queryset().values_list('session', flat=True)

    def from_index(self):
        return self.get_queryset().filter(
            referrer__iexact=str(reverse_lazy('index_view'))).distinct()

    def direct(self):
        return self.get_queryset().filter(referrer__isnull=True)

    def from_instagram(self):
        return self.from_source('instagram')

    def from_facebook(self):
        return self.get_queryset()\
            .filter(
                Q(referrer__icontains='fb') |
                Q(referrer__icontains='facebook') |
                Q(user_agent__icontains='fb') |
                Q(user_agent__icontains='facebook'))\
            .distinct()

    def from_google(self):
        return self.from_source('google')

    def from_googleads(self):
        return self.from_source('ads.google.com')

    def from_pinterest(self):
        return self.from_source('pinterest')

    def from_source(self, source):
        assert type(source) == str
        return self.filter(
            Q(referrer__icontains=source) |
            Q(user_agent__icontains=source)).distinct()

    # DATE & TIME

    def today(self):
        return self.get_queryset().today()

    def yesterday(self):
        return self.get_queryset().yesterday()

    def last_7_days(self):
        return self.get_queryset().last_7_days()

    def last_14_days(self):
        return self.get_queryset().last_14_days()

    def last_30_days(self):
        # 1 month
        return self.get_queryset().last_30_days()

    def last_90_days(self):
        # 3 months
        return self.get_queryset().last_90_days()

    def last_180_days(self):
        # 6 months
        return self.get_queryset().last_180_days()

    def last_year(self):
        return self.get_queryset().last_year()

    # GENERAL

    def views(self, *args, **kwargs):
        return self.get_queryset().views()

    def bots(self, *args, **kwargs):
        return self.get_queryset().bots()


class ViewsQuerySet(models.QuerySet):

    def sessions_by_referrers(self, count=100):
        site = Site.objects.first()

        qs = self.exclude(referrer='unknown')\
            .exclude(referrer='').values('referrer')\
            .annotate(sessions_count=Count('session'))\
            .exclude(referrer__startswith='/')\
            .order_by('-sessions_count')

        if site:
            qs = qs.exclude(referrer__icontains=f'{site.domain}')
        return qs[:count]

    def sessions_by_landing_pages(self, count=10):
        return self.values('path')\
            .annotate(sessions_count=Count('session'))\
            .order_by('-sessions_count')[:count]

    # FIELDS, REFERRER, PATH

    def by_path(self, path):
        """ Filter queryset based on given path """

        return self.by_field('path__icontains', path)

    def by_referrer(self, referrer):
        """ Filter queryset based on given referrer """
        return self.by_field('referrer__icontains', referrer)

    def by_field(self, field_name__condition, value):
        """ Filter queryset based on given field name, condition and value """

        error_message = f"This must be a string: {field_name__condition}"
        assert type(field_name__condition) is str, error_message

        field_query = {f'{field_name__condition}': value}
        return self.filter(**field_query)

    # DATES & TIMES

    def today(self):
        today = date.today()
        return self.filter(
            created__day=today.day, created__year=today.year,
            created__month=today.month).order_by('-created')

    def yesterday(self):
        yst = date.today() - datetime.timedelta(1)
        return self.filter(
            created__day=yst.day, created__year=yst.year,
            created__month=yst.month).order_by('-created')

    def last_7_days(self):
        return self.get_last_n_days(7)

    def last_14_days(self):
        return self.get_last_n_days(14)

    def last_30_days(self):
        return self.get_last_n_days(30)

    def last_90_days(self):
        return self.get_last_n_days(90)

    def last_180_days(self):
        return self.get_last_n_days(180)

    def last_year(self):
        return self.get_last_n_days(365)

    def get_last_n_days(self, days_count):
        day = date.today() - datetime.timedelta(days=days_count)
        return self.filter(
            created__day__gte=day.day, created__year__gte=day.year,
            created__month__gte=day.month).order_by('-created')

    def views(self, *args, **kwargs):
        """
        Return all hit entries except when bots are filtered
        from trackr settings, in which case it would filter out
        all know bots (is_bot == True)
        """

        site = Site.objects.first()
        qs = self.exclude(path__iexact='/stat/')
        if site and site.trackrsetting\
                and site.trackrsetting.filter_bot is True:
            return qs.exclude(is_bot=True)

        return qs

    def bots(self, *args, **kwargs):
        return self.filter(is_bot=True)


class ViewsManager(models.Manager, ViewsManagerMixin):

    def get_queryset(self, *args, **kwargs):
        return ViewsQuerySet(self.model, using=self._db)
