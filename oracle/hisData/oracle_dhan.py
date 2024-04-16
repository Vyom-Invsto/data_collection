from dhanhq import dhanhq
from oracle.hisData.utils.instrument import InstrumentFinder
import pandas as pd
import pytz
from datetime import datetime

# Specify the time zone for India
india_timezone = pytz.timezone("Asia/Kolkata")


class Dhan:
    def __init__(self) -> None:
        pass

    def login(self, client_id, access_token):
        """
        To login on dhan api

        Args:
            client_id (str): your dhan client id
            access_token (str): access token to dhan api app
        """
        self.dhan = dhanhq(client_id, access_token)

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
