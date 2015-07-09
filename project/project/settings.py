import os

# before turning off this switch:
# 1. make sure you have managed all static files
DEBUG=True

if os.environ.has_key('NLP_DEBUG'):
    print 'Enter debug mode for database.'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'nlp_project.db'
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'QA_Project',
            'USER': 'nlp_project',
            'PORT': 3306,
            'PASSWORD': 'nlp_project',
            'HOST': '127.0.0.1',
        }
    }

SECRET_KEY = '_mw2k_abk#x97bc#_w*fb%&k#uw9_3*63@3kzl(2hb)!lbi8j$'
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'bdbk',
    'zhwiki',
    'processor',
    'ui'
]
MIDDLEWARE_CLASSES = []

ALLOWED_HOSTS = ['localhost']
ROOT_URLCONF = 'project.urls'

STATIC_URL = '/static/'
# set this to the static file directory you want to serve in a production server
# STATIC_ROOT =
