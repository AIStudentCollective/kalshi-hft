import argparse

import os

from cryptography.hazmat.primitives import serialization
from datetime import datetime

import asyncio
import zmq

import dotenv

from multiprocessing import Process
from exchange_interface.publishers import Publishers
from exchange_interface.kalshi_client import KalshiHttpClient, Environment

from trading_logic.strategy import BaseStrategy
from scripts.utils import signal_handler, create_shutdown_handler
import signal
from time import sleep

def main(): 
    dotenv.load_dotenv()

    log_file = "logging/messages-1748022111.1667926.log"
    key_id = os.getenv("KEY_ID")
    private_key_path = os.getenv("KEY_PATH")
    key = KalshiHttpClient.load_private_key_from_file(private_key_path)

    http_client = KalshiHttpClient(key_id=key_id, private_key=key, environment=Environment.PROD)

    # specify a list of tickers to subscribe to
    tickers = ["KXHIGHNY-25MAY23-B60.5"]

    # only spawning one strategy process, should create one per ticker
    strat = BaseStrategy(http_client, tickers[0], MAX_LATENCY=None)

    broker = Publishers.broker()

    # grace period sets time to wait for subscribers
    backtest_publisher = Publishers.backtest_publisher(log_file, grace_period=1)

    workers = {
        "broker": Process(
            target=asyncio.run,
            kwargs={"main": broker}
        ),
        "strat": Process(
            target=strat.handler
        ),
        "backtest_pub": Process(
            target=asyncio.run,
            kwargs={"main": backtest_publisher}
        )
    }

    for w in workers.values():
        w.start()

    shutdown_handler = create_shutdown_handler(workers)
    signal.signal(signal.SIGINT, shutdown_handler)   
    signal.signal(signal.SIGTERM, shutdown_handler)  

    while True:
        pass  

if __name__ == "__main__":
    main()