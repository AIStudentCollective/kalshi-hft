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
import signal

from trading_logic.strategy import BaseStrategy 

import dotenv

def signal_handler(sig, frame, workers):
    print("Shutting down all markets...")
    for name, worker in workers.items():
        worker.terminate()
        worker.join()
    print("All markets stopped.")
    exit(0)

def create_shutdown_handler(workers):
    def shutdown(signum, frame):
        """Handles shutdown signals (e.g., Ctrl+C or system shutdown)."""
        print("\nShutting down all processes...")
        for name, p in workers.items():
            print(f"Stopping {name}...")
            p.terminate()
            p.join()
        print("All processes stopped.")
        exit(0)
    return shutdown

def main():
    dotenv.load_dotenv()

    key_id = os.getenv("KEY_ID")
    private_key_path = os.getenv("KEY_PATH")
    key = KalshiHttpClient.load_private_key_from_file(private_key_path)

    http_client = KalshiHttpClient(key_id=key_id, private_key=key, environment=Environment.PROD)

    # specify a list of tickers to subscribe to
    tickers = ["KXHIGHNY-25APR03-B70.5"]

    # only spawning one strategy process, should create one per ticker
    strat = BaseStrategy(http_client, tickers[0], MAX_LATENCY=0.01)

    broker = Publishers.broker()
    kalshi_publisher = Publishers.kalshi_publisher(key_id, key, http_client, tickers)

    workers = {
        "broker": Process(
            target=asyncio.run,
            kwargs={"main": broker}
        ),
        "kalshi_pub": Process(
            target=asyncio.run,
            kwargs={"main": kalshi_publisher}
        ), 
        "logger": Process(target=LoggingSubscriber.logging),
        "strat": Process(
            target=strat.handler
        ),
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