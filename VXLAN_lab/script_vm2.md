```shell
sudo mn --custom topology.py --topo topo --link=t

h2 ifconfig h2-eth0 10.0.0.4 netmask 255.0.0.0 # Inside mininet

# Inside another terminal
sudo ifconfig s2 10.0.0.3/8 up 
sudo ovs-vsctl add-br br1
sudo ovs-vsctl add-port br1 enp0s8
sudo ifconfig br1 192.168.56.102/24 up
sudo route add default gw 192.168.56.201
sudo ovs-vsctl add-port s2 vx2 -- set interface vx2 type=vxlan options:remote_ip=192.168.56.101
```
