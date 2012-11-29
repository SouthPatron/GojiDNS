# Django settings for project.


DEBUG=False
TEMPLATE_DEBUG=False

TIME_ZONE = 'UTC'
USE_TZ = True

LOGIN_URL='/login'
LOGIN_REDIRECT_URL='/home'
LOGOUT_URL='/logout'

USE_I18N = True
USE_L10N = True
LANGUAGE_CODE = 'en-us'

ugettext = lambda s: s
LANGUAGES = (
	('en', ugettext('English')),
)


MEDIA_ROOT = ''
MEDIA_URL = ''

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')kt0vroa=ayl16fyl0d6+wzh^0_k1fggah$y^=m9gt3+9_nlu9'

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
	'django.contrib.messages.context_processors.messages',

	# Hereforth, non-default context processors
	'django.core.context_processors.request',
)


MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.middleware.transaction.TransactionMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dna.urls'

WSGI_APPLICATION = 'dnssystem.wsgi.application'


INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	'django.contrib.admin',
	'django.contrib.admindocs',

	'dna',

	'ravensuite',

)

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



# Load site specific configurations

try:
	from settings_site import *
except ImportError, e:
	pass


