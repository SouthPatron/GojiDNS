from django.contrib import admin
from goji.models import *


admin.site.register( AuthenticationCode )
admin.site.register( Profile )
admin.site.register( EmailChangeRequest )
admin.site.register( Domain )
admin.site.register( Resource )
admin.site.register( NameserverStatus )

