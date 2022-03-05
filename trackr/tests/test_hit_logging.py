
from django.test import TestCase

from sitemgr.tests import TestMixin

from trackr.models import Hit, Campaign


class TestHitLogging(TestMixin, TestCase):

    def test_new_hit_on_pageview(self):
        self.client.get('/')
        self.assertEqual(Hit.objects.count(), 1)

        self.client.get('/')
        self.assertEqual(Hit.objects.count(), 1)

    def test_new_hit_with_query(self):
        self.client.get('/?q=query&oq=original_query&hl=lang&source=web')
        self.assertIn('query', Hit.objects.first().path)
        self.assertEqual(Hit.objects.count(), 1)
        self.assertEqual(Hit.objects.first().q, 'query')

        self.assertEqual(Campaign.objects.count(), 1)
        self.assertEqual(
            Campaign.objects.first(), Hit.objects.first().campaign)

    def test_new_hit_campaign(self):
        q = '/about/?utm_source=fb&utm_medium=Facebook_Mobile_Feed&utm_'\
            'campaign=6168080546366&utm_content=6168080546766'
        self.client.get(q)
        self.assertEqual(Campaign.objects.count(), 1)

        # no campaign should be created here
        q = '/about/?utm_source=fb'
        self.client.get(q)
        self.assertEqual(Campaign.objects.count(), 1)

        q = '/about/?utm_source=fb&utm_campaign=6168080546366'
        self.client.get(q)
        self.assertEqual(Campaign.objects.count(), 2)

        q = '/about/?utm_campaign=6168080546366'
        self.client.get(q)
        self.assertEqual(Campaign.objects.count(), 3)
        self.assertEqual(
            Campaign.objects.filter(name='6168080546366').count(), 3)

    def setUp(self):
        self.init()

    @classmethod
    def setUpTestData(cls):
        pass
