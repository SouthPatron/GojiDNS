import re
import datetime

from django.http import Http404

from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.core.validators import email_re

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.utils.ipv6 import is_valid_ipv6_address

from ravensuite.enums.world import CountryList, TimezoneList
from ravensuite.enums.datetime import MonthList

import goji.models as gojiModels
import goji.logic.emails as gojiEmails
import goji.logic.registration as gojiReg


# ----------- Message Exception ----------------------------

class MessageError( Exception ):
	pass

# ----------- Support Functions ----------------------------

DOMAIN = 'gojidns.net'

ttl_select_options = [ 
	[ 300, '(5 minutes)' ],
	[ 900, '(15 minutes)' ],
	[ 1800, '(30 minutes )' ],
	[ 3600, '(1 hour)' ],
	[ 7200, '(2 hours)' ],
	[ 14400, '(4 hours)' ],
	[ 28800, '(8 hours )' ],
	[ 57600, '(16 hours)' ],
	[ 86400, '(1 day)' ],
	[ 172800, '(2 days)' ],
	[ 345600, '(4 days)' ],
	[ 604800, '(1 week)' ],
	[ 1209600, '(2 weeks)' ],
	[ 2419200, '(4 weeks)' ]
]

def is_valid_hostname( domain ):
	hostname_re = re.compile(
			r'^(?![0-9]+$)(?!-)[a-zA-Z0-9-]{,63}(?<!-)$',
			re.IGNORECASE
		)
	return (hostname_re.search( domain ) is not None)


def is_valid_domain_name( domain ):
	domain_re = re.compile(
			r'^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))$',
			re.IGNORECASE
		)
	return (domain_re.search( domain ) is not None)

def is_valid_email( email ):
	return (email_re.match( email ) is not None)


def is_valid_ip4( address ):
	ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')
	return (ipv4_re.search( address ) is not None)


def is_valid_ip6( address ):
	return (is_valid_ipv6_address( address ))



def _get_resource_type( name ):
	if name == 'ns':
		return gojiModels.ResourceType.NS
	elif name == 'mx':
		return gojiModels.ResourceType.MX
	elif name == 'a':
		return gojiModels.ResourceType.A
	elif name == 'txt':
		return gojiModels.ResourceType.TXT
	elif name == 'cname':
		return gojiModels.ResourceType.CNAME
	elif name == 'srv':
		return gojiModels.ResourceType.SRV
	else:
		raise RuntimeError( 'No ResourceType matching {}'.format( name ) )

def _get_resource_template( action, rtype ):
	if rtype == gojiModels.ResourceType.NS:
		rname = 'ns'
	elif rtype == gojiModels.ResourceType.MX:
		rname = 'mx'
	elif rtype == gojiModels.ResourceType.A:
		rname = 'a'
	elif rtype == gojiModels.ResourceType.TXT:
		rname = 'txt'
	elif rtype == gojiModels.ResourceType.CNAME:
		rname = 'cname'
	elif rtype == gojiModels.ResourceType.SRV:
		rname = 'srv'
	else:
		raise RuntimeError( 'No such resource type: {}'.format( rtype ) )

	return 'pages/members/resources/{}_{}.html'.format( rname, action )


def parse_int( val, default = None ):
	try:
		if val is not None:
			return int( val )
	except TypeError:
		pass
	except ValueError:
		pass
	
	return default


def _validate_resource( rsc ):
	if rsc.resource_type == gojiModels.ResourceType.NS:
		if is_valid_domain_name( rsc.name ) is False:
			raise MessageError( _("The name server has to be a valid hostname") )
		if is_valid_hostname( rsc.value ) is False:
			if is_valid_domain_name( rsc.value ) is False:
				raise MessageError( _("The subdomain has to be a valid subdomain") )

		# TODO: This subdomain can not conflict with a CNAME
		return


	if rsc.resource_type == gojiModels.ResourceType.MX:
		if is_valid_domain_name( rsc.name ) is False:
			raise MessageError( _("The mail server has to be a valid hostname") )

		if is_valid_hostname( rsc.value ) is False:
			if is_valid_domain_name( rsc.value ) is False:
				raise MessageError( _("The subdomain has to be a valid subdomain") )

		if rsc.preference is None or rsc.preference < 0 or rsc.preference > 65535:
			raise MessageError( _("The preference field should be in the range of 0 to 65535 inclusive") )
		
		# TODO: This subdomain can not conflict with a CNAME
		return


	if rsc.resource_type == gojiModels.ResourceType.A:

		if is_valid_domain_name( rsc.name ) is False:
			if is_valid_hostname( rsc.name ) is False:
				raise MessageError( _("The hostname has to be a valid hostname") )

		if is_valid_ip4( rsc.value ) is False:
			if is_valid_ip6( rsc.value ) is False:
				raise MessageError( _("The IP address has to be a valid IPv4 or IPv6 address") )


		return


	if rsc.resource_type == gojiModels.ResourceType.CNAME:

		if is_valid_domain_name( rsc.name ) is False:
			if is_valid_hostname( rsc.name ) is False:
				raise MessageError( _("The hostname has to be a valid hostname") )

		if is_valid_domain_name( rsc.value ) is False:
				raise MessageError( _("The alias has to be a valid domain name") )

		# TODO: This subdomain can not conflict with a CNAME
		return


	if rsc.resource_type == gojiModels.ResourceType.TXT:
		return


	if rsc.resource_type == gojiModels.ResourceType.SRV:


		if rsc.preference is None or rsc.preference < 0 or rsc.preference > 65535:
			raise MessageError( _("The priority has to be between 0 and 65535 inclusive") )

		if rsc.weight is None or rsc.weight < 0 or rsc.weight > 65535:
			raise MessageError( _("The weight has to be between 0 and 65535 inclusive") )

		if rsc.port is None or rsc.port < 0 or rsc.port > 65535:
			raise MessageError( _("The port has to be between 0 and 65535 inclusive") )

		return


	raise MessageError( _("Unknown resource type") )





def _update_resource( request, rsc, save = True ):
	if rsc.static is True:
		raise MessageError( _("This entry can not be updated.") )

	rsc.name = request.POST.get( 'name' )
	rsc.value = request.POST.get( 'value' )
	rsc.preference = parse_int( request.POST.get( 'preference', None ) )
	rsc.ttl = parse_int( request.POST.get( 'ttl', None ) )

	rsc.protocol = parse_int( request.POST.get( 'protocol', None ) )
	rsc.port = parse_int( request.POST.get( 'port', None ) )
	rsc.weight = parse_int( request.POST.get( 'weight', None ) )

	_validate_resource( rsc )

	if save is True:
		rsc.save()
	
	return rsc


# ----------- Views --------------------------------------



@login_required
def domain_list( request ):
	obj_list = gojiModels.Domain.objects.filter( profile__user = request.user ).exclude( status = gojiModels.DomainStatus.DELETED )
	return render_to_response(
				'pages/members/domain_list.html',
				{
					'list' : obj_list
				},
				context_instance=RequestContext(request)
			)


@login_required
def domain( request, domain ):
	try:
		obj = gojiModels.Domain.objects.exclude( status = gojiModels.DomainStatus.DELETED ).get( name = domain, profile__user = request.user )
	except gojiModels.Domain.DoesNotExist:
		messages.error( request, _("That domain does exist. Unable to view it.") )
		return redirect( reverse( 'goji-domain-list' ) )

	return render_to_response(
				'pages/members/domain.html',
				{
					'domain' : obj,
				},
				context_instance=RequestContext(request)
			)


@login_required
def domain_edit( request, domain ):

	try:
		dom = gojiModels.Domain.objects.exclude( status = gojiModels.DomainStatus.DELETED ).get( name = domain, profile__user = request.user )
	except gojiModels.Domain.DoesNotExist:
		messages.error( request, _("That domain does exist. Unable to view it.") )
		return redirect( reverse( 'goji-domain-list' ) )

	if request.method == 'POST' and request.POST is not None:

		dom.status = parse_int( request.POST.get( 'status', dom.status ), dom.status )
		dom.email = request.POST.get( 'email', dom.email )

		dom.ttl = parse_int( request.POST.get( 'ttl', dom.ttl ), dom.ttl )
		dom.refresh = parse_int( request.POST.get( 'refresh', dom.refresh ) )
		dom.retry = parse_int( request.POST.get( 'retry', dom.retry ) )
		dom.expire = parse_int( request.POST.get( 'expire', dom.expire ) )

		dom.save()

		return redirect( reverse( 'goji-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				'pages/members/domain_edit.html',
				{
					'domain' : dom,
					'ttl_options' : ttl_select_options,
				},
				context_instance=RequestContext(request)
			)



@login_required
def domain_add( request ):

	domain = ''
	email = ''

	if request.method == 'POST' and request.POST is not None:
		domain = request.POST.get( 'domain' )
		email = request.POST.get( 'email' )


		createIt = True

		if is_valid_domain_name( domain ) is False:
			messages.error( request, _("That domain name doesn't look valid. Please try again.") )
			createIt = False
		else:
			if is_valid_email( email ) is False:
				messages.error( request, _("You need to enter a valid email address for the SOA. Please try again.") )
				createIt = False

	
		if createIt is True:
			try:
				try:
					dom = gojiModels.Domain.objects.get( name = domain )
					if dom.status == gojiModels.DomainStatus.DELETED:
						dom.delete()
				except gojiModels.Domain.DoesNotExist:
					pass

				dom = gojiModels.Domain.objects.create(
						profile = request.user.goji_profile,
						name = domain,
						primary = 'ns1.{}'.format( DOMAIN ),
						email = email
					)

				for xnum in range(1,3):
					gojiModels.Resource.objects.create(
						domain = dom,
						resource_type = gojiModels.ResourceType.NS,
						name = 'ns{}.{}'.format( xnum, DOMAIN ) ,
						value = '',
						static = True,
					)

				return redirect( reverse( 'goji-domain', kwargs = { 'domain' : domain } ) )

			except IntegrityError, ie:
				messages.error( request, _("That domain name already exists in our system. You'll have to choose another.") )

	return render_to_response(
				'pages/members/domain_add.html',
				{
					'domain' : domain,
					'email' : email,
				},
				context_instance=RequestContext(request)
			)

@login_required
def domain_clone( request ):

	source = ''
	target = ''
	replace = 'yes'

	if request.method == 'POST' and request.POST is not None:

		source = request.POST.get( 'source' )
		target = request.POST.get( 'target' )
		replace = request.POST.get( 'replace', None )

		createIt = True

		if createIt is True and is_valid_domain_name( source ) is False:
			messages.error( request, _("Please select a valid source domain from which to clone.") )
			createIt = False

		if createIt is True and is_valid_domain_name( target ) is False:
			messages.error( request, _("The target domain name doesn't appear to be valid. Please try again.") )
			createIt = False

		if createIt is True:
			try:
				sdom = gojiModels.Domain.objects.exclude( status = gojiModels.DomainStatus.DELETED ).get( name = source, profile__user = request.user )

			except gojiModels.Domain.DoesNotExist:
				messages.error( request, _("The source domain doesn't exist. Please try again.") )
				createIt = False

		if createIt is True:
			try:
				ddom = gojiModels.Domain.objects.get( name = target )

				if ddom.status == gojiModels.DomainStatus.DELETED:
					ddom.delete()
				else:
					messages.error( request, _("The target domain already exists on our system. Please try again.") )
					createIt = False

			except gojiModels.Domain.DoesNotExist:
				pass


		if createIt is True:
			oldid = sdom.pk

			sdom.pk = None
			sdom.name = target
			sdom.save()

			for rsc in gojiModels.Resource.objects.filter( domain = oldid ):
				rsc.pk = None
				rsc.domain = sdom

				if replace is not None:

					if rsc.value == source:
						rsc.value = target
					else:
						rsc.value = rsc.value.replace( source, target, 1 )

				rsc.save()

			return redirect( reverse( 'goji-domain', kwargs = { 'domain' : target } ) )


	obj_list = gojiModels.Domain.objects.filter( profile__user = request.user ).exclude( status = gojiModels.DomainStatus.DELETED )

	return render_to_response(
				'pages/members/domain_clone.html',
				{
					'list' : obj_list,
					'source' : source,
					'target' : target,
					'replace' : replace,
				},
				context_instance=RequestContext(request)
			)


@login_required
def domain_delete( request, domain ):
	try:
		dom = gojiModels.Domain.objects.exclude( status = gojiModels.DomainStatus.DELETED ).get( name = domain, profile__user = request.user )

	except gojiModels.Domain.DoesNotExist:
		messages.error( request, _("That domain does not appear to exist.") )
		return redirect( reverse( 'goji-domain-list' ) )


	if request.method == 'POST' and request.POST is not None:
		dom.status = gojiModels.DomainStatus.DELETED
		dom.save()
		return redirect( reverse( 'goji-domain-list' ) )

	return render_to_response(
				'pages/members/domain_delete.html',
				{
					'domain' : dom,
				},
				context_instance=RequestContext(request)
			)


@login_required
def domain_resource_add( request, domain ):

	rtype = _get_resource_type( request.GET.get( 'type', 'ns' ) )
	tname = _get_resource_template( 'add', rtype )

	dom = get_object_or_404( gojiModels.Domain, name = domain, profile__user = request.user )

	if request.method == 'POST' and request.POST is not None:
		rsc = gojiModels.Resource(
				resource_type = rtype,
				domain = dom,
			)

		try:
			_update_resource( request, rsc )
			return redirect( reverse( 'goji-domain', kwargs = { 'domain' : domain } ) )
		except MessageError, merr:
			messages.error( request, merr.message )
			pass

	return render_to_response(
				tname,
				{
					'domain' : dom,
					'ttl_options' : ttl_select_options,
				},
				context_instance=RequestContext(request)
			)


@login_required
def domain_resource_edit( request, domain, rid ):

	rsc = get_object_or_404( gojiModels.Resource, pk = rid, domain__name = domain, domain__profile__user = request.user )
	tname = _get_resource_template( 'edit', rsc.resource_type )

	if request.method == 'POST' and request.POST is not None:

		try:
			_update_resource( request, rsc )
			return redirect( reverse( 'goji-domain', kwargs = { 'domain' : domain } ) )
		except MessageError, merr:
			messages.error( request, merr.message )
			pass

	return render_to_response(
				tname,
				{
					'domain' : rsc.domain,
					'resource' : rsc,
					'ttl_options' : ttl_select_options,
				},
				context_instance=RequestContext(request)
			)


@login_required
def domain_resource_delete( request, domain, rid ):

	rsc = get_object_or_404( gojiModels.Resource, pk = rid, domain__name = domain, domain__profile__user = request.user )

	tname = _get_resource_template( 'delete', rsc.resource_type )

	if request.method == 'POST' and request.POST is not None:
		rsc.delete()
		return redirect( reverse( 'goji-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				tname,
				{
					'domain' : rsc.domain,
					'resource' : rsc,
				},
				context_instance=RequestContext(request)
			)




@login_required
def profile( request ):

	prof = request.user.goji_profile

	if request.method == 'POST' and request.POST is not None:
		prof.user.first_name = request.POST.get( 'first_name', prof.user.first_name )
		prof.user.last_name = request.POST.get( 'last_name', prof.user.last_name )
		prof.user.save()

		new_email = request.POST.get( 'email', prof.user.email )
		if new_email != prof.user.email:
			try:
				User.objects.get( email = new_email )
				messages.error( request, _("That email address already exists on our system. Sorry. You have to pick another one. Perhaps you've already changed it?") )
			except User.DoesNotExist:
				req = gojiReg.CreateUserEmailChangeCode( prof.user, new_email )
				gojiEmails.SendUserEmailChangeConfirmation( request.user, req )


		dob_day = parse_int( request.POST.get( 'dob_day', None ) )
		dob_month = parse_int( request.POST.get( 'dob_month', None ) )
		dob_year = parse_int( request.POST.get( 'dob_year', None ) )

		if dob_day is not None and dob_month is not None and dob_year is not None:
			prof.dob = datetime.date( day = dob_day, month = dob_month, year = dob_year )


		gender = parse_int( request.POST.get( 'gender', None ) )
		if gender is not None:
			if gender == 0:
				gender = None

		prof.gender = gender

		country = request.POST.get( 'country', None )
		if country is not None and country == '':
			country = None
		prof.country = country

		timezone = request.POST.get( 'timezone', None )
		if timezone is not None and timezone == '':
			timezone = None
		prof.timezone = timezone or 'UTC'


		prof.website = request.POST.get( 'website', None )
		prof.location = request.POST.get( 'location', None )
		prof.phone = request.POST.get( 'phone', None )


		prof.save()
		return redirect( reverse( 'goji-profile' ) )

	start_year = 1900
	end_year = datetime.date.today().year + 1

	return render_to_response(
				'pages/members/profile.html',
				{
					'profile' : prof,
					'countries' : CountryList.choices(),
					'timezones' : TimezoneList.choices(),
					'days' : range(1,32),
					'months' : MonthList.choices(),
					'years' : range( start_year, end_year ),
				},
				context_instance=RequestContext(request)
			)


@login_required
def change_password( request ):


	if request.method == 'POST' and request.POST is not None:
		old_password = request.POST.get( 'current', None )
		new_password1 = request.POST.get( 'new_password1', None )
		new_password2 = request.POST.get( 'new_password2', None )

		messages.error( request, _("Those passwords do not match.") )

		return redirect( reverse( 'goji-change-password' ) )


	return render_to_response(
				'pages/members/change_password.html',
				{
				},
				context_instance=RequestContext(request)
			)



@login_required
def network_status( request ):
	obj_list = gojiModels.NameserverStatus.objects.all()
	return render_to_response(
				'pages/members/network_status.html',
				{
					'list' : obj_list,
				},
				context_instance=RequestContext(request)
			)


