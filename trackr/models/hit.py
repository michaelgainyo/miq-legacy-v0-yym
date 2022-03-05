
import logging
import datetime

try:
    from urlparse import urlparse, parse_qs  # Python 2
except ImportError:
    from urllib.parse import urlparse, parse_qs  # Python 3
from trackr.ua.user_agents.parsers import parse

from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from config.mixins import TimeStampsModelMixin

from ..managers import ViewsManager

logger = logging.getLogger(__name__)
User = get_user_model()


def parse_utm(url):
    parsed = urlparse(url)
    return parse_qs(parsed.query, keep_blank_values=True)


class Hit(TimeStampsModelMixin):
    class Meta:
        ordering = ('-updated', )
        verbose_name = 'Hit'
        verbose_name_plural = 'Hits'

    count = models.PositiveIntegerField(default=0)
    path = models.CharField(max_length=300)
    referrer = models.TextField(default='')

    session = models.CharField(max_length=100, null=True)
    user_agent = models.TextField(default='')
    ip = models.GenericIPAddressField(
        unpack_ipv4=True, null=True,
        verbose_name=_('ip address'), blank=True)

    campaign = models.ForeignKey(
        'Campaign', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='hits')
    q = models.CharField(
        max_length=300, null=True, blank=True,
        help_text='Google search query')
    os = models.CharField(max_length=300, null=True, blank=True)
    browser = models.CharField(max_length=300, null=True, blank=True)

    is_mobile = models.BooleanField(_('is mobile'), default=False)
    is_bot = models.BooleanField(_('is bot'), default=False)

    # Managers
    objects = ViewsManager()

    def parse(self, save=False):
        parsed = self.get_parsed()

        q = parsed.get('q')
        os = parsed.get('os')
        browser = parsed.get('browser')

        self.is_bot = parsed.get('is_bot')
        self.is_mobile = parsed.get('is_mobile')

        if q and not self.q:
            self.q = q

        if os and not self.os:
            self.os = os

        if browser and not self.browser:
            self.browser = browser

        camp = parsed.get('utm_campaign')
        if camp and not self.campaign:
            try:
                camp, new = Campaign.objects.get_or_create(
                    name=parsed.get('utm_campaign'),
                    source=parsed.get('utm_source'),
                    medium=parsed.get('utm_medium'),
                    content=parsed.get('utm_content')
                )
            except Exception:
                camp = Campaign.objects.create(
                    name=parsed.get('utm_campaign'),
                    source=parsed.get('utm_source'),
                    medium=parsed.get('utm_medium'),
                    content=parsed.get('utm_content'))
            else:
                self.campaign = camp

        if save is True:
            self.save()

    def get_parsed(self):
        parsed_dict = {}

        def get_parsed_from_dict(to_parse):
            msg = '{} must be a dict'
            assert type(to_parse) is dict, msg.format('to parse')
            parsed = {}

            for key in to_parse.keys():
                val = to_parse.get(key)
                val = val[0] if type(val) is list else val

                if val or key == 'q' or key == 'sk':
                    parsed[key] = val

            return parsed

        for url in [self.referrer, self.path]:
            u = url
            p_url = parse_utm(url)
            if p_url:
                parsed_dict.update(get_parsed_from_dict(p_url))

            keys = p_url.keys()
            if 'url' in keys or 'u' in keys:
                url = p_url.get('url', p_url.get('u'))
                url = url[0] if type(url) is list else url
                if url:
                    p_url = parse_utm(url)
                    if p_url:
                        parsed_dict.update(get_parsed_from_dict(p_url))

            if 'q' in parsed_dict.keys():
                medium = parsed_dict.get('utm_medium')
                medium = medium[0] if type(medium) is list else medium
                if not medium or medium == 'Others':
                    domain = urlparse(u).netloc
                    source = None

                    if 'google' in domain:
                        medium = 'Google_{}_Search'.format(
                            parsed_dict.get('source', 'web').capitalize())
                        source = 'google'
                    elif 'bing' in domain:
                        medium = 'Bing_Web_Search'
                        source = 'bing'

                    parsed_dict['utm_medium'] = medium

                    if source:
                        parsed_dict['utm_source'] = source

                campaign = parsed_dict.get('utm_campaign')
                if not campaign:
                    parsed_dict['utm_campaign'] = 'search'

            if 'from' in parsed_dict.keys():
                source = parsed_dict.get('from')
                if 'yandex' in source:
                    parsed_dict['utm_campaign'] = 'search'
                    parsed_dict['utm_medium'] = 'Yandex_Web_Search'
                    parsed_dict['utm_source'] = 'yandex'

        parsed = parse(self.user_agent)
        parsed_dict.update({
            'os': parsed.os.family,
            'browser': parsed.browser.family,
            'device_brand': parsed.device.brand,
            'device': parsed.device.family,
            'model': parsed.device.model,
            'is_mobile': parsed.is_mobile,
            'is_pc': parsed.is_pc,
            'is_tablet': parsed.is_tablet,
            'is_email_client': parsed.is_email_client,
            'is_bot': parsed.is_bot,
        })

        return parsed_dict

    @property
    def is_online(self):

        now = datetime.datetime.now()
        online_timeout = 300  # in seconds

        if self.last_seen and now < self.last_seen + datetime.timedelta(
                seconds=online_timeout):
            return True

        return False

    @property
    def last_seen(self):
        return cache.get('seen_%s' % self.session)

    def get_session(self):
        return Session.objects.filter(session_key=self.session).first()

    @property
    def session_data(self):
        return self.get_session().get_decoded()

    @property
    def source(self):
        return Hit.objects.filter(ip=self.ip).first().referrer

    @property
    def visitor(self):
        user = User.objects.filter(profile__ip=self.ip)

        if user.exists():
            return user.first()

    @property
    def staff_list_url(self):
        return reverse('trackr:hit_list')

    @property
    def staff_delete_url(self):
        return reverse('trackr:hit_delete', args=[self.id])

    @property
    def staff_detail_url(self):
        return reverse('trackr:hit_detail', args=[self.id])

    @property
    def detail_url(self):
        return self.staff_detail_url

    def __str__(self):
        txt = '(%s) - %s ' % (self.count, self.path)
        if self.visitor:
            txt += f'{self.visitor}'

        return txt


class Campaign(TimeStampsModelMixin):
    name = models.CharField(max_length=300, db_index=True)
    source = models.CharField(max_length=300, null=True, blank=True)
    medium = models.CharField(max_length=300, null=True, blank=True)
    content = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return f'{self.name}'
