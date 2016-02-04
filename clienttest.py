#!/usr/bin/env python

from ammonitrixclient.client import *
from ammonitrixclient.nrpe import *

__author__ = 'rvanleeuwen'
__email__ = 'rvanleeuwen@ebay.com'


client = Client(name='laptopreinoud/testname')

#client.set_server(server_hostname='127.0.0.1', protocol='http')
client.set_server(server_hostname='10.41.4.124', protocol='http')


#client.set_check_data([{
#             "index_name": "ads",
#             "healthy_shards": 6,
#             "shards_missing_replicas": 0}])

nrpe = Nrpe('/etc/nagios/nrpe.d/')
results = nrpe.execute_commands()

for check, result in results.iteritems():
    client.set_name('laptopreinoud/{}'.format(check))
    check_data = result['result']
    check_data['resultcode'] = result['resultcode']
    client.set_check_data([check_data])
    client.send_result()
    print "sent laptopreinoud/{}".format(check)
# print results