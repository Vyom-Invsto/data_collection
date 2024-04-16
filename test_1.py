from oracle  import OracleLiveData

ora = OracleLiveData(broker_name='finvasia')
ora.login(
    user_id="FA307801",
    password="Vyom@invsto1",
    factor2="44VR726763CN2JS3SAQ5366QLE62H2VA",
    vc="FA307801_U",
    api_key="3ecf70874d69583b02d599b1471c749b",
    imei="abc1234",
)
ret = ora.get_accountdetails()
print(ret)

def onerror(ms):
    print(ms)

def onclose(ms):
    print(ms)

def onmessage(msg):
    print(msg)

instruments = ["TATAMOTORS", "TATASTEEL", "TCS"]
ora.get_livedata(
    instruments=instruments, exchange="NSE", onclose=onclose, onerror=onerror, onmessage=onmessage, searchscrip=True
)