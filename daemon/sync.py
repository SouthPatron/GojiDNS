#!/usr/bin/env python

import sys, os, os.path
import uuid
import re

import psycopg2
import psycopg2.extras

from django.utils.ipv6 import is_valid_ipv6_address

def is_valid_ip4( address ):
	ipv4_re = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')
	return (ipv4_re.search( address ) is not None)

def is_valid_ip6( address ):
	return (is_valid_ipv6_address( address ))






DB_HOST = "192.168.131.128"
DB_NAME = "gojidns"
DB_USER = "gojidns_www"
DB_PASSWORD = "dog elephant shoe"

PATH_ROOT = "/var/bind/gojidns"

DB_HOST = "localhost"
DB_NAME = "gojidns"
DB_USER = "postgres"
DB_PASSWORD = ""

PATH_ROOT = "/home/durand/bind/gojidns"


def generate_name( path_root, name ):
	flatname = "".join( re.split( r'[^A-Za-z0-9]', name ) )

	while len( flatname ) < 4:
		flatname = flatname + 'z'

	location = '{}/{}'.format( flatname[0:2], flatname[2:4] )

	full_loc = os.path.join( path_root, location )
	full_name = os.path.join( full_loc, name )

	return ( full_loc, full_name )



def dump_domain( conn, f, row ):

	print '{} belongs to {}'.format( row['name'], row['profile_id'] )


	f.write( "@\tIN\tSOA\t{}.\t{}.\t{}\t{}\t{}\t{}\t{}\n".format(
			row[ 'primary' ],
			row[ 'email' ],
			'2012120422',
			'14400',
			'14400',
			'1209600',
			'7200',
		) )


	resources = conn.cursor( cursor_factory=psycopg2.extras.DictCursor )
	resources.execute( """SELECT * FROM goji_resource WHERE domain_id = %(did)s""", { 'did' : row['id'] } )

	for rsc in resources:
		rsc_type = int( rsc[ 'resource_type' ] )

		# 1 - NS, 2 - MX, 3 - A/AAAA, 4 - TXT, 5 - CNAME, 6 - SRV

		if rsc_type == 1:
			f.write( "@\t\tNS\t{}.\n".format( rsc[ 'name' ] ) )
		elif rsc_type == 2:
			f.write( "@\t\tMX\t{}\t{}.\n".format( rsc['preference'], rsc[ 'name' ] ) )
		elif rsc_type == 3:
			val = rsc[ 'value' ]
			if is_valid_ip6( val ) is True:
				f.write( "@\t\tAAAA\t{}.\n".format( val ) )
			else:
				f.write( "@\t\tA\t{}.\n".format( val ) )

		elif rsc_type == 4:
			f.write( "@\t\tTXT\t\"{}\".\n".format( rsc['value'] ) )
		elif rsc_type == 5:
			f.write( "{}\t\tCNAME\t{}.\n".format( rsc['name'], rsc['value'] ) )
		elif rsc_type == 6:
			pass


	resources.close()


 
def main():
	conn_string = "host='{}' dbname='{}' user='{}' password='{}'".format(
			DB_HOST,
			DB_NAME,
			DB_USER,
			DB_PASSWORD
		)

	conn = psycopg2.connect(conn_string)

	cursor_name_uuid = uuid.uuid1()
	cursor_name = "{}".format( cursor_name_uuid.int )

	cursor = conn.cursor( cursor_name, cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("""SELECT * FROM goji_domain""" )
 
	for row in cursor:
		name = row[ 'name' ]

		full_loc, full_name = generate_name( PATH_ROOT, name )

		if os.path.exists( full_loc ) is False:
			os.makedirs( full_loc )

		f = open( full_name, 'w' )

		dump_domain( conn, f, row )

		f.close()


 	cursor.close()


if __name__ == "__main__":
	main()


