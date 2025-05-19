### source: https://github.com/Harvard-CS145/routing

# Final Project: Distance-Vector Routing Algorithm

**Author**: Chung Thị Mai Anh  
**Student ID**: 23021460  
**Course**: INT2213 7, Computer Networks – University of Engineering and Technology, VNU  
**Repository**: [Harvard-CS145/routing](https://github.com/Harvard-CS145/routing)

---

## 🚀 Overview

This project implements the **Distance-Vector (DV) Routing Protocol** as part of a network simulation framework.  
Routers use distributed DV algorithms to compute the lowest-cost paths to all destinations inside a simulated autonomous system.

Implemented in `DVrouter.py`, the algorithm:
- Maintains a distance vector with the cost and next hop for each destination
- Exchanges routing updates with neighbors periodically or upon change
- Reacts to link failures and cost changes correctly
- Recomputes the entire routing table based on neighbors' advertisements

---
## Algorithm Summary
Each router keeps:
- routing_table: destination → (cost, next_hop)
- neighbor_dv: distance vectors received from neighbors
- link_cost: direct cost to each neighbor

Updates happen:
- When new DV is received
- When link goes up/down
- Periodically (heartbeat)

Distance vectors are exchanged via Packet.ROUTING, encoded as JSON.
Infinity is set to 16 to prevent count-to-infinity loops.