#!/usr/bin/env python

from ammonitrixclient.client import *
from ammonitrixclient.nrpe import *


client = Client(name='laptopreinoud/testname')

client.set_server(server_hostname='10.41.4.124', protocol='http')

nrpe = Nrpe('/etc/nagios/nrpe.d/')
results = nrpe.execute_commands()

for check, result in results.iteritems():
    client.set_name('laptopreinoud/{}'.format(check))
    check_data = result['result']
    check_data['resultcode'] = result['resultcode']

    client.set_check_data([check_data])
    client.send_result()
    print "sent laptopreinoud/{}".format(check)