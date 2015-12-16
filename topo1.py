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
        print "enter __init__ NetworkTopo"
        super( NetworkTopo, self).__init__(*args, **params )
        print "exit __init__ NetworkTopo"

    def build( self, **_opts ):

        subnetFactory = SubnetFactory('10.0.0.0/8')

        for n in range(self.RN):
            ip1,ip2 = subnetFactory.getLink()
            print "host network: ",(ip1,ip2)
            asn = 100+n
            c = str(n)
            r = self.addNode( 'r'+c, cls=LinuxRouter, ip=ip1, asn=asn )
            s = self.addSwitch( 's' + c)
            self.addLink( s, r, intfName2='r%s-eth1'%c, params2={ 'ip' : ip1 } )
            h = self.addHost( 'h'+c, ip=ip2, defaultRoute='via '+addrOnly(ip1))
            self.addLink( h, s )

        for n in range(self.RN): # can only add links when ALL of the routers are defined, hence a second loop is needed
            for m in range(n+1,self.RN):
                asn = 100+n
                remoteAsn = 100+m
                cm = str(m)
                cn = str(n)
                ra = 'r'+cn ; rb = 'r'+cm ; intfca = ra+'-'+rb ; intfcb = rb+'-'+ra
                ip1,ip2 = subnetFactory.getLink()
                print "adding peer", ra, rb, intfca,intfcb, ip1 , ip2 , asn, remoteAsn
                self.addLink( ra, rb, intfName1=intfca, intfName2=intfcb, params1={ 'ip' : ip1, 'asn' : asn } , params2={ 'ip' : ip2, 'asn' : remoteAsn } )
