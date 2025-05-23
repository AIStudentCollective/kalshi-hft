from enum import Enum
import heapq
from typing import List
from bisect import insort


class Side(Enum):
    BID = 0 
    ASK = 1

class Limit():
    def __init__(self, price, side):
        self.volume = 0
        self.price = price
        self.side = side

    # Least is worst 
    def __lt__(self, other):
        if self.side == Side.BID:
            return self.price > other.price
        if self.side == Side.ASK:
            return self.price < other.price
    
    def __repr__(self) -> str:
        return f"{self.price} {self.volume}"
    
class BookSide():
    def __init__(self, side):
        self.limits: list[Limit] = []

        for i in range(0, 101):
            self.limits.append(Limit(i, side))

        self.active_limits: List[Limit] = []
        self.limitset = set()
     
    def add_order(self, price, vol): 
        self.limits[price].volume += vol
        if self.limits[price].volume > 0 and not self.limits[price] in self.limitset:
            insort(self.active_limits, self.limits[price])
            self.limitset.add(self.limits[price])

        if self.limits[price].volume == 0 and self.limits[price] in self.limitset:
            self.active_limits.remove(self.limits[price])
            self.limitset.remove(self.limits[price])

    def remove_order(self, price, vol):
        self.add_order(price, -vol)
 
    # ignore is set if we have our own orders on the book and want to ignore it
    def get_best(self, ignore):
        if len(self.active_limits) == 0:
            return None

        if ignore and len(self.active_limits) <= 1:
            return None

        return self.active_limits[1] if ignore else self.active_limits[0]

""" Orderbook that stores in bid-ask format """
class OrderBook:
    def __init__(self):
        self.bid_book = BookSide(Side.BID)
        self.ask_book = BookSide(Side.ASK)
    
    def add_order(self, side, price, vol):
        book = self.bid_book if side == Side.BID else self.ask_book
        book.add_order(price, vol)

    def remove_order(self, side, price, vol): 
        book = self.bid_book if side == Side.BID else self.ask_book
        book.remove_order(price, vol)

    def get_best(self, side, ignore):
        book = self.bid_book if side == Side.BID else self.ask_book
        return book.get_best(ignore)
    
    def clear(self):
        for lim in self.bid_book.active_limits:
            self.bid_book.remove_order(lim.price, lim.volume)

        for lim in self.ask_book.active_limits:
            self.ask_book.remove_order(lim.price, lim.volume)