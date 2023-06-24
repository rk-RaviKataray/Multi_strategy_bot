import json
import pandas as pd




def generate_expiry_data():

    global ema_data
    global expiry_nifty
    global expiry_banknifty
    global expiry_finnifty


    # Opening JSON file
    with open('data_ema.json', 'r') as openfile:
        ema_data = json.load(openfile)
    print('Loaded Ema Data')

    df = pd.read_csv('NFO.csv')
    expiry_nifty_df = df[df['Symbol'] == 'NIFTY']
    expiry_bnnifty_df = df[df['Symbol'] == 'BANKNIFTY']
    expiry_finnifty_df = df[df['Symbol'] == 'FINNIFTY']
    expiry_nifty = expiry_nifty_df['Expiry Date'].sort_values().drop_duplicates().reset_index(drop=True)
    expiry_banknifty = expiry_bnnifty_df['Expiry Date'].sort_values().drop_duplicates().reset_index(drop=True)
    expiry_finnifty = expiry_finnifty_df['Expiry Date'].sort_values().drop_duplicates().reset_index(drop=True)


def get_nifty_expiry():
    return str(expiry_nifty[0])

def get_banknifty_expiry():
    return str(expiry_banknifty[0])

def get_finnifty_expiry():
    return str(expiry_finnifty[0])

def get_ema_data(symbol):
    
    return ema_data[symbol]

