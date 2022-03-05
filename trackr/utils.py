
import json
from django.utils import dateformat
from django.core.validators import validate_ipv46_address


def get_chart(manager):
    from .models import Path

    hits = manager.order_by('created').all()
    x_axis = [
        dateformat.format(hit.created, 'H:i a') for hit in hits]

    series = []

    keys = [
        (path.name, path.get_today_manager)
        for path in Path.objects.all()]

    for name, fn in iter(keys):
        fn = fn()
        hits = fn.all()

        series.append({
            'name': f'{name}',
            'data': [hit.count for hit in hits],
        })

    return json.dumps({
        'chart': {'type': 'column'},
        'title': {'text': 'today views'},
        'xAxis': {'categories': x_axis},
        'series': series
    })


def get_referrer(request):
    return request.META.get('HTTP_REFERER', '')


def get_ip(request):
    ip = '127.0.0.1'
    try:
        ip = request.META.get(
            'HTTP_X_FORWARDED_FOR',
            request.META.get('REMOTE_ADDR', '127.0.0.1'))
        validate_ipv46_address(ip)
    except Exception as e:
        print(e)
    return ip


def get_path(request):
    path = 'unknown'
    if request:
        try:
            path = request.get_full_path_info() or request.get_full_path()
        except Exception as e:
            path = request.path_info or request.path
            print(e)

    return path
