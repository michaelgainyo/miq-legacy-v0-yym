
import logging


from .models import TrackrSetting
from .logger import log_request

logger = logging.getLogger(__name__)


class TrackrMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # code to be executed before the view is called

        response = self.get_response(request)

        # code to be executed after the view is called

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        try:
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                ip = request.META['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()
                request.META['REMOTE_ADDR'] = ip
        except Exception as e:
            logger.error(e, exc_info=1)

        try:
            log_request(request)

        except Exception as e:
            logger.error(e, exc_info=1)

    def process_template_response(self, request, response):

        settings = TrackrSetting.objects.first()
        if settings:
            if settings.fb_pixel_id:
                response.context_data['fb_pixel_id'] = settings.fb_pixel_id

            if settings.ga_tracking_id:
                pk = settings.ga_tracking_id
                response.context_data['ga_tracking_id'] = pk
        # print('hit context data\n', response.context_data)
        # print('hit template name\n', response.template_name)
        # alter the given response by changing
        # response.template_name and response.context_data
        return response

