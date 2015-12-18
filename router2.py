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
from importlib import import_module

try:
    __module = import_module(sys.argv[2])
    print "successfuly imported a topology from " + sys.argv[2]
except:
    if len(sys.argv)>2:
        print "tried and failed to import a topology from " + sys.argv[2]
    __module = import_module('topo1')

network = __module.network

try:
    RN = int(sys.argv[1])
    assert RN > 0 and RN < 1000
except:
    RN = 3 # default number of routers for this topology
print "will build %d node topo" % RN

def run():
    "Test linux router"
    net = network(RN)
    net.start()
    for r in LinuxRouter._routers:
       net.get(r).start()
    CLI( net )
    for r in LinuxRouter._routers:
       net.get(r).stop()
    net.stop()
    #rmtree(TEMPDIR)

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
