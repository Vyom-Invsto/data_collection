from datetime import datetime
from pytz import timezone
import pyotp
from oracle.shoonyApi.api_helper import ShoonyaApiPy


class Finvasia():

    instruments = []
    onmessage=None
    
    def __init__(self):
        self.api = ShoonyaApiPy()

    def login(self, userId: str, password: str, factor2: str, vc: str, api_key: str, imei: str):
        '''
        userid: finvasia user id
        password: finvasia pwd
        yob: finvasia year of birth

        return: login in finvasia account
        '''
        '''
        {'request_time': '14:11:22 01-04-2023', 'actid': 'FA96920', 'access_type': ['WEB', 'TT', 'MOB', 'API'], 'uname': 'JANHAVI DEVENDRA PATIL', 'prarr': [{'prd': 'C', 's_prdt_ali': 'CNC', 'exch': ['NSE', 'BSE', 'NIPO', 'BSTAR']}, {'prd': 'M', 's_prdt_ali': 'NRML', 'exch': []}, {'prd': 'I', 's_prdt_ali': 'MIS', 'exch': ['NSE', 'BSE']}, {'prd': 'H', 's_prdt_ali': 'CO', 'exch': ['NSE', 'BSE']}, {'prd': 'B', 's_prdt_ali': 'BO', 'exch': ['NSE', 'BSE']}], 'stat': 'Ok', 'susertoken': '62ec509b24eb4c5b2a59f99089331468b608b579f10070ef7b2eab33fbd0bea9', 'email': 'janhavi886@gmail.com', 'uid': 'FA96920', 'brnchid': 'HO', 'totp_set': '1', 'orarr': ['MKT', 'LMT', 'SL-LMT', 'SL-MKT'], 'exarr': ['NSE', 'NIPO', 'BSE', 'BSTAR'], 'values': [], 'mws': {}, 'brkname': 'FINV', 'lastaccesstime': '1680338482'}
        '''
        # credentials
        user = userId
        pwd = password
        factor2 = pyotp.TOTP(factor2).now()
        vc = vc
        api_key = api_key
        imei = imei

        ret = self.api.login(userid=user, password=pwd, twoFA=factor2,
                             vendor_code=vc, api_secret=api_key, imei=imei)

        if ret==None:
            print("\nError While Logging into Shoonya\n")

        # Change return formate
        newretDic={
            'time': ret['request_time'],
            'userid': ret['actid'],
            'name':ret['uname'],
            'email':ret['email'],
            'token':ret['susertoken']
            }
        
        return newretDic

    def set_session(self, user_id, password, token):

        ret=self.api.set_session(userid=user_id, password=password, usertoken=token)
        
        if ret==None:
            print("\nError While Logging into Shoonya\n")
        return ret

    def get_accountdetails(self):
        try:
            ret = self.api.get_limits()
        except:
            print("Error with Shoonya(Not working)!")
            ret=None
        return ret

    def get_historicaldata(self, instrument, exchange, from_date, to_date, interval):
        '''
        To get the historical data of the instrument

        instrument (str): provide the token of the instrument
        exchange (str): name the exchange
        from_date (timestamp): provide the datetime in timestamp format
        to_date (timestamp): provide the datetime in timestamp format
        interval (int): Candle size in minutes
        '''
        # Check the shoonya api
        if self.get_accountdetails()==None:
            return
        
        ret = self.api.get_time_price_series(
            exchange=exchange, token=instrument, starttime=from_date, endtime=to_date, interval=interval)
        return ret
