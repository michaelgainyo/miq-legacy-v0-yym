
from django import template


register = template.Library()


@register.inclusion_tag(
    'staff/components/navbar.html', takes_context=True)
def show_staff_navbar(context):
    return {
        'context': context,
        'site': context['site'],
        'perms': context['perms'],
        'request': context['request']}


@register.inclusion_tag(
    'staff/components/sidebar.html', takes_context=True)
def show_staff_sidebar(context):
    return {
        'context': context,
        'site': context['site'],
        'perms': context['perms'],
        'request': context['request']}


@register.inclusion_tag(
    'components/footer.html', takes_context=True)
def show_search_form(context):
    return {
        'context': context,
        'next': context['request'].path_info}
