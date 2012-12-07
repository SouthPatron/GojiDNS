import re

from django.utils.translation import ugettext as _

from django.core.urlresolvers import reverse
from django.core.validators import email_re

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.db import IntegrityError
from django.contrib import messages

import goji.models as gojiModels


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

def is_valid_domain_name( domain ):
	domain_re = re.compile(
			r'^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))$',
			re.IGNORECASE
		)
	return (domain_re.search( domain ) is not None)



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


def _update_resource( request, rsc, save = True ):
	rsc.name = request.POST.get( 'name' )
	rsc.value = request.POST.get( 'value' )
	rsc.preference = parse_int( request.POST.get( 'preference', None ) )
	rsc.ttl = parse_int( request.POST.get( 'ttl', None ) )

	rsc.protocol = parse_int( request.POST.get( 'protocol', None ) )
	rsc.port = parse_int( request.POST.get( 'port', None ) )
	rsc.weight = parse_int( request.POST.get( 'weight', None ) )

	if save is True:
		rsc.save()
	
	return rsc


# ----------- Views --------------------------------------



def domain_list( request ):
	obj_list = gojiModels.Domain.objects.filter( profile__user = request.user )
	return render_to_response(
				'pages/members/domain_list.html',
				{
					'list' : obj_list
				},
				context_instance=RequestContext(request)
			)

def domain( request, domain ):
	obj = get_object_or_404( gojiModels.Domain, name = domain, profile__user = request.user )
	return render_to_response(
				'pages/members/domain.html',
				{
					'domain' : obj,
				},
				context_instance=RequestContext(request)
			)


def domain_edit( request, domain ):

	dom = get_object_or_404( gojiModels.Domain, name = domain, profile__user = request.user )

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
			if email_re.match( email ) is None:
				messages.error( request, _("You need to enter a valid email address for the SOA. Please try again.") )
				createIt = False

	
		if createIt is True:
			try:
				dom = gojiModels.Domain.objects.create(
						profile = request.user.goji_profile,
						name = domain,
						primary = 'ns1.{}'.format( DOMAIN ),
						email = email
					)

				for xnum in range(1,6):
					gojiModels.Resource.objects.create(
						domain = dom,
						resource_type = gojiModels.ResourceType.NS,
						name = 'ns{}.{}'.format( xnum, DOMAIN ) ,
						value = domain,
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
				sdom = gojiModels.Domain.objects.get( name = source, profile__user = request.user )

			except gojiModels.Domain.DoesNotExist:
				messages.error( request, _("The source domain doesn't exist. Please try again.") )
				createIt = False

		if createIt is True:
			try:
				ddom = gojiModels.Domain.objects.get( name = target )
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


	obj_list = gojiModels.Domain.objects.filter( profile__user = request.user )
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


def domain_delete( request, domain ):
	try:
		dom = gojiModels.Domain.objects.get( name = domain, profile__user = request.user )
	except gojiModels.Domain.DoesNotExist:
		messages.error( request, _("That domain does not appear to exist. Nothing deleted.") )
		return redirect( reverse( 'goji-domain-list' ) )


	if request.method == 'POST' and request.POST is not None:
		dom.delete()
		return redirect( reverse( 'goji-domain-list' ) )

	return render_to_response(
				'pages/members/domain_delete.html',
				{
					'domain' : dom,
				},
				context_instance=RequestContext(request)
			)


def domain_resource_add( request, domain ):

	rtype = _get_resource_type( request.GET.get( 'type', 'ns' ) )
	tname = _get_resource_template( 'add', rtype )

	dom = get_object_or_404( gojiModels.Domain, name = domain, profile__user = request.user )

	if request.method == 'POST' and request.POST is not None:
		rsc = gojiModels.Resource(
				resource_type = rtype,
				domain = dom,
			)

		_update_resource( request, rsc )
		return redirect( reverse( 'goji-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				tname,
				{
					'domain' : dom,
					'ttl_options' : ttl_select_options,
				},
				context_instance=RequestContext(request)
			)


def domain_resource_edit( request, domain, rid ):

	rsc = get_object_or_404( gojiModels.Resource, pk = rid, domain__name = domain, domain__profile__user = request.user )
	tname = _get_resource_template( 'edit', rsc.resource_type )

	if request.method == 'POST' and request.POST is not None:
		_update_resource( request, rsc )
		return redirect( reverse( 'goji-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				tname,
				{
					'domain' : rsc.domain,
					'resource' : rsc,
					'ttl_options' : ttl_select_options,
				},
				context_instance=RequestContext(request)
			)


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


