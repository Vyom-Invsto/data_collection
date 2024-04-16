from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket import data_ws
from oracle.hisData.utils.instrument import InstrumentFinder
import requests
import json
import pyotp
from urllib import parse
import sys
from datetime import datetime
from pytz import timezone
import pandas as pd


class Fyers:
    def __init__(self):
        # API endpoints
        self.BASE_URL = "https://api-t2.fyers.in/vagator/v2"
        self.BASE_URL_2 = "https://api.fyers.in/api/v2"
        self.URL_SEND_LOGIN_OTP = self.BASE_URL + "/send_login_otp"
        self.URL_VERIFY_TOTP = self.BASE_URL + "/verify_otp"
        self.URL_VERIFY_PIN = self.BASE_URL + "/verify_pin"
        self.URL_TOKEN = self.BASE_URL_2 + "/token"

        self.SUCCESS = 1
        self.ERROR = -1

    def active_api(self, client_id: str, secret_key: str, redirect_uri: str):
        response_type = "code"
        state = "sample_state"

        # Create a session model with the provided credentials
        session = fyersModel.SessionModel(
            client_id=client_id,
            secret_key=secret_key,
            redirect_uri=redirect_uri,
            response_type=response_type,
        )

        # Generate the auth code using the session model
        response = session.generate_authcode()

        return response

    def send_login_otp(self, fy_id, app_id):
        try:
            payload = {"fy_id": fy_id, "app_id": app_id}

            result_string = requests.post(url=self.URL_SEND_LOGIN_OTP, json=payload)
            if result_string.status_code != 200:
                return [self.ERROR, result_string.text]

            result = json.loads(result_string.text)
            request_key = result["request_key"]

            return [self.SUCCESS, request_key]

        except Exception as e:
            return [self.ERROR, e]

    def generate_totp(self, secret):
        try:
            generated_totp = pyotp.TOTP(secret).now()
            return [self.SUCCESS, generated_totp]

        except Exception as e:
            return [self.ERROR, e]

    def verify_totp(self, request_key, totp):
        try:
            payload = {"request_key": request_key, "otp": totp}

            result_string = requests.post(url=self.URL_VERIFY_TOTP, json=payload)
            if result_string.status_code != 200:
                return [self.ERROR, result_string.text]

            result = json.loads(result_string.text)
            request_key = result["request_key"]

            return [self.SUCCESS, request_key]

        except Exception as e:
            return [self.ERROR, e]

    def verify_PIN(self, request_key, pin):
        try:
            payload = {
                "request_key": request_key,
                "identity_type": "pin",
                "identifier": pin,
            }

            result_string = requests.post(url=self.URL_VERIFY_PIN, json=payload)
            if result_string.status_code != 200:
                return [self.ERROR, result_string.text]

            result = json.loads(result_string.text)
            access_token = result["data"]["access_token"]

            return [self.SUCCESS, access_token]

        except Exception as e:
            return [self.ERROR, e]

    def get_authtoken(self, fy_id, app_id, redirect_uri, app_type, access_token):
        try:
            payload = {
                "fyers_id": fy_id,
                "app_id": app_id,
                "redirect_uri": redirect_uri,
                "appType": app_type,
                "code_challenge": "",
                "state": "sample_state",
                "scope": "",
                "nonce": "",
                "response_type": "code",
                "create_cookie": True,
            }
            headers = {"Authorization": f"Bearer {access_token}"}

            result_string = requests.post(
                url=self.URL_TOKEN, json=payload, headers=headers
            )

            if result_string.status_code != 308:
                return [self.ERROR, result_string.text]

            result = json.loads(result_string.text)
            url = result["Url"]
            returns = parse.parse_qs(parse.urlparse(url).query)
            auth_code = returns["auth_code"][0]

            return [self.SUCCESS, auth_code]

        except Exception as e:
            return [self.ERROR, e]

    def getToken(
        self, fyers_id, factor2, pin, client_id: str, secret_key: str, redirect_uri: str
    ):
        self.client_id = client_id
        send_otp_result = self.send_login_otp(fy_id=fyers_id, app_id="2")
        if send_otp_result[0] != self.SUCCESS:
            print(f"send_login_otp failure - {send_otp_result[1]}")
            sys.exit()
        else:
            print("send_login_otp success")

        # Step 2 - Generate totp
        generate_totp_result = self.generate_totp(secret=factor2)
        if generate_totp_result[0] != self.SUCCESS:
            print(f"generate_totp failure - {generate_totp_result[1]}")
            sys.exit()
        else:
            print("generate_totp success")

        # Step 3 - Verify totp and get request key from verify_otp API
        request_key = send_otp_result[1]
        totp = generate_totp_result[1]
        verify_totp_result = self.verify_totp(request_key=request_key, totp=totp)
        if verify_totp_result[0] != self.SUCCESS:
            print(f"verify_totp_result failure - {verify_totp_result[1]}")
            sys.exit()
        else:
            print("verify_totp_result success")

        # Step 4 - Verify pin and send back access token
        request_key_2 = verify_totp_result[1]
        verify_pin_result = self.verify_PIN(request_key=request_key_2, pin=pin)
        if verify_pin_result[0] != self.SUCCESS:
            print(f"verify_pin_result failure - {verify_pin_result[1]}")
            sys.exit()
        else:
            print("verify_pin_result success")

        # Step 5 - Get auth code for API V2 App from trade access token
        client_id_list = list(client_id.split("-"))
        token_result = self.get_authtoken(
            fy_id=fyers_id,
            app_id=client_id_list[0],
            redirect_uri=redirect_uri,
            app_type=client_id_list[1],
            access_token=verify_pin_result[1],
        )
        if token_result[0] != self.SUCCESS:
            print(f"token_result failure - {token_result[1]}")
            sys.exit()
        else:
            print("token_result success")

        # Step 6 - Get API V2 access token from validating auth code
        auth_code = token_result[1]

        appSession = fyersModel.SessionModel(
            client_id=client_id,
            redirect_uri=redirect_uri,
            response_type="code",
            secret_key=secret_key,
            grant_type="authorization_code",
        )

        appSession.set_token(auth_code)
        response = appSession.generate_token()
        self.access_token = response["access_token"]

        return self.access_token

    def login(self, token: str):
        self.fyers = fyersModel.FyersModel(client_id=self.client_id, token=token)
        return self.fyers

    def get_accountdetails(self):
        return self.fyers.get_profile()

    def get_historicaldata(
        self,
        instrument: str,
        exchange: str,
        interval: str,
        from_date: str,
        to_date: str,
    ):
        fyInstrument = InstrumentFinder(name=instrument, brokerage="fyers")[1]
        to_date = datetime.now().strftime("%Y-%m-%d") if to_date is None else to_date
        data = {
            "symbol": f"{fyInstrument}",
            "resolution": f"{interval}",
            "date_format": "1",
            "range_from": f"{from_date}",
            "range_to": f"{to_date}",
            "cont_flag": "1",
        }
        hisdata = self.fyers.history(data)
        try:
            df = pd.DataFrame(
                hisdata["candles"],
                columns=["Datetime", "Open", "High", "Low", "Close", "Volume"],
            )
            df["Datetime"] = pd.to_datetime(df["Datetime"], unit="s")
            df.set_index("Datetime", inplace=True)
            df["Instrument"] = instrument
            return df
        except:
            return hisdata
