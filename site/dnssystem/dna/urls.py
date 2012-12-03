from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView as TV, RedirectView as RV


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	url( r'^$', RV.as_view(
				url = '/members',
				permanent = False
			),
			name = 'dna-index' ),

	url( r'^members$', 'dna.views.domain_list', name = 'dna-members' ),

	url( r'^members/domain/(?P<domain>\S+)/resource/(?P<rid>\d+)/delete$', 'dna.views.domain_resource_delete', name = 'dna-domain-resource-delete' ),
	url( r'^members/domain/(?P<domain>\S+)/resource/(?P<rid>\d+)$', 'dna.views.domain_resource_edit', name = 'dna-domain-resource-edit' ),
	url( r'^members/domain/(?P<domain>\S+)/resource/add$', 'dna.views.domain_resource_add', name = 'dna-domain-resource-add' ),

	url( r'^members/domain/(?P<domain>\S+)/edit$', 'dna.views.domain_edit', name = 'dna-domain-edit' ),
	url( r'^members/domain/(?P<domain>\S+)$', 'dna.views.domain', name = 'dna-domain' ),


	url( r'^members/domain_add$', 'dna.views.domain_add', name = 'dna-domain-add' ),
	url( r'^members/domain_clone$', 'dna.views.domain_clone', name = 'dna-domain-clone' ),
	url( r'^members/domain_delete/(?P<domain>\S+)$', 'dna.views.domain_delete', name = 'dna-domain-delete' ),


	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls))
)


