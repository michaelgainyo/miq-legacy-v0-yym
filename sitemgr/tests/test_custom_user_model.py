from django.test import TestCase
from django.core.exceptions import ValidationError

from .import TestMixin
from sitemgr.models import User, Profile

# Create your tests here.


class TestCustomUserModel(TestMixin, TestCase):

    def test_new_user_has_profile(self):
        u = self.u
        u.full_clean()
        self.assertTrue(Profile.objects.filter(user=self.u).exists())

    def test_username_min_lenght(self):
        # min lenght = 4
        u = User(username='i')

        try:
            u.full_clean()
        except ValidationError as e:
            self.assertTrue('username' in e.message_dict)

    def test_username_unwanted_chars(self):
        # @
        names = [
            'mich@el', 'm-ichael', 'm+chavel', 'bab}{',
            '*yuou', '$dolla', '#uini'
        ]
        for name in names:
            u = User(username=name)

            try:
                u.full_clean()
            except ValidationError as e:
                self.assertTrue('username' in e.message_dict)

    def test_username_is_not_digit(self):
        names = ['123456', '12345.6']
        for name in names:
            u = User(username=name)

            try:
                u.full_clean()
            except ValidationError as e:
                self.assertTrue('username' in e.message_dict)

    def test_username_is_unicode_only(self):
        u = User(username='1,2u3456')

        try:
            u.full_clean()
        except ValidationError as e:
            self.assertTrue('username' in e.message_dict)

    def test_firstname_min_lenght(self):
        # min lenght = 2
        u = User(first_name='m')

        try:
            u.full_clean()
        except ValidationError as e:
            self.assertTrue('first_name' in e.message_dict)

    def test_username_firstname_email_not_blank(self):
        u = User()

        try:
            u.full_clean()
        except ValidationError as e:
            self.assertTrue('username' in e.message_dict)
            self.assertTrue('first_name' in e.message_dict)
            # self.assertTrue('email' in e.message_dict)

    def setUp(self):
        # print("setUp: Run once for every test method to setup clean data.")
        pass

    @classmethod
    def setUpTestData(cls):
        cls.u = User.objects.create(
            username='michael',
            first_name='michael',
            password='pass',
            email='email@email.com')

