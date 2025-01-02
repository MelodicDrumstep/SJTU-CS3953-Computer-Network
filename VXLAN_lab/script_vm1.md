```shell
sudo mn --custom topology.py --topo topo --link=tc

h1 ifconfig h1-eth0 10.0.0.1 netmask 255.0.0.0 # Inside mininet

# Inside another terminal
sudo ifconfig s1 10.0.0.2/8 up 
sudo ovs-vsctl add-br br1
sudo ovs-vsctl add-port br1 enp0s8
sudo ifconfig br1 192.168.56.101/24 up
sudo route add default gw 192.168.56.201
sudo ovs-vsctl add-port s1 vx1 -- set interface vx1 type=vxlan options:remote_ip=192.168.56.102
```