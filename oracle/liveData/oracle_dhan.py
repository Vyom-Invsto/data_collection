from dhanhq import dhanhq, marketfeed
from oracle.liveData.utils.instrument import InstrumentFinder
import pandas as pd
import pytz
from datetime import datetime

# Specify the time zone for India
india_timezone = pytz.timezone("Asia/Kolkata")


class Dhan:
    def __init__(self) -> None:
        self.client_id=None
        self.access_token=None

    def login(self, client_id, access_token=None):
        """
        To login on dhan api

        Args:
            client_id (str): your dhan client id
            access_token (str): access token to dhan api app
        """
        self.client_id = client_id if client_id is not None else self.client_id
        self.access_token = access_token if access_token is not None else self.access_token
        if access_token is not None:
            self.dhan = dhanhq(self.client_id, access_token)
            return self.dhan
        else:
            print("Please provide access token to login.")

    def set_session(self, client_id, password, token):
        self.client_id =  client_id if client_id is not None else self.client_id
        self.access_token = token if token is not None else self.access_token
        if self.access_token is not None:
            self.dhan = dhanhq(self.client_id, self.access_token)
            return self.dhan
        else:
            print("Please provide access token to login.")

    def get_accountdetails(self):
        try:
            ret = self.dhan.get_fund_limits()
        except:
            print("Error with Shoonya(Not working)!")
            ret = None
        return ret

    def get_historicaldata(
        self, instrument, exchange, interval, from_date, to_date=None
    ):
        data = self.dhan.historical_minute_charts(
            symbol=InstrumentFinder(name=instrument, brokerage="dhan")[1],
            exchange_segment=exchange,
            instrument_type="EQUITY",
            expiry_code=0,
            from_date=from_date,
            to_date=to_date,
        )
        return data

    async def on_connect(self, instance):
        print("Connected to websocket")

    async def on_message(self, instance, message):
        Dhan.onmessage(message)

    def main(self, stopTime):
        subscription_code = marketfeed.Ticker
        print("Subscription code :", subscription_code)
        
        print(self.client_id)
        print(self.access_token)
        feed = marketfeed.DhanFeed(
            self.client_id,
            self.access_token,
            Dhan.instruments,
            subscription_code,
            on_connect=self.on_connect,
            on_message=self.on_message,
        )

        feed.run_forever()

    def get_livedata(
        self,
        instruments: list,
        exchange: str,
        onmessage: callable,
        onerror: callable,
        onclose: callable,
        searchscrip=False,
        stopTime: str = "15:30",
    ):

        Dhan.instruments = list()
        if searchscrip:
            for ins in instruments:
                inst = InstrumentFinder(name=ins[1], brokerage="dhan")[1]
                ret = (ins[0], inst)
                Dhan.instruments.append(ret)

        else:
            Dhan.instruments = instruments

        Dhan.onmessage = onmessage
        Dhan.onerror = onerror
        Dhan.onclose = onclose
        self.main(stopTime=stopTime)
