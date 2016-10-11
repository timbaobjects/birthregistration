# Django settings for unicefng project.
import dj_database_url
import os

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

DEBUG = config(u'DEBUG', cast=config.boolean, default=True)
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': dj_database_url.parse(config(u'DATABASE_URL',
                                            default=u'sqlite://unicefng.db')),
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = config(u'TIME_ZONE', default=u'Africa/Lagos')

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
SECRET_KEY = config(u'SECRET_KEY', default=u'+*x2)pdq%r9rcz*=eb216t0o1+vw5#vx&(8ss$k6mbko!p!+p1')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'unicefng.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'unicefng.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

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
    # External apps
    "django_mysql",
    "django_tables2",
    "selectable",
    "patterns",
    "locations",
    "reporters",
    "br",
    u'campaigns',
    "rest_framework",
    "pipeline",
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
}

LOGIN_REDIRECT_URL = '/'

RAPIDSMS_HANDLERS = (
    'rapidsms.contrib.echo.handlers.echo.EchoHandler',
    'rapidsms.contrib.echo.handlers.ping.PingHandler',
)

LOCATIONS_GRAPH_MAXAGE = 3600  # number of seconds cache the locations graph
PAGE_SIZE = 30  # Number of submissions viewable per page
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

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
