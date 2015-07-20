import os

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
    'spider',
    'zhwiki',
    'ui',
]
MIDDLEWARE_CLASSES = []

USE_TZ = True
TIME_ZONE = 'Asia/Shanghai'

ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'project.urls'

STATIC_URL = '/static/'
# set this to the static file directory you want to serve in a production server
# STATIC_ROOT = 'static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s Process:%(process)d Thread:%(thread)d - %(message)s'
        },
        'standard': {
            'format': '%(levelname)s %(asctime)s %(module)s - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'file-main': {
            'level': 'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django_request.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'file-maintaince': {
            'level': 'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django_maintaince.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 20,
            'formatter':'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['file-main', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'bdbk.extractor': {
            'handlers': ['file-maintaince'],
            'level': 'INFO',
            'propagate': False
        },
        'spider.handler': {
            'handlers': ['file-maintaince'],
            'level': 'INFO',
            'propagate': False
        },
    },

}

SCRAPY_LOG_FILE = 'logs/spider.log'
SCRAPY_LOG_LEVEL = 'INFO'

BDBK_SETTINGS = {
    'page_source_mongodb': {
        'host': 'localhost',
        'port': 11111,
    }
}
