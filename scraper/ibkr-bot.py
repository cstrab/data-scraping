import ibapi
from ibapi.client import EClient
from ibapi.wrapper import EWrapper

# Class for IBKR Connection
class IBApi(EWrapper,EClient):
    def __init__(self):
        EClient.__init__(self, self)

# Bot Logic
class Bot:
    ib = None
    def __init__(self):
        ib = IBApi()

# Start Bot
bot = Bot()
