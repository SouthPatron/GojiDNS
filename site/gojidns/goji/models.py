# GojiDNS - Developed by South Patron CC - http://www.southpatron.com/
#
# This file is part of GojiDNS.
#
# GojiDNS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GojiDNS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with GojiDNS.  If not, see <http://www.gnu.org/licenses/>.


import datetime

from django.db import models
from django.contrib.auth.models import User

from ravensuite.utils.enum import ChoicesEnum
from ravensuite.enums.world import CountryList, TimezoneList
from ravensuite.enums.people import Gender

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
		DELETED = ( 99, 'DELETED' ),
	)

Protocols = ChoicesEnum(
		TCP = ( 1, 'tcp' ),
		UDP = ( 2, 'udp' ),
		XMPP = ( 3, 'xmpp' ),
		TLS = ( 4, 'tls' ),
	)

ServerStatus = ChoicesEnum(
		OK = ( 0, 'OK' ),

		SQL = ( 10, 'Database error' ),
		IP4 = ( 20, 'IP4 Error' ),
		IP6 = ( 30, 'IP6 Error' ),
		BIND = ( 40, 'Bind Error' ),

		NEVERMET = ( 99, 'Not yet met' ),
	)



class AuthenticationCode( models.Model ):
	profile = models.ForeignKey( 'goji.Profile', on_delete = models.CASCADE )
	created_at = models.DateTimeField( auto_now_add = True )
	code = models.CharField( unique = True, max_length = 16 )


class EmailChangeRequest( models.Model ):
	profile = models.ForeignKey( 'goji.Profile', on_delete = models.CASCADE )
	created_at = models.DateTimeField( auto_now_add = True )
	old_address = models.EmailField( max_length = 254 )
	new_address = models.EmailField( max_length = 254 )
	code = models.CharField( unique = True, max_length = 16 )


class Profile( models.Model ):
	class Meta:
		pass

	user = models.OneToOneField( User, on_delete = models.CASCADE, related_name = 'goji_profile' )

	dob = models.DateField( null = True, default = None )

	gender = models.IntegerField( null = True, default = None, choices = Gender.choices() )

	country = models.CharField( max_length = 2, null = True, default = None, choices = CountryList.choices() )
	timezone = models.CharField( max_length = 64, default = 'UTC', choices = TimezoneList.choices() )

	website = models.CharField( max_length = 255, null = True, default = None )
	location = models.CharField( max_length = 255, null = True, default = None )
	phone = models.CharField( max_length = 255, null = True, default = None )


	def __unicode__( self ):
		return u'{}'.format( self.user.email )



class Domain( models.Model ):
	class Meta:
		ordering = [ 'name', ]

	profile = models.ForeignKey( Profile, on_delete = models.CASCADE )

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

	def __unicode__( self ):
		return self.name

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

	def get_resource_srv( self ):
		return self.resource_set.filter( resource_type = ResourceType.SRV )


class Resource( models.Model ):
	class Meta:
		ordering = [ '-static', 'preference', 'name', 'value', ]

	domain = models.ForeignKey( Domain, on_delete = models.CASCADE )

	resource_type = models.IntegerField( choices = ResourceType.choices() )
	name = models.CharField( null = True, max_length = 253, default = None )
	value = models.CharField( null = True, max_length = 253, default = None )
	preference = models.IntegerField( null = True, default = None )
	ttl = models.IntegerField( null = True, default = None )

	protocol = models.IntegerField( null = True, default = None, choices = Protocols.choices() )
	port = models.IntegerField( null = True, default = None )
	weight = models.IntegerField( null = True, default = None )

	static = models.BooleanField( default = False )

	def __unicode__( self ):
		return u'{} {} {} {}'.format( ResourceType.get( self.resource_type )[1], self.name, self.value, self.ttl )

	def save( self, *args, **kwargs ):
		rc = super( Resource, self ).save( *args, **kwargs )
		self.domain.save()
		return rc


class NameserverStatus( models.Model ):
	class Meta:
		ordering = [ 'hostname', ]

	hostname = models.CharField( max_length = 253, unique = True )
	first_seen = models.DateTimeField( auto_now_add = True )
	heartbeat = models.DateTimeField( auto_now_add = True )
	status = models.IntegerField( default = ServerStatus.NEVERMET, choices = ServerStatus.choices() )
	last_okay = models.DateTimeField( auto_now_add = True )

	def is_okay( self ):
		return ( self.status == ServerStatus.OK )

	def save( self ):
		if self.status == ServerStatus.OK:
			self.last_okay = datetime.datetime.now()
		return super( NameserverStatus, self ).save()



class Faq( models.Model ):
	class Meta:
		ordering = [ 'position', 'question'  ]

	position = models.IntegerField( default = 0 )
	question = models.CharField( max_length = 253 )
	answer = models.TextField()

	def __unicode__( self ):
		return self.question




# ------- Signals 

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


@receiver( post_save, sender = User, dispatch_uid = '7b4c534a' )
def user_post_save( sender, **kwargs ):
	instance = kwargs[ 'instance' ]

	try:
		prof = Profile.objects.get( user = instance )
	except Profile.DoesNotExist:
		prof = Profile.objects.create( user = instance, )

