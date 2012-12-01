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


class Profile( models.Model ):
	class Meta:
		pass

	user = models.OneToOneField( User, on_delete = models.CASCADE, related_name = 'dna_profile' )


class Domain( models.Model ):
	name = models.CharField( max_length = 253, unique = True )

	primary = models.CharField( max_length = 253 )
	email = models.CharField( max_length = 253 )
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
	domain = models.ForeignKey( Domain, on_delete = models.CASCADE )

	resource_type = models.IntegerField( choices = ResourceType.choices() )
	name = models.CharField( null = True, max_length = 253, default = None )
	value = models.CharField( null = True, max_length = 253, default = None )
	preference = models.IntegerField( null = True, default = None )
	ttl = models.IntegerField( null = True, default = None )


