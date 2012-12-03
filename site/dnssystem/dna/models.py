import datetime

from django.db import models
from django.contrib.auth.models import User

from ravensuite.utils.enum import ChoicesEnum

ResourceType = ChoicesEnum(
		NS = ( 1, 'Nameserver' ),
		MX = ( 2, 'Mail' ),
		A = ( 3, 'A' ),
		TXT = ( 4, 'TXT' ),
		CNAME = ( 5, 'CNAME' ),
		SRV = ( 6, 'SRV' ),
	)

DomainStatus = ChoicesEnum(
		ACTIVE = ( 1, 'ACTIVE' ),
		DISABLED = ( 2, 'DISABLED' ),
		EDIT_MODE = ( 3, 'EDIT' ),
	)


class Profile( models.Model ):
	class Meta:
		pass

	user = models.OneToOneField( User, on_delete = models.CASCADE, related_name = 'dna_profile' )


class Domain( models.Model ):
	class Meta:
		ordering = [ 'name', ]

	name = models.CharField( max_length = 253, unique = True )

	is_master = models.BooleanField( default = True )

	last_modified = models.DateTimeField( auto_now = True, auto_now_add = True )
	status = models.IntegerField( choices = DomainStatus.choices(), default = DomainStatus.ACTIVE )

	primary = models.CharField( max_length = 253 )
	email = models.EmailField( max_length = 254 )
	ttl = models.IntegerField( default = 7200 )
	refresh = models.IntegerField( null = True, default = None )
	retry = models.IntegerField( null = True, default = None )
	expire = models.IntegerField( null = True, default = None )

	def get_resource_ns( self ):
		return self.resource_set.filter( resource_type = ResourceType.NS )

	def get_resource_mx( self ):
		return self.resource_set.filter( resource_type = ResourceType.MX )

	def get_resource_a( self ):
		return self.resource_set.filter( resource_type = ResourceType.A )

	def get_resource_txt( self ):
		return self.resource_set.filter( resource_type = ResourceType.TXT )

	def get_resource_cname( self ):
		return self.resource_set.filter( resource_type = ResourceType.CNAME )


class Resource( models.Model ):
	class Meta:
		ordering = [ '-static', 'preference', 'name', 'value', ]

	domain = models.ForeignKey( Domain, on_delete = models.CASCADE )

	resource_type = models.IntegerField( choices = ResourceType.choices() )
	name = models.CharField( null = True, max_length = 253, default = None )
	value = models.CharField( null = True, max_length = 253, default = None )
	preference = models.IntegerField( null = True, default = None )
	ttl = models.IntegerField( null = True, default = None )

	static = models.BooleanField( default = False )

	def save( self, *args, **kwargs ):
		rc = super( Resource, self ).save( *args, **kwargs )
		self.domain.save()
		return rc


