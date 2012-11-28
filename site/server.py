#!/usr/bin/env python


from twisted.names import dns, server, client, cache
from twisted.application import service, internet


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
			result = self.mapping[name] # get the result


			return [ 
					(dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(result, self.ttl)),),
					(dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(result, self.ttl)),),
					(dns.RRHeader(name, dns.A, dns.IN, self.ttl, dns.Record_A(result, self.ttl)),),
				]
		else:
			return self._lookup(name, dns.IN, dns.A, timeout)

## this sets up the application

application = service.Application( 'dnsserver', uid = 1000, gid = 100 )

mapping = {
	'douglas.green' : '127.0.0.1'
}

# set up a resolver that uses the mapping or a secondary nameserver
dnsdb = MapResolver(mapping, servers=[('192.168.16.1', 53)])


# create the protocols
f = server.DNSServerFactory(caches=[cache.CacheResolver()], clients=[dnsdb])
p = dns.DNSDatagramProtocol(f)
f.noisy = p.noisy = False


# register as tcp and udp
ret = service.MultiService()
PORT = 53000

for (klass, arg) in [(internet.TCPServer, f), (internet.UDPServer, p)]:
	s = klass(PORT, arg)
	s.setServiceParent(ret)


# run all of the above as a twistd application
ret.setServiceParent(service.IServiceCollection(application))


# run it through twistd!
if __name__ == '__main__':
	import sys
	print "Usage: twistd -y %s" % sys.argv[0]


