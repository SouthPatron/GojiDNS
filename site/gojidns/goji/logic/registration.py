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

		except IntegrityError, ie:
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
			ac = gojiModels.AuthenticationCode.objects.create( profile = luser.sp_profile, code = User.objects.make_random_password( length = 16 ) )
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



