
from zope.interface import implements

from twisted.python import failure
from twisted.internet import interfaces
from twisted.names import dns, error, server, common, client, cache

import psycopg2.extras

#@ivar name: The name about which this reply contains information.
#@ivar type: The query type of the original request.
#@ivar cls: The query class of the original request.
#@ivar ttl: The time-to-live for this record.
#@ivar payload: An object that implements the IEncodable interface

#@ivar auth: A C{bool} indicating whether this C{RRHeader} was parsed from an
#authoritative message.


#(A, NS, MD, MF, CNAME, SOA, MB, MG, MR, NULL, WKS, PTR, HINFO, MINFO, MX, TXT,
# RP, AFSDB) = range(1, 19)
#AAAA = 28
#SRV = 33
#NAPTR = 35
#A6 = 38
#DNAME = 39
#SPF = 99


class DbResolver( common.ResolverBase ):
	implements(interfaces.IResolver)

	def __init__( self, dbconn ):
		self.dbconn = dbconn
		self.ttl = 10
		common.ResolverBase.__init__( self )

	def _loadDomain( self, name ):
		cursor = self.dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cursor.execute("""SELECT * FROM dna_domain WHERE name = %(name)s LIMIT 1""",
						{ 'name' : name } )

		if cursor.rowcount != 1:
			return None

		for row in cursor:
			cursor.close()
			return row


	def lookupAddress( self, name, timeout = None ):
		domain = self._loadDomain( name )

		if domain is None:
			m = dns.Message( rCode = dns.EREFUSED )
			err = failure.Failure(self.exceptionForCode(m.rCode)(m))
			err.trap(error.DNSQueryRefusedError)
			return err


		cursor = self.dbconn.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cursor.execute("""SELECT * FROM dna_resource WHERE domain_id = %(did)s""",
						{ 'did' : domain['id'] } )

		answers = []
		auths = []
		adds = []

		for row in cursor:
			if row['resource_type'] == 1:
				auths.append(
					dns.RRHeader(
						name, dns.NS, dns.IN, domain['ttl'],
						dns.Record_NS( row['name'], ttl = row['ttl'] )
					)
				)

			if row['resource_type'] == 3:
				print '{}'.format( row )
				if row['name'] == '':
					answers.append(
						dns.RRHeader(
							name, dns.A, dns.IN, domain['ttl'],
							dns.Record_A( row['value'], ttl = row['ttl'] )
						)
					)


		cursor.close()

		return [ answers, auths, adds, ]


		# answer
		# authority
		# additional section


		arg1 = dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(result, self.ttl))
		arg2 = dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(result, self.ttl))
		arg3 = dns.RRHeader(name, dns.MX, dns.IN, self.ttl, dns.Record_MX( name='mail.smksoftware.com', ttl = self.ttl))
		arg4 = dns.RRHeader(name, dns.NS, dns.IN, self.ttl, dns.Record_NS( 'ns1.smksoftware.com', self.ttl))
		arg5 = dns.RRHeader(name, dns.TXT, dns.IN, self.ttl, dns.Record_TXT('v=spf1 include:_spf.google.com ip4:75.127.97.109 -all', ttl=self.ttl))
		arg6 = dns.RRHeader(name, dns.AAAA, dns.IN, self.ttl, dns.Record_AAAA('2600:3c01::a', ttl=self.ttl))

		# CNAME and SOA
		#
		# arg0 = dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(result, self.ttl))
		# arg0 = dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(result, self.ttl))


		return [ 
				( arg1, arg2, arg3 ),
				( arg4, arg5, ),
				( arg6, ),
			]


