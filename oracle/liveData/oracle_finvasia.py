from datetime import datetime
from pytz import timezone
import pyotp
from oracle.shoonyApi.api_helper import ShoonyaApiPy


class Finvasia:

    instruments = []
    onmessage = None

    def __init__(self):
        self.api = ShoonyaApiPy()

    def orderParametersDic(self, para):
        paraDic = {
            # Order side
            "BUY": "B",
            "SELL": "S",
            # Product type
            "CNC": "C",
            "NRML": "M",
            "MIS": "I",
        }

        return paraDic[para]

    def login(
        self, userId: str, password: str, factor2: str, vc: str, api_key: str, imei: str
    ):
        """
        userid: finvasia user id
        password: finvasia pwd
        yob: finvasia year of birth

        return: login in finvasia account
        """
        """
        {'request_time': '14:11:22 01-04-2023', 'actid': 'FA96920', 'access_type': ['WEB', 'TT', 'MOB', 'API'], 'uname': 'JANHAVI DEVENDRA PATIL', 'prarr': [{'prd': 'C', 's_prdt_ali': 'CNC', 'exch': ['NSE', 'BSE', 'NIPO', 'BSTAR']}, {'prd': 'M', 's_prdt_ali': 'NRML', 'exch': []}, {'prd': 'I', 's_prdt_ali': 'MIS', 'exch': ['NSE', 'BSE']}, {'prd': 'H', 's_prdt_ali': 'CO', 'exch': ['NSE', 'BSE']}, {'prd': 'B', 's_prdt_ali': 'BO', 'exch': ['NSE', 'BSE']}], 'stat': 'Ok', 'susertoken': '62ec509b24eb4c5b2a59f99089331468b608b579f10070ef7b2eab33fbd0bea9', 'email': 'janhavi886@gmail.com', 'uid': 'FA96920', 'brnchid': 'HO', 'totp_set': '1', 'orarr': ['MKT', 'LMT', 'SL-LMT', 'SL-MKT'], 'exarr': ['NSE', 'NIPO', 'BSE', 'BSTAR'], 'values': [], 'mws': {}, 'brkname': 'FINV', 'lastaccesstime': '1680338482'}
        """
        # credentials
        user = userId
        pwd = password
        factor2 = pyotp.TOTP(factor2).now()
        vc = vc
        api_key = api_key
        imei = imei

        ret = self.api.login(
            userid=user,
            password=pwd,
            twoFA=factor2,
            vendor_code=vc,
            api_secret=api_key,
            imei=imei,
        )

        if ret == None:
            print("\nError While Logging into Shoonya\n")
            return ret

        else:
            # Change return formate
            newretDic = {
                "time": ret["request_time"],
                "userid": ret["actid"],
                "name": ret["uname"],
                "email": ret["email"],
                "token": ret["susertoken"],
            }

            return newretDic

    def set_session(self, user_id, password, token):

        ret = self.api.set_session(userid=user_id, password=password, usertoken=token)

        if ret == None:
            print("\nError While Logging into Shoonya\n")
        return ret

    def get_accountdetails(self):
        try:
            ret = self.api.get_limits()
        except:
            print("Error with Shoonya(Not working)!")
            ret = None
        return ret

    def get_historicaldata(self, instrument, exchange, from_date, to_date, interval):
        """
        To get the historical data of the instrument

        instrument (str): provide the token of the instrument
        exchange (str): name the exchange
        from_date (timestamp): provide the datetime in timestamp format
        to_date (timestamp): provide the datetime in timestamp format
        interval (int): Candle size in minutes
        """
        # Check the shoonya api
        if self.get_accountdetails() == None:
            return

        ret = self.api.get_time_price_series(
            exchange=exchange,
            token=instrument,
            starttime=from_date,
            endtime=to_date,
            interval=interval,
        )
        return ret

    # application callbacks
    def event_handler_order_update(message):
        print("order event: " + str(message))

    def event_handler_price_update(message):
        IST = timezone("Asia/Kolkata")
        nowtime = datetime.now(tz=IST).strftime("%H:%M:%S")
        message["time"] = nowtime
        Finvasia.onmessage(message)

    def open_callback(self):
        self.api.subscribe(Finvasia.instruments)

    def main(self, stopTime):
        # Check the shoonya api
        if self.get_accountdetails() == None:
            return

        self.api.start_websocket(
            order_update_callback=Finvasia.event_handler_order_update,
            subscribe_callback=Finvasia.event_handler_price_update,
            socket_open_callback=self.open_callback,
            socket_error_callback=Finvasia.onerror,
            socket_close_callback=Finvasia.onclose,
        )
        while True:
            # Close websocket
            nowtime = datetime.now(tz=timezone("UTC")).strftime("%H:%M")
            if nowtime > stopTime:
                print("\nWebsocket Closed\n")
                self.api.close_websocket()
                break

    def get_livedata(
        self,
        instruments: list,
        exchange: str,
        onmessage: callable,
        onerror: callable,
        onclose: callable,
        searchscrip: bool = False,
        stopTime: str = "15:30",
    ):
        """
        To Get the tick data

        instruments (list): list of the instrument tokens with the exchange name (like: ["NSE|2885", "NSE|26000"])
        exchange (str): name the exchange
        onmessage (function): create a onmessage function with the message as the parameter (like: onmessage(message) )
        """
        # Check the shoonya api
        if self.get_accountdetails() == None:
            return

        if searchscrip == True:
            # Creating Tokens
            newInstruments = []

            for instrument in instruments:
                ret = self.api.searchscrip(exchange=exchange, searchtext=instrument)
                if ret is not None:
                    script_code = ret["values"][0]["token"]
                    script_code = exchange + "|" + script_code
                    newInstruments.append(script_code)

            if len(newInstruments) > 0:
                # Updating class variable
                Finvasia.instruments = newInstruments

        else:
            Finvasia.instruments = instruments

        Finvasia.onmessage = onmessage
        Finvasia.onerror = onerror
        Finvasia.onclose = onclose
        self.main(stopTime=stopTime)
