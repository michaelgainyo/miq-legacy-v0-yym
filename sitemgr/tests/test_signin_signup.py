from django.test import TestCase

from .import TestMixin
from django.urls import reverse
from sitemgr.models import Profile

# Create your tests here.


class TestSigninSignupViews(TestMixin, TestCase):

    def test_user_login(self):
        usr = self.get_usr(username='usr')
        self.login('usr', 'pass')
        ip = usr.last_login_ip

        self.client.logout()
        self.assertEqual(ip, usr.last_login_ip)

    def test_new_signup(self):
        url = reverse('accounts:register')
        self.assertEqual(Profile.objects.count(), 0)

        self.client.post(url, {
            'username': 'newuser',
            'first_name': 'Firstname',
            'email': 'new@email.com',
            'password1': 'ooi334weoi',
            'password2': 'ooi334weoi'
        })
        # TODO - site.settings.require_login
        # TODO - site.settings.is_live

        self.assertEqual(Profile.objects.count(), 1)
        usr = Profile.objects.first().user
        self.assertNotEqual(usr.signup_ip, None)

    def test_signin_signup_urls(self):
        usr = self.get_usr()
        self.get_url(usr.detail_url, 302)  # 'accounts:account'
        self.get_url(usr.profile.detail_url)   # 'accounts:profile'
        self.get_url(reverse('accounts:notifications'), 302)
        self.get_url(reverse('accounts:account_edit'), 302)

        self.login(usr.username, 'pass')
        self.get_url(usr.detail_url)
        self.get_url(reverse('accounts:account_edit'))

        self.get_url(reverse('accounts:notifications'), 403)

        usr.profile.add_post_perms()
        self.get_url(reverse('accounts:notifications'))

        usr.profile.add_post_perms(remove=True)
        self.get_url(reverse('accounts:notifications'), 403)

        self.get_url(reverse('accounts:register'), 302)
        self.get_url(reverse('accounts:login'), 302)

        self.get_url(reverse('accounts:logout'))
        self.get_url(reverse('accounts:register'))
        # self.get_url(reverse('accounts:register_done'))
        self.get_url(reverse('accounts:login'))

        self.get_url(reverse('accounts:password_reset'))

        # TO FIX
        self.get_url(reverse('accounts:password_reset_done'))
        # self.get_url(reverse('accounts:password_reset_confirm'))
        self.get_url(reverse('accounts:password_reset_complete'))

    def setUp(self):
        self.init()
        # print("setUp: Run once for every test method to setup clean data.")

    @classmethod
    def setUpTestData(cls):
        pass
