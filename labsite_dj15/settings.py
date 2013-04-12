# Django settings for labsite_dj15 project.
import os

DEBUG = True
# DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Zhanrui.Liang', 'ray040123@gmail.com'),
)

_rootDir = '/home/ray/cppta/labsite_dj15/labsite_dj15/'

def relpath(path):
    return os.path.join(_rootDir, path)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'labsite',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'quick',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Shanghai'

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

MEDIA_ROOT = relpath('media/')

MEDIA_URL = '/media/'

STATIC_ROOT = relpath('static/')

STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    relpath('asset/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'dajaxice.finders.DajaxiceFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*k9qwe*m5bu-=yb61ha*r^_=m%pw1+0epccdbiv@7+c0!)n(+p'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'labsite_dj15.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'labsite_dj15.wsgi.application'

TEMPLATE_DIRS = (
    relpath('template/'),
    relpath('app0/template/'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_evolution',
    'labsite_dj15.app0',
    'django.contrib.admin',
    'django.contrib.admindocs',
    # 'dajaxice',
    # 'dajax',
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
AUTH_USER_MODEL = 'app0.User'

# URL
HOME_URL = '/m/my/'
LOGIN_REDIRECT_URL = HOME_URL
LOGIN_URL = '/m/login/'
LOGOUT_REDIRECT_URL = HOME_URL
LOGOUT_URL = '/m/logout/'
ASSIGNMENT_BASE_DIR = relpath('assignments/')
ASSIGNMENT_URL = '/m/ass/'
GRADE_URL = '/m/grade/'
REGISTER_URL = '/m/register/'
SUBMISSIONS_URL = '/m/subm/'
POST_URL = '/m/post'
