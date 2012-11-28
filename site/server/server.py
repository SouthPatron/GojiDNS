from twisted.names import dns, server, client, cache
from twisted.application import service, internet

from resolver import MapResolver


PORT = 53000

mapping = {
	'douglas.green' : '127.0.0.1'
}


application = service.Application( 'dns', uid = 1000, gid = 100 )

dnsdb = MapResolver( mapping, servers = [('192.168.16.1', 53)] )


f = server.DNSServerFactory( caches=[cache.CacheResolver()], clients=[dnsdb] )
p = dns.DNSDatagramProtocol( f )
f.noisy = p.noisy = False

ret = service.MultiService()

for (klass, arg) in [(internet.TCPServer, f), (internet.UDPServer, p)]:
	s = klass(PORT, arg)
	s.setServiceParent(ret)


# run all of the above as a twistd application
ret.setServiceParent(service.IServiceCollection(application))


# run it through twistd!
if __name__ == '__main__':
	import sys
	print "Usage: twistd -y %s" % sys.argv[0]


