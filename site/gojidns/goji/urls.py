from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView as TV, RedirectView as RV

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('goji.views.public',
	url( r'^$', 'index', name = 'goji-public-index' ),
	url( r'^v/login$', 'login', name = 'goji-public-login' ),
	url( r'^v/logout$', 'logout', name = 'goji-public-logout' ),
	url( r'^v/register$', 'register', name = 'goji-public-register' ),
	url( r'^v/authenticate$', 'authenticate', name = 'goji-public-authenticate' ),
	url( r'^v/resend_authentication$', 'resend_authentication', name = 'goji-public-resend-authentication' ),
	url( r'^v/reset_password$', 'reset_password', name = 'goji-public-reset-password' ),


	url( r'^v/confirm_email/(?P<code>\S+)$', 'confirm_email', name = 'goji-public-confirm-email-code' ),
	url( r'^v/confirm_email$', 'confirm_email', name = 'goji-public-confirm-email' ),


	url( r'^faq$',
			TV.as_view( template_name = 'pages/public/general/faq.html' ),
			name = 'goji-public-faq'
		),



	url( r'^legal$',
			TV.as_view( template_name = 'pages/public/general/legal.html' ),
			name = 'goji-public-legal'
		),

	url( r'^features$',
			TV.as_view( template_name = 'pages/public/general/features.html' ),
			name = 'goji-public-features'
		),

	url( r'^contact-us$', 'contact_us', name = 'goji-public-contact-us' ),
)

urlpatterns += patterns('goji.views.members',

	url( r'^members$','domain_list', name = 'goji-domain-list' ),

	url( r'^members/domain/(?P<domain>\S+)/resource/(?P<rid>\d+)/delete$', 'domain_resource_delete', name = 'goji-domain-resource-delete' ),
	url( r'^members/domain/(?P<domain>\S+)/resource/(?P<rid>\d+)$', 'domain_resource_edit', name = 'goji-domain-resource-edit' ),
	url( r'^members/domain/(?P<domain>\S+)/resource/add$', 'domain_resource_add', name = 'goji-domain-resource-add' ),

	url( r'^members/domain/(?P<domain>\S+)/edit$', 'domain_edit', name = 'goji-domain-edit' ),
	url( r'^members/domain/(?P<domain>\S+)$', 'domain', name = 'goji-domain' ),


	url( r'^members/domain_add$', 'domain_add', name = 'goji-domain-add' ),
	url( r'^members/domain_clone$', 'domain_clone', name = 'goji-domain-clone' ),
	url( r'^members/domain_delete/(?P<domain>\S+)$', 'domain_delete', name = 'goji-domain-delete' ),


	url( r'^members/profile$', 'profile', name = 'goji-profile' ),


	url( r'^members/network_status$', 'network_status', name = 'goji-network-status' ),

	url( r'^members/change_password$', 'change_password', name = 'goji-change-password' ),



)

urlpatterns += patterns('',
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls))
)

