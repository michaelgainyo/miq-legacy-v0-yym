
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

User = get_user_model()


class TestMixin(object):
    def get_usr(self, username='usr', password='pass'):
        return User.objects.create_user(
            username=username,
            first_name='michael',
            password=password,
            email='email@email.com')

    def get_url(self, url, status=200):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status)

    def login(self, username, password):
        login = self.client.login(username=username, password=password)
        self.assertTrue(login)

    def init(self):
        self.site, new = Site.objects.get_or_create(
            name='My site', domain='127.0.0.1:8000')
