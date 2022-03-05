from django import template

register = template.Library()


@register.inclusion_tag('filemgr/image/img-widget.html', takes_context=True)
def render_img(context, image_obj, cls=None, id=None, alt=None, extra=None):
    # TODO: Site protect image
    if not alt and image_obj:
        alt = image_obj.get_alt_text

    return {
        'img': image_obj,
        'alt': alt,
        'cls': cls, 'id': id, 'extra': extra,
        'context': context,
        'request': context['request']
    }
