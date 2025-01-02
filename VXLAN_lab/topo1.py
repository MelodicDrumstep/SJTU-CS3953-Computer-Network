from mininet.topo import Topo

class Topo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1')
        self.addLink(h1, s1, bw=10, loss=0, delay='5ms')

topos = {'topo': lambda: Topo()}