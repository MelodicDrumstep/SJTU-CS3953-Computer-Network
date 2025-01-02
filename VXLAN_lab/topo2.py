from mininet.topo import Topo

class Topo(Topo):
    def build(self):
        s2 = self.addSwitch('s2')
        h2 = self.addHost('h2')
        self.addLink(h2, s2, bw=10, loss=0, delay='5ms')

topos = {'topo': lambda: Topo()}