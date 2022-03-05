
from config.mixins import BootstrapModelFormMixin
from .models import Article


class ArticleEditForm(BootstrapModelFormMixin):
    class Meta:
        model = Article
        fields = ('name', 'slug', 'description', 'image', 'publish')
