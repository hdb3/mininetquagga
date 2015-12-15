#!/usr/bin/python

"""
router2.py
 derived from linuxrouter.py from mininet project ('Example network with Linux IP router')

"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import ipaddress # note - this requires the py2-ipaddress module!
from subnetfactory import SubnetFactory, addrOnly
from pprint import pprint

RN = 3 # number of routers in this topology

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    routers=[]
    def __init__( self, name, asn, **params ):
        super( LinuxRouter, self).__init__(name, **params )
        LinuxRouter.routers.append((name,asn))

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

    def start( self ):
        print "starting: %s" % self
        print self.cmd( 'route' )
        print self.cmd( './run.sh %s' % self )

class NetworkTopo( Topo ):

    def build( self, **_opts ):

        subnetFactory = SubnetFactory('10.0.0.0/8')

        for n in range(RN):
            ip1,ip2 = subnetFactory.getLink()
            print "host network: ",(ip1,ip2)
            asn = 100+n
            c = chr(ord('0')+n)
            r = self.addNode( 'r'+c, cls=LinuxRouter, ip=ip1, asn=asn )
            s = self.addSwitch( 's' + c)
            self.addLink( s, r, intfName2='r%s-eth1'%c, params2={ 'ip' : ip1 } )
            h = self.addHost( 'h'+c, ip=ip2, defaultRoute='via '+addrOnly(ip1))
            self.addLink( h, s )

        for n in range(RN): # can only add links when ALL of the routers are defined, hence a second loop is needed
            for m in range(n+1,RN):
                asn = 100+n
                remoteAsn = 100+m
                cm = chr(ord('0')+m)
                cn = chr(ord('0')+n)
                ra = 'r'+cn ; rb = 'r'+cm ; intfca = ra+'-'+rb ; intfcb = rb+'-'+ra
                # local = LinuxRouter.get(ra)
                # remote = LinuxRouter.get(rb)
                ip1,ip2 = subnetFactory.getLink()
                print "adding peer", ra, rb, intfca,intfcb, ip1 , ip2 , asn, remoteAsn
                # self.addLink( ra, rb, intfName1=intfc, intfName2=intfc, params1={ 'ip' : ip1 } , params2={ 'ip' : ip2 } )
                self.addLink( ra, rb, intfName1=intfca, intfName2=intfcb, params1={ 'ip' : ip1, 'asn' : asn } , params2={ 'ip' : ip2, 'asn' : remoteAsn } )
                # local.addNeighbour(remote.asn,ip2)
                # remote.addNeighbour(local.asn,ip1)
          
        # r0 = self.addNode( 'r0', cls=LinuxRouter, ip='10.0.1.1/24' )
        # r1 = self.addNode( 'r1', cls=LinuxRouter, ip='10.1.1.1/24' )
        # r2 = self.addNode( 'r2', cls=LinuxRouter, ip='10.2.1.1/24' )


        # s0, s1, s2 = [ self.addSwitch( s ) for s in 's0', 's1', 's2' ]

        # self.addLink( s0, r0, intfName2='r0-eth1', params2={ 'ip' : '10.0.1.1/24' } )
        # self.addLink( s1, r1, intfName2='r1-eth1', params2={ 'ip' : '10.1.1.1/24' } )
        # self.addLink( s2, r2, intfName2='r2-eth1', params2={ 'ip' : '10.2.1.1/24' } )

        # h0 = self.addHost( 'h0', ip='10.0.1.2/24', defaultRoute='via 10.0.1.1' )
        # h1 = self.addHost( 'h1', ip='10.1.1.2/24', defaultRoute='via 10.1.1.1' )
        # h2 = self.addHost( 'h2', ip='10.2.1.2/24', defaultRoute='via 10.2.1.1' )

        # for h, s in [ (h0, s0), (h1, s1), (h2, s2) ]:
            # self.addLink( h, s )

        # self.addLink( r0, r1, intfName1='r0-r1', intfName2='r0-r1', params1={ 'ip' : '10.254.254.1/30' } , params2={ 'ip' : '10.254.254.2/30' } )
        # self.addLink( r0, r2, intfName1='r0-r2', intfName2='r0-r2', params1={ 'ip' : '10.254.254.5/30' } , params2={ 'ip' : '10.254.254.6/30' } )
        # self.addLink( r1, r2, intfName1='r1-r2', intfName2='r1-r2', params1={ 'ip' : '10.254.254.9/30' } , params2={ 'ip' : '10.254.254.10/30' } )

def printConfig(config):
    print "hostname bgpd"
    print "password bgpd"
    print "enable password bgpd"
    print "log file bgpd.log"
    for router in config:
        asn = config[router]['asn']
        print "! view from AS %d %s" % (asn,router)
        print "!-%d-router bgp %d" % (asn,asn)
        for peer in config[router]['peers']:
            remoteIP = peer['ip']
            remoteASN = peer['asn']
            print "!-%d-neighbor %s remote-as %d" % (asn,remoteIP,remoteASN)

    print "redistribute static"
    print "redistribute connected"

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )
    net.start()
    configBGP = {}
    for r,asn in LinuxRouter.routers:
       # print "router BGP %s %d" % (r,asn)
       configBGP[r]={}
       configBGP[r]['asn']=asn
       configBGP[r]['peers']=[]
       for intf in net.get(r).intfList():
           remote = intf.link.intf2 if intf == intf.link.intf1 else intf.link.intf1
           if 'asn' in intf.params:
               # print "BGP peer for %s is AS:%d at %s" % (r,remote.params['asn'],remote.params['ip'])
               configBGP[r]['peers'].append({ 'ip' : addrOnly(remote.params['ip']), 'asn' : remote.params['asn']})
    printConfig(configBGP)
    for r,asn in LinuxRouter.routers:
       net.get(r).start()
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
