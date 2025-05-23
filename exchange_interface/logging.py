import zmq
from exchange_interface.packet_processor import PacketType, NormalizedPacket
import time

class LoggingSubscriber:
    def logging(): 
        ctx = zmq.Context()

        sock = ctx.socket(zmq.SUB)
        sock.connect("ipc:///tmp/main_feed")
        sock.subscribe(b'')

        f_name = f"logging/messages-{time.time()}.log"
        handle = open(f_name, "a")

        while True:
            packet: NormalizedPacket = sock.recv_pyobj()
            if packet.packet_type != PacketType.OTHER:
                print(packet)
                handle.write(str(packet) + '\n')
