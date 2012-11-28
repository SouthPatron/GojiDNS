
from twisted.names import dns, server, client, cache


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


class MapResolver( client.Resolver ):
	"""
	Resolves names by looking in a mapping. 
	If `name in mapping` then mapping[name] should return a IP
	else the next server in servers will be asked for name    
	"""
	def __init__( self, mapping, servers ):
		self.mapping = mapping
		self.ttl = 10
		client.Resolver.__init__( self, servers = servers )

	def lookupAddress( self, name, timeout = None ):
		if name in self.mapping:
			result = self.mapping[ name ]


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
		else:
			return self._lookup(name, dns.IN, dns.A, timeout)


