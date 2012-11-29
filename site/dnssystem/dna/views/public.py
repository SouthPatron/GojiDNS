from django.shortcuts import render_to_response, redirect
from django.template import RequestContext


def home( request ):
	return render_to_response(
				'pages/home.html',
				{},
				context_instance=RequestContext(request)
			)

