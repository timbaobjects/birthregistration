# Django settings for unicefng project.
import dj_database_url
import os
from django.contrib.messages import constants as messages
from prettyconf import config

# The top directory for this project. Contains requirements/, manage.py,
# and README.rst, a unicefng directory with settings etc (see
# PROJECT_PATH), as well as a directory for each Django app added to this
# project.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))

config.starting_path = PROJECT_ROOT

# The directory with this project's templates, settings, urls, static dir,
# wsgi.py, fixtures, etc.
PROJECT_PATH = os.path.join(PROJECT_ROOT, 'unicefng')

DEBUG = config('DEBUG', cast=config.boolean, default=True)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': dj_database_url.parse(
        config('DATABASE_URL', default='sqlite://unicefng.db')),
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = CELERY_TIMEZONE = config('TIME_ZONE', default='Africa/Lagos')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/public/media/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'public', 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/public/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'public', 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files to collect
STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = config('SECRET_KEY')


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'unicefng.middleware.SubdomainMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'unicefng.urls'
SUBDOMAIN_URLCONFS = {
    None: 'unicefng.urls',
    'br': 'br.urls',
    'dr': 'dr.urls',
}

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'unicefng.wsgi.application'

TEMPLATES = [
    {
        u'BACKEND': u'django.template.backends.django.DjangoTemplates',
        u'APP_DIRS': True,
        u'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
        ],
        u'OPTIONS': {
            u'context_processors': (
                u'django.template.context_processors.debug',
                u'django.template.context_processors.request',
                u'django.contrib.auth.context_processors.auth',
                u'django.contrib.messages.context_processors.messages',
                u'django.template.context_processors.i18n',
                u'django.template.context_processors.media',
                u'django.template.context_processors.static',
                u'django.template.context_processors.tz',
            ),
            u'debug': DEBUG,
        }
    }
]

FIXTURE_DIRS = (
    os.path.join(PROJECT_PATH, 'fixtures'),
)

# A sample logging configuration.
# This logs all rapidsms messages to the file `rapidsms.log`
# in the project directory.  It also sends an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'basic': {
            'format': '%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'basic',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'basic',
            'filename': os.path.join(PROJECT_PATH, 'rapidsms.log'),
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'rapidsms': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django.contrib.sites',
    # External apps
    "base",
    "django_mysql",
    "django_tables2",
    "selectable",
    "django_celery_beat",
    "bootstrap3",
    "django_filters",
    "patterns",
    "locations",
    "reporters",
    "br",
    "dr",
    "profiles",
    "campaigns",
    "ipd",
    "rest_framework",
    "pipeline",
    "bootstrap_pagination",
    # RapidSMS
    "rapidsms",
    "rapidsms.backends.database",
    "rapidsms.contrib.handlers",
    "rapidsms.contrib.httptester",
    "rapidsms.contrib.messagelog",
    "rapidsms.contrib.messaging",
    "rapidsms.contrib.registration",
    "rapidsms.contrib.echo",
    "rapidsms.contrib.default",  # Must be last
)

INSTALLED_BACKENDS = {
    "message_tester": {
        "ENGINE": "rapidsms.backends.database.DatabaseBackend",
    },
    "polling": {
        "ENGINE": "rapidsms.backends.database.DatabaseBackend",
    },
}

LOGIN_REDIRECT_URL = '/'

RAPIDSMS_HANDLERS = (
    'rapidsms.contrib.echo.handlers.echo.EchoHandler',
    'rapidsms.contrib.echo.handlers.ping.PingHandler',
)

LOCATIONS_GRAPH_MAXAGE = 3600  # number of seconds cache the locations graph
PAGE_SIZE = 30  # Number of submissions viewable per page
SITE_ID = 1
# STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# django-pipeline settings
PIPELINE = {
    'STYLESHEETS': {
        'rapidsms': {
            'source_filenames': (
                'css/bootstrap.css',
                'css/bootstrap-responsive.css',
                'css/custom.css',
                'css/style.css',
                'css/datepicker.css',
                'css/select2.css',
            ),
            'output_filename': 'css/rapidsms.css',
            'extra_context': {
                'media': 'screen,projection',
            },
        },
        'dashboard': {
            'source_filenames': (
                'css/bootstrap3.css',
                'css/nv.d3.css',
                'css/custom-dashboard.css',
            ),
            'output_filename': 'css/dashboard.css',
            'extra_context': {
                'media': 'screen,projection',
            },
        },
        'centers': {
            'source_filenames': (
                'css/select2.css',
                'css/handsontable.full.css'
            ),
            'output_filename': 'css/centers.css',
            'extra_context': {
                'media': 'screen,projection'
            }
        }
    },
    'JAVASCRIPT': {
        'rapidsms': {
            'source_filenames': (
                'js/jquery-1.8.1.js',
                'js/bootstrap.js',
                'js/bootstrap-datepicker.js',
                'js/select2.js',
                'js/custom.js',
            ),
            'output_filename': 'js/rapidsms.js',
        },
        'dashboard': {
            'source_filenames': (
                'js/jquery-1.10.2.js',
                'js/bootstrap3.js',
                'js/d3.v3.js',
                'js/nv.d3.js',
                'js/Uri.js',
            ),
            'output_filename': 'js/dashboard.js',
        },
        'centers': {
            'source_filenames': (
                'js/handsontable.full.js',
                'js/select2.js'
            ),
            'output_filename': 'js/centers.js',
        }
    }
}
# Population
POPULATION_RATIOS = {
    'below1': 0.0364,
    '1to4': 0.2,
    'above5': .45,
}

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=config.list, default=[])
BROKER_URL = config('BROKER_URL', default='redis://localhost:6379/0')
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL', default='webmaster@localhost')

EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = config('EMAIL_PORT', default=25)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=config.boolean, default=False)

REST_FRAMEWORK = {
    u'PAGE_SIZE': PAGE_SIZE,
    u'DEFAULT_PAGINATION_CLASS': u'rest_framework.pagination.LimitOffsetPagination',
}

MESSAGE_TAGS = {
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
    messages.INFO: 'alert-info',
}

SENDFILE_BACKEND = config(u'SENDFILE_BACKEND',
    default=u'sendfile.backends.development')

SENDFILE_ROOT = config(u'SENDFILE_DOCUMENT_ROOT',
    default=os.path.join(PROJECT_PATH, u'documents'))

SENDFILE_URL = u'/protected'

SENDSMS_URL = config('SENDSMS_URL', default='')
SENDSMS_USERNAME = config('SENDSMS_USERNAME', default='')
SENDSMS_PASSWORD = config('SENDSMS_PASSWORD', default='')
SENDSMS_SHORTCODE = config('SENDSMS_SHORTCODE', default='')
