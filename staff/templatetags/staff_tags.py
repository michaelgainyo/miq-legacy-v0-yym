from django import template

register = template.Library()


@register.inclusion_tag(
    'staff/sidebar.html', takes_context=True)
def show_staff_sidebar(context):
    return {}
