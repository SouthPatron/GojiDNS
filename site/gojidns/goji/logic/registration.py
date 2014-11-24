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


from django.contrib.auth.models import User
from django.db import IntegrityError

import goji.models as gojiModels


def RegisterNewUser( email, password, firstname, lastname ):
	luser = None
	failures = 0

	while luser is None:
		try:
			username = User.objects.make_random_password( length = 30 )
			luser = User.objects.create_user( username, email, password )

			luser.first_name = firstname
			luser.last_name = lastname
			luser.is_active = False
			luser.is_staff = False
			luser.is_superuser = False
			luser.save()

			return luser

		except IntegrityError as ie:
			failures += 1
			if failures > 16:
				raise	# Significant error
			luser = None

def ResetUserPassword( luser ):
	password = User.objects.make_random_password( length = 30 )
	luser.set_password( password )
	luser.save()
	return password


def CreateUserAuthenticationCode( luser ):
	failures = 0

	while failures < 20:
		try:
			ac = gojiModels.AuthenticationCode.objects.create( profile = luser.goji_profile, code = User.objects.make_random_password( length = 16 ) )
			return ac
		except IntegrityError:
			failures += 1
			if failures > 16:
				raise

def AuthenticateUser( code ):
	ac = gojiModels.AuthenticationCode.objects.get( code = code )
	ac.profile.user.is_active = True
	ac.profile.user.save()
	ac.delete()
	return ac.profile.user


def CreateUserEmailChangeCode( luser, new_email ):
	failures = 0

	while failures < 20:
		try:
			ac = gojiModels.EmailChangeRequest.objects.create(
					profile = luser.goji_profile,
					code = User.objects.make_random_password( length = 16 ),
					old_address = luser.email,
					new_address = new_email,
				)
			return ac
		except IntegrityError:
			failures += 1
			if failures > 16:
				raise



