from .utils.brokers import brokersObjs


class OracleHisData:
    def __init__(self, broker_name):
        """
        broker (str): name of the broker
        """
        self.brokerName = broker_name

        # Creating brokers object
        self.broker = brokersObjs[broker_name]()

    def active_api(self, client_id: str, secret_key: str, redirect_uri: str):
        """
        Only for fyers to active the api.
        Copy the return uri and go on brower to active api.

        Args:
            client_id (str): app id or the client id of the api
            secret_key(str): secret key of the api
            redirect_uri(str): redirect_uri of the api
        """
        self.broker.active_api(client_id, secret_key, redirect_uri)

    def getToken(
        self, fyers_id, factor2, pin, client_id: str, secret_key: str, redirect_uri: str
    ):
        """
        Only for the fyers to get the access token

        Args:
            fyers_id: fyers user id
            factor2/totpcode: security code for totp
            pin: login pin
            client_id/app_id: app id
            secret_key: app secret key
            redirect_uri: redirect url of the app
        """

        if self.brokerName == "fyers":
            ret = self.broker.getToken(
                fyers_id, factor2, pin, client_id, secret_key, redirect_uri
            )
            return ret
        else:
            print("Only for the fyers to get the authcode uri")

    def login(
        self,
        user_id=None,
        password=None,
        factor2=None,
        api_key=None,
        api_secret=None,
        vc=None,
        imei=None,
        client_id=None,
        token=None,
    ):
        """
        Login to the brokers api

        user_id (str): user_id/client_id for finvasia and samco
        password (str): password for finvasia and samco
        factor2 (str): factor2/yob for finvasia and samco
        api_key (str): api_key/secret_key for binance and finvasia
        api_secret (str): api_secret for binance
        vc (str): vc for finvasia
        imei (str): imei for finvasia
        client_id/app_id: for fyers
        token: token for fyers
        """

        # Checking for broker and logining in
        if self.brokerName == "binance":
            if api_key != None and api_secret != None:
                ret = self.broker.login(api_key=api_key, api_secret=api_secret)
                return ret
            else:
                print("Please provides the correct login parameters!")

        elif self.brokerName == "finvasia":
            if (
                user_id != None
                and password != None
                and factor2 != None
                and vc != None
                and api_key != None
                and imei != None
            ):
                ret = self.broker.login(
                    userId=user_id,
                    password=password,
                    factor2=factor2,
                    vc=vc,
                    api_key=api_key,
                    imei=imei,
                )
                return ret
            else:
                print("Please provides the correct login parameters!")

        elif self.brokerName == "fyers":
            if token is not None:
                ret = self.broker.login(token)
                return ret
            else:
                print("Please provides the correct login parameters!")

        elif self.brokerName == "samco":
            if user_id != None and password != None and factor2 != None:
                ret = self.broker.login(userId=user_id, password=password, yob=factor2)
                return ret
            else:
                print("Please provides the correct login parameters!")

    def set_session(self, user_id, password, token):
        """
        To generate new session

        user_id (str): user_id/client_id for finvasia and samco
        password (str): password for finvasia and samco
        token (str): session token
        """

        ret = self.broker.set_session(user_id, password, token)
        return ret

    def get_accountdetails(self):
        """
        Get the account details of the broker
        """
        ret = self.broker.get_accountdetails()
        return ret

    def get_historicaldata(
        self, instrument, exchange, interval, from_date, to_date=None
    ):
        con = (
            type(exchange) == str
            and type(instrument) == str
            and from_date != None
            and interval != None
        )

        if con:
            data = self.broker.get_historicaldata(
                instrument=instrument,
                exchange=exchange,
                from_date=from_date,
                to_date=to_date,
                interval=interval,
            )
            return data
        else:
            print("Please provides the correct parameters!")
