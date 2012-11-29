from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView as TV


from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

	url( r'^$',
			'dna.views.home',
			name = 'dna-home'
		),


	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls))
)


