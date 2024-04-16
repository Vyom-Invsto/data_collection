import threading
import time
import pandas as pd
import random
import string
from datetime import datetime
import os


def generate_price():
    return round(random.uniform(10, 1000), 2)

def generate_volume():
    return random.randint(1, 1000)

def generate_tick_data():
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tick_data = {
            'Timestamp': timestamp,
            'Price': generate_price(),
            'Volume': generate_volume()
        }
        yield tick_data

def resample_previous_minute_data(previous_minute_df):
    if len(previous_minute_df) > 0:
        previous_minute_df['Timestamp'] = pd.to_datetime(previous_minute_df['Timestamp'])
        previous_minute_df.set_index('Timestamp', inplace=True)
        ohlc_data = previous_minute_df[:-1]['Price'].resample('1Min').ohlc() 
        print("Resampled data for previous minute (OHLC):")
        # print(ohlc_data)
       
        last_row = ohlc_data.iloc[-1]  
        with open('resampled_data.csv', mode='a') as f:
            f.write(f"{ohlc_data.index[-1]},{last_row['open']},{last_row['high']},{last_row['low']},{last_row['close']}\n")
        
        


def read_and_store_tick_data():
    df = pd.DataFrame(columns=['Timestamp', 'Symbol', 'Price', 'Volume'])
    previous_minute_df = pd.DataFrame(columns=['Timestamp', 'Symbol', 'Price', 'Volume'])
    global PreviousMinute
    generator = generate_tick_data()
    while True:
        tick_data = next(generator)
        df = pd.concat([df, pd.DataFrame(tick_data, index=[0])], ignore_index=True)
        
       
        current_minute = datetime.strptime(tick_data['Timestamp'], '%Y-%m-%d %H:%M:%S').minute
        if 'PreviousMinute' not in globals():
            PreviousMinute = current_minute
        if current_minute != PreviousMinute:
            PreviousMinute = current_minute
            
            all_data = pd.concat([previous_minute_df, df], ignore_index=True)
            resample_previous_minute_data(all_data)
            previous_minute_df = df.copy()
            df = pd.DataFrame(columns=['Timestamp', 'Symbol', 'Price', 'Volume'])
        
        print(df) 
        time.sleep(1)  


def main():
    tick_generator_thread = threading.Thread(target=generate_tick_data)
    tick_generator_thread.daemon = True
    tick_generator_thread.start()

    tick_reader_thread = threading.Thread(target=read_and_store_tick_data)
    tick_reader_thread.daemon = True
    tick_reader_thread.start()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
