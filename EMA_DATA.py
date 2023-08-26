
from pya3 import *
import pandas as pd
import datetime
import pytz
import json
import os
import pathlib
from retrying import retry



@retry(stop_max_attempt_number=3, wait_fixed=10000)
def gen_data():
    # User Credential
    user_id = '771791'
    api_key = 'jOf1uqDV2objI4Obj33QuoTN4Iz7qXD0mW5X0WgupaH8k9NvWV0hqifsdN6Rf1vmEmGEbHJsLq448Kkt6tU7u5qocJyOTQOYJAxxcq1dyqHzs1br5IGFnpsQrPUATctt'
    year_dict = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}

    # Connect and get session Id
    alice = Aliceblue(user_id=user_id, api_key=api_key)
    print(alice.get_session_id())
    print("******************************  CONNECTION ESTABLISHED WITH API  *******************************")
    alice.get_contract_master("NFO")
    sleep(5)
    #pathlib.Path('/home/ravik/.config/JetBrains/PyCharmCE2022.2/scratches/NFO.csv').rename('/home/ravik/.config/JetBrains/PyCharmCE2022.2/scratches/Dynamic Update/NFO.csv')


    print('STEP-1: NFO DATA DOWNLOAD COMPLETE')

    nifty = alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26000))
    bank_nifty = alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26009))
    fin_nifty = alice.get_scrip_info(alice.get_instrument_by_token('INDICES', 26037))



    print("STEP-2: CALCULATING ATM AT CLOSE")

    nifty_close_atm = round(float(nifty['PrvClose']), -2)
    bank_nifty_close_atm = round(float(bank_nifty['PrvClose']), -2)
    fin_nifty_close_atm = round(float(fin_nifty['PrvClose']), -2)



    df = pd.read_csv('NFO.csv')
    expiry_nifty_df = df[df['Symbol'] == 'NIFTY']
    expiry_bnnifty_df = df[df['Symbol'] == 'BANKNIFTY']
    expiry_finnifty_df = df[df['Symbol'] == 'FINNIFTY']


    expiry_nifty = expiry_nifty_df['Expiry Date'].sort_values().drop_duplicates().reset_index(drop=True)
    expiry_banknifty = expiry_bnnifty_df['Expiry Date'].sort_values().drop_duplicates().reset_index(drop=True)
    expiry_finnifty = expiry_finnifty_df['Expiry Date'].sort_values().drop_duplicates().reset_index(drop=True)


    nifty_expiry = expiry_nifty[0] if str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date()) == str(
        expiry_nifty[0]) else expiry_nifty[0]
    banknifty_expiry = expiry_banknifty[0] if str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date()) == str(
        expiry_banknifty[0]) else expiry_banknifty[0]
    finnifty_expiry = expiry_finnifty[0] if str(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).date()) == str(
        expiry_finnifty[0]) else expiry_finnifty[0]

    print("UPCOMING EXPIRIES:\n")
    print("NIFTY : {}\n".format(nifty_expiry))
    print("BANKNIFTY : {}\n".format(banknifty_expiry))
    print("FINNIFTY : {}\n".format(finnifty_expiry))

    dic = {}



    def create_dic(symbol, expiry, strike, o_type, expiry_):
        try:
            base_symbol = symbol
            option_type = "C" if o_type == "CE" else "P"
            striki = str(int(strike))
            trading_symbol = base_symbol + expiry_ + option_type + striki

            date_ = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
            if date_.strftime('%A') == 'Monday':
                days = 3
            else:
                days = 1

            instrument = alice.get_instrument_for_fno(exch='NFO', symbol=symbol, expiry_date=expiry, is_fut=False,
                                                    strike=strike, is_CE=True if o_type == "CE" else False)

            

            from_datetime = datetime.datetime.now(pytz.timezone('Asia/Kolkata')) - datetime.timedelta(
                days=days)  # From last & days
            to_datetime = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))  # To now
            interval = "1"  # ["1", "D"]
            indices = False  # For Getting index data
            df_ = alice.get_historical(instrument, from_datetime, to_datetime, interval, indices)
            #print(df_)
            lst = []
            for i in range(len(df_)):
                if (int(df_['datetime'][i].split(' ')[1].split(':')[1])) % 15 == 14:
                    lst.append(df_['close'][i])
            dic[trading_symbol] = lst
        except:
            print("{} instrument not tradable".format(trading_symbol))

    def get_expiry_date_trading_symbol(expiry_):
        expiry_ = str(expiry_)
        expiry_date = (expiry_.split("-")[2])
        expiry_year = str(expiry_.split("-")[0])
        month_list = year_dict.keys()
        for x in month_list:
            if year_dict[x] == expiry_.split("-")[1]:
                expiry_month = str(x)
        return expiry_date + expiry_month + expiry_year[2:]


    expiry_format_banknifty = get_expiry_date_trading_symbol(str(banknifty_expiry))
    expiry_format_nifty = get_expiry_date_trading_symbol(str(nifty_expiry))
    expiry_format_finnifty = get_expiry_date_trading_symbol(str(finnifty_expiry))

    print("STEP-3: GENERATING DATA FOR BANKNIFTY........")
    print("NON TRADABLE INSTRUMENTS BANKNIFTY:")

    for x in range(-20, 20):
        create_dic("BANKNIFTY", banknifty_expiry, int(bank_nifty_close_atm) + (x * 100), "CE", expiry_format_banknifty)
        create_dic("BANKNIFTY", banknifty_expiry, int(bank_nifty_close_atm) + (x * 100), "PE", expiry_format_banknifty)

    print("STEP-4: GENERATING DATA FOR NIFTY........")
    print("NON TRADABLE INSTRUMENTS NIFTY:")

    for x in range(-10, 11):
        create_dic("NIFTY", nifty_expiry, nifty_close_atm + (x * 100), "CE", expiry_format_nifty)
        create_dic("NIFTY", nifty_expiry, nifty_close_atm + (x * 100), "PE", expiry_format_nifty)

    print("STEP-5: GENERATING DATA FOR FINNIFTY........")
    print("NON TRADABLE INSTRUMENTS FINNIFTY:")


    for x in range(-10, 11):
        create_dic("FINNIFTY", finnifty_expiry, fin_nifty_close_atm + (x * 100), "CE", expiry_format_finnifty)
        create_dic("FINNIFTY", finnifty_expiry, fin_nifty_close_atm + (x * 100), "PE", expiry_format_finnifty)

    if os.path.exists("data_ema.json"):
        os.remove("data_ema.json")

    with open("data_ema.json", "w") as outfile:
        json.dump(dic, outfile, indent=3)

    print('STEP-6: NEW "data_ema.json" GENERATED')
    print("**********************************  TASK COMPLETE   *********************************************")


gen_data()