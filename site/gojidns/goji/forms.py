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


from django.contrib.auth.models import User
from django import forms
from goji.models import AuthenticationCode


class AuthenticationForm( forms.Form ):
	code = forms.CharField( required = True )


class UserForm( forms.Form ):

	email = forms.EmailField( required = True )

	firstname = forms.CharField( required = True, max_length = 255, min_length = 1 )
	lastname = forms.CharField( required = True, max_length = 256, min_length = 1 )
	password1 = forms.CharField( required = True, max_length = 256, min_length = 6 )
	password2 = forms.CharField( required = True, max_length = 256, min_length = 6 )


	def clean( self ):
		cleaned_data = super(UserForm, self).clean()

		email = cleaned_data.get( 'email', '' )

		if User.objects.filter( email = email ).count() > 0:
			msg = u"That email address is already registered!"
			self._errors['email'] = self.error_class([msg])
			del cleaned_data['email']


		pass1 = cleaned_data.get( 'password1', '' )
		pass2 = cleaned_data.get( 'password2', '' )

		if pass1 != pass2:
			msg = u"Password fields must match!"
			self._errors['password1'] = self.error_class([msg])
			self._errors['password2'] = self.error_class([msg])
			del cleaned_data['password1']
			del cleaned_data['password2']

		return cleaned_data


