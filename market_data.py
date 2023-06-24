import UltraDict
import json
import datetime
import pytz
from pya3 import *


class strategy_name(Enum):
    DATA = 0
    NORMAL = 1
    GREEDY = 2


def socket(alice):
    global token_dict
    global LTP
    global socket_opened
    global subscribe_flag
    global subscribe_list


    LTP = 0
    token_dict = UltraDict(recurse=True)


    token_dict['NIFTY_SPOT'] = [
    {"TOKEN": 0, "LP": 0.0,"EMA": 0, "FCH": 0},
    {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "NOE": 0,"BROKERAGE": 0},
    {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0, "NOE": 0,"BROKERAGE": 0}
    ]
    token_dict['BANKNIFTY_SPOT'] = [
    {"TOKEN": 0, "LP": 0.0, "EMA": 0, "FCH": 0},
    {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "NOE": 0, "BROKERAGE": 0},
    {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0, "NOE": 0, "BROKERAGE": 0}
    ]
    token_dict['FINNIFTY_SPOT'] = [
    {"TOKEN": 0, "LP": 0.0, "EMA": 0, "FCH": 0},
    {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "NOE": 0, "BROKERAGE": 0},
    {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0, "NOE": 0, "BROKERAGE": 0}
    ]

 

    socket_opened = False
    subscribe_flag = False
    subscribe_list = []
    unsubscribe_list = []

    def socket_open():  # Socket open callback function
        print("Connected")
        #global socket_opened
        socket_opened = True
        if subscribe_flag:  # This is used to resubscribe the script when reconnect the socket.
            alice.subscribe(subscribe_list)

    def socket_close():  # On Socket close this callback function will trigger
        #global socket_opened, LTP
        socket_opened = False
        LTP = 0
        print("Closed")

    def socket_error(message):  # Socket Error Message will receive in this callback function
        #global LTP
        LTP = 0
        print("Error :", message)

    def feed_data(message):  # Socket feed data will receive in this callback function
        #global LTP, subscribe_flag, token_dict

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
                token_dict[Token_Acknowledgement_status['ts']] = [
                    {"TOKEN": Token_Acknowledgement_status['tk'], "LP": 0.0, "EMA": 0, "FCH": 0},
                    {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "NOE": 0, "BROKERAGE": 0},
                    {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0, "NOE": 0, "BROKERAGE": 0}
                ]



            pass
        else:
            # print("Feed :", feed_message)
            Feed = feed_message
            if Feed["tk"] == '26000':
                token_dict['NIFTY_SPOT'][strategy_name.DATA.value]["TOKEN"] = Feed['tk']
                token_dict['NIFTY_SPOT'][strategy_name.DATA.value]["LP"] = float(Feed['lp'])

            if Feed["tk"] == '26009':
                token_dict['BANKNIFTY_SPOT'][strategy_name.DATA.value]["TOKEN"] = Feed['tk']
                token_dict['BANKNIFTY_SPOT'][strategy_name.DATA.value]["LP"] = float(Feed['lp'])

            if Feed["tk"] == '26037':
                token_dict['FINNIFTY_SPOT'][strategy_name.DATA.value]["TOKEN"] = Feed['tk']
                token_dict['FINNIFTY_SPOT'][strategy_name.DATA.value]["LP"] = float(Feed['lp'])

            for x in token_dict.keys():
                if Feed["tk"] == token_dict[x][strategy_name.DATA.value]["TOKEN"]:
                    token_dict[x][strategy_name.DATA.value]["LP"] = float(Feed['lp']) if 'lp' in feed_message else token_dict[x][strategy_name.DATA.value]["LP"]
            # LTP = feed_message['lp'] if 'lp' in feed_message else LTP  # If LTP in the response it will store in LTP variable
            # print(type(feed_message["tk"]))
            if feed_message["tk"] == '243769':
                print(feed_message)

    # Socket Connection Request
    alice.start_websocket(socket_open_callback=socket_open, socket_close_callback=socket_close,
                          socket_error_callback=socket_error, subscription_callback=feed_data, run_in_background=True)
    #global socket_opened
    while not socket_opened:
        pass
    #global subscribe_list

    # Subscribe the Instrument
    print("Initial Subscribe for Index at :", datetime.datetime.now(pytz.timezone('Asia/Kolkata')))

    subscribe_list = [alice.get_instrument_by_token('INDICES', 26000), alice.get_instrument_by_token('INDICES', 26009),
                      alice.get_instrument_by_token('INDICES', 26037)]

    alice.subscribe(subscribe_list)
    sleep(1.5)



    def get_atm():
        global nifty_atm
        global banknifty_atm
        global finnifty_atm
        while True:
            if datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour >= 9 \
                    and datetime.datetime.now(pytz.timezone('Asia/Kolkata')).minute >= 00 \
                    and datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second >= 00:
                #nifty_atm = int(round(float(token_dict['NIFTY_SPOT'][strategy_name.DATA.value]["LP"]), -2))
                #banknifty_atm = int(round(float(token_dict['BANKNIFTY_SPOT'][strategy_name.DATA.value]["LP"]), -2))
                #finnifty_atm = int(round(float(token_dict['FINNIFTY_SPOT'][strategy_name.DATA.value]["LP"]), -2))
                nifty_atm=18600
                banknifty_atm=43600
                finnifty_atm=19500


                print("nifty atm = {} \nBanknifty atm = {} \nFinnifty atm = {}".format(nifty_atm, banknifty_atm))
                break
        
        return nifty_atm, banknifty_atm, finnifty_atm

def get_nifty_atm():
    return nifty_atm

def get_banknifty_atm():
    return banknifty_atm

def get_finnifty_atm():
    return finnifty_atm