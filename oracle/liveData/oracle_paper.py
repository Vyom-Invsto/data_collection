import random
import string
import time
from datetime import datetime
from pytz import timezone

class Paper():
    def __init__(self):
        pass

    def get_nowtime(self, market):

        marketdic = {
            'India': 'Asia/Kolkata',
            'US': 'US/Eastern',
            'Crypto': 'UTC'
        }

        marketzone = marketdic[market]

        IST = timezone(marketzone)
        nowtime = datetime.now(tz=IST).strftime('%H:%M')

        return nowtime

    def get_historicaldata(self, market, instrumentName, startprice, volatility):
        tokenNumber = ''.join(random.choices(string.digits, k=5))

        Uperlevel = startprice*(1+(volatility))
        Lowlevel = startprice*(1-(volatility))

        startprice = round(random.uniform(Lowlevel, Uperlevel), 2)

        msg = {
            "status": "success",
            "data": {
                f"{instrumentName}": {
                    "instrument_token": tokenNumber,
                    "last_price": startprice
                }
            }
        }

        return msg

    def market_status(self, market):
        marketdic = {
            'India': {
                'Asia/Kolkata': ['09:15', '15:30']
            },
            'US': {
                'US/Eastern': ['09:30', '16:00']
            },
            'Crypto': {
                'UTC': ['00:00', '24:00']
            }
        }

        market = marketdic[market]

        opentime = market[list(market.keys())[0]][0]
        closetime = market[list(market.keys())[0]][1]

        IST = timezone(list(market.keys())[0])
        nowtime = datetime.now(tz=IST).strftime('%H:%M')

        if opentime <= nowtime <= closetime:
            return {'Market': 'Open'}
        else:
            return {'Market': 'Close'}

    def get_livedata(self, market, instrumentName, startprice, volatility, onmessage, searchscrip: bool= False):
        def price_generator(startprice, volatility):
            Uperlevel = startprice*(1+(volatility))
            Lowlevel = startprice*(1-(volatility))

            startprice = round(random.uniform(Lowlevel, Uperlevel), 2)
            return startprice

        def check_market_status(market, startprice, volatility):
            while self.market_status(market)['Market'] == 'Open':
                startprice = price_generator(startprice, volatility)
                yield startprice
                time.sleep(1)
            else:
                exit(print('Market closed!'))

        tokenNumber = ''.join(random.choices(string.digits, k=5))

        for price in (check_market_status(market, startprice, volatility)):
            msg = {
                "status": "success",
                "data": {
                    f"{instrumentName}": {
                        "instrument_token": tokenNumber,
                        "last_price": price
                    }
                }
            }
            onmessage(msg)
