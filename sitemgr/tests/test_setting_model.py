
from django.test import TestCase
from django.urls import reverse

from .import TestMixin

# Create your tests here.


class TestSettingModel(TestMixin, TestCase):

    def test_site_close(self):
        site = self.site
        print(site)
        print(site.settings)

        r = self.client.get(reverse('sitemgr:index'))
        self.assertEqual(r.status_code, 200)

        self.assertFalse(site.settings.is_live)

        r = self.client.get(reverse('sitemgr:about'))
        # self.assertEqual(r.status_code, 302)

    def setUp(self):
        self.init()

    @classmethod
    def setUpTestData(cls):
        pass
