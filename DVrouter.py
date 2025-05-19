####################################################
# DVrouter.py 
# Name: Chung Thị Mai Anh
# Student ID: 23021460
#####################################################

import json # thư viện chuẩn xử lí chuỗi JSON
from router import Router # lớp cơ sở Router, lớp này cung cấp các hàm send(), self.addr, self.addr (địa chỉ router)
from packet import Packet # lớp Packet để tạo và gửi gói tin định tuyến (ROUTING packet)

INFINITY = 16 # để tránh vòng lặp vô tận (count-to-infinity problem) trong DV routing

class DVrouter(Router): # lớp DVrouter kế thừa Router
    def __init__(self, addr, heartbeat_time):
        super().__init__(addr) # gọi constructor của lớp cha để gán self.addr
        self.heartbeat_time = heartbeat_time # thời gian gửi định kỳ DV (ms)
        self.last_time = 0 # lưu thời điểm lần cuối gửi DV

        self.addr = addr
        self.routing_table = {addr: (0, addr)}  # bảng định tuyến chính: dst -> (cost, next_hop); chính nó, cost = 0
        self.link_cost = {}                     # bảng lưu chi phí trực tiếp đến các hàng xóm: neighbor -> direct cost
        self.neighbor_dv = {}                   # bảng lưu DV (distance vector) mà mình nhận được từ các hàng xóm: neighbor -> {dst: cost}
    
    # hai bảng ánh xạ: cổng <-> địa chỉ hàng xóm: 
        self.port_to_neighbor = {}              # port number -> neighbor addr
        self.neighbor_to_port = {}              # neighbor addr -> port number

    def handle_packet(self, port, packet): # hàm xử lý gói tin đến
        if packet.is_traceroute: # nếu gói tin là gói tin dữ liệu từ client (traceroute)?
            dst = packet.dst_addr
            if dst in self.routing_table:
                next_hop = self.routing_table[dst][1]
                if next_hop in self.neighbor_to_port:
                    self.send(self.neighbor_to_port[next_hop], packet)
        else: # nếu gói tin là gói tin định tuyến (ROUTING packet) chứa DV từ hàng xóm
            neighbor = packet.src_addr
            try:
                received = json.loads(packet.content) # parse JSON thành dict
            except:
                return # ỏ qua nếu lỗi gói tin
            # Loại các cost lỗi ≥ INFINITY
            self.neighbor_dv[neighbor] = {dst: cost for dst, cost in received.items() if cost < INFINITY}

            # Tính lại toàn bộ bảng định tuyến nếu có thay đổi
            if self.recompute_routes():
                self.broadcast_dv()

    def handle_new_link(self, port, endpoint, cost): # khi có liên kết mới (ví dụ link A <-> B được tạo)
        self.port_to_neighbor[port] = endpoint
        self.neighbor_to_port[endpoint] = port
        self.link_cost[endpoint] = cost
        self.routing_table[endpoint] = (cost, endpoint) # tự thêm hàng xóm này vào routing table nếu cần

        # Tính lại định tuyến toàn mạng nếu DV thay đổi
        if self.recompute_routes():
            self.broadcast_dv()
        else:
            self.broadcast_dv()  # gửi dù không thay đổi để thông báo hàng xóm mới

    def handle_remove_link(self, port): # khi có một liên kết bị gỡ bỏ (link down)
        if port not in self.port_to_neighbor:
            return
        neighbor = self.port_to_neighbor[port]

        # Xoá khỏi tất cả bảng liên quan đến hàng xóm này
        del self.port_to_neighbor[port]
        self.neighbor_to_port.pop(neighbor, None)
        self.link_cost.pop(neighbor, None)
        self.neighbor_dv.pop(neighbor, None)

        # Tính lại định tuyến và broadcast nếu có thay đổi
        self.recompute_routes()
        self.broadcast_dv()

    def handle_time(self, time_ms): # hàm được gọi định kỳ (theo thời gian heartbeat)
        if time_ms - self.last_time >= self.heartbeat_time:
            self.last_time = time_ms
            self.broadcast_dv()

    def recompute_routes(self): # hàm tính lại toàn bộ routing_table dựa trên thông tin từ các hàng xóm
        updated = False
        new_table = {self.addr: (0, self.addr)}

        # 1. Thêm các hàng xóm trực tiếp
        for neighbor, cost in self.link_cost.items():
            if cost < INFINITY:
                new_table[neighbor] = (cost, neighbor)

        # 2. Học thêm từ DV của các hàng xóm
        for neighbor, their_dv in self.neighbor_dv.items():
            if neighbor not in self.link_cost:
                continue  # bỏ nếu link down
            cost_to_neighbor = self.link_cost[neighbor]
            for dst, neighbor_cost in their_dv.items():
                if dst == self.addr:
                    continue
                total = cost_to_neighbor + neighbor_cost
                if total >= INFINITY:
                    continue
                if dst not in new_table or total < new_table[dst][0]:
                    new_table[dst] = (total, neighbor)

        # 3. So sánh nếu bảng mới khác bảng cũ
        if new_table != self.routing_table:
            self.routing_table = new_table
            updated = True

        return updated

    def broadcast_dv(self): # gửi DV hiện tại của mình cho tất cả hàng xóm
        dv = {dst: cost for dst, (cost, _) in self.routing_table.items()}
        payload = json.dumps(dv) # chuyển thành JSON string
        for neighbor, port in self.neighbor_to_port.items():
            pkt = Packet(Packet.ROUTING, self.addr, neighbor, payload)
            self.send(port, pkt)

    def __repr__(self): # hàm in trạng thái router trên GUI mô phỏng
        return f"[{self.addr}] " + ', '.join(f"{dst}:({cost},{nh})" for dst, (cost, nh) in self.routing_table.items())
