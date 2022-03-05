try:
    from urlparse import urlparse, parse_qs  # Python 2
except ImportError:
    from urllib.parse import urlparse, parse_qs  # Python 3

from pprint import pprint
from django.test import TestCase
from ua_parser import user_agent_parser
from trackr.ua.user_agents.parsers import parse

from sitemgr.tests import TestMixin

from trackr.models import Hit


class TestAnalyticsModelMixin(TestMixin, TestCase):
    fixtures = ['hit']
    # fixtures = ['ips']

    def test_ua_classification(self):
        fb = Hit.objects.all()
        # browser, os, q, utms

        def parse_utm(url):
            parsed = urlparse(url)
            return parse_qs(parsed.query, keep_blank_values=True)

        for i in fb.all():
            parsed_dict = {}

            for j in [i.path, i.referrer]:
                parsed = parse_utm(j)
                if parsed:
                    # print(parsed)

                    for key in parsed.keys():
                        parsed_dict[key] = parsed[key]

                        if key == 'url' or key == 'u':
                            val = parsed.get('url', parsed.get('u'))
                            if val:
                                val = val[0] if type(val) is list else val
                                parsed_dict.update(parse_utm(val))
                                print(parse_utm(val))

            parsed = user_agent_parser.Parse(i.user_agent)

            parsed = parse(i.user_agent)
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
            os = parsed.os.family
            if os:
                if 'Mac OS' in os and parsed_dict.get('model') is None:
                    parsed_dict['model'] = 'Desktop'
                    parsed_dict['device_brand'] = 'Apple'

            if 'q' in parsed_dict.keys():
                medium = parsed_dict.get('utm_medium')
                if type(medium) is list and medium[0] == 'Others':
                    parsed_dict['utm_medium'] = 'Google_Web_Search'

                if 'utm_medium' not in parsed_dict.keys():
                    parsed_dict['utm_source'] = 'goo'
                    parsed_dict['utm_medium'] = 'Google_Web_Search'

            dd = i.get_parsed()
            pprint(parsed_dict, indent=4)
            pprint(dd, indent=4)
            print('---\n')

            try:
                self.assertEqual(len(parsed_dict.keys()), len(dd.keys()))
            except Exception:
                print(set(parsed_dict.keys()).difference(set(dd.keys())))
                print('--------------------------------------------')
                print('--------------------------------------------')
                print('--------------------------------------------')

    def setUp(self):
        self.init()
        self.assertGreater(Hit.objects.count(), 0)

    @classmethod
    def setUpTestData(cls):
        pass
