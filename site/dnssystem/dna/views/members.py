from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext

import dna.models as dnaModels

# ----------- Support Functions ----------------------------

DOMAIN = 'dnadns.co.za'

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

def _get_resource_type( name ):
	if name == 'ns':
		return dnaModels.ResourceType.NS
	elif name == 'mx':
		return dnaModels.ResourceType.MX
	elif name == 'a':
		return dnaModels.ResourceType.A
	elif name == 'txt':
		return dnaModels.ResourceType.TXT
	elif name == 'cname':
		return dnaModels.ResourceType.CNAME
	elif name == 'srv':
		return dnaModels.ResourceType.SRV
	else:
		raise RuntimeError( 'No ResourceType matching {}'.format( name ) )

def _get_resource_template( action, rtype ):
	if rtype == dnaModels.ResourceType.NS:
		rname = 'ns'
	elif rtype == dnaModels.ResourceType.MX:
		rname = 'mx'
	elif rtype == dnaModels.ResourceType.A:
		rname = 'a'
	elif rtype == dnaModels.ResourceType.TXT:
		rname = 'txt'
	elif rtype == dnaModels.ResourceType.CNAME:
		rname = 'cname'
	elif rtype == dnaModels.ResourceType.SRV:
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
	obj_list = dnaModels.Domain.objects.all()
	return render_to_response(
				'pages/members/domain_list.html',
				{
					'list' : obj_list
				},
				context_instance=RequestContext(request)
			)

def domain( request, domain ):
	obj = get_object_or_404( dnaModels.Domain, name = domain )
	return render_to_response(
				'pages/members/domain.html',
				{
					'domain' : obj,
				},
				context_instance=RequestContext(request)
			)


def domain_edit( request, domain ):

	dom = get_object_or_404( dnaModels.Domain, name = domain )

	if request.method == 'POST' and request.POST is not None:

		dom.status = parse_int( request.POST.get( 'status', dom.status ), dom.status )
		dom.email = request.POST.get( 'email', dom.email )

		dom.ttl = parse_int( request.POST.get( 'ttl', dom.ttl ), dom.ttl )
		dom.refresh = parse_int( request.POST.get( 'refresh', dom.refresh ) )
		dom.retry = parse_int( request.POST.get( 'retry', dom.retry ) )
		dom.expire = parse_int( request.POST.get( 'expire', dom.expire ) )

		dom.save()

		return redirect( reverse( 'dna-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				'pages/members/domain_edit.html',
				{
					'domain' : dom,
					'ttl_options' : ttl_select_options,
				},
				context_instance=RequestContext(request)
			)



def domain_add( request ):

	if request.method == 'POST' and request.POST is not None:
		domain = request.POST.get( 'domain' )
		email = request.POST.get( 'email' )

		dom = dnaModels.Domain.objects.create(
				name = domain,
				primary = 'ns1.{}'.format( DOMAIN ),
				email = email
			)

		for xnum in range(1,6):
			dnaModels.Resource.objects.create(
				domain = dom,
				resource_type = dnaModels.ResourceType.NS,
				name = 'ns{}.{}'.format( xnum, DOMAIN ) ,
				value = domain,
				static = True,
			)

		return redirect( reverse( 'dna-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				'pages/members/domain_add.html',
				{
				},
				context_instance=RequestContext(request)
			)

def domain_clone( request ):
	if request.method == 'POST' and request.POST is not None:

		source = request.POST.get( 'source' )
		target = request.POST.get( 'target' )
		replace = request.POST.get( 'replace', None )

		sdom = get_object_or_404( dnaModels.Domain, name = source )

		oldid = sdom.pk

		sdom.pk = None
		sdom.name = target
		sdom.save()

		for rsc in dnaModels.Resource.objects.filter( domain = oldid ):
			rsc.pk = None
			rsc.domain = sdom

			if replace is not None:

				if rsc.value == source:
					rsc.value = target
				else:
					rsc.value = rsc.value.replace( source, target, 1 )

			rsc.save()

		return redirect( reverse( 'dna-domain', kwargs = { 'domain' : target } ) )


	obj_list = dnaModels.Domain.objects.all()
	return render_to_response(
				'pages/members/domain_clone.html',
				{
					'list' : obj_list,
				},
				context_instance=RequestContext(request)
			)


def domain_delete( request, domain ):
	dom = get_object_or_404( dnaModels.Domain, name = domain )

	if request.method == 'POST' and request.POST is not None:
		dom.delete()
		return redirect( reverse( 'dna-domain-list' ) )

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

	dom = get_object_or_404( dnaModels.Domain, name = domain )

	if request.method == 'POST' and request.POST is not None:
		rsc = dnaModels.Resource(
				resource_type = rtype,
				domain = dom,
			)

		_update_resource( request, rsc )
		return redirect( reverse( 'dna-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				tname,
				{
					'domain' : dom,
					'ttl_options' : ttl_select_options,
				},
				context_instance=RequestContext(request)
			)


def domain_resource_edit( request, domain, rid ):

	rsc = get_object_or_404( dnaModels.Resource, pk = rid, domain__name = domain )
	tname = _get_resource_template( 'edit', rsc.resource_type )

	if request.method == 'POST' and request.POST is not None:
		_update_resource( request, rsc )
		return redirect( reverse( 'dna-domain', kwargs = { 'domain' : domain } ) )

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

	rsc = get_object_or_404( dnaModels.Resource, pk = rid, domain__name = domain )

	tname = _get_resource_template( 'delete', rsc.resource_type )

	if request.method == 'POST' and request.POST is not None:
		rsc.delete()
		return redirect( reverse( 'dna-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				tname,
				{
					'domain' : rsc.domain,
					'resource' : rsc,
				},
				context_instance=RequestContext(request)
			)


