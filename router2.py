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
from os import symlink, mkdir, getcwd, chmod, chown, chown
from tempfile import mkdtemp
from shutil import rmtree
from pwd import getpwnam
import sys
from linuxrouter import LinuxRouter
from topo1 import NetworkTopo

try:
    RN = int(sys.argv[1])
    assert RN > 0 and RN < 100
except:
    RN = 3 # default number of routers for this topology
print "will build %d node topo" % RN
# BGPD='/usr/local/sbin/bgpd'
# ZEBRA='/usr/local/sbin/zebra'
BGPCONFFILE = 'bgpd.conf'
ZEBRACONFFILE = 'zebra.conf'
TEMPDIR=mkdtemp(dir='/tmp')
USER=getpwnam('quagga')[2]
GROUP=getpwnam('quagga')[3]
chown(TEMPDIR,USER,GROUP)

def run():
    "Test linux router"
    topo = NetworkTopo(RN)
    net = Mininet( topo=topo )
    net.start()
    for r in LinuxRouter._routers:
       net.get(r).start()
    CLI( net )
    for r in LinuxRouter._routers:
       net.get(r).stop()
    net.stop()
    rmtree(TEMPDIR)

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
