from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response, redirect
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
				context_instance=RequestContext(request),
			)


def logout( request ):
	auth.logout( request )
	return redirect( '/' )


