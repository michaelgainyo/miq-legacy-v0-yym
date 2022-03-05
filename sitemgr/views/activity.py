
import datetime

from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth import get_user_model

User = get_user_model()


def log_activity(request):
    def process_request(request):
        user = request.user
        last_seen_timeout = 60 * 60 * 24 * 7
        now = datetime.datetime.now()
        if user.is_authenticated:
            cache.set(
                'seen_%s' % (user.username), now,
                last_seen_timeout)
            return True
        else:
            key = request.session.session_key
            if key:
                cache.set(
                    'seen_%s' % (key), now,
                    last_seen_timeout)
                return True
        return False

    data = {'status': 'ok'}
    if process_request(request):
        pass

    return JsonResponse(data)
