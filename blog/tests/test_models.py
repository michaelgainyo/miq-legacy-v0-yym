
from django.test import TestCase
from django.contrib.auth import get_user_model

from sitemgr.tests import TestMixin
from blog.models import Article, Category

User = get_user_model()


class Mixin(TestMixin):
    def setUp(self):
        self.init()
        self.art = Article.objects.create(
            category=Category.objects.create(name='Cat'),
            title='Article')


class TestArticleModel(Mixin, TestCase):

    def test_explicit_article_redirect(self):
        art = self.art
        art.publish = True
        art.is_explicit = True
        art.save()
        self.get_url(art.detail_url, 302)

        usr = self.get_usr(username='user', password='pass')
        self.login(usr.username, 'pass')

        self.get_url(art.detail_url)

    def test_article_unpublished_is_404(self):
        art = self.art
        self.get_url(art.detail_url, 404)

        art.publish = True
        art.save()
        self.get_url(art.detail_url)

    @classmethod
    def setUpTestData(cls):
        pass
