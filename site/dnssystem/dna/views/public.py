from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext

import dna.models as dnaModels

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


def home( request ):
	obj_list = dnaModels.Domain.objects.all()
	return render_to_response(
				'pages/home.html',
				{
					'list' : obj_list
				},
				context_instance=RequestContext(request)
			)

def domain( request, domain ):
	obj = get_object_or_404( dnaModels.Domain, name = domain )
	return render_to_response(
				'pages/domain.html',
				{
					'domain' : obj,
				},
				context_instance=RequestContext(request)
			)

def domain_add( request ):

	if request.method == 'POST' and request.POST is not None:
		domain = request.POST.get( 'domain' )
		email = request.POST.get( 'email' )

		dom = dnaModels.Domain.objects.create(
				name = domain,
				primary = 'ns1.djm.co.za',
				email = email
			)

		return redirect( reverse( 'dna-domain', kwargs = { 'domain' : domain } ) )

	return render_to_response(
				'pages/domain_add.html',
				{
				},
				context_instance=RequestContext(request)
			)

def domain_clone( request ):
	if request.method == 'POST' and request.POST is not None:

		source = request.POST.get( 'source' )
		target = request.POST.get( 'target' )

		sdom = get_object_or_404( dnaModels.Domain, name = source )

		oldid = sdom.pk

		sdom.pk = None
		sdom.name = target
		sdom.save()

		for rsc in dnaModels.Resource.objects.filter( domain = oldid ):
			rsc.pk = None
			rsc.domain = sdom
			rsc.save()

		return redirect( reverse( 'dna-domain', kwargs = { 'domain' : target } ) )


	obj_list = dnaModels.Domain.objects.all()
	return render_to_response(
				'pages/domain_clone.html',
				{
					'list' : obj_list,
				},
				context_instance=RequestContext(request)
			)


def domain_delete( request, domain ):
	if request.method == 'POST' and request.POST is not None:
		dom = get_object_or_404( dnaModels.Domain, name = domain )
		dom.delete()
		return redirect( reverse( 'dna-home' ) )

	return render_to_response(
				'pages/domain_delete.html',
				{},
				context_instance=RequestContext(request)
			)


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

	return 'pages/resources/{}_{}.html'.format( rname, action )


def _update_resource( request, rsc, save = True ):
	rsc.name = request.POST.get( 'name' )
	rsc.value = request.POST.get( 'value' )

	try:
		val = request.POST.get( 'preference', None )
		if val is not None:
			val = int( val )

		rsc.preference = val
	except ValueError:
		rsc.preference = None

	try:
		val = request.POST.get( 'ttl', None )
		if val is not None:
			val = int( val )

		rsc.ttl = val
	except ValueError:
		rsc.ttl = None

	if save is True:
		rsc.save()
	
	return rsc



def domain_resource_add( request, domain ):

	rtype = _get_resource_type( request.GET.get( 'type', 'ns' ) )
	tname = _get_resource_template( 'add', rtype )

	dom = get_object_or_404( dnaModels.Domain, name = domain )

	if request.method == 'POST' and request.POST is not None:
		rsc = dnaModels.Resource(
				resource_type = dnaModels.ResourceType.NS,
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
					'resource' : rsc,
				},
				context_instance=RequestContext(request)
			)


