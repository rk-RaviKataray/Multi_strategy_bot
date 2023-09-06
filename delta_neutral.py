from flask import Flask, jsonify, render_template, request, send_file
import webbrowser
import time as t
import threading
from pya3 import *
import pandas as pd
import datetime
import pytz
import json
import os
import pathlib
import multiprocessing
from multiprocessing import Process
from UltraDict import UltraDict
import retrying
from flask_cors import CORS
import mibian
import scipy


global delta_dict_expected
global ema_instance_list

def get_delta_neutral_strikes(delta, base_symbol):

    return delta_dict_expected[base_symbol][delta]

def get_current_short_strikes(base_symbol,delta):

    return delta_dict_current[base_symbol][delta]

    
def update_delta_dict_expected(base_symbol, target_delta):
 
        global delta_dict_expected

        closest_key = None
        closest_difference = None

        for key, value in token_dict.items():
            if key.startswith(base_symbol[0]):
                option_type = 'CALL' if key[-6] == 'C' else 'PUT'

                delta = value['DELTA']
                difference = abs(delta - target_delta)

                if closest_key is None or difference < closest_difference:
                    closest_key = key
                    closest_difference = difference
        delta_dict_expected[base_symbol][abs(target_delta)][option_type] = closest_key    

        for i in range(len(check_entries.instances)):

            if check_entries.instances[i].symbol == closest_key:
                delta_dict_expected[base_symbol][abs(target_delta)][option_type] = check_entries.instances[i]    
                return    

        obj = check_entries(closest_key , quantity=quantity_dic[base_symbol],is_hedge=False)
        delta_dict_expected[base_symbol][abs(target_delta)][option_type] = obj
        obj.start()

def calculate_dates_to_expiry(expiry):
    expiry = datetime.datetime.strptime(expiry, "%Y-%m-%d")
    current_date = datetime.datetime.now()
    days_to_expiry = expiry - current_date
    return days_to_expiry.days

def is_current_date_greater_than_latest_expiry(string_input_with_date):
    # string_input_with_date = "2023-08-03"
    past = datetime.datetime.strptime(string_input_with_date, "%Y-%m-%d")
    present = datetime.datetime.now()
    return past.date() < present.date()

def calculate_delta(underlyingPrice, StrikePrice, interestRate, daysToExpiration,option_type, option_price):
    if option_type == 'C':
        c = mibian.BS([underlyingPrice, StrikePrice, interestRate, daysToExpiration], callPrice=option_price)

        a = mibian.BS([underlyingPrice, StrikePrice, interestRate, daysToExpiration], volatility=c.impliedVolatility)

        return round(a.callDelta, 2)

    elif option_type == 'P':
        c = mibian.BS([underlyingPrice, StrikePrice, interestRate, daysToExpiration], putPrice=option_price)

        a = mibian.BS([underlyingPrice, StrikePrice, interestRate, daysToExpiration], volatility=c.impliedVolatility)

        return round(a.putDelta, 2)




app = Flask(__name__)
CORS(app, origins=["https://purple-artist-lvljo.ineuron.app:5000"]) 


# User Credential
user_id = '771791'
api_key = 'jOf1uqDV2objI4Obj33QuoTN4Iz7qXD0mW5X0WgupaH8k9NvWV0hqifsdN6Rf1vmEmGEbHJsLq448Kkt6tU7u5qocJyOTQOYJAxxcq1dyqHzs1br5IGFnpsQrPUATctt'

# Connect and get session Id
alice = Aliceblue(user_id=user_id, api_key=api_key)
print(alice.get_session_id())
# if os.path.exists("//home/ravik/Desktop/Dynamic Update/NFO.csv"):
#   os.remove("/home/ravik/Desktop/Dynamic Update/NFO.csv")
# alice.get_contract_master("NFO")
# pathlib.Path('/home/ravik/Desktop/Dynamic Update/NFO.csv').rename('/home/ravik/Desktop/Dynamic Update/NFO.csv')
print("master contract downloaded")
sleep(1.5)

LTP = 0
token_dict = UltraDict(recurse=True,create=True)
delta_dict_current = UltraDict(recurse=True,create=True)
delta_dict_expected = UltraDict(recurse=True,create=True)

'''
token_dict = {
    'NIFTY_SPOT': {"TOKEN": 0, "LP": 0.0, "POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0, "NOE": 0,
                   "BROKERAGE": 0},
    'BANKNIFTY_SPOT': {"TOKEN": 0, "LP": 0.0, "POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0,
                       "NOE": 0, "BROKERAGE": 0},
    'FINNIFTY_SPOT': {"TOKEN": 0, "LP": 0.0, "POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0,
                      "NOE": 0, "BROKERAGE": 0}}
                      '''

token_dict['NIFTY_SPOT'] = {"TOKEN": 0, "LP": 0.0, "POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0, "NOE": 0,
                            "BROKERAGE": 0, "QUANTITY":0,'DELTA':0}
token_dict['BANKNIFTY_SPOT'] = {"TOKEN": 0, "LP": 0.0, "POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0,
                                "NOE": 0, "BROKERAGE": 0,"QUANTITY":0,'DELTA':0}
token_dict['FINNIFTY_SPOT'] = {"TOKEN": 0, "LP": 0.0, "POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0,
                               "NOE": 0, "BROKERAGE": 0,"QUANTITY":0,'DELTA':0}

delta_dict_current['NIFTY'] = {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}
delta_dict_current['BANKNIFTY'] =   {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}
delta_dict_current['FINNIFTY'] =   {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}


delta_dict_expected['NIFTY'] = {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}
delta_dict_expected['BANKNIFTY'] =   {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}
delta_dict_expected['FINNIFTY'] =   {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}


socket_opened = False
subscribe_flag = False
global subscribe_list
subscribe_list = []
unsubscribe_list = []
Nifty_spot = 0
BankNifty_spot = 0
#nifty_atm = 0
#banknifty_atm = 0
#finnifty_atm = 0
# expiry_nifty = []
# expiry_banknifty = []
# expiry_finnifty = []
nifty_quantity = 500
bank_nifty_quantity = 300
finnifty_quantity = 160
NIFTY_TOTAL_PNL = 0
NIFTY_TOTAL_BROKERAGE = 0
NIFTY_NET_PNL = 0
NIFTY_TOTAL_ENTRIES = 0
BANKNIFTY_TOTAL_PNL = 0
BANKNIFTY_TOTAL_BROKERAGE = 0
BANKNIFTY_NET_PNL = 0
BANKNIFTY_TOTAL_ENTRIES = 0
FINNIFTY_TOTAL_PNL = 0
FINNIFTY_TOTAL_BROKERAGE = 0
FINNIFTY_NET_PNL = 0
FINNIFTY_TOTAL_ENTRIES = 0
N_time_ = 0
BN_time_ = 0
FN_time_= 0
interestRate = 10
ema_instance_list = []




N_pnl_list_for_dynamic_graph = []
BN_pnl_list_for_dynamic_graph = []
FN_pnl_list_for_dynamic_graph = []


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


expiry_nifty = expiry_nifty[1] if is_current_date_greater_than_latest_expiry(expiry_nifty[0]) else expiry_nifty[0]
expiry_banknifty = expiry_banknifty[1] if is_current_date_greater_than_latest_expiry(expiry_banknifty[0]) else expiry_banknifty[0]
expiry_finnifty = expiry_finnifty[1] if is_current_date_greater_than_latest_expiry(expiry_finnifty[0]) else expiry_finnifty[0]


print('next nifty expiry is on {}'.format(expiry_nifty))
print('next banknifty expiry is on {}'.format(expiry_banknifty))
print('next finnifty expiry is on {}'.format(expiry_finnifty))

nifty_days_to_expiry = calculate_dates_to_expiry(expiry_nifty)
bn_days_to_expiry = calculate_dates_to_expiry(expiry_banknifty)
fn_days_to_expiry = calculate_dates_to_expiry(expiry_finnifty)



def socket():
    def socket_open():  # Socket open callback function
        print("Connected")
        global socket_opened
        socket_opened = True
        if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
            alice.subscribe(get_subscribe_list(banknifty_atm,nifty_atm,finnifty_atm,expiry_banknifty,expiry_nifty,expiry_finnifty))

    def socket_close():  # On Socket close this callback function will trigger
        global socket_opened, LTP
        socket_opened = False
        LTP = 0
        print("Closed")

    def socket_error(message):  # Socket Error Message will receive in this callback function
        global LTP
        LTP = 0
        print("Error :", message)

    def feed_data(message):  # Socket feed data will receive in this callback function
        global LTP, subscribe_flag, token_dict, nifty_days_to_expiry, bn_days_to_expiry, fn_days_to_expiry, interestRate, Nifty_spot, BN_spot, FN_spot

        feed_message = json.loads(message)
        if feed_message["t"] == "ck":
            print("Connection Acknowledgement status :%s (Websocket Connected)" % feed_message["s"])
            subscribe_flag = True
            print("subscribe_flag :", subscribe_flag)
            print("-------------------------------------------------------------------------------")
            pass
        elif feed_message["t"] == "tk":
            print("Token Acknowledgement status :%s " % feed_message)
            print("-------------------------------------------------------------------------------")
            Token_Acknowledgement_status = feed_message
            if Token_Acknowledgement_status["ts"] not in token_dict.keys():  
                token_dict[Token_Acknowledgement_status['ts']] = {"TOKEN": Token_Acknowledgement_status['tk'],
                                                                  "LP": LTP, "POS": "", "PNL": 0.0, "LAST_ENTRY": 0.0,
                                                                  "EMA": 0.0, "FCH": 0.0, "NOE": 0.0,
                                                                  "BROKERAGE": 0.0,"QUANTITY":0}
            pass
        else:
            # print("Feed :", feed_message)
            Feed = feed_message
            if Feed["tk"] == '26000':
                token_dict['NIFTY_SPOT']["TOKEN"] = Feed['tk']
                token_dict['NIFTY_SPOT']["LP"] = float(Feed['lp'])
                Nifty_spot = float(Feed['lp'])

            if Feed["tk"] == '26009':
                token_dict['BANKNIFTY_SPOT']["TOKEN"] = Feed['tk']
                token_dict['BANKNIFTY_SPOT']["LP"] = float(Feed['lp'])
                BN_spot = float(Feed['lp'])

            if Feed["tk"] == '26037':
                token_dict['FINNIFTY_SPOT']["TOKEN"] = Feed['tk']
                token_dict['FINNIFTY_SPOT']["LP"] = float(Feed['lp'])
                FN_spot = float(Feed['lp'])

            for x in token_dict.keys():
                if Feed["tk"] == token_dict[x]["TOKEN"]:
                     
                    if 'lp' in feed_message:
                        token_dict[x]["LP"] = float(Feed['lp']) 
                        if x[0] == 'N':
                            if x[-6] == "C":
                                # underlyingPrice, StrikePrice, interestRate, daysToExpiration,option_type, option_price
                                token_dict[x]["DELTA"] = calculate_delta(underlyingPrice=Nifty_spot, StrikePrice=int(x[-5:]), interestRate= interestRate, daysToExpiration=nifty_days_to_expiry, option_type='C', option_price=Feed['lp'])
                            elif x[-6] == "P":
                                token_dict[x]["DELTA"] = calculate_delta(underlyingPrice=Nifty_spot, StrikePrice=int(x[-5:]), interestRate= interestRate, daysToExpiration=nifty_days_to_expiry, option_type='P', option_price=Feed['lp'])
                        
                        elif x[0] == 'B':
                            if x[-6] == "C":
                                token_dict[x]["DELTA"] = calculate_delta(underlyingPrice=BN_spot, StrikePrice=int(x[-5:]), interestRate= interestRate, daysToExpiration=bn_days_to_expiry, option_type='C', option_price=Feed['lp'])

                            elif x[-6] == "P":
                                token_dict[x]["DELTA"] = calculate_delta(underlyingPrice=BN_spdgot, StrikePrice=int(x[-5:]), interestRate= interestRate, daysToExpiration=bn_days_to_expiry, option_type='P', option_price=Feed['lp'])

                        elif x[0] == 'F':
                            if x[-6] == "C":
                                token_dict[x]["DELTA"] = calculate_delta(underlyingPrice=FN_spot, StrikePrice=int(x[-5:]), interestRate= interestRate, daysToExpiration=fn_days_to_expiry, option_type='C', option_price=Feed['lp'])

                            elif x[-6] == "P":
                                token_dict[x]["DELTA"] = calculate_delta(underlyingPrice=FN_spot, StrikePrice=int(x[-5:]), interestRate= interestRate, daysToExpiration=fn_days_to_expiry, option_type='P', option_price=Feed['lp'])
                        print(token_dict[x])


            # LTP = feed_message['lp'] if 'lp' in feed_message else LTP  # If LTP in the response it will store in LTP variable
            # print(type(feed_message["tk"]))
            #if feed_message["tk"] == '243769':
            #    print(feed_message)

    # Socket Connection Request
    alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                          socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)
    global socket_opened
    while not socket_opened:
        pass
    global subscribe_list, unsubscribe_list

    # Subscribe the Instrument
    print("Initial Subscribe for Index at :", datetime.datetime.now(pytz.timezone('Asia/Kolkata')))

    subscribe_list = [alice.get_instrument_by_token('INDICES', 26000), alice.get_instrument_by_token('INDICES', 26009),
                      alice.get_instrument_by_token('INDICES', 26037)]

    alice.subscribe(subscribe_list)


class processing_multi( ):

    def __init__(self, obj):
        super(processing_multi, self).__init__()
        self.obj = obj
        # self.hedge = hedge

    def run(self):
        [x.start() for x in self.obj]
        # self.hedge.hedge()




class check_entries(threading.Thread):

    instances = []

    def __init__(self, symbol, quantity,is_hedge):
        super(check_entries, self).__init__()
        check_entries.instances.append(self)
        self.current_time = None
        self.symbol = symbol
        self.lng_count = 0
        self.sht_count = 0
        self.lng = False
        self.sht = False
        self.lng_counter = 0
        self.sht_counter = 0
        self.price = 0
        self.ema = 0
        self.brokerage = 0
        self.long_entry_price = [0.0]
        self.long_exit_price = [0.0]
        self.short_entry_price = [0.0]
        self.short_exit_price = [0.0]
        self.long_pnl = 0
        self.short_pnl = 0
        self.long_pnl_booked = 0
        self.short_pnl_booked = 0
        self.first_trade = True
        self.first_candle_high = 0
        self.hedge_entry_price = []
        self.hedge_exit_price = []
        self.quantity = quantity
        self.long_brokerage = 0
        self.short_brokerage = 0
        self.price_crossed_ema = False
        self.price_greater_than_ema_loop = False
        self.price_less_than_ema_loop = False
        self.temp_closing_candle_variable = 0
        self.is_hedge = is_hedge
        self.pnl_list_for_dynamic_graph = []
        self.strategy = strategy
        self._stop_flag = threading.Event()

        self.logger = logging.getLogger(self.symbol)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(message)s")

        if not os.path.exists(f'instrument_data/{self.strategy}/{self.symbol}'):
            # Create the folder
            os.makedirs(f'instrument_data/{self.strategy}/{self.symbol}')

        # Create a console handler and add it to the logger
        log_file = os.path.join(f'./instrument_data/{self.strategy}/{self.symbol}', f"{self.symbol}.log")
        ch = logging.FileHandler(filename=log_file)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


    def run(self):

        start_time = int(9) * 60 * 60 + int(29) * 60 + int(58)
           
        end_time = int(15) * 60 * 60 + int(20) * 60 + int(59)

        if not os.path.exists(f"./instrument_data/{self.strategy}/{self.symbol}"):
            os.makedirs(f"./instrument_data/{self.strategy}/{self.symbol}")

        if is_hedge:
            self.hedge()

        while True:
                while start_time < \
                        (datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour * 60 * 60 + datetime.datetime.now(
                            pytz.timezone('Asia/Kolkata')).minute * 60 + datetime.datetime.now(
                            pytz.timezone('Asia/Kolkata')).second) \
                        < end_time:

                    with open(f"./instrument_data/{self.strategy}/{self.symbol}/candle_data.jsonl", 'a') as self.candle_data_file:
                        global token_dict
                        token_dict[self.symbol]['PNL'] = 0.0
                        token_dict[self.symbol]['LAST_ENTRY'] = 0.0
                        token_dict[self.symbol]['NOE'] = 0
                        token_dict[self.symbol]['BROKERAGE'] = 0.0
                        token_dict[self.symbol]['POS'] = ""
                    
                        token_dict[self.symbol]["QUANTITY"] = self.quantity

                        if datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second == 00:
                        
                            time_ = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s')
                            open_ = self.pnl_list_for_dynamic_graph[0]
                            high_ = max(self.pnl_list_for_dynamic_graph)
                            low_= min(self.pnl_list_for_dynamic_graph)
                            close_ = int(token_dict[self.symbol]["PNL"])
                            self.pnl_list_for_dynamic_graph.clear()
                            candle_data_to_append = {"time": int(time_)+19800, "open": open_, "high": high_, "low":low_, "close": close_}
                            json.dump(candle_data_to_append, self.candle_data_file)
                            self.candle_data_file.write('\n')
                            self.candle_data_file.flush()
                            os.fsync(self.candle_data_file)
                            sleep(1)



                        token_dict[self.symbol]["BROKERAGE"] = self.short_brokerage + self.long_brokerage

                        if self.lng == True:
                            token_dict[self.symbol]['PNL'] = self.long_pnl_booked + self.short_pnl_booked + (
                                    (float(token_dict[self.symbol]["LP"]) - token_dict[self.symbol][
                                        'LAST_ENTRY']) * self.quantity)
                            #print(f'{self.symbol}calculating pnl lng')


                        elif self.sht == True:
                            token_dict[self.symbol]['PNL'] = self.long_pnl_booked + self.short_pnl_booked + (
                                    (token_dict[self.symbol]['LAST_ENTRY'] - float(
                                        token_dict[self.symbol]["LP"])) * self.quantity)
                            #print(f'{self.symbol}calculating pnl sht')




    

    def go_long(self, pivot, reason):
        print(f'{self.symbol}in go long func')
        if (float(token_dict[self.symbol]["LP"]) > pivot) and self.lng == False:
            #print(f'{self.symbol}if (float(token_dict[self.symbol]["LP"]) > pivot) and self.lng == False:')
            # self.sht_counter = 0
            # sleep(5)
            self.lng_counter = self.lng_counter + 1
            #print(f'{self.symbol}in lng func  {self.lng_counter}')
            if (float(token_dict[self.symbol]["LP"]) > pivot) and self.lng == False:
                # and self.lng_counter == 6:
                #print(f'{self.symbol} in if (float(token_dict[self.symbol]["LP"]) > pivot) after waiting for 5 secs')
                self.price = float(token_dict[self.symbol]["LP"])
                self.lng_count = self.lng_count + 1
                token_dict[self.symbol]["NOE"] = token_dict[self.symbol]["NOE"] + 1
                self.lng = True
                token_dict[self.symbol]["POS"] = "LONG"
                # self.sht = False
                self.lng_counter = 0
                self.logger.debug('{} went long at price-{}, time-{}:{}:{}'.format(self.symbol,
                                                                       self.price,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone('Asia/Kolkata')).hour,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone(
                                                                               'Asia/Kolkata')).minute,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone(
                                                                               'Asia/Kolkata')).second))
                token_dict[self.symbol]['LAST_ENTRY'] = float(token_dict[self.symbol]["LP"])
                self.long_entry_price.append(float(token_dict[self.symbol]["LP"]))

                self.logger.debug(f'long entry dict:{self.long_entry_price}')
                self.logger.debug(f'long exit dict:{self.long_exit_price}')
                # self.short_exit_price.append(float(token_dict[self.symbol]["LP"]))

                # self.price_crossed_ema = True if reason == "EMA" else False
                '''
                if len(self.short_entry_price) == len(self.short_exit_price):
                    self.short_pnl_booked = self.short_pnl_booked + ((
                                                                             self.short_entry_price[
                                                                                 len(self.short_entry_price) - 1] -
                                                                             self.short_exit_price[
                                                                                 len(self.short_exit_price) - 1]) * self.quantity)

                    self.short_brokerage = self.short_brokerage + self.calc_brokerage(
                        self.short_entry_price[len(self.short_entry_price) - 1], self.short_exit_price[
                            len(self.short_exit_price) - 1], "SHORT")
                '''

    def go_short(self, pivot, reason):
        #print(f'{self.symbol}in sht func')
        while self.first_trade:
            #print(f'{self.symbol}in self.first_trade:')
            self.short_entry_price.append(self.price)
            self.logger.debug('{} went short at price-{}, time-{}:{}:{}'.format(self.symbol,
                                                                    self.price,
                                                                    datetime.datetime.now(
                                                                        pytz.timezone('Asia/Kolkata')).hour,
                                                                    datetime.datetime.now(
                                                                        pytz.timezone('Asia/Kolkata')).minute,
                                                                    datetime.datetime.now(
                                                                        pytz.timezone('Asia/Kolkata')).second))
            self.first_trade = False
            self.sht = True
            token_dict[self.symbol]["POS"] = "SHORT"
            token_dict[self.symbol]["NOE"] = token_dict[self.symbol]["NOE"] + 1
            token_dict[self.symbol]["LAST_ENTRY"] = self.price
            self.logger.debug(f'short entry dict: {self.short_entry_price}')
            break

            # if len(self.long_entry_price) == len(self.long_exit_price):
            #    self.long_pnl_booked = (self.long_pnl_booked + (
            #            self.long_entry_price[len(self.long_entry_price) - 1] - self.long_exit_price[
            #        len(self.long_exit_price) - 1])) * self.quantity

        if (float(token_dict[self.symbol]["LP"]) < pivot) and self.sht == False:
            #print(f'{self.symbol}in sht func not first trade')
            self.lng_counter = 0
            # sleep(5)
            self.sht_counter = self.sht_counter + 1
            # print(f'{self.symbol}in sht func not first trade {self.sht_counter}')
            if (token_dict[self.symbol]["LP"] < pivot):
                # and self.sht_counter == 6:
                self.price = float(token_dict[self.symbol]["LP"])
                self.sht_count = self.sht_count + 1
                token_dict[self.symbol]["NOE"] = token_dict[self.symbol]["NOE"] + 1
                self.sht = True
                token_dict[self.symbol]["POS"] = "SHORT"
                # self.lng = False
                self.sht_counter = 0
                self.logger.debug('{} went short at price-{}, time-{}:{}:{}'.format(self.symbol,
                                                                        self.price,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone('Asia/Kolkata')).hour,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone(
                                                                                'Asia/Kolkata')).minute,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone(
                                                                                'Asia/Kolkata')).second))
                token_dict[self.symbol]['LAST_ENTRY'] = float(token_dict[self.symbol]["LP"])
                # self.long_exit_price.append(float(token_dict[self.symbol]["LP"]))
                self.short_entry_price.append(float(token_dict[self.symbol]["LP"]))
                self.logger.debug(f'short entry dict: {self.short_entry_price}')
                self.price_crossed_ema = True if reason == "EMA" else False

                if len(self.long_entry_price) == len(self.long_exit_price):
                    self.long_pnl_booked = self.long_pnl_booked + ((
                                                                           self.long_exit_price[
                                                                               len(self.long_exit_price) - 1] -
                                                                           self.long_entry_price[
                                                                               len(self.long_entry_price) - 1]) * self.quantity)

                    self.long_brokerage = self.long_brokerage + self.calc_brokerage(
                        self.long_entry_price[len(self.long_entry_price) - 1], self.long_exit_price[
                            len(self.long_exit_price) - 1], "LONG")

    def close_long_pos(self, pivot):
        #print('in close_long_pos')
        if (token_dict[self.symbol]['LP'] < pivot) and self.lng == True:

            sleep(6)
            if (token_dict[self.symbol]['LP'] < pivot) and self.lng == True:

                self.logger.debug('square-off {} at price {}'.format(self.symbol, token_dict[self.symbol]['LP']))
                token_dict[self.symbol]['POS'] = ' '
                self.long_exit_price.append(token_dict[self.symbol]['LP'])
                er.debug(f'long entry dict: {self.long_entry_price}')
                er.debug(f'long exit dict: {self.long_exit_price}')
                er.debug(f'last entry was at : {self.long_entry_price[-1]} and exit at: {self.long_exit_price[-1]}')
                self.lng = False

                if len(self.long_entry_price) == len(self.long_exit_price):
                    self.long_pnl_booked = self.long_pnl_booked + ((
                                                                           self.long_exit_price[
                                                                               len(self.long_exit_price) - 1] -
                                                                           self.long_entry_price[
                                                                               len(self.long_entry_price) - 1]) * self.quantity)

                    self.long_brokerage = self.long_brokerage + self.calc_brokerage(
                        self.long_entry_price[len(self.long_entry_price) - 1], self.long_exit_price[
                            len(self.long_exit_price) - 1], "LONG")

                return True
        return False

    def close_short_pos(self, pivot):
        #print('in close_short_pos')
        if (token_dict[self.symbol]['LP'] > pivot) and self.sht == True:
            sleep(6)
            if (token_dict[self.symbol]['LP'] > pivot) and self.sht == True:
                print('square-off {} at price {}'.format(self.symbol, token_dict[self.symbol]['LP']))
                token_dict[self.symbol]['POS'] = ' '
                self.short_exit_price.append(token_dict[self.symbol]['LP'])
                self.sht = False

                self.logger.debug(f'short entry dict: {self.short_entry_price}')
                self.logger.debug(f'short exit dict: {self.short_exit_price}')
                self.logger.debug(f'last entry was at : {self.short_entry_price[-1]} and exit at: {self.short_exit_price[-1]}')

                if len(self.short_entry_price) == len(self.short_exit_price):
                    self.short_pnl_booked = self.short_pnl_booked + ((
                                                                             self.short_entry_price[
                                                                                 len(self.short_entry_price) - 1] -
                                                                             self.short_exit_price[
                                                                                 len(self.short_exit_price) - 1]) * self.quantity)
                    self.logger.debug(f'short pnl booked until now:{self.short_pnl_booked}')

                    self.short_brokerage = self.short_brokerage + self.calc_brokerage(
                        self.short_entry_price[len(self.short_entry_price) - 1], self.short_exit_price[
                            len(self.short_exit_price) - 1], "SHORT")
                return True
        return False

    def hedge(self):
        self.go_long(0,'HEDGE')
        self.logger.debug('HEDGE-{} went long at price-{}, time-{}:{}:{}'.format(self.symbol,
                                                                     self.price,
                                                                     datetime.datetime.now(
                                                                         pytz.timezone('Asia/Kolkata')).hour,
                                                                     datetime.datetime.now(
                                                                         pytz.timezone('Asia/Kolkata')).minute,
                                                                     datetime.datetime.now(
                                                                         pytz.timezone('Asia/Kolkata')).second))

        start_time = int(9) * 60 * 60 + int(19) * 60 + int(30)
        time_now = (datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour * 60 * 60 + datetime.datetime.now(
            pytz.timezone('Asia/Kolkata')).minute * 60 + datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second)
        end_time = int(15) * 60 * 60 + int(30) * 60 + int(59)     

        while start_time <= time_now <= end_time:
            time_now = (datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour * 60 * 60 + datetime.datetime.now(
                pytz.timezone('Asia/Kolkata')).minute * 60 + datetime.datetime.now(
                pytz.timezone('Asia/Kolkata')).second)
            self.pnl_list_for_dynamic_graph.append(float(token_dict[self.symbol]["PNL"]))
            if self.lng == True:
                token_dict[self.symbol]['PNL'] = (
                        (token_dict[self.symbol]['LP'] - token_dict[self.symbol]['LAST_ENTRY']) * self.quantity)

                if datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second == 00:
                        
                        time_ = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s')
                        open_ = self.pnl_list_for_dynamic_graph[0]
                        high_ = max(self.pnl_list_for_dynamic_graph)
                        low_= min(self.pnl_list_for_dynamic_graph)
                        close_ = int(token_dict[self.symbol]["PNL"])
                        self.pnl_list_for_dynamic_graph.clear()
                        candle_data_to_append = {"time": int(time_)+19800, "open": open_, "high": high_, "low":low_, "close": close_}
                        json.dump(candle_data_to_append, self.candle_data_file)
                        self.candle_data_file.write('\n')
                        self.candle_data_file.flush()
                        os.fsync(self.candle_data_file)
                        sleep(1)
                sleep(1)

    def exit_open_positions(self):
        self.current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        if self.lng:
            self.long_exit_price.append(token_dict[self.symbol]["LP"])
            print("exited long - {} at price-{}, time {}:{}:{}".format(self.symbol,
                                                                       token_dict[self.symbol]["LP"],
                                                                       datetime.datetime.now(
                                                                           pytz.timezone('Asia/Kolkata')).hour,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone(
                                                                               'Asia/Kolkata')).minute,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone(
                                                                               'Asia/Kolkata')).second))
            self.long_brokerage = self.long_brokerage + self.calc_brokerage(
                        self.long_entry_price[len(self.long_entry_price) - 1], self.long_exit_price[
                            len(self.long_exit_price) - 1], "LONG")
            
            self.lng = False

        elif self.sht:
            self.short_exit_price.append(token_dict[self.symbol]["LP"])
            print("exited short - {} at price-{}, time {}:{}:{}".format(self.symbol,
                                                                        token_dict[self.symbol]["LP"],
                                                                        datetime.datetime.now(
                                                                            pytz.timezone('Asia/Kolkata')).hour,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone(
                                                                                'Asia/Kolkata')).minute,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone(
                                                                                'Asia/Kolkata')).second))
        

            self.short_brokerage = self.short_brokerage + self.calc_brokerage(
                self.short_entry_price[len(self.short_entry_price) - 1], self.short_exit_price[
                    len(self.short_exit_price) - 1], "SHORT")
            
            self.sht = False

    def calculate_pnl(self, quantity):
        for i in range(len(self.long_entry_price)):
            self.long_pnl = self.long_pnl + (self.long_entry_price[i] - self.long_exit_price[i])

        for i in range(len(self.long_exit_price)):
            self.short_pnl = self.short_pnl + (self.short_entry_price[i] - self.short_exit_price[i])

        print("pnl of {} is {}".format(self.symbol, (self.long_pnl + self.short_pnl) * quantity))
        return (self.long_pnl + self.short_pnl) * quantity

    def calc_brokerage(self, entry_, exit_, pos):
        Brokerage = 40
        STT = (float(exit_) if pos == "LONG" else float(entry_)) * 0.0005 * float(self.quantity)
        ex_tsn_chg = (float(entry_ + exit_) * 0.00053) * float(self.quantity)
        SEBI_charges = (float(entry_ + exit_)) * self.quantity * 0.000001
        GST = (Brokerage + SEBI_charges + ex_tsn_chg) * 0.18
        stamp_duty = (float(entry_) if pos == "LONG" else float(exit_)) * 0.00003 * float(self.quantity)
        totalcharges = Brokerage + SEBI_charges + ex_tsn_chg + stamp_duty + GST + STT
        return totalcharges

    def calculate_brokerage(self, quantity):
        Brokerage = 40
        long_total_charges = []
        short_total_charges = []

        for i in range(len(self.long_entry_price)):
            for j in range(len(self.long_exit_price)):
                if i == j:
                    STT = float(self.long_exit_price[i]) * 0.0005 * float(quantity)
                    ex_tsn_chg = (float(self.long_entry_price[i] + self.long_exit_price[i]) * 0.00053) * float(quantity)
                    SEBI_charges = 1
                    GST = (Brokerage + SEBI_charges + ex_tsn_chg) * 0.18
                    stamp_duty = (float(self.long_entry_price[i]) * 0.00003) * float(quantity)
                    long_totalcharges = long_total_charges + Brokerage + SEBI_charges + ex_tsn_chg + stamp_duty + GST + STT
                    long_total_charges.append(long_totalcharges)

        for k in range(len(self.short_entry_price)):
            for l in range(len(self.short_exit_price)):
                if k == l:
                    STT = float(self.short_entry_price[k]) * 0.0005 * float(quantity)
                    ex_tsn_chg = (float(self.short_entry_price[k] + self.short_exit_price[k]) * 0.00053) * float(
                        quantity)
                    SEBI_charges = 1
                    GST = (Brokerage + SEBI_charges + ex_tsn_chg) * 0.18
                    stamp_duty = (float(self.short_exit_price[k]) * 0.00003) * float(quantity)
                    short_totalcharges = short_total_charges + Brokerage + SEBI_charges + ex_tsn_chg + stamp_duty + GST + STT
                    short_total_charges.append(short_totalcharges)

        print(" Total brokerage for {} is {}".format(self.symbol, long_total_charges + short_total_charges))

        return long_total_charges + short_total_charges

    def get_ema_25(self):
        moving_averages = round(pd.Series(self.closing_price).ewm(span=25, adjust=False).mean(), 2)
        return moving_averages.tolist()[-1]


class delta_neutral(Process):

    def __init__(self,base_symbol,delta):
        super(delta_neutral, self).__init__()
        self.delta = delta
        self.base_symbol = base_symbol
        


    def run():
        while True:

            expected_call_strike, expected_put_strike = get_delta_neutral_strikes(delta=self.delta, base_symbol= self.base_symbol)

            current_call_strike, current_put_strike = get_current_short_strikes(self.base_symbol,delta=self.delta)


            if expected_call_strike != current_call_strike:

                if not isinstance(expected_call_strike, check_entries):
                    expected_call_strike_obj = check_entries(expected_call_strike.symbol , quantity=quantity_dic[self.base_symbol],is_hedge=False)

                if isinstance(current_call_strike, check_entries):
                    current_call_strike.close_short_pos()

                expected_call_strike_obj.go_short()

                delta_dict_current[self.base_symbol][self.delta]['CALL'] = expected_call_strike_obj

            if expected_put_strike != current_put_strike:

                if not isinstance(expected_put_strike, check_entries):
                    expected_put_strike_obj= check_entries(expected_put_strike, quantity=quantity_dic[self.base_symbol],is_hedge=False)

                if isinstance(current_put_strike, check_entries):
                    current_put_strike.close_short_pos()

                expected_put_strike_obj.go_short()
                delta_dict_current[self.base_symbol][self.delta]['PUT'] = expected_put_strike_obj


            sleep(5)


@app.route('/_stuff', methods=['GET','POST'])
def stuff():


    NIFTY_TOTAL_PNL_list = []
    NIFTY_TOTAL_BROKERAGE_list = []
    NIFTY_TOTAL_ENTRIES_list = []
    global N_pnl_list_for_dynamic_graph 
    global N_time_


    BANKNIFTY_TOTAL_PNL_list = []
    BANKNIFTY_TOTAL_BROKERAGE_list = []
    BANKNIFTY_TOTAL_ENTRIES_list = []
    global BN_pnl_list_for_dynamic_graph 
    global BN_time_


    FINNIFTY_TOTAL_PNL_list = []
    FINNIFTY_TOTAL_BROKERAGE_list = []
    FINNIFTY_TOTAL_ENTRIES_list = []
    global FN_pnl_list_for_dynamic_graph 
    global FN_time_

    global token_dict


    # json2html.convert(json=input)
    updated_html = ""

    
    #for x in ema_instance_list:
    for x in token_dict.keys():

        

        background_color = ''
        if token_dict[x]["POS"] == 'LONG':
            background_color = '#D6EEEE'
    
        elif token_dict[x]["LAST_ENTRY"] == 0:
            background_color = '#f6efc6'
        
    
        updated_html = updated_html + """
        <tr style="background-color: {background_color};">
            <td>  {instrument}   </td>
            <td>  {lp}   </td>
            <td>  {pos}   </td>
            <td onclick="showPopup('{instrument}')" style="color:{font_color}">  {pnl}   </td>
            <td>  {brokerage}   </td>
            <td>  {last_entry}   </td>
           
            <td>  {noe}   </td>
            <td>  {quantity}   </td>
            <td>  {delta}   </td>


        </tr>
        """.format(background_color = background_color,
                   font_color = '#009900' if token_dict[x]["PNL"] > 0 else '#fa2723' ,
                   instrument=x, lp=round(token_dict[x]["LP"], 2),
                   pos=token_dict[x]["POS"],
                   pnl=round(token_dict[x]["PNL"], 2), brokerage=round(token_dict[x]["BROKERAGE"], 2),
                   last_entry=round(token_dict[x]["LAST_ENTRY"], 2),
                   noe=int(token_dict[x]["NOE"]),
                   quantity = int(token_dict[x]["QUANTITY"], delta= token_dict[x]["DELTA"] )
                  )

        if x[0] == "N":
            NIFTY_TOTAL_PNL_list.append(token_dict[x]["PNL"])
            NIFTY_TOTAL_BROKERAGE_list.append(token_dict[x]["BROKERAGE"])
            NIFTY_TOTAL_ENTRIES_list.append(token_dict[x]["NOE"])
         

        elif x[0] == "B":
            BANKNIFTY_TOTAL_PNL_list.append(token_dict[x]["PNL"])
            BANKNIFTY_TOTAL_BROKERAGE_list.append(token_dict[x]["BROKERAGE"])
            BANKNIFTY_TOTAL_ENTRIES_list.append(token_dict[x]["NOE"])
        

        elif x[0] == "F":
            FINNIFTY_TOTAL_PNL_list.append(token_dict[x]["PNL"])
            FINNIFTY_TOTAL_BROKERAGE_list.append(token_dict[x]["BROKERAGE"])
            FINNIFTY_TOTAL_ENTRIES_list.append(token_dict[x]["NOE"])
     


    NIFTY_TOTAL_PNL = round(sum(NIFTY_TOTAL_PNL_list), 2)
    NIFTY_NET_PNL = round((sum(NIFTY_TOTAL_PNL_list) - sum(NIFTY_TOTAL_BROKERAGE_list)), 2)
    N_pnl_list_for_dynamic_graph.append(NIFTY_NET_PNL)

    if not os.path.exists("./instrument_data/NIFTY"):
        os.makedirs("./instrument_data/NIFTY")

    if datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second == 00 and N_time_ != int(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s')):
        with open("./instrument_data/NIFTY/candle_data.jsonl", 'a') as N_candle_data_file:
            N_time_ = int(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s'))
            N_open_ = N_pnl_list_for_dynamic_graph[0]
            N_high_ = max(N_pnl_list_for_dynamic_graph)
            N_low_= min(N_pnl_list_for_dynamic_graph)
            N_close_ = int(NIFTY_NET_PNL)
            N_pnl_list_for_dynamic_graph.clear()
            N_candle_data_to_append = {"time": int(N_time_)+19800, "open": N_open_, "high": N_high_, "low":N_low_, "close": N_close_}
            json.dump(N_candle_data_to_append, N_candle_data_file)
            N_candle_data_file.write('\n')
            N_candle_data_file.flush()
            os.fsync(N_candle_data_file)


    BANKNIFTY_TOTAL_PNL = round(sum(BANKNIFTY_TOTAL_PNL_list), 2)
    BANKNIFTY_NET_PNL = round((sum(BANKNIFTY_TOTAL_PNL_list) - sum(BANKNIFTY_TOTAL_BROKERAGE_list)), 2)
    BN_pnl_list_for_dynamic_graph.append(BANKNIFTY_NET_PNL)

    if not os.path.exists("./instrument_data/BANKNIFTY"):
        os.makedirs("./instrument_data/BANKNIFTY")

    if datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second == 00 and BN_time_ != int(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s')):
        with open("./instrument_data/BANKNIFTY/candle_data.jsonl", 'a') as BN_candle_data_file:
            BN_time_ = int(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s'))
            BN_open_ = BN_pnl_list_for_dynamic_graph[0]
            BN_high_ = max(BN_pnl_list_for_dynamic_graph)
            BN_low_= min(BN_pnl_list_for_dynamic_graph)
            BN_close_ = int(BANKNIFTY_NET_PNL)
            BN_pnl_list_for_dynamic_graph.clear()
            BN_candle_data_to_append = {"time": int(BN_time_)+19800, "open": BN_open_, "high": BN_high_, "low":BN_low_, "close": BN_close_}
            json.dump(BN_candle_data_to_append, BN_candle_data_file)
            BN_candle_data_file.write('\n')
            BN_candle_data_file.flush()
            os.fsync(BN_candle_data_file)


    FINNIFTY_TOTAL_PNL = round(sum(FINNIFTY_TOTAL_PNL_list), 2)
    FINNIFTY_NET_PNL = round((sum(FINNIFTY_TOTAL_PNL_list) - sum(FINNIFTY_TOTAL_BROKERAGE_list)), 2)
    FN_pnl_list_for_dynamic_graph.append(FINNIFTY_NET_PNL)

    if not os.path.exists("./instrument_data/FINNIFTY"):
        os.makedirs("./instrument_data/FINNIFTY")

    
    if datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second == 00 and FN_time_ != int(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s')):
        with open("./instrument_data/FINNIFTY/candle_data.jsonl", 'a') as FN_candle_data_file:
            FN_time_ = int(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s'))
            FN_open_ = FN_pnl_list_for_dynamic_graph[0]
            FN_high_ = max(FN_pnl_list_for_dynamic_graph)
            FN_low_= min(FN_pnl_list_for_dynamic_graph)
            FN_close_ = int(FINNIFTY_NET_PNL)
            FN_pnl_list_for_dynamic_graph.clear()
            FN_candle_data_to_append = {"time": int(FN_time_)+19800, "open": FN_open_, "high": FN_high_, "low":FN_low_, "close": FN_close_}
            json.dump(FN_candle_data_to_append, FN_candle_data_file)
            FN_candle_data_file.write('\n')
            FN_candle_data_file.flush()
            os.fsync(FN_candle_data_file)
            


    font_kolor_total_nifty = '#009900' if NIFTY_NET_PNL > 0 else '#fa2723'
    font_kolor_total_banknifty = '#009900' if BANKNIFTY_NET_PNL > 0 else '#fa2723'
    font_kolor_total_finnifty = '#009900' if FINNIFTY_NET_PNL > 0 else '#fa2723'

         

    updated_html2 = """
    <tr class="bg-light sticky-top top-0">
            <td>  {NIFTY_TOTAL_PNL}   </td>
            <td>  {NIFTY_TOTAL_BROKERAGE}   </td>
            <td onclick="showPopup('NIFTY')" style="color:{font_color_nifty}">  {NIFTY_NET_PNL}   </td>
            <td>  {NIFTY_TOTAL_ENTRIES}   </td>
            <td>  {BANKNIFTY_TOTAL_PNL}   </td>
            <td>  {BANKNIFTY_TOTAL_BROKERAGE}   </td>
            <td onclick="showPopup('BANKNIFTY')" style="color:{font_color_bn}">  {BANKNIFTY_NET_PNL}   </td>
            <td>  {BANKNIFTY_TOTAL_ENTRIES}   </td>
            <td>  {FINNIFTY_TOTAL_PNL}  </td>
            <td>  {FINNIFTY_TOTAL_BROKERAGE}  </td>
            <td onclick="showPopup('FINNIFTY')" style="color:{font_color_fn}">  {FINNIFTY_NET_PNL}  </td>
            <td>  {FINNIFTY_TOTAL_ENTRIES}  </td>


        </tr>
        """.format(NIFTY_TOTAL_PNL=NIFTY_TOTAL_PNL,
                   NIFTY_TOTAL_BROKERAGE=round(sum(NIFTY_TOTAL_BROKERAGE_list), 2),
                   NIFTY_NET_PNL=NIFTY_NET_PNL,
                   NIFTY_TOTAL_ENTRIES=sum(NIFTY_TOTAL_ENTRIES_list),
                   BANKNIFTY_TOTAL_PNL=BANKNIFTY_TOTAL_PNL,
                   BANKNIFTY_TOTAL_BROKERAGE=round(sum(BANKNIFTY_TOTAL_BROKERAGE_list), 2),
                   BANKNIFTY_NET_PNL=BANKNIFTY_NET_PNL,
                   BANKNIFTY_TOTAL_ENTRIES=sum(BANKNIFTY_TOTAL_ENTRIES_list),
                   FINNIFTY_TOTAL_PNL=FINNIFTY_TOTAL_PNL,
                   FINNIFTY_TOTAL_BROKERAGE=round(sum(FINNIFTY_TOTAL_BROKERAGE_list), 2),
                   FINNIFTY_NET_PNL=FINNIFTY_NET_PNL,
                   FINNIFTY_TOTAL_ENTRIES=sum(FINNIFTY_TOTAL_ENTRIES_list),
                   font_color_nifty = font_kolor_total_nifty,
                   font_color_bn = font_kolor_total_banknifty,
                   font_color_fn = font_kolor_total_finnifty,
                   )

    html1 = """
        <table class="table table-striped" id="rearrangeable-table">
            <thead class="bg-light sticky-top top-0">
                <tr>
                    <td>  <strong> INSTRUMENT  </strong> </td>
                    <td>  <strong> LP  </strong>  </td>
                    <td>  <strong> POS  </strong>  </td>
                    <td>  <strong> PNL  </strong>  </td>
                    <td>  <strong> BROKERAGE  </strong>  </td>
                    <td>  <strong> LAST_ENTRY </strong>   </td>
                    <td>  <strong> NOE  </strong>  </td>
                    <td>  <strong> QUANTITY  </strong>  </td>

                </tr>
            </thead>
            <tbody>
                {}
            </tbody>
        </table>
        """.format(updated_html)

    html2 = """
    <table class="table table-striped">
            <thead>
                <tr>
                    <td>  <strong> N_TOTAL_PNL  </strong> </td>
                    <td>  <strong> N_TOTAL_BROKERAGE  </strong>  </td>
                    <td>  <strong> N_NET_PNL  </strong>  </td>
                    <td>  <strong> N_TOTAL_ENTRIES  </strong>  </td>
                    <td>  <strong> BN_TOTAL_PNL  </strong> </td>
                    <td>  <strong> BN_TOTAL_BROKERAGE  </strong>  </td>
                    <td>  <strong> BN_NET_PNL  </strong>  </td>
                    <td>  <strong> BN_TOTAL_ENTRIES  </strong>  </td>
                    <td>  <strong > FN_TOTAL_PNL </strong> </td>
                    <td>  <strong> FN_TOTAL_BROKERAGE </strong> </td>
                    <td>  <strong> FN_NET_PNL </strong> </td>
                    <td>  <strong> FN_TOTAL_ENTRIES </strong> </td>
                </tr>
            </thead>
            {}
        </table>
        """.format(updated_html2)


    html = {"individual_html": html1, "summary_html": html2, 'delta_dict_expected':delta_dict_expected, 'delta_dict_current':delta_dict_current}


    return jsonify(result=html)


@app.route('/api/candle_data/<filename>')
def serve_file(filename):
    try:
        data_directory = os.path.join('instrument_data', filename,'candle_data.jsonl')
    
        # Send the file's content as the API response
        return send_file(data_directory, mimetype='application/json')
    except Exception as e:
        print('Error serving file:', e)
        return '', 500


@app.route('/')
def index():
    return render_template('dy1.html')

def get_subscribe_list(BN_spot,Nifty_spot,FN_spot,expiry_banknifty,expiry_nifty,expiry_finnifty):
    subscribe_list = []
    Nifty_spot, BN_spot, FN_spot
                      

    for x in range(-20, 20):

        for is_CE in [True, False]:
            script = alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=str(expiry_banknifty),
                                                    is_fut=False, strike=int(BN_spot) + (x*100), is_CE=is_CE)
            subscribe_list.append(script)

    for x in range(-10, 10):

        for is_CE in [True, False]:
            script = alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=str(expiry_nifty),
                                                    is_fut=False, strike=int(Nifty_spot) + (x*100), is_CE=is_CE)
            subscribe_list.append(script)
    
    for x in range(-10, 10):

        for is_CE in [True, False]:
            script = alice.get_instrument_for_fno(exch='NFO', symbol='FINNIFTY', expiry_date=str(expiry_finnifty),
                                                    is_fut=False, strike=int(FN_spot) + (x*100), is_CE=is_CE)
            subscribe_list.append(script)
        
    
    return subscribe_list



if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(message)s")
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    year_dict = {'JAN': '01', 'FEB': '02', 'MAR': '03', 'APR': '04', 'MAY': '05', 'JUN': '06', 'JUL': '07', 'AUG': '08',
                 'SEP': '09', 'OCT': '10', 'NOV': '11', 'DEC': '12'}


    def get_expiry_date_trading_symbol(expiry_):
        expiry_ = str(expiry_)
        expiry_date = (expiry_.split("-")[2])
        expiry_year = str(expiry_.split("-")[0])
        month_list = year_dict.keys()
        for x in month_list:
            if year_dict[x] == expiry_.split("-")[1]:
                expiry_month = str(x)

        return expiry_date + expiry_month + expiry_year[2:]


    def get_symbol(base_symbol, spot_price_at_9_19_58, strike, option_type, expiry_):
        base_symbol = base_symbol
        option_type = option_type
        striki = str(round(spot_price_at_9_19_58, -2) + strike)
        trading_symbol = base_symbol + expiry_ + option_type + striki
        return trading_symbol

    


    socket()
    sleep(1.5)

    expiry_format_banknifty = get_expiry_date_trading_symbol(str(expiry_banknifty))
    expiry_format_nifty = get_expiry_date_trading_symbol(str(expiry_nifty))
    expiry_format_finnifty = get_expiry_date_trading_symbol(str(expiry_finnifty))

    print(
        "waiting for ATM at 9:20, current time- {}:{}".format(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour,
                                                              datetime.datetime.now(
                                                                  pytz.timezone('Asia/Kolkata')).minute))
    if datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour >= 0 \
                and datetime.datetime.now(pytz.timezone('Asia/Kolkata')).minute >= 31:
                minut = 31
    else:
        minut = 0
    while True:
        if datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour >= 0 \
                and datetime.datetime.now(pytz.timezone('Asia/Kolkata')).minute >= 0\
                and datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second >= 00:

            global nifty_atm,banknifty_atm,finnifty_atm
            nifty_atm = int(round(float(token_dict['NIFTY_SPOT']["LP"]), -2))
            banknifty_atm = int(round(float(token_dict['BANKNIFTY_SPOT']["LP"]), -2))
            finnifty_atm = int(round(float(token_dict['FINNIFTY_SPOT']["LP"]), -2))

            # nifty_atm = 19600
            # banknifty_atm = 45400
            # finnifty_atm = 20000

            print("Nifty atm = {} \nBanknifty atm = {} \nFinnifty atm = {}".format(nifty_atm, banknifty_atm, finnifty_atm))
            break


    #print("trying to resubcribe")

    #Nifty_spot
    alice.subscribe(get_subscribe_list(banknifty_atm,nifty_atm,finnifty_atm,expiry_banknifty,expiry_nifty,expiry_finnifty))
    
    sleep(5)

    # ,nifty_quantity = 50
    # ,bank_nifty_quantity = 25
    # ,finnifty_quantity = 50

    # create objects
    # N_ATM_CE = check_entries(str(get_symbol('NIFTY', nifty_atm, 0, 'C', expiry_format_nifty)), nifty_quantity,is_hedge=False)
    # N_ATM_PE = check_entries(str(get_symbol('NIFTY', nifty_atm, 0, 'P', expiry_format_nifty)), nifty_quantity,is_hedge=False)

    # N_OTM_CE_100 = check_entries(str(get_symbol('NIFTY', nifty_atm, 100, 'C', expiry_format_nifty)), nifty_quantity,is_hedge=False)
    # N_OTM_PE_100 = check_entries(str(get_symbol('NIFTY', nifty_atm, 100, 'P', expiry_format_nifty)), nifty_quantity,is_hedge=False)

    # N_OTM_CE_200 = check_entries(str(get_symbol('NIFTY', nifty_atm, 200, 'C', expiry_format_nifty)), nifty_quantity,is_hedge=False)
    # N_OTM_PE_200 = check_entries(str(get_symbol('NIFTY', nifty_atm, 200, 'P', expiry_format_nifty)), nifty_quantity,is_hedge=False)

    # N_ITM_CE_100 = check_entries(str(get_symbol('NIFTY', nifty_atm, -100, 'C', expiry_format_nifty)), nifty_quantity,is_hedge=False)
    # N_ITM_PE_100 = check_entries(str(get_symbol('NIFTY', nifty_atm, -100, 'P', expiry_format_nifty)), nifty_quantity,is_hedge=False)

    # N_ITM_CE_200 = check_entries(str(get_symbol('NIFTY', nifty_atm, -200, 'C', expiry_format_nifty)), nifty_quantity,is_hedge=False)
    # N_ITM_PE_200 = check_entries(str(get_symbol('NIFTY', nifty_atm, -200, 'P', expiry_format_nifty)), nifty_quantity,is_hedge=False)

    # N_HEDGE_CE = check_entries(str(get_symbol('NIFTY', nifty_atm, 500, 'C', expiry_format_nifty)), nifty_quantity * 2,is_hedge=True)
    # N_HEDGE_PE = check_entries(str(get_symbol('NIFTY', nifty_atm, -500, 'P', expiry_format_nifty)), nifty_quantity * 2,is_hedge=True)

    # N_HEDGE_CE_50 = check_entries(str(get_symbol('NIFTY', nifty_atm, 50, 'C', expiry_format_nifty)), nifty_quantity / 2,is_hedge=True)
    # N_HEDGE_PE_50 = check_entries(str(get_symbol('NIFTY', nifty_atm, -50, 'P', expiry_format_nifty)), nifty_quantity / 2,is_hedge=True)

    # N_HEDGE_CE_150 = check_entries(str(get_symbol('NIFTY', nifty_atm, 150, 'C', expiry_format_nifty)), nifty_quantity / 2,is_hedge=True)
    # N_HEDGE_PE_150 = check_entries(str(get_symbol('NIFTY', nifty_atm, -150, 'P', expiry_format_nifty)), nifty_quantity / 2,is_hedge=True)

    # BN_ATM_CE = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 0, 'C', expiry_format_banknifty)),
    #                           bank_nifty_quantity,is_hedge=False)
    # BN_ATM_PE = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 0, 'P', expiry_format_banknifty)),
    #                           bank_nifty_quantity,is_hedge=False)

    # BN_OTM_CE_100 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 200, 'C', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)
    # BN_OTM_PE_100 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 200, 'P', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)

    # BN_OTM_CE_200 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 400, 'C', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)
    # BN_OTM_PE_200 = check_entries(str(get_symbol('BANKNIFTY', bannifty_days_to_expiryknifty_atm, 400, 'P', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)

    # BN_OTM_CE_300 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 600, 'C', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)
    # BN_OTM_PE_300 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 600, 'P', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)

    # BN_ITM_CE_100 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -200, 'C', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)
    # BN_ITM_PE_100 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -200, 'P', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)

    # BN_ITM_CE_200 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -400, 'C', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)
    # BN_ITM_PE_200 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -400, 'P', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)

    # BN_ITM_CE_300 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -600, 'C', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)
    # BN_ITM_PE_300 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -600, 'P', expiry_format_banknifty)),
    #                               bank_nifty_quantity,is_hedge=False)
    # #
    # BN_HEDGE_CE = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 900, 'C', expiry_format_banknifty)),
    #                             bank_nifty_quantity * 2.5,is_hedge=True)
    # BN_HEDGE_PE = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -900, 'P', expiry_format_banknifty)),
    #                             bank_nifty_quantity * 2.5,is_hedge=True)

    # BN_HEDGE_CE_100 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 100, 'C', expiry_format_banknifty)),
    #                             bank_nifty_quantity * 0.5,is_hedge=True)
    # BN_HEDGE_PE_100 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -100, 'P', expiry_format_banknifty)),
    #                             bank_nifty_quantity * 0.5,is_hedge=True)

    # BN_HEDGE_CE_300 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 300, 'C', expiry_format_banknifty)),
    #                             bank_nifty_quantity * 0.5,is_hedge=True)
    # BN_HEDGE_PE_300 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -300, 'P', expiry_format_banknifty)),
    #                             bank_nifty_quantity * 0.5,is_hedge=True)
    
    # BN_HEDGE_CE_500 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, 500, 'C', expiry_format_banknifty)),
    #                             bank_nifty_quantity * 0.5,is_hedge=True)
    # BN_HEDGE_PE_500 = check_entries(str(get_symbol('BANKNIFTY', banknifty_atm, -500, 'P', expiry_format_banknifty)),
    #                             bank_nifty_quantity * 0.5,is_hedge=True)

    # FN_ATM_CE = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, 0, 'C', expiry_format_finnifty)),
    #                           finnifty_quantity,is_hedge=False)
    # FN_ATM_PE = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, 0, 'P', expiry_format_finnifty)),
    #                           finnifty_quantity,is_hedge=False)
    # FN_OTM_CE_50 = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, 100, 'C', expiry_format_finnifty)),
    #                              finnifty_quantity,is_hedge=False)
    # FN_OTM_PE_50 = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, 100, 'P', expiry_format_finnifty)),
    #                              finnifty_quantity,is_hedge=False)
    # FN_ITM_CE_50 = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, -100, 'P', expiry_format_finnifty)),
    #                              finnifty_quantity,is_hedge=False)
    
    
    
    # FN_HEDGE_CE_50 = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, 50, 'C', expiry_format_finnifty)),
    #                              finnifty_quantity/2,is_hedge=True)
    # FN_HEDGE_PE_50 = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, -50, 'P', expiry_format_finnifty)),
    #                              finnifty_quantity/2,is_hedge=True)
    # FN_HEDGE_CE = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, 300, 'C', expiry_format_finnifty)),
    #                              finnifty_quantity/2,is_hedge=True)
    # FN_HEDGE_PE = check_entries(str(get_symbol('FINNIFTY', finnifty_atm, -300, 'P', expiry_format_finnifty)),
    #                              finnifty_quantity/2,is_hedge=True)

    #
    # NIFTY_OBJ_LIST = [N_ATM_CE, N_ATM_PE]
    # N_OTM_CE_100, N_OTM_PE_100, N_OTM_CE_200, N_OTM_PE_200, N_ITM_CE_100,
    # N_ITM_PE_100, N_ITM_CE_200, N_ITM_PE_200]
    #

    # N_call_list = [N_ATM_CE,
    #                N_OTM_CE_100, N_OTM_CE_200
    #                # , N_ITM_CE_100, N_ITM_CE_200
    #                ]
    # N_put_list = [N_ATM_PE,
    #               # N_OTM_PE_100, N_OTM_PE_200,
    #               N_ITM_PE_100, N_ITM_PE_200
    #               ]

    # N_call_list_HEDGE = [N_HEDGE_CE, N_HEDGE_CE_50, N_HEDGE_CE_150 ]
    # N_put_list_HEDGE = [N_HEDGE_PE, N_HEDGE_PE_50, N_HEDGE_PE_150  ]



    # BN_call_list = [BN_ATM_CE, BN_OTM_CE_100, BN_OTM_CE_200, BN_OTM_CE_300
    #                 # ,BN_ITM_CE_100, BN_ITM_CE_200, BN_ITM_CE_300
    #                 ]
    # BN_put_list = [BN_ATM_PE,
    #                # BN_OTM_PE_100, BN_OTM_PE_200, BN_OTM_PE_300,
    #                BN_ITM_PE_100, BN_ITM_PE_200, BN_ITM_PE_300]

    # BN_call_list_HEDGE = [BN_HEDGE_CE, BN_HEDGE_CE_100, BN_HEDGE_CE_300, BN_HEDGE_CE_500 ]
    # BN_put_list_HEDGE= [BN_HEDGE_PE, BN_HEDGE_PE_100, BN_HEDGE_PE_300, BN_HEDGE_PE_500 ]

    # FN_call_list = [FN_ATM_CE, FN_OTM_CE_50
    #                 # , FN_ITM_CE_50
    #                 ]
    # FN_put_list = [FN_ATM_PE,
    #                # , FN_OTM_PE_50,
    #                FN_ITM_CE_50]

    # FN_call_list_HEDGE = [FN_HEDGE_CE, FN_HEDGE_CE_50 ]
    # FN_put_list_HEDGE= [FN_HEDGE_PE, FN_HEDGE_PE_50 ]



    # N_CALL_PROCESS = processing_multi(N_call_list)
    # N_PUT_PROCESS = processing_multi(N_put_list)

    # N_CALL_HEDGE_PROCESS = processing_multi(N_call_list_HEDGE)
    # N_PUT_HEDGE_PROCESS = processing_multi(N_put_list_HEDGE)

  

    # BN_CALL_PROCESS = processing_multi(BN_call_list)  # BN_HEDGE_CE
    # BN_PUT_PROCESS = processing_multi(BN_put_list)  # BN_HEDGE_PE

    # BN_CALL_HEDGE_PROCESS = processing_multi(BN_call_list_HEDGE)
    # BN_PUT_HEDGE_PROCESS = processing_multi(BN_put_list_HEDGE)


    # FN_CALL_PROCESS = processing_multi(FN_call_list)
    # FN_PUT_PROCESS = processing_multi(FN_put_list)

    # FN_CALL_HEDGE_PROCESS = processing_multi(FN_call_list_HEDGE)
    # FN_PUT_HEDGE_PROCESS = processing_multi(FN_put_list_HEDGE)


    # N_CALL_PROCESS.start()
    # N_PUT_PROCESS.start()

    # N_CALL_HEDGE_PROCESS.start()
    # N_PUT_HEDGE_PROCESS.start()

    # BN_CALL_PROCESS.start()
    # BN_PUT_PROCESS.start()

    # BN_CALL_HEDGE_PROCESS.start()
    # BN_PUT_HEDGE_PROCESS.start()

    # FN_CALL_PROCESS.start()
    # FN_PUT_PROCESS.start()

    # FN_CALL_HEDGE_PROCESS.start()
    # FN_PUT_HEDGE_PROCESS.start()

    num_processes = 3
    
    pairs = [(base_symbol, delta) for base_symbol in delta_dict_expected.keys() for delta in delta_dict_expected[base_symbol].keys()]


    processes = []

    pairs = [(base_symbol,delta) for base_symbol in delta_dict_expected.keys() for delta in
             delta_dict_expected[base_symbol].keys()]

    with multiprocessing.Pool(processes=num_processes) as pool:
        # Create a list of (base_symbol, delta) pairs
        
        
        # Use the map function to apply the update_delta_dict_expected function
        pool.starmap(update_delta_dict_expected, pairs)
        
        print("Updated delta_dict_expected:", delta_dict_expected)

    for pair in pairs:
        process = delta_neutral(pair[0],pair[1])
        processes.append(process)
        process.start()

    ema_instances = check_entries.instances

    # Print the symbols of all Symbol instances
    for ema_instance in ema_instances:
        ema_instance_list.append(ema_instance.symbol)

        
       
    def update_delta(delta_dict_expected):
        for key, value in delta_dict_expected.items():
            for x in list(value.keys()):
                update_delta_dict_expected(key, x)
                update_delta_dict_expected(key, -x)


    


    # BN_PROCESS1.start()
    # BN_PROCESS2.start()
    # BN_PROCESS3.start()
    # BN_PROCESS4.start()
    # BN_PROCESS5.start()
    # BN_PROCESS6.start()
    # BN_PROCESS7.start()

    # FLASK_PROCESS.start()

    # N_CALL_PROCESS.join()
    # N_PUT_PROCESS.join()  ##

    # BN_CALL_PROCESS.join()
    # BN_PUT_PROCESS.join()

    ## Start the threads
    # [x.start() for x in NIFTY_OBJ_LIST]
    # [x.start() for x in BANKNIFTY_OBJ_LIST]

    # N_HEDGE_CE.hedge()
    # N_HEDGE_PE.hedge()

    # app.run()
    p = Process(target=app.run(host='0.0.0.0',port=5000))
    p.start()

    # BN_HEDGE_CE.hedge()
    # BN_HEDGE_PE.hedge()

    # [x.join() for x in NIFTY_OBJ_LIST]
    # [x.join() for x in BANKNIFTY_OBJ_LIST]

    # exiting all positions
    # [x.exit_open_positions() for x in N_call_list]
    # [x.exit_open_positions() for x in N_put_list]

    # [x.exit_open_positions() for x in BN_call_list]
    # [x.exit_open_positions() for x in BN_put_list]

    # N_HEDGE_CE.exit_open_positions()
    # N_HEDGE_PE.exit_open_positions()
    #
    # BN_HEDGE_CE.exit_open_positions()
    # BN_HEDGE_PE.exit_open_positions()

    print("---------------------------------------------------------------------------------------------\n")
    print("Exited all positions")

    print("----------------------------------------------------------------------------------------------\n")