#!/usr/bin/env python

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
# from django.conf.urls import patterns, include, url
#




import sys, os, os.path
import uuid
import re
import datetime
import subprocess
import socket

import psycopg2
import psycopg2.extras

from django.utils.ipv6 import is_valid_ipv6_address

from config.config import Config


# ---------------------------------- GLOBAL VARIABLES --------

config = Config()

# ---------------------------------- DETECTED ----------------

FQDN = socket.getfqdn( socket.gethostname() )

# ---------------------------------- SUPPORT FUNCTIONS -------


def is_valid_ip4( address ):
	ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')
	return (ipv4_re.search( address ) is not None)

def is_valid_ip6( address ):
	return (is_valid_ipv6_address( address ))

DEVNULL = open( os.devnull, 'w' )



def generate_name( path_root, name ):
	flatname = "".join( re.split( r'[^A-Za-z0-9]', name ) )

	while len( flatname ) < 4:
		flatname = flatname + 'z'

	location = '{}/{}'.format( flatname[0:2], flatname[2:4] )

	full_loc = os.path.join( path_root, location )
	full_name = os.path.join( full_loc, name )

	return ( full_loc, full_name, os.path.join( location, name ) )

def email_to_rname( email ):
	username, domain = email.split('@', 1)
	username = username.replace('.', '\\.')
	return '.'.join((username, domain))


def dump_domain( conn, f, row ):
	timestamp = datetime.datetime.now().strftime( '%y%j%H%M' )
	
	f.write( '; {} [{}]\n'.format( row['name'], row[ 'id' ] ) )

	f.write( "@\tIN\tSOA\t{}.\t{}.\t{}\t{}\t{}\t{}\t{}\n".format(
			row[ 'primary' ],
			email_to_rname( row[ 'email' ] ),
			timestamp,
			row[ 'refresh' ] or '14400',
			row[ 'retry' ] or '14400',
			row[ 'expire' ] or '1209600',
			row[ 'ttl' ]
		) )


	resources = conn.cursor( cursor_factory=psycopg2.extras.DictCursor )
	resources.execute( """SELECT * FROM goji_resource WHERE domain_id = %(did)s""", { 'did' : row['id'] } )

	# 1 - NS, 2 - MX, 3 - A/AAAA, 4 - TXT, 5 - CNAME, 6 - SRV
	for rsc in resources:
		rsc_type = int( rsc[ 'resource_type' ] )
		rsc_name = rsc[ 'name' ]
		rsc_value = rsc[ 'value' ]
		rsc_ttl = rsc[ 'ttl' ] or ''

		if rsc_type == 1:
			if len( rsc_value ) == 0:
				rsc_value = '@'

			f.write( "{}\t\tNS\t{}.\n".format( rsc_value, rsc_name ) )

		elif rsc_type == 2:
			if len( rsc_value ) == 0:
				rsc_value = '@'

			f.write( "{}\t{}\tMX\t{}\t{}.\n".format(
				rsc_value,
				rsc_ttl,
				rsc['preference'],
				rsc_name ) )

		elif rsc_type == 3:
			if len( rsc_name ) == 0:
				rsc_name = '@'

			atype = 'A'
			if is_valid_ip6( rsc_value ) is True:
				atype = 'AAAA'

			f.write( "{}\t{}\t{}\t{}\n".format(
					rsc_name,
					rsc_ttl,
					atype,
					rsc_value,
					) )

		elif rsc_type == 4:
			if len( rsc_name ) == 0:
				rsc_name = '@'

			def replic(m):
				return "\\" + m.group(1)

			f.write( "{}\t{}\tTXT\t\"{}\"\n".format(
					rsc_name,
					rsc_ttl,
					re.sub( r"([;\"\\])", replic, rsc_value )
				) )


		elif rsc_type == 5:

			f.write( "{}\t{}\tCNAME\t{}.\n".format(
					rsc_name,
					rsc_ttl,
					rsc_value )
				)

		elif rsc_type == 6:

			rsc_proto = int( rsc['protocol'] )
			if rsc_proto == 1:
				rsc_proto = '_tcp'
			elif rsc_proto == 2:
				rsc_proto = '_udp'
			elif rsc_proto == 3:
				rsc_proto = '_xmpp'
			elif rsc_proto == 4:
				rsc_proto = '_tls'

			f.write( "{}.{}\t{}\tSRV\t{}\t{}\t{}\t{}.\n".format(
					rsc_name,
					rsc_proto,
					rsc_ttl,
					rsc['preference'],
					rsc['weight'],
					rsc['port'],
					rsc_value )
				)

			pass

	resources.close()



def delete_domain( full_name, row ):
	try:
		os.remove( full_name )
		os.rmdir( os.path.dirname( full_name ) )
		os.rmdir( os.path.dirname( os.path.dirname( full_name ) ) )
	except OSError:
		pass

def rndc_addzone( row, full_name ):
	name = row[ 'name' ]
	subprocess.call( [
			config.RNDC_BIN,
			"addzone",
			name,
			"{{ type master; file \"gojidns/{}\"; }};".format( full_name ),
		],
			stdin = DEVNULL,
			stdout = DEVNULL,
			stderr = DEVNULL
		)


def rndc_delzone( row ):
	name = row[ 'name' ]
	subprocess.call( [
			config.RNDC_BIN,
			"delzone",
			name,
		],
			stdin = DEVNULL,
			stdout = DEVNULL,
			stderr = DEVNULL
		)

def rndc_reload( row ):
	name = row[ 'name' ]
	subprocess.call( [
			config.RNDC_BIN,
			"reload",
			name,
		],
			stdin = DEVNULL,
			stdout = DEVNULL,
			stderr = DEVNULL
		)


def heartbeat( conn, hostname, status ):
	last_okay = ""

	if status == 0:
		last_okay = ", last_okay = NOW()"

	cursor = conn.cursor( cursor_factory = psycopg2.extras.DictCursor )
	cursor.execute( """UPDATE goji_nameserverstatus SET heartbeat = NOW(), status = %(status)s{} WHERE hostname = %(hostname)s""".format( last_okay ),
		{
			'status' : status,
			'hostname' : hostname,
		}
	)

	cursor.close()



def process_changes( conn ):
	cursor_name_uuid = uuid.uuid1()
	cursor_name = "{}".format( cursor_name_uuid.int )

	cursor = conn.cursor( cursor_name, cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("""SELECT * FROM goji_domain WHERE last_modified >= (NOW() - INTERVAL '15 minutes')""" )
 
	for row in cursor:
		name = row[ 'name' ]
		status = int( row['status'] )

		full_loc, full_name, basename = generate_name( config.PATH_ROOT, name )

		# 1 - Active, 2 - Disabled, 3 - Edit, 99 - Deleted, 

		if status == 1:
			if os.path.exists( full_loc ) is False:
				os.makedirs( full_loc )

			f = open( full_name, 'w' )
			dump_domain( conn, f, row )
			f.close()

			rndc_addzone( row, basename )
			rndc_reload( row )

		elif status == 2 or status == 99:
			delete_domain( full_name, row )

			rndc_delzone( row )

		elif status == 3:
			# Do nothing 'cos it's being editted
			pass


	cursor.close()



 
def main():
	conn_string = "host='{}' dbname='{}' user='{}' password='{}'".format(
			config.DB_HOST,
			config.DB_NAME,
			config.DB_USER,
			config.DB_PASSWORD
		)

	conn = psycopg2.connect(conn_string)

	process_changes( conn )

	heartbeat( conn, FQDN, 0 )

	conn.commit()
	conn.close()


if __name__ == "__main__":
	main()


DEVNULL.close()


