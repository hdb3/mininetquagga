#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import ipaddress # note - this requires the py2-ipaddress module!
from subnetfactory import SubnetFactory, addrOnly
from linuxrouter import LinuxRouter

class NetworkTopo( Topo ):

    def __init__( self, n=3, *args, **params ):
        self.RN = n
        super( NetworkTopo, self).__init__(*args, **params )

    def build( self, **_opts ):

        linkSubnetFactory = SubnetFactory('10.0.0.0/8')
        hostSubnetFactory = SubnetFactory('172.16.0.0/12')

        for n in range(self.RN):
            ip1,ip2 = hostSubnetFactory.getLink()
            print "host network: ",(ip1,ip2)
            asn = 100+n
            c = str(n)
            r = self.addNode( 'r'+c, cls=LinuxRouter, ip=ip1, asn=asn )
            h = self.addHost( 'h'+c, ip=ip2, defaultRoute='via '+addrOnly(ip1))
            self.addLink( h, r, intfName2='r%s-eth1'%c, params2={ 'ip' : ip1 } )

        for n in range(1,self.RN): # can only add links when ALL of the routers are defined, hence a second loop is needed
            cn = str(n) ; r0 = 'r0' ; ra = 'r'+cn ; intfca = r0+'-'+ra ; intfcb = ra+'-'+r0
            asn = 100 ; remoteAsn = 100+n
            ip1,ip2 = linkSubnetFactory.getLink()
            print "adding peer", r0, ra, intfca,intfcb, ip1 , ip2 , asn, remoteAsn
            self.addLink( r0, ra, intfName1=intfca, intfName2=intfcb, params1={ 'ip' : ip1, 'asn' : asn } , params2={ 'ip' : ip2, 'asn' : remoteAsn } )

def network(RN):
    topo = NetworkTopo(RN)
    return Mininet( topo=topo , controller = None )
