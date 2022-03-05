from django import template

from ..models import Category


register = template.Library()


@register.inclusion_tag(
    'blog/components/sidebar.html', takes_context=True)
def show_blog_sidebar(context):

    return {
        'categories': Category.objects.all()[:7],
        'context': context,
        'perms': context.get('perms'),
        'site': context.get('site'),
        'request': context['request'],
    }


@register.inclusion_tag(
    'blog/components/cat_navbar.html', takes_context=True)
def show_blog_nav_categories(context):
    return {
        'categories': Category.objects.all,
        'request': context['request'],
    }
