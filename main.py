import argparse

import os

from cryptography.hazmat.primitives import serialization
from datetime import datetime

import asyncio
import zmq

from multiprocessing import Process
from exchange_interface.publishers import Publishers
from exchange_interface.logging import LoggingSubscriber
from exchange_interface.kalshi_client import KalshiHttpClient, Environment

from scripts.utils import signal_handler, create_shutdown_handler

import signal

from trading_logic.strategy import BaseStrategy 

import dotenv

def main():
    dotenv.load_dotenv()

    key_id = os.getenv("KEY_ID")
    private_key_path = os.getenv("KEY_PATH")
    key = KalshiHttpClient.load_private_key_from_file(private_key_path)

    http_client = KalshiHttpClient(key_id=key_id, private_key=key, environment=Environment.PROD)

    # specify a list of tickers to subscribe to
    tickers = ["KXHIGHNY-25MAY23-B60.5"]

    broker = Publishers.broker()
    kalshi_publisher = Publishers.kalshi_publisher(key_id, key, http_client, tickers)

    # add process for broker and logging
    workers = [
        Process(
            target=asyncio.run,
            kwargs={"main": broker}
        ), 
        Process(target=LoggingSubscriber.logging),
    ]

    # add each new strat
    for ticker in tickers:
        # create new strategy process for each ticker
        strat = BaseStrategy(http_client, ticker, MAX_LATENCY=0.01)
        workers.append(
            Process(
                target=strat.handler
            )
        )

    # add publisher
    workers.append(Process(
            target=asyncio.run,
            kwargs={"main": kalshi_publisher}
        )
    )

    for w in workers:
        w.start()

    shutdown_handler = create_shutdown_handler(workers)
    signal.signal(signal.SIGINT, shutdown_handler)   
    signal.signal(signal.SIGTERM, shutdown_handler)  

    while True:
        pass  

if __name__ == "__main__":
    main()