from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI

class CustomTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        self.addLink(h1, s1)                    # h1 to s1
        self.addLink(s1, s2, bw=15, loss=4)     # s1 to s2 with 15 Mbps and 4% loss
        self.addLink(s2, s3, bw=15, loss=4)     # s2 to s3 with 15 Mbps and 4% loss
        self.addLink(s2, h2)                    # s2 to h2
        self.addLink(s3, h3)                    # s3 to h3
        self.addLink(s3, h4)                    # s3 to h4

if __name__ == '__main__':
    topo = CustomTopo()
    net = Mininet(topo=topo, switch=OVSKernelSwitch, link=TCLink)
    net.start()

    # Run iperf tests
    print("Testing TCP bandwidth between h1 and h3 with 4% packet loss")
    h1, h3 = net.get('h1', 'h3')
    net.iperf((h1, h3), l4Type='TCP')

    print("Testing TCP bandwidth between h2 and h4 with 4% packet loss")
    h2, h4 = net.get('h2', 'h4')
    net.iperf((h2, h4), l4Type='TCP')

    # Open CLI for additional tests or debugging
    CLI(net)
    net.stop()
