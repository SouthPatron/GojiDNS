from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView as TV


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	url( r'^$', 'dna.views.home', name = 'dna-home' ),
	url( r'^domain/(?P<domain>.*)$', 'dna.views.domain', name = 'dna-domain' ),

	url( r'^domain_add$', 'dna.views.domain_add', name = 'dna-domain-add' ),
	url( r'^domain_clone$', 'dna.views.domain_clone', name = 'dna-domain-clone' ),
	url( r'^domain_delete/(?P<domain>.*)$', 'dna.views.domain_delete', name = 'dna-domain-delete' ),

	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls))
)


