import os
import sys
import requests
from exchange_interface.orderbook import Side, OrderBook
from exchange_interface.packet_processor import NormalizedPacket, PacketType, Source
from dotenv import load_dotenv
from exchange_interface.kalshi_client import KalshiHttpClient, Environment
import zmq
from typing import Dict, Any, List, Optional
from datetime import datetime
from datetime import datetime
import uuid
from requests import HTTPError

import time

class MarketOrderException(Exception):
    pass

class LimitOrderException(Exception):
    pass

class CancelOrderException(Exception):
    pass


class BaseStrategy():
    def __init__(self, http_client, ticker, MAX_LATENCY=None):  
        self.book = OrderBook()
        self.http_client = http_client 
        self.ticker = ticker
        self.MAX_LATENCY = MAX_LATENCY

    def handler(self): 
        ctx = zmq.Context()

        sock = ctx.socket(zmq.SUB)
        sock.connect("ipc:///tmp/main_feed")
        sock.subscribe(b'')

        while True:
            packet: NormalizedPacket = sock.recv_pyobj()
            if packet.packet_type != PacketType.OTHER:
                self.process_packet(packet)
    
    def process_packet(self, packet): 
        # need to make sure the packet actually is for this strategy
        if packet.source == Source.KALSHI and packet.data['market_ticker'] == self.ticker:
            # Remember that kalshi gives yes/no but our book is in bid ask
            if packet.packet_type == PacketType.ORDERBOOK_SNAPSHOT:
                # clear order book and restore from snapshot
                self.book.clear()
                for lim in packet.data['yes']:
                    self.book.add_order(Side.BID, lim[0], lim[1])

                for lim in packet.data['no']:
                    self.book.add_order(Side.ASK, 100 - lim[0], lim[1])

            elif packet.packet_type == PacketType.ORDERBOOK_DELTA:
                if packet.data['side'] == 'yes':
                    self.book.add_order(Side.BID, packet.data['price'], packet.data['delta'])
                else:
                    # Yes ask = 100 - no bid
                    self.book.add_order(Side.ASK, 100 - packet.data['price'], packet.data['delta'])

        # If packet is too old, we just ignore it and dont trade on it 
        if self.MAX_LATENCY is not None and time.time() - packet.timestamp > self.MAX_LATENCY:
            return

        self.strategy(packet)

    def strategy(self, packet):
        raise NotImplementedError 

    def place_market_order(self, ticker, id, volume, side):
        if side == Side.BID:
            order_data = {
                "action": "buy",
                "count": volume,
                "side": "yes",
                "ticker": ticker,
                "type": "market",
                "client_order_id": id
            }
        if side == Side.ASK:
            order_data = {
                "action": "buy",
                "count": volume,
                "side": "no",
                "ticker": ticker,
                "type": "market",
                "client_order_id": id
            } 
        try:
            self.http_client.placeOrder(order_data, "/trade-api/v2/portfolio/orders") 
        except Exception as e:
            raise MarketOrderException()

    def place_limit_order(self, ticker, id, volume, side, price):
        if side == Side.BID:
            order_data = {
                "action": "buy",
                "count": volume,
                "side": "yes",
                "ticker": ticker,
                "yes_price": price,
                "type": "limit",
                "client_order_id": id
            }
        if side == Side.ASK:
            order_data = {
                "action": "buy",
                "count": volume,
                "side": "no",
                "ticker": ticker,
                "no_price": 100 - price,
                "type": "limit",
                "client_order_id": id
            }
        try:
            self.http_client.placeOrder(order_data, "/trade-api/v2/portfolio/orders") 
        except Exception as e:
            raise LimitOrderException()
 
    def cancel_order(self, order_id: str, side) -> Any:
        try:
            self.http_client.delete(
                path=f"/trade-api/v2/portfolio/orders/{order_id}"
            )
        except HTTPError as e:
            # This happens when the order doesent exist/we cancelled it already 
            raise CancelOrderException()
