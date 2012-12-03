from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response
from django.template import RequestContext


def home( request ):
	return render_to_response(
				'pages/home.html',
				{
				},
				context_instance=RequestContext(request)
			)

