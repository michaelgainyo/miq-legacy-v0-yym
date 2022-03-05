# import json

from django import template

register = template.Library()


@register.inclusion_tag('widgets/icn-btn.html', takes_context=True)
def render_btn(context, icn=None, cta=None, cls='', type=None):
    return {
        'cta': cta,
        'icn': icn, 'cls': cls,
        'context': context,
        'request': context['request']
    }


@register.inclusion_tag('widgets/icn-a.html', takes_context=True)
def render_a(context, url, icn, a_title=None, cta=None, cls=None, **kwargs):
    return {
        'url': url, 'a_title': a_title,
        'cta': cta,
        'icn': icn, 'cls': cls,
        'new_tab': kwargs.get('new_tab', False),
        'context': context,
        'request': context['request']
    }


@register.inclusion_tag(
    'components/navbar.html', takes_context=True)
def show_navbar(context):
    return {
        'context': context,
        'perms': context.get('perms'),
        'site': context.get('site'),
        'request': context['request']
    }


@register.inclusion_tag(
    'components/footer.html', takes_context=True)
def show_footer(context):
    return {
        'context': context,
        'site': context.get('site'),
        'request': context['request'],
        'next': context['request'].path_info
    }
