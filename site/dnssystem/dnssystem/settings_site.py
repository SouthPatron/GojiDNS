# Django settings for project.

DEBUG = True
TEMPLATE_DEBUG = True

# --- These settings should be overriden in settings_local.py, especially
# --- the databases.

import os
from os.path import dirname

SITE_ID = 1

# ------------------ File locations

WEBSITE_BASE = dirname( dirname( dirname( dirname( __file__ ) ) ) )

STATIC_ROOT = WEBSITE_BASE + '/static'


# ------------------- Database information

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'dnssystem',
		'USER': 'postgres',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

# ------------------ Email information

SEND_BROKEN_LINK_EMAILS = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ADMINS = (
	( 'Support', 'support@smksoftware.com' ),
)

MANAGERS = ADMINS



# --- Here comes the local stuff.

try:
	from settings_local import *
except ImportError, e:
	pass


