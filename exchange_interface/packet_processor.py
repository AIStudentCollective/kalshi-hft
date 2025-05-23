import json
from enum import Enum
import time

class Source(Enum):
    KALSHI = 0
    LOCAL = 1

class PacketType(Enum):
    ORDERBOOK_SNAPSHOT = 0
    ORDERBOOK_DELTA = 1
    TRADE = 2
    FILL = 3
    LOCAL_TRADE = 4
    LOCAL_CANCEL = 5
    OTHER = 6

class NormalizedPacket:
    def __init__(self, source: Source, timestamp: float, packet_type: PacketType, data: dict):
       self.source = source
       self.timestamp = timestamp
       self.packet_type = packet_type
       self.data = data

    def __str__(self):
        return json.dumps(
            {
                'source': self.source.name,
                'timestamp': self.timestamp,
                'packet_type': self.packet_type.name,
                'data': self.data
            }
        )

class Processor():
    # This is the default packet format for trading strategies
    def process_normalized(packet: str) -> NormalizedPacket:
       jpacket = json.loads(packet)

       return NormalizedPacket(Source[jpacket['source']], jpacket['timestamp'], PacketType[jpacket['packet_type']], jpacket['data']) 

    # Converts raw kalshi packet into normalized format
    def process_kalshi(packet: str) -> NormalizedPacket:
        curr_time = time.time()

        jpacket = json.loads(packet.replace("'", "\""))
        if jpacket['type'] == 'orderbook_snapshot':
            return NormalizedPacket(Source.KALSHI, curr_time, PacketType.ORDERBOOK_SNAPSHOT, jpacket['msg'])
        elif jpacket['type'] == 'orderbook_delta':
            return NormalizedPacket(Source.KALSHI, curr_time, PacketType.ORDERBOOK_DELTA, jpacket['msg'])
        elif jpacket['type'] == 'trade':
            return NormalizedPacket(Source.KALSHI, curr_time, PacketType.TRADE, jpacket['msg'])
        elif jpacket['type'] == 'fill':
            return NormalizedPacket(Source.KALSHI, curr_time, PacketType.FILL, jpacket['msg'])
        else: return NormalizedPacket(Source.KALSHI, curr_time, PacketType.OTHER, {}) 