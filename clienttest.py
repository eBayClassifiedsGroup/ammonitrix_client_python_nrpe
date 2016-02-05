#!/usr/bin/env python

from ammonitrixclient.client import *
from ammonitrixclient.nrpe import *


client = Client(name='laptopreinoud/testname')

client.set_server(server_hostname='10.41.4.124', protocol='http')

nrpe = Nrpe('/etc/nagios/nrpe.d/')
results = nrpe.execute_commands()

for check, result in results.iteritems():
    client.set_name('laptopreinoud/{}'.format(check))
    client.set_tags(['foo', 'bar', 1])
    client.set_check_data(result)
    client.send_result()
    print "sent laptopreinoud/{}".format(check)