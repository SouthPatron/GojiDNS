from twisted.names import dns, server, cache
from twisted.application import service, internet

from resolver import DbResolver

import psycopg2
import psycopg2.extras
import sys


PORT = 53000
 

dbconn_string = "host='localhost' dbname='gojidns' user='postgres' password=''"
dbconn = psycopg2.connect( dbconn_string )
 

application = service.Application( 'dns', uid = 1000, gid = 100 )

dnsdb = DbResolver( dbconn )


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


