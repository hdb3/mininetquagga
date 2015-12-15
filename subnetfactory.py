import ipaddress  # note - this requires the py2-ipaddress module!
from sys import exit
from ipaddress import IPv4Network

class SubnetFactory( object ):

    def __init__( self, subnet):
        self.allocated = []
        self.free = [ipaddress.IPv4Network(subnet)]

    def split(self,subnet):
        nets = list(subnet.subnets(prefixlen_diff=1))
        try:
            return (nets[0],nets[1])
        except:
            exit(1)

    def splitTill(self,subnet,reqSize):
        if reqSize == subnet.prefixlen:
            return subnet
        else:
            n1,n2 = self.split(subnet)
            self.free.append(n2)
            return self.splitTill(n1,reqSize)

    def request(self,reqSize):
        smallest = None
        for net in self.free:
            if net.prefixlen > reqSize:
                continue
            if net.prefixlen == reqSize:
                smallest = net
                break
            if not smallest or net.prefixlen > smallest.prefixlen:
                smallest = net
        # we found the smallest free subnet big enough...
        # print "found ", smallest.prefixlen
        if not smallest:
            print "Can't allocate ",reqSize
            exit(1)
        self.free.remove(smallest)
        if smallest.prefixlen == reqSize:
            return smallest
        else:
            return self.splitTill(smallest,reqSize)

    def getLink(self):
        ips = self.request(30).hosts()
        net30 = lambda addr: str(addr)+'/30'
        return (net30(next(ips)), net30(next(ips)))

#@staticmethod
def addrOnly(addr):
    return str(IPv4Network(addr,strict=False).network_address)
