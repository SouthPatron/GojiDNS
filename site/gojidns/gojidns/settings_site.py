# GojiDNS - Developed by South Patron CC - http://www.southpatron.com/
#
# This file is part of GojiDNS.
#
# GojiDNS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GojiDNS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GojiDNS.  If not, see <http://www.gnu.org/licenses/>.
# from django.conf.urls import patterns, include, url
#


# Django settings for project.

DEBUG = False
TEMPLATE_DEBUG = False

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
		'NAME': 'gojidns',
		'USER': 'postgres',
		'PASSWORD': '',
		'HOST': '',
		'PORT': '',
	}
}

# ------------------ Email information

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ADMINS = (
	( 'Support', 'support@gojidns.com' ),
)

MANAGERS = ADMINS



# --- Here comes the local stuff.

try:
	from gojidns.settings_local import *
except ImportError as e:
	pass


