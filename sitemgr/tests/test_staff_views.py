
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class StaffViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # cls.client = Client()

        User.objects.create_user(
            username='usr', email='email@user.com',
            password='iuN8i')
        User.objects.create_superuser(
            username='staff', email='email@staff.com',
            password='iuN8i')

    def test_staff_urls(self):
        url = reverse('sitemgr:staff_dashboard')

        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

        login = self.client.login(username='usr', password='iuN8i')
        self.assertTrue(login)

        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

        login = self.client.login(username='staff', password='iuN8i')
        self.assertTrue(login)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
