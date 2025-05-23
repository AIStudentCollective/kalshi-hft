import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from exchange_interface.orderbook import OrderBook, Side

book = OrderBook()

# test getting best
book.add_order(Side.BID, 3, 10)
book.add_order(Side.BID, 2, 5)
book.add_order(Side.BID, 4, 10)

assert(book.get_best(Side.BID, ignore=False).price == 4)
assert(book.get_best(Side.BID, ignore=True).price == 3)

# test removing order
book.remove_order(Side.BID, 4, 1)
assert(book.get_best(Side.BID, ignore=False).price == 4)
book.remove_order(Side.BID, 4, 9)
assert(book.get_best(Side.BID, ignore=False).price == 3)

# test ask side

book.add_order(Side.ASK, 3, 10)
book.add_order(Side.ASK, 2, 5)
book.add_order(Side.ASK, 4, 10)

assert(book.get_best(Side.ASK, ignore=False).price == 2)
assert(book.get_best(Side.ASK, ignore=True).price == 3)

print("Order book passed all tests")