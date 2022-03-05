
import logging
import datetime
from datetime import date
from pprint import pprint
from collections import Counter

from django.db.models.functions import (
    TruncDate, TruncDay, TruncHour, TruncMonth)

# from django.db import models
# from django.db.models import Q, Count
# from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from trackr.models import Hit


class AnalyticsModelMixin(object):

    def top_referrings(self, count=10) -> list:
        return Counter(self.referrings.values_list('path', flat=True))\
            .most_common(count)

    def top_referrers(self, count=10) -> list:
        return Counter(self.referrers.values_list('referrer', flat=True))\
            .most_common(count)

    @property
    def referrings(self):
        return Hit.objects.views().by_referrer(self.detail_url)

    @property
    def referrers(self):
        return self.views.exclude(referrer__icontains=self.detail_url)

    @property
    def today(self):
        return self.views.today()

    @property
    def yesterday(self):
        return self.views.yesterday()

    @property
    def last_7_days(self):
        return self.views.last_7_days()

    @property
    def views(self):
        return Hit.objects.views().by_path(self.detail_url)
