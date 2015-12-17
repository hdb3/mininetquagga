#!/usr/bin/python

from mininet.node import Node
from mininet.log import setLogLevel, info
import ipaddress # note - this requires the py2-ipaddress module!
from os import symlink, mkdir, getcwd, chmod, chown, chown
from tempfile import mkdtemp
from shutil import rmtree
from pwd import getpwnam
import sys

BGPCONFFILE = 'bgpd.conf'
ZEBRACONFFILE = 'zebra.conf'
TEMPDIR=mkdtemp(dir='/tmp')
USER=getpwnam('quagga')[2]
GROUP=getpwnam('quagga')[3]
chown(TEMPDIR,USER,GROUP)

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    _routers=[]
    def __init__( self, name, asn, **params ):
        super( LinuxRouter, self).__init__(name, **params )
        LinuxRouter._routers.append(name)
        self.asn = asn

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

        dirpath = TEMPDIR + '/' + self.name
        self.path = dirpath
        dir = mkdir(dirpath,0777)
        f = open(dirpath+'/'+BGPCONFFILE, 'w')

        f.write( "hostname %s\n" % self.name )
        f.write( "password bgpd\n" )
        f.write( "enable password bgpd\n" )
        f.write( "log file bgpd.log\n" )
        f.write( "router bgp %d\n" % self.asn )
        for intf in self.intfList():
           remote = intf.link.intf2 if intf == intf.link.intf1 else intf.link.intf1
           if 'asn' in intf.params:
               f.write( "  neighbor %s remote-as %d\n" % (remote.params['ip'],remote.params['asn']) )
        f.write( "redistribute static\n" )
        f.write( "redistribute connected\n" )
        f.close()
        chown(dirpath,USER,GROUP)

        symlink(getcwd() + '/'+ ZEBRACONFFILE, dirpath + '/'+ ZEBRACONFFILE)
        self.cmd('/bin/mount --bind ' + dirpath + ' /var/run')

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()
        # we could always delete the tmp directory now... (self.path)

    def start( self ):
        self.cmd( 'cd /var/run && zebra -f zebra.conf -d' )
        self.cmd( 'cd /var/run && bgpd -f bgpd.conf -d' )

    def stop( self ):
        self.cmd( 'cd /var/run && kill $(<bgpd.pid) $(<zebra.pid) ' )
