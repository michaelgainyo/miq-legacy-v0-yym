
from django.test import TestCase
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.auth import get_user_model

from sitemgr.tests import TestMixin
from blog.models import Article, Category

User = get_user_model()


class BlogViewsTest(TestMixin, TestCase):

    def test_create_article(self):
        self.login('staff', self.p)

        self.client.post(
            reverse('blog:article_create'),
            {'title': 'Article 2'})
        # self.assertEqual(r.status_code, 301)
        self.assertEqual(Article.objects.count(), 1)

        self.client.post(
            reverse('blog:article_create'),
            {'title': 'Article 2', 'category': self.cat.pk})

        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(Article.unpublished.count(), 2)

        article = Article.objects.last()
        self.get_url(article.detail_url, 404)

        article.publish = True
        article.save()
        self.get_url(article.detail_url)
        self.assertEqual(Article.published.count(), 1)

    def test_urls(self):

        self.get_url(reverse('blog:articles'))
        self.get_url(self.cat.detail_url)
        self.get_url(self.article.detail_url, 404)

        self.article.publish = True
        self.article.save()
        self.get_url(self.article.detail_url)

    def test_staff_urls(self):
        self.get_url(reverse('blog:article_list'), 302)

        self.login('usr', self.p)
        self.get_url(reverse('blog:article_list'), 403)

        self.login('staff', self.p)
        self.get_url(reverse('blog:article_list'))
        self.get_url(reverse('blog:article_create'))
        self.get_url(reverse('blog:category_list'))
        self.get_url(reverse('blog:category_create'))

        self.get_url(self.cat.staff_edit_url)
        self.get_url(self.article.staff_edit_url)

    @classmethod
    def setUpTestData(cls):
        Site.objects.first().save()
        cls.cat = Category.objects.create(name='Cat 1')
        cls.article = Article.objects.create(
            category=cls.cat, title='Article 1')
        cls.p = 'iuN8i'
        User.objects.create_user(
            username='usr', email='email@usr.com',
            password=cls.p)

        User.objects.create_superuser(
            username='staff', email='email@staff.com',
            password='iuN8i')
