import requests


def InstrumentFinder(name: str, brokerage: str):
    """
    To fetch the name of the instrument and securitycode.
    https://84qcxu5xms.us-east-2.awsapprunner.com/get_instrument_token/SBIN/zerodha

    Args:
        name(str): name of the instrument
        brokerage(str): name of the brokerage
    return:
        list: instrument_name, securitycode (only for nse).
    """

    url = rf"https://84qcxu5xms.us-east-2.awsapprunner.com/get_instrument_token/{name}/{brokerage}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

    if response.status_code == 200:
        try:
            ret = response.json()[0]
            instrument_name = ret[0]
            securitycode = ret[1]
        except:
            print("Error while fetching instruments name.")
            print(f"ApiResponse: {response.json()}, For instrument: {name} of brokers: {brokerage}.")
            
            instrument_name = -1
            securitycode = -1
    else:
        instrument_name = -1
        securitycode = -1

    return [instrument_name, securitycode]


if __name__ == "__main__":
    ret = InstrumentFinder(name="SBIN", brokerage="fyers")
    print(ret)
