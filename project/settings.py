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
            'NAME': 'nlp_project',
            'USER': 'nlp_project',
            'PORT': 17806,
            'PASSWORD': 'nlp_project',
            'HOST': '127.0.0.1',
        }
    }

SECRET_KEY = '_mw2k_abk#x97bc#_w*fb%&k#uw9_3*63@3kzl(2hb)!lbi8j$'
INSTALLED_APPS = ['bdbk', 'zhwiki']
MIDDLEWARE_CLASSES = []
