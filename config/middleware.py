
from django.conf import settings


class CORSMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        self.process_response(request, response)

        return response

    def process_response(self, request, response):

        response["Access-Control-Allow-Origin"] = settings.CORS_ORIGIN
        response["Access-Control-Allow-Headers"] = "X-CSRFTOKEN, Content-Type, Accept, Origin"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response["Access-Control-Max-Age"] = 86400
        response["Access-Control-Allow-Credentials"] = 'true'

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_template_response(self, request, response):
        return response
