import os
import zmq
import websockets

from exchange_interface.kalshi_client import Environment, KalshiHttpClient, KalshiWebSocketClient, Util
from exchange_interface.packet_processor import NormalizedPacket, Source, PacketType, Processor

import time
class Publishers:
    async def backtest_publisher(file, grace_period):
        ctx = zmq.Context()

        sock = ctx.socket(zmq.PUB)
        sock.connect("ipc:///tmp/pub")

        # This is not ideal, but we need to wait for subscribers to connect
        time.sleep(grace_period)

        # read in file and send all packets over the message broker
        with open(file, 'r') as f:
            for line in f:
                packet = Processor.process_normalized(line)
                sock.send_pyobj(packet) 

    async def kalshi_publisher(key_id, key, http_client, tickers):
        env = Environment.PROD
    
        ctx = zmq.Context()

        sock = ctx.socket(zmq.PUB)
        sock.connect("ipc:///tmp/pub") 
         
        ws_client: KalshiWebSocketClient = KalshiWebSocketClient(
            key_id, 
            key,
            http_client,
            sock,
            tickers,
            env
        )

        await ws_client.run()

    async def broker(): 
        ctx = zmq.Context()

        # we call this pub socket because publishers are publishing to it
        pub_sock = ctx.socket(zmq.SUB)
        pub_sock.bind("ipc:///tmp/pub")
        pub_sock.subscribe(b'')

        # we call this sub socket because the trading logic and logging subscribe to it
        sub_sock = ctx.socket(zmq.PUB)
        sub_sock.bind("ipc:///tmp/main_feed")

        pub_sock.recv()

        while True:
            packet = pub_sock.recv_pyobj()
            sub_sock.send_pyobj(packet)