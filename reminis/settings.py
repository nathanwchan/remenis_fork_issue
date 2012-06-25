# Django settings for reminis project.
import socket
import os.path

if socket.gethostname() == 'Nathans-MacBook-Air.local':
    DEBUG = True
else:
    DEBUG = False

TEMPLATE_DEBUG = DEBUG

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
    ('Nathan Chan', 'nchan87+django@gmail.com'),
)

SITE_ROOT_URL = ''

if DEBUG:
    SITE_ROOT_URL = 'http://localhost:8000' 
else: 
    SITE_ROOT_URL = 'http://warm-samurai-5146.herokuapp.com/'
    
MANAGERS = ADMINS

if not DEBUG:
    import dj_database_url
    DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': '/Users/nathanwchan/djcode/reminis/reminis.db',                      # Or path to database file if using sqlite3.
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#        'NAME': SITE_ROOT + '/reminis.db',                      # Or path to database file if using sqlite3.
#        'USER': '',                      # Not used with sqlite3.
#        'PASSWORD': '',                  # Not used with sqlite3.
#        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#    }
#}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = 'static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(SITE_ROOT, 'core/static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '8n0s+#vt^uo(^_fdz=ks%+!$%hc^ohmxa_zq=18u=p7_pi1vt3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'reminis.FacebookConnectMiddleware.FacebookConnectMiddleware',
#    'facebook.middleware.SignedRequestMiddleware',
#    'facebook.middleware.AppRequestMiddleware',
)

ROOT_URLCONF = 'reminis.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'reminis.wsgi.application'

TEMPLATE_DIRS = (
    SITE_ROOT + '/templates',
)

INSTALLED_APPS = (              
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reminis.core',
#    'django.contrib.admindocs',
#    'django_facebook',
    'south',
#    'facebook',
#    'facebook.modules.profile.page',
#    'facebook.modules.profile.user',
#    'facebook.modules.profile.event',
#    'facebook.modules.profile.application',
#    'facebook.modules.connections.post',
)

FACEBOOK_APP_ID = '301406439948925'
FACEBOOK_APP_SECRET = 'd4e5d448e3e40c2fb13e21d8b4ef40e4'
FACEBOOK_STORE_LIKES = True
FACEBOOK_STORE_FRIENDS = True
FACEBOOK_LOGIN_DEFAULT_REDIRECT = '/facebook/connect/'
FACEBOOK_REGISTRATION_BACKEND = 'django_facebook.registration_backends.UserenaBackend'

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'django_facebook.auth_backends.FacebookBackend',
)
AUTH_PROFILE_MODULE = 'django_facebook.FacebookProfile'
ACCOUNT_ACTIVATION_DAYS = 10
TEMPLATE_CONTEXT_PROCESSORS = (
#    'django.core.context_processors.debug',
#    'django.core.context_processors.i18n',
#    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django_facebook.context_processors.facebook',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
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
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


try:
    from local_settings import *
except:
    pass

