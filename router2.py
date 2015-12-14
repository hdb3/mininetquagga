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

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):

    def build( self, **_opts ):

        r0 = self.addNode( 'r0', cls=LinuxRouter, ip='10.0.1.1/24' )
        r1 = self.addNode( 'r1', cls=LinuxRouter, ip='10.1.1.1/24' )
        r2 = self.addNode( 'r2', cls=LinuxRouter, ip='10.2.1.1/24' )


        s0, s1, s2 = [ self.addSwitch( s ) for s in 's0', 's1', 's2' ]

        self.addLink( s0, r0, intfName2='r0-eth1', params2={ 'ip' : '10.0.1.1/24' } )
        self.addLink( s1, r1, intfName2='r1-eth1', params2={ 'ip' : '10.1.1.1/24' } )
        self.addLink( s2, r2, intfName2='r2-eth1', params2={ 'ip' : '10.2.1.1/24' } )

        h0 = self.addHost( 'h0', ip='10.0.1.2/24', defaultRoute='via 10.0.1.1' )
        h1 = self.addHost( 'h1', ip='10.1.1.2/24', defaultRoute='via 10.1.1.1' )
        h2 = self.addHost( 'h2', ip='10.2.1.2/24', defaultRoute='via 10.2.1.1' )

        for h, s in [ (h0, s0), (h1, s1), (h2, s2) ]:
            self.addLink( h, s )

        self.addLink( r0, r1, intfName1='r0-r1', intfName2='r0-r1', params1={ 'ip' : '10.254.254.1/30' } , params2={ 'ip' : '10.254.254.2/30' } )
        self.addLink( r0, r2, intfName1='r0-r2', intfName2='r0-r2', params1={ 'ip' : '10.254.254.5/30' } , params2={ 'ip' : '10.254.254.6/30' } )
        self.addLink( r1, r2, intfName1='r1-r2', intfName2='r1-r2', params1={ 'ip' : '10.254.254.9/30' } , params2={ 'ip' : '10.254.254.10/30' } )


def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )
    net.start()
    info( '*** Routing Table on Router:\n' )
    print net[ 'r0' ].cmd( 'route' )
    print net[ 'r1' ].cmd( 'route' )
    print net[ 'r2' ].cmd( 'route' )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
