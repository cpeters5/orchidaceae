"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import environ
import os
import logging.config

# root = environ.Path(__file__) - 2  # get root of the project
ROOT_DIR = environ.Path(__file__) - 2  # get root of the project

env = environ.Env()

# environ.Env.read_env()  # reading .env file
DOT_ENV_FILE = env.str("DOT_ENV_FILE", default=".env")
if DOT_ENV_FILE:
    env.read_env(str(ROOT_DIR.path(DOT_ENV_FILE)))

# SITE_ROOT = root()
SITE_ROOT = ROOT_DIR

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY =  env.str('DJANGO_SECRET_KEY', default=''),

SITE_ID = 1

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
PYTHONUNBUFFERED=True

ALLOWED_HOSTS = [
    'orchidroots.org',
    'www.orchidroots.org',
    'orchidroots.com',
    'www.orchidroots.com',
    'bluenanta.com',
    # 'www.bluenanta.com',
    # 'beta.bluenanta.com',
    '157.245.210.148',
    '127.0.0.1',
    'localhost',
]


# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'session_cleanup',
    'django_crontab',
    # 'dbview',
    # 'rest_framework',

    #local
    'myproject',
    'accounts',
    'documents',
    'donation',
    'search',
    'utils',

    # 'bromeliaceae',
    'detail',
    'orchiddb',
    # 'cactaceae',
    # 'other',

    # Legacy
    'orchidlist',

    # Third Party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.facebook',
    'bootstrap_modal_forms',
    'crispy_forms',
    'robots',  # use myproject/robots.txt
    'jquery',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_FAIL_SILENTLY = not DEBUG
AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

INTERNAL_IPS = [
    # ...
    '157.245.210.148',
    # ...
]

ROOT_URLCONF = 'myproject.urls'

ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE=True

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend"
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'accounts/templates')],
        'OPTIONS': {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# TEMPLATE_CONTEXT_PROCESSORS = (
#     "django.core.context_processors.request",
#     "django.contrib.auth.context_processors.auth",
    # "allauth.account.context_processors.account",
    # "allauth.socialaccount.context_processors.socialaccount",
# )

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databasesz

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'orchidroots',
        'PORT': env.str('PORT', default=''),
        'HOST': env.str('DBHOST', default=''),
        'USER': env.str('DBUSER', default=''),
        'PASSWORD': env.str('DBPASSWD', default=''),
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
LOGIN_URL = '/login/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_ROOT = '/webapps/static/'
MEDIA_ROOT  = '/webapps/static/media/'
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_MAX_MEMORY_SIZE = 52428800

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES' : ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_AUTHENTICATION_CLASSES' : ('rest_framework_simplejwt.authentication.JWTAuthentication',)
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

from session_cleanup.settings import weekly_schedule
CELERYBEAT_SCHEDULE = {
    'session_cleanup': weekly_schedule
}

CRONJOBS = [
    ('*/2 * * * *', 'myproject.cron.my_cron_job')
]

LOGGING_CONFIG = None
try:
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                # exact format is not important, this is the minimum information
                'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'console',
            },
            'sentry': {
                'level': 'WARNING',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            },
            # 'logfile': {
            #     'level':'DEBUG',
            #     'class':'logging.FileHandler',
            #     'filename': BASE_DIR + "/../log/logfile",
            # },
        },
        'loggers': {
            '': {
                'level': 'WARNING',
                'handlers': ['console', 'sentry']
            },
            'myproject': {
                'level': 'INFO',
                'handlers': ['console', 'sentry'],
                # required to avoid double logging with root logger
                'propagate': False,
            },
        },
    })
except: # noqa
    pass


# allauth account settings
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

#https://django-allauth.readthedocs.io/en/latest/providers.html
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'METHOD': 'oauth2',
        'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        'SCOPE': ['email', 'public_profile'],
        # 'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
        'INIT_PARAMS': {'cookie': True},
        'FIELDS': [
            'id',
            'email',
            'name',
            'first_name',
            'last_name',
            'link',
            'picture'
        ],
        'EXCHANGE_TOKEN': True,
        'VERIFIED_EMAIL': True,
        'VERSION': 'v7.0',
    }
}
LOGIN_REDIRECT_URL = "/"
SOCIAL_AUTH_FACEBOOK_KEY = env.str('SOCIAL_FACEBOOK_KEY', default='')
SOCIAL_AUTH_FACEBOOK_SECRET = env.str('SOCIAL_FACEBOOK_SECRET', default='') #app key
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
ACCOUNT_ADAPTER = 'accounts.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.SocialAccountAdapter'
SOCIALACCOUNT_FORMS = {
    'signup': 'accounts.forms.SocialPasswordForm'
}
SOCIALACCOUNT_AUTO_SIGNUP = False

ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True

# mail settings
# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
ANYMAIL = {
    "MAILGUN_API_KEY": env.str("MAILGUN_API_KEY", default=''),
    "MAILGUN_SENDER_DOMAIN": env.str("MAILGUN_DOMAIN", default=''),
    "MAILGUN_API_URL": env.str("MAILGUN_API_URL", default="https://api.mailgun.net/v3"),
}
DEFAULT_FROM_EMAIL = "admin@mail.orchidroots.org"  # if you don't already have this in settings
SERVER_EMAIL = "admin@mail.orchidroots.org"

STRIPE_SECRET_KEY = env.str('STRIPE_SECRET_KEY', default='')
STRIPE_PUBLISHABLE_KEY = env.str('STRIPE_PUBLISHABLE_KEY', default='')

# paypal settings
PAYPAL_CLIENT_ID = env('PAYPAL_CLIENT_ID', default='')
PAYPAL_SECRET =  env('PAYPAL_SECRET', default='')
#  Use Gmail (Works)
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'cpeters5@gmail.com'
# EMAIL_HOST_PASSWORD = 'kvitodlpllgxuvtl'

# Use Yahoo mail. need to setup twostep verification?
# EMAIL_HOST = 'smtp.yahoo.com'
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'cpeters5'
# EMAIL_HOST_PASSWORD = 'srblyfdjfkkdkimm'

# Use django-sendmail
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
# DJANGO_MAILBOX_ADMIN_ENABLED = True
# DJANGO_MAILBOX_STRIP_UNALLOWED_MIMETYPES = False
# DJANGO_MAILBOX_ALLOWED_MIMETYPES = False
# DJANGO_MAILBOX_TEXT_STORED_MIMETYPES = X-Django-Mailbox-Altered-Message
# DJANGO_MAILBOX_ATTACHMENT_INTERPOLATION_HEADER = mailbox_attachments/%Y/%m/%d/
# DJANGO_MAILBOX_MAX_MESSAGE_SIZE = False
# DJANGO_MAILBOX_STORE_ORIGINAL_MESSAGE = False

# Setup support for proxy headers
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

try:
    from .local_settings import * # NOQA
except: # NOQA
    pass
