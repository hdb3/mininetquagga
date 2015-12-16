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

try:
    RN = int(sys.argv[1])
    assert RN > 0 and RN < 11
except:
    RN = 3 # default number of routers for this topology
# print len(sys.argv), "'%s'" % sys.argv[1]
print "will build %d node topo" % RN
BGPD='/usr/local/sbin/bgpd'
ZEBRA='/usr/local/sbin/zebra'
BGPCONFFILE = 'bgpd.conf'
ZEBRACONFFILE = 'zebra.conf'
TEMPDIR=mkdtemp(dir='/tmp')
#chmod(TEMPDIR,0777)
symlink(getcwd() + '/'+ ZEBRACONFFILE,TEMPDIR + '/'+ ZEBRACONFFILE)
USER=getpwnam('quagga')[2]
GROUP=getpwnam('quagga')[3]
#chownQuagga=lambda p : chown(p,USER,GROUP)
#chownQuagga(TEMPDIR)
chown(TEMPDIR,USER,GROUP)

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    _routers=[]
    def __init__( self, name, asn, **params ):
        super( LinuxRouter, self).__init__(name, **params )
        LinuxRouter._routers.append((name,asn))

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

    def start( self, path ):
        subdir = path + '/' + self.name
        print "starting zebra for %s in %s" % (self,subdir)
        self.cmd( 'cd ' + subdir + ' && ' + ZEBRA + ' -f ../zebra.conf -i %s/zebra.pid -z %s/zebra.api -d' % (subdir,subdir) )
        print "starting bgpd for %s in %s" % (self,subdir)
        self.cmd( 'cd ' + subdir + ' && ' + BGPD + ' -f %s/bgpd.conf -i %s/bgpd.pid -z %s/zebra.api -d' % (subdir,subdir,subdir) )

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
                ip1,ip2 = subnetFactory.getLink()
                print "adding peer", ra, rb, intfca,intfcb, ip1 , ip2 , asn, remoteAsn
                self.addLink( ra, rb, intfName1=intfca, intfName2=intfcb, params1={ 'ip' : ip1, 'asn' : asn } , params2={ 'ip' : ip2, 'asn' : remoteAsn } )
          
def writeBGPconfig(config,router,path):
    f = open(path, 'w')
    f.write( "hostname %s\n" % router )
    f.write( "password bgpd\n" )
    f.write( "enable password bgpd\n" )
    f.write( "log file bgpd.log\n" )
    asn = config[router]['asn']
    f.write( "router bgp %d\n" % asn )
    for peer in config[router]['peers']:
        remoteIP = peer['ip']
        remoteASN = peer['asn']
        f.write( "  neighbor %s remote-as %d\n" % (remoteIP,remoteASN) )

    f.write( "redistribute static\n" )
    f.write( "redistribute connected\n" )
    f.close()
    #chownQuagga(path)
    chown(path,USER,GROUP)

def buildBGPconfig(net):
    configBGP = {}
    for r,asn in LinuxRouter._routers:
       configBGP[r]={}
       configBGP[r]['asn']=asn
       configBGP[r]['peers']=[]
       for intf in net.get(r).intfList():
           remote = intf.link.intf2 if intf == intf.link.intf1 else intf.link.intf1
           if 'asn' in intf.params:
               configBGP[r]['peers'].append({ 'ip' : addrOnly(remote.params['ip']), 'asn' : remote.params['asn']})
    return configBGP

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )
    net.start()
    config=buildBGPconfig(net)
    for r,asn in LinuxRouter._routers:
       dirpath = TEMPDIR + '/' + r
       dir = mkdir(dirpath,0777)
       # chownQuagga(dir)
       chown(dirpath,USER,GROUP)
       writeBGPconfig(config,r,dirpath+'/'+BGPCONFFILE)
       net.get(r).start(TEMPDIR)
    CLI( net )
    net.stop()
    # rmtree(TEMPDIR)

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
