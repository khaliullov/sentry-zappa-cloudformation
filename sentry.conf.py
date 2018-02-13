# This file is just Python, with a touch of Django which means
# you can inherit and tweak settings to your hearts content.
from sentry.conf.server import *

import os.path

CONF_ROOT = os.path.dirname(__file__)
BASE_DIR = CONF_ROOT

INSTALLED_APPS += ('sentry_auth_google','sentry_plugins.jira','sentry_plugins.slack',)

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')

DEBUG_TOOLBAR_CONFIG = {
    'HIDE_IN_STACKTRACES': [],
}

WSGI_APPLICATION = 'sentry.wsgi.application'

SENTRY_FEATURES['auth:register'] = False

SENTRY_OPTIONS.update({
    'system.url-prefix': 'https://sentry.###REDACTED###',
    'system.secret-key': os.environ.get('SECRET_KEY',
                                        '###REDACTED###'),
    'mail.from': 'sentry@###REDACTED###',
    'mail.backend': 'django.core.mail.backends.smtp.EmailBackend',
    'mail.port': int(os.environ.get('EMAIL_PORT', 587)),
    'mail.host': os.environ.get('EMAIL_HOST', 'email-smtp.eu-west-1.amazonaws.com'),
    'mail.username': os.environ.get('EMAIL_HOST_USER', ''),
    'mail.password': os.environ.get('EMAIL_HOST_PASSWORD', ''),
    'mail.subject-prefix': '[Sentry] ',
    'mail.use-tls': bool(os.environ.get('EMAIL_USE_TLS', '1')),
    'redis.clusters': {
        'default': {
            'hosts': {
                 0: {
                     'host': os.environ.get('REDIS_HOST', 'localhost'),
                     'port': int(os.environ.get('REDIS_PORT', 6379)),
                }
            }
        }
    },
    'filestore.backend': 's3',
    'filestore.options': {
        'bucket_name': os.environ.get('AWS_S3_FILE_BUCKET', ''),
    },
})

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('DB_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('DB_USER', ''),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', ''),  # Set to empty string for localhost.
        'PORT': os.environ.get('DB_PORT', ''),  # Set to empty string for default.
        'AUTOCOMMIT': True,
        'ATOMIC_REQUESTS': False,
    }
}

# You should not change this setting after your database has been created
# unless you have altered all schemas first
SENTRY_USE_BIG_INTS = True

# If you're expecting any kind of real traffic on Sentry, we highly recommend
# configuring the CACHES and Redis settings

###########
# General #
###########

# Instruct Sentry that this install intends to be run by a single organization
# and thus various UI optimizations should be enabled.
SENTRY_SINGLE_ORGANIZATION = True
DEBUG = False

#########
# Cache #
#########

# Sentry currently utilizes two separate mechanisms. While CACHES is not a
# requirement, it will optimize several high throughput patterns.

# If you wish to use memcached, install the dependencies and adjust the config
# as shown:
#
#   pip install python-memcached
#
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': ['127.0.0.1:11211'],
#     }
# }

# A primary cache is required for things such as processing events
SENTRY_CACHE = 'sentry.cache.redis.RedisCache'

#########
# Queue #
#########

# See https://docs.sentry.io/on-premise/server/queue/ for more
# information on configuring your queue broker and workers. Sentry relies
# on a Python framework called Celery to manage queues.

CELERY_ALWAYS_EAGER = True
BROKER_URL = 'redis://' + os.environ.get('REDIS_HOST', 'localhost') + ':' + os.environ.get('REDIS_PORT', '6379')

###############
# Rate Limits #
###############

# Rate limits apply to notification handlers and are enforced per-project
# automatically.

SENTRY_RATELIMITER = 'sentry.ratelimits.redis.RedisRateLimiter'

##################
# Update Buffers #
##################

# Buffers (combined with queueing) act as an intermediate layer between the
# database and the storage API. They will greatly improve efficiency on large
# numbers of the same events being sent to the API in a short amount of time.
# (read: if you send any kind of real data to Sentry, you should enable buffers)

SENTRY_BUFFER = 'sentry.buffer.redis.RedisBuffer'

##########
# Quotas #
##########

# Quotas allow you to rate limit individual projects or the Sentry install as
# a whole.

SENTRY_QUOTAS = 'sentry.quotas.redis.RedisQuota'

########
# TSDB #
########

# The TSDB is used for building charts as well as making things like per-rate
# alerts possible.

SENTRY_TSDB = 'sentry.tsdb.redis.RedisTSDB'

###########
# Digests #
###########

# The digest backend powers notification summaries.

SENTRY_DIGESTS = 'sentry.digests.backends.redis.RedisBackend'

##############
# Web Server #
##############

# If you're using a reverse SSL proxy, you should enable the X-Forwarded-Proto
# header and uncomment the following settings
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# If you're not hosting at the root of your web server,
# you need to uncomment and set it to the path where Sentry is hosted.
# FORCE_SCRIPT_NAME = '/sentry'

# SENTRY_WEB_HOST = '0.0.0.0'
# SENTRY_WEB_PORT = 9000
SENTRY_WEB_OPTIONS = {
    'workers': 1,  # the number of web workers
    'protocol': 'uwsgi',  # Enable uwsgi protocol instead of http
}
