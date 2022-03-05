
from sitemgr import views

from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login

from .models import Article, Category


class Mixin(LoginRequiredMixin):
    pass


class ArticlesView(views.ListView):
    queryset = Article.published.prefetch_related('images').all()
    featured = None
    context_object_name = 'articles'
    template_name = 'blog/articles.html'
    paginate_by = 5

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        featured = self.queryset.filter(feature=True)
        if featured.exists():
            self.featured = featured.first()
            qs = qs.exclude(pk=self.featured.pk)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured'] = self.featured

        return context


class ArticleView(views.DetailView):
    template_name = 'blog/article-base.html'
    context_object_name = 'article'
    obj = None
    more = None

    def get_template_names(self):
        try:
            return [f'blog/article-{self.object.gallery_layout}.html']
        except Exception:
            return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.more:
            context['more'] = self.more

        return context

    def get_object(self, *args, **kwargs):
        obj = self.obj or get_object_or_404(
            Article, category__slug=self.kwargs.get('category__slug'),
            slug=self.kwargs.get('slug'), publish=True)
        self.more = self.more or Article.objects\
            .exclude(pk__in=[obj.pk])\
            .filter(publish=True).order_by('?')[:6]

        return obj

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and self.get_object().is_explicit:
            return redirect_to_login(request.get_full_path())

        return super().dispatch(request, *args, **kwargs)


class CategoryView(views.ListView):
    model = Article
    category = None
    paginate_by = 50
    template_name = 'blog/articles-temp-3.html'

    def get_queryset(self, *args, **kwargs):
        cat = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        self.category = cat
        return super().get_queryset(*args, **kwargs)\
            .filter(category=cat, publish=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category

        return context
