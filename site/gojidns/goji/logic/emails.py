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


from ravensuite.utils.email import send_templated_email, build_address

import goji.models as gojiModels


BCC_LIST = [ '"Archive" <archive@gojidns.com>', ]
FROM_ADDRESS = '"GojiDNS" <support@gojidns.com>'


def SendUserAuthenticationRequestEmail( user, code ):
	send_templated_email(
		'emails/authentication_request',
		FROM_ADDRESS,
		keys = { 'code' : code },
		user = user,
		bcc_list = BCC_LIST,
	)
	return True


def SendUserRegistrationSuccessEmail( user ):
	send_templated_email(
		'emails/registration_successful',
		FROM_ADDRESS,
		user = user,
		bcc_list = BCC_LIST,
	)
	return True


def SendUserPasswordResetEmail( user, password ):
	send_templated_email(
		'emails/password_reset',
		FROM_ADDRESS,
		keys = { 'new_password' : password },
		user = user,
		bcc_list = BCC_LIST,
	)
	return True


def SendUserEmailChangeConfirmation( user, req ):
	send_templated_email(
		'emails/email_change',
		FROM_ADDRESS,
		keys = { 'req' : req, },
		user = user,
		bcc_list = BCC_LIST,
	)
	return True



def SendContactUsEmail( user, req, subject, comment, ccself ):

	to_list = [ FROM_ADDRESS, ]
	cc_list = []

	if ccself is True: 
		cc_list = [ build_address( user ), ]

	send_templated_email(
		'emails/contact_form',
		FROM_ADDRESS,
		keys = {
			'subject' : subject,
			'comment' : comment,
			'req' : req,
		},
		to_list = to_list,
		cc_list = cc_list,
		bcc_list = BCC_LIST,
	)
	return True



