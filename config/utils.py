
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType


def get_model(app_name, model_name):
    app_name = str(app_name)
    model_name = str(model_name)

    try:
        model = apps.get_model(app_name, model_name)
    except Exception:
        raise ObjectDoesNotExist('This model does not exist')
    else:
        return model


def get_content_type(model):
    return ContentType.objects.get_for_model(model)
