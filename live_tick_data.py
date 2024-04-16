import threading
import time
import mysql.connector
from datetime import datetime, timedelta
import pandas as pd
from oracle import OracleLiveData
import concurrent.futures

def onerror(error_message):
    print(f"Error: {error_message}")

def onclose(close_message):
    print(f"Connection closed: {close_message}")

def onmessage(message):
    process_json_data(message)

def process_json_data(data):
    try:
        if 'lp' in data:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            symbol = data.get('tk')
            price = float(data.get('lp'))
            print(f"Received message: {data}")
        else:
            pass
       
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="invsto"
        )
        cursor = connection.cursor()
        table_name = f"tick_data_{symbol}"
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, timestamp DATETIME, price FLOAT)"
        cursor.execute(create_table_query)
        
        query = f"INSERT INTO {table_name} (timestamp, price) VALUES (%s, %s)"
        cursor.execute(query, (timestamp, price))
        connection.commit()
        print(f"Data inserted into {table_name}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        onerror(f"Error processing data: {e}")


def data_ingestion():
    ora = OracleLiveData(broker_name='finvasia')
    
    try:
        ora.login(
            user_id="FA307801",
            password="Vyom@invsto1",
            factor2="44VR726763CN2JS3SAQ5366QLE62H2VA",
            vc="FA307801_U",
            api_key="3ecf70874d69583b02d599b1471c749b",
            imei="abc1234",
        )
    except Exception as e:
        onerror(f"Login failed: {e}")
        return
    
    try:
        instruments = ["TATAMOTORS", "TATASTEEL", "TCS"]
        ora.get_livedata(
            instruments=instruments,
            exchange="NSE",
            onclose=onclose,
            onerror=onerror,
            onmessage=onmessage,
            searchscrip=True
        )
    except Exception as e:
        onerror(f"Failed to get live data: {e}")
        return

    while True:
        time.sleep(1)

def main():
    data_ingestion_thread = threading.Thread(target=data_ingestion)
    data_ingestion_thread.daemon = True
    data_ingestion_thread.start()
    

    table_to_resample = "tick_data_11536" 
    resampling_thread = threading.Thread(target=resample_table_data, args=(table_to_resample,))
    resampling_thread.daemon = True
    resampling_thread.start()

    resampling_thread.join()

    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
