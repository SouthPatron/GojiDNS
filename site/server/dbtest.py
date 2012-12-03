#!/usr/bin/env python


import psycopg2
#note that we have to import the Psycopg2 extras library!
import psycopg2.extras
import sys
 
def main():
	conn_string = "host='localhost' dbname='dnssystem' user='postgres' password=''"
	# print the connection string we will use to connect
	print "Connecting to database\n	->%s" % (conn_string)
 
	conn = psycopg2.connect(conn_string)
 
	# HERE IS THE IMPORTANT PART, by specifying a name for the cursor
	# psycopg2 creates a server-side cursor, which prevents all of the
	# records from being downloaded at once from the server.
	cursor = conn.cursor('cursor_unique_name', cursor_factory=psycopg2.extras.DictCursor)
	cursor.execute("""SELECT * FROM dna_domain WHERE name = %(name)s""", { 'name' : 'doggles.co.za' } )
 
	# Because cursor objects are iterable we can just call 'for - in' on
	# the cursor object and the cursor will automatically advance itself
	# each iteration.
	# This loop should run 1000 times, assuming there are at least 1000
	# records in 'my_table'
	row_count = 0
	for row in cursor:
		row_count += 1
		print "row: %s    %s\n" % (row_count, row)
		print "   domain: %s\n" % ( row['name'] )
 
if __name__ == "__main__":
	main()

