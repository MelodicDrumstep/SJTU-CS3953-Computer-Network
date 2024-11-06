#!/bin/bash

# Drop traffic on the redundant link between s1 and s3 to avoid loops

# Drop packets entering s1 from port 3 (connected to s3) with high priority
sudo ovs-ofctl add-flow s1 "priority=10,in_port=3,actions=drop"

# Drop packets entering s3 from port 4 (connected to s1) with high priority
sudo ovs-ofctl add-flow s3 "priority=10,in_port=4,actions=drop"

# Add flood rules for unmatched traffic with lower priority to maintain connectivity
sudo ovs-ofctl add-flow s1 "priority=1,actions=flood"
sudo ovs-ofctl add-flow s2 "priority=1,actions=flood"
sudo ovs-ofctl add-flow s3 "priority=1,actions=flood"
