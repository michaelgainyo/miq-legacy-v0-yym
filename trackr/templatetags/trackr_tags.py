
from django import template

from ..models import Hit, Path, TrackrSetting


register = template.Library()


@register.inclusion_tag(
    'trackr/components/ga-tracking-code.html', takes_context=True)
def show_ga_tracking_code(context):
    ga_id = None
    code = TrackrSetting.objects
    if code.exists():
        ga_id = code.first().ga_tracking_id

    request = context['request']

    return {
        'context': context,
        'request': request,
        'ga_tracking_id': ga_id,
    }


@register.inclusion_tag(
    'trackr/components/fb-tracking-code.html', takes_context=True)
def show_fb_tracking_code(context):

    request = context['request']
    site = context.get('site')
    fb_pixel_id = TrackrSetting.objects.first().fb_pixel_id or ''
    obj = context.get('object') or context.get('product')
    order = context.get('order') or context.get('placed')
    extra = ""

    if obj:
        name = f'{obj._meta.model_name}'.capitalize() + 'View'
        extra += f"fbq('trackCustom', '{name}');\n"

    return {
        'context': context,
        'request': request,
        'fb_pixel_id': fb_pixel_id.strip(),
        'site': site,
        'obj': obj,
        'order': order,

        'extra': extra,
    }


@register.inclusion_tag('trackr/components/summary.html')
def show_today_summary():
    return {'views': Hit.today, 'paths': Path.objects.all}
