
import logging
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Hit
from .utils import get_path, get_referrer, get_ip


User = get_user_model()
logger = logging.getLogger(__name__)
paths_blacklist = ['admin', 'staff', 'media', '.ico']


def log_request(request, *args, **kwargs):

    created = False
    ip = get_ip(request)
    path = get_path(request)
    referrer = get_referrer(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'unknown')

    # skip this paths
    for key in paths_blacklist:
        if key in path:
            logger.debug(f'Skipping path[{path}]: [{key}] is blacklisted')
            return

    if not request.session.session_key:
        try:
            request.session.save()
        except Exception as e:
            logger.error(e, exc_info=True)

    session = request.session.session_key

    new_hit = Hit.objects.filter(
        Q(path=path, ip=ip, user_agent=user_agent, session=session) |
        Q(path=path, ip=ip, user_agent=user_agent) |
        Q(path=path, ip=ip, session=session) |
        Q(path=path, ip=ip) |
        Q(session=session, path=path)).first()

    if not new_hit:
        try:
            new_hit, created = Hit.objects.get_or_create(
                user_agent=user_agent,
                ip=ip, session=session, path=path)

        except Exception as e:
            logger.error(f'{e}', exc_info=1)

            new_hit = Hit.objects.create(
                user_agent=user_agent,
                ip=ip, session=session, path=path)
            created = True

    if new_hit:
        new_hit.count += 1

        new_hit.user_agent = user_agent
        new_hit.referrer = referrer

        if created:
            logger.info(
                f'New Hit[{new_hit.pk}]. '
                f'Mobile[{new_hit.is_mobile}]. '
                f'Bot[{new_hit.is_bot}]')

        new_hit.parse(save=False)
        new_hit.save()

        user = request.user if request.user.is_authenticated\
            else User.objects.filter(
                pk=request.session.get('uid')).first()

        if user:
            if user.profile.ip != ip:
                logger.warn(
                    f'User[{user.pk}] {user} '
                    f'IP change: {user.profile.ip} > {ip}')

                user.profile.ip = ip
                user.profile.save()

        if referrer == path:
            logger.debug('Page Reload')

    logger.debug(f'View: {new_hit.visitor}[{request.user}] {new_hit.ip}, ')
