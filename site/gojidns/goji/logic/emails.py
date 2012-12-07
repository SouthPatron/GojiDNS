from ravensuite.utils.email import send_templated_email

import goji.models as gojiModels


BCC_LIST = [ '"Archive" <archive@gojidns.net>', ]
FROM_ADDRESS = '"South Patron" <support@gojidns.net>'


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



