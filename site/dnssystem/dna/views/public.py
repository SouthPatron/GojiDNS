from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext

import dna.models as dnaModels


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
		print '%r' % request.POST
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

