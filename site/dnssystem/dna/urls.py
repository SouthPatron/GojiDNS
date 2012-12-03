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
)

urlpatterns += patterns('dna.views.members',

	url( r'^members$','domain_list', name = 'dna-domain-list' ),

	url( r'^members/domain/(?P<domain>\S+)/resource/(?P<rid>\d+)/delete$', 'domain_resource_delete', name = 'dna-domain-resource-delete' ),
	url( r'^members/domain/(?P<domain>\S+)/resource/(?P<rid>\d+)$', 'domain_resource_edit', name = 'dna-domain-resource-edit' ),
	url( r'^members/domain/(?P<domain>\S+)/resource/add$', 'domain_resource_add', name = 'dna-domain-resource-add' ),

	url( r'^members/domain/(?P<domain>\S+)/edit$', 'domain_edit', name = 'dna-domain-edit' ),
	url( r'^members/domain/(?P<domain>\S+)$', 'domain', name = 'dna-domain' ),


	url( r'^members/domain_add$', 'domain_add', name = 'dna-domain-add' ),
	url( r'^members/domain_clone$', 'domain_clone', name = 'dna-domain-clone' ),
	url( r'^members/domain_delete/(?P<domain>\S+)$', 'domain_delete', name = 'dna-domain-delete' ),

)

urlpatterns += patterns('',
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls))
)

