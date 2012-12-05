
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'gojidns',
		'USER': 'gojidns_www',
		'PASSWORD': 'dog elephant shoe',
		'HOST': '',
		'PORT': '',
	}
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

"""
LOGGING = { 
	'version': 1,
	'disable_existing_loggers': True,
	'formatters': {
		'simple': {
			'format': '%(levelname)s %(message)s',
		},  
	},  
	'handlers': {
		'console':{
			'level':'DEBUG',
			'class':'logging.StreamHandler',
			'formatter': 'simple'
		},  
	},  
	'loggers': {
		'django': {
			'handlers': ['console'],
			'level': 'DEBUG',
		},  
	}   
}
"""
