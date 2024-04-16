# import ccxt


class Binance():

    def __init__(self):
        pass

    # def login(self, api_key, api_secret):
    #     login = ccxt.binance({
    #         api_key: api_key,
    #         api_secret: api_secret
    #     })
    #     return login

    # def get_historical_data(self, timeframe: str, symbol: str, limit: int, exchange=ccxt.binance):
    #     ohlcv = exchange.fetch_ohlcv(
    #         symbol=symbol, timeframe=timeframe, limit=limit)
    #     for data in ohlcv:
    #         print(data)
    #     return data

    # def get_live_data(self, timeframe: str, symbol: str, exchange=ccxt.binance, searchscrip: bool= False):
    #     ohlcv = exchange.fetch_ohlcv(symbol=symbol, timeframe=timeframe)
    #     for data in ohlcv:
    #         print(data)
    #     return data

    # def get_accountdetails(self, api_key, api_secret, exchange=ccxt.binance):
    #     balance = exchange.fetch_balance()
    #     return balance