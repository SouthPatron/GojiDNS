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


import urllib

from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages


import ravensuite.enums.world as large_enums

import goji.logic.emails as gojiEmails
import goji.logic.registration as gojiReg
import goji.forms as gojiForms
import goji.models as gojiModels



def index( request ):
	return render_to_response(
				'pages/public/index.html',
				{
				},
				context_instance=RequestContext(request)
			)



def register( request ):
	if request.method == 'POST' and request.POST:
		form = gojiForms.UserForm( request.POST )

		if form.is_valid() is True:
			email = form.cleaned_data[ 'email' ]
			password = form.cleaned_data[ 'password1' ]
			firstname = form.cleaned_data[ 'firstname' ]
			lastname = form.cleaned_data[ 'lastname' ]

			agreement = request.POST.get( 'agreement', None )

			if agreement is None:
				messages.error( request, _("You need to accept the terms and conditions to use this service.") )
			else:
				luser = gojiReg.RegisterNewUser( email, password, firstname, lastname  )
				ac = gojiReg.CreateUserAuthenticationCode( luser )

				gojiEmails.SendUserAuthenticationRequestEmail( luser, ac.code )

				messages.success( request, _("You should receive an email in your inbox shortly. Your authentication code will be in there.") )
				return redirect( reverse( 'goji-public-authenticate' ) )

		else:
			messages.error( request, _("There were some errors in your information. Please look below to find all the reasons and fix them up.") )
	else:
		form = gojiForms.UserForm()

	return render_to_response(
				'pages/public/register.html',
				{ 'form' : form },
				context_instance=RequestContext(request),
			)


def authenticate( request ):
	if request.method == 'POST' and request.POST:
		form = gojiForms.AuthenticationForm( request.POST )
		if form.is_valid() is True:
			cd = form.cleaned_data

			try:
				user = gojiReg.AuthenticateUser( code = cd['code'] )

				gojiEmails.SendUserRegistrationSuccessEmail( user )

				messages.success( request, _("You have been authenticated. You can now log in! :)") )
				return redirect( reverse( 'goji-public-login' ) )
			except gojiModels.AuthenticationCode.DoesNotExist:
				messages.error( request, _("No such authentication found. Please try again and check carefully. :-/") )

		else:
			messages.error( request, _("There were some errors. Please look below to find all the reasons and fix them up.") )

	else:
		form = gojiForms.AuthenticationForm()

	return render_to_response(
				'pages/public/authenticate.html',
				{ 'form' : form },
				context_instance=RequestContext(request),
			)


def resend_authentication( request ):
	if request.method == 'POST' and request.POST:

		email = request.POST.get( 'email', '' )

		if email != '':
			try:
				luser = User.objects.get( email = request.POST[ 'email' ] )
				ac = gojiReg.CreateUserAuthenticationCode( luser )
				gojiEmails.SendUserAuthenticationRequestEmail( luser, ac.code )
			except User.DoesNotExist:
				pass

			messages.success( request, _("An authentication email was sent to that address.") )
			return redirect( reverse( 'goji-public-authenticate' ) )
		else:
			messages.error( request, _("You have to enter your email address into the field.") )

	return render_to_response(
				'pages/public/resend_authentication.html',
				context_instance=RequestContext(request),
			)


def reset_password( request ):
	if request.method == 'POST' and request.POST:

		email = request.POST.get( 'email', '' )

		if email != '':
			try:
				luser = User.objects.get( email = request.POST[ 'email' ] )
				password = gojiReg.ResetUserPassword( luser )
				gojiEmails.SendUserPasswordResetEmail( luser, password )
			except User.DoesNotExist:
				pass

			messages.success( request, _("Your password was reset. Please wait for the reset email.") )
			return redirect( reverse( 'goji-public-login' ) )
		else:
			messages.error( request, _("You have to enter your email address into the field.") )

	return render_to_response(
				'pages/public/reset_password.html',
				context_instance=RequestContext(request),
			)


def confirm_email( request, code = None ):

	weGotIt = False

	if code is None and request.method == 'POST' and request.POST:
		code = request.POST.get( 'code', None )

	if code is not None:
		try:
			creq = gojiModels.EmailChangeRequest.objects.get( code = code )
			weGotIt = True
		except gojiModels.EmailChangeRequest.DoesNotExist:
			messages.warning( request, _("We couldn't find that code in our system. Please request an update again. Maybe it just expired or you've already used it.") )


	if weGotIt is True:
		user = creq.profile.user

		if creq.old_address == user.email:
			try:
				User.objects.get( email = creq.new_address )
				messages.error( request, _("That email address already exists on our system. Sorry. You have to pick another one. Perhaps you've already changed it?") )
				if request.user.is_authenticated() is True:
					return redirect( reverse( 'goji-profile' ) )

				return redirect( reverse( 'goji-public-login' ) )

			except User.DoesNotExist:
				pass

			user.email = creq.new_address
			user.save()
			messages.success( request, _("Your email address was updated as requested.") )
		else:
			messages.warning( request, _("Your email address has changed since your update request. We're going to err on the side of caution. Please try and update it again now.") )

		creq.delete()

		if request.user.is_authenticated() is True:
			return redirect( reverse( 'goji-profile' ) )

		return redirect( reverse( 'goji-public-login' ) )


	return render_to_response(
				'pages/public/confirm_email.html',
				context_instance=RequestContext(request),
			)


def login( request ):

	if request.method == 'POST' and request.POST:

		email = request.POST.get( 'email', '' )
		password = request.POST.get( 'password', '' )

		if email != '' and password != '':
			try:
				luser = User.objects.get( email = email )
				luser = auth.authenticate( username = luser.username, password = password )
				if luser is not None:
					if luser.is_active:
						auth.login( request, luser )

						if request.GET and request.GET.get( 'next', None ) is not None:
							next_url = request.GET.get( 'next' )

							if len( next_url ) > 0:
								return redirect( next_url )

						return redirect( reverse( 'goji-domain-list' ) )
					else:
						messages.error( request, _("You are not yet authenticated.") )
				else:
					messages.error( request, _("Either your username or password was incorrect. Please try again.") )

			except User.DoesNotExist:
				messages.error( request, _("Either your username or password was incorrect. Please try again.") )
		else:
			messages.error( request, _("You have to enter your email address and password into the fields below in order to login.") )


	return render_to_response(
				'pages/public/login.html',
				{
					'query' : urllib.parse.urlencode( request.GET ),
				},
				context_instance=RequestContext(request),
			)


def logout( request ):
	auth.logout( request )
	return redirect( reverse( 'goji-public-index' ) )



def faq( request ):
	obj_list = gojiModels.Faq.objects.all()
	return render_to_response(
				'pages/public/general/faq.html',
				{
					'list' : obj_list,
				},
				context_instance=RequestContext(request)
			)


