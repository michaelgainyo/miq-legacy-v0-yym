
from pathlib import Path
from django.urls import reverse_lazy

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = 'secret_key-goes-here'

DEBUG = True

ALLOWED_HOSTS = ['*']

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.forms',
]

VENDORS_APPS = ['rest_framework']

MY_APPS = [
    'blog', 'staff', 'trackr',
    'sitemgr.apps.SitemgrConfig', 'filemgr',
]

INSTALLED_APPS = DJANGO_APPS + VENDORS_APPS + MY_APPS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

MIDDLEWARE = [
    # CORS
    'config.middleware.CORSMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    #
    'trackr.middleware.TrackrMiddleware',
    'sitemgr.middleware.StaffMiddleware',
    'sitemgr.middleware.SiteMgrMiddleware',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

"""
LOCALIZATION
"""

USE_I18N = True
USE_L10N = True
USE_TZ = False
TIME_ZONE = 'America/New_York'

LANGUAGE_CODE = 'en'
LANGUAGES = (('en', 'English'), ('fr', 'French'))
LOCALE_PATHS = [BASE_DIR / 'locale']

"""
USER MODEL
"""

AUTH_USER_MODEL = 'sitemgr.User'


"""
SITE
"""

SITE_ID = 1

"""
AUTHENTICATION
"""

LOGIN_URL = reverse_lazy('accounts:login')
LOGIN_REDIRECT_URL = reverse_lazy('accounts:account')

"""
STATIC & MEDIA
"""
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


"""
REST FRAMEWORK
"""

CORS_ORIGIN = "http://192.168.1.189:3003"

"""
EMAIL
"""

EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST = 'smtp.gmail.com'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
