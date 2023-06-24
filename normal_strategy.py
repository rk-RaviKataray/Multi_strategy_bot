from pya3 import *
import pandas as pd
import datetime
import pytz
from enum import Enum
import market_data
import expiry_data

def create_N_call_objects_for_normal_strategy():
    global normal_strategy_N_call_obj_list
    normal_strategy_N_call_obj_list = []


    for x in [5, 2, 1, 0]:
        obj_ce = greed_strategy(
            str(symbol_helper.get_symbol('NIFTY', market_data.get_nifty_atm, x * 100, 'C',expiry_format_nifty)),
            quantity.nifty_quantity)
        normal_strategy_N_call_obj_list.append(obj_ce)


def create_N_put_objects_for_normal_strategy():
    global normal_strategy_N_put_obj_list
    normal_strategy_N_put_obj_list = []


    for x in [0, -1, -2, -5]:
        obj_pe = greed_strategy(
            str(symbol_helper.get_symbol('NIFTY', market_data.get_nifty_atm, x * 100, 'P', expiry_format_nifty)),
            quantity.nifty_quantity)
        normal_strategy_N_put_obj_list.append(obj_pe)

def create_BN_call_objects_for_normal_strategy():
    global normal_strategy_BN_call_obj_list
    normal_strategy_BN_call_obj_list = []


    for x in [5,3,2, 1, 0]:
        obj_ce = greed_strategy(
            str(symbol_helper.get_symbol('BANKNIFTY', market_data.get_banknifty_atm, x * 100, 'C', expiry_format_banknifty)),
            quantity.bank_nifty_quantity)
        normal_strategy_BN_call_obj_list.append(obj_ce)


def create_BN_put_objects_for_normal_strategy():
    global normal_strategy_BN_put_obj_list
    normal_strategy_BN_put_obj_list = []


    for x in [0, -1, -2, -3, -5]:
        obj_pe = greed_strategy(
            str(symbol_helper.get_symbol('BANKNIFTY', market_data.get_banknifty_atm, x * 100, 'P', expiry_format_banknifty)),
            quantity.bank_nifty_quantity)
        normal_strategy_BN_put_obj_list.append(obj_pe)

def create_FN_call_objects_for_normal_strategy():
    global normal_strategy_FN_call_obj_list
    normal_strategy_FN_call_obj_list = []


    for x in [1, 0]:
        obj_ce = greed_strategy(
            str(symbol_helper.get_symbol('FINNIFTY', market_data.get_finnifty_atm, x * 100, 'C', expiry_format_finnifty)),
            quantity.finnifty_quantity)
        normal_strategy_FN_call_obj_list.append(obj_ce)


def create_FN_put_objects_for_normal_strategy():
    global normal_strategy_FN_put_obj_list
    normal_strategy_FN_put_obj_list = []


    for x in [0, -1]:
        obj_pe = greed_strategy(
            str(symbol_helper.get_symbol('FINNIFTY', market_data.get_finnifty_atm, x * 100, 'P', expiry_format_finnifty)),
            runner.finnifty_quantity)
        normal_strategy_FN_put_obj_list.append(obj_pe)


def execute_normal_startegy():

    global expiry_format_banknifty
    global expiry_format_nifty
    global expiry_format_finnifty

    expiry_format_banknifty = symbol_helper.get_expiry_date_trading_symbol(expiry_data.get_banknifty_expiry())
    expiry_format_nifty = symbol_helper.get_expiry_date_trading_symbol(expiry_data.get_nifty_expiry())
    expiry_format_finnifty = symbol_helper.get_expiry_date_trading_symbol(expiry_data.get_finnifty_expiry())

    # create objects
    create_N_call_objects_for_normal_strategy()
    create_N_put_objects_for_normal_strategy()

    create_BN_call_objects_for_normal_strategy()
    create_BN_put_objects_for_normal_strategy()

    create_FN_call_objects_for_normal_strategy()
    create_FN_put_objects_for_normal_strategy()

    N_CALL_PROCESS = multi_processing.processing_multi(normal_strategy_N_call_obj_list)
    N_PUT_PROCESS = multi_processing.processing_multi(normal_strategy_N_put_obj_list)

    BN_CALL_PROCESS = multi_processing.processing_multi(normal_strategy_BN_call_obj_list)
    BN_PUT_PROCESS = multi_processing.processing_multi(normal_strategy_BN_put_obj_list)

    FN_CALL_PROCESS = multi_processing.processing_multi(normal_strategy_FN_call_obj_list)
    FN_PUT_PROCESS = multi_processing.processing_multi(normal_strategy_FN_put_obj_list)

    N_CALL_PROCESS.start()
    N_PUT_PROCESS.start()

    BN_CALL_PROCESS.start()
    BN_PUT_PROCESS.start()

    FN_CALL_PROCESS.start()
    FN_PUT_PROCESS.start()


class strategy_name(Enum):
    DATA = 0
    NORMAL = 1
    normal = 2


class normal_strategy(threading.Thread):

    def __init__(self, symbol, quantity):
        super(normal_strategy, self).__init__()
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
        self.closing_price = expiry_data.get_ema_data(self.symbol)
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

    def run(self):

        #global market_data.token_dict
        start_time = int(9) * 60 * 60 + int(20) * 60 + int(30)
        time_now = (datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour * 60 * 60 + datetime.datetime.now(
            pytz.timezone('Asia/Kolkata')).minute * 60 + datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second)
        end_time = int(15) * 60 * 60 + int(30) * 60 + int(59)
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['PNL'] = 0.0
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['LAST_ENTRY'] = 0.0
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['NOE'] = 0
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['BROKERAGE'] = 0.0
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['POS'] = ""
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["EMA"] = market_data.token_dict[self.symbol][strategy_name.DATA.value][
            "EMA"]
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["FCH"] = market_data.token_dict[self.symbol][strategy_name.DATA.value][
            "FCH"]

        while True:
            while start_time < \
                    (datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour * 60 * 60 + datetime.datetime.now(
                        pytz.timezone('Asia/Kolkata')).minute * 60 + datetime.datetime.now(
                        pytz.timezone('Asia/Kolkata')).second) \
                    < end_time:

                # print("{}:{}".format(datetime.datetime.now(pytz.timezone('Asia/Kolkata')), market_data.token_dict[self.symbol]))
                # sleep(1)
                sleep(0.3)
                self.price = float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"])
                # print(f'{self.symbol}beginning of the loop')

                market_data.token_dict[self.symbol][strategy_name.DATA.value]["EMA"] = market_data.token_dict[self.symbol][strategy_name.DATA.value]["EMA"]

                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["BROKERAGE"] = self.short_brokerage + self.long_brokerage

                if self.lng == True:
                    market_data.token_dict[self.symbol][strategy_name.NORMAL.value][
                        'PNL'] = self.long_pnl_booked + self.short_pnl_booked + (
                            (float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]) - market_data.token_dict[self.symbol][strategy_name.DATA.value][
                                'LAST_ENTRY']) * self.quantity)
                    # print(f'{self.symbol}calculating pnl lng')


                elif self.sht == True:
                    market_data.token_dict[self.symbol][strategy_name.NORMAL.value][
                        'PNL'] = self.long_pnl_booked + self.short_pnl_booked + (
                            (market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['LAST_ENTRY'] - float(
                                market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"])) * self.quantity)
                    # print(f'{self.symbol}calculating pnl sht')

                if self.first_trade:
                    self.go_short(-1, "First_trade")

                while not self.price_crossed_ema:
                    # print(f'{self.symbol} in not self.price_crossed_ema loop ')

                    if float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]) > self.ema:
                        # print(f'{self.symbol} in lp > ema loop ')
                        if not self.price_greater_than_ema_loop:
                            # print(f'{self.symbol}in not self.price_greater_than_ema_loop ')
                            self.price_greater_than_ema_loop = True
                            if self.price_greater_than_ema_loop == True and self.price_less_than_ema_loop == True:
                                sleep(4)
                                # print(
                                #    f'{self.symbol}in self.price_greater_than_ema_loop == True and self.price_less_than_ema_loop == True ')
                                if market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"] > self.ema:
                                    # print(f'{self.symbol}in market_data.token_dict[self.symbol]["LP"] > self.ema')
                                    self.price_crossed_ema = True
                                    self.price = market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]
                                    self.lng_counter = 5
                                    break
                                else:
                                    self.price_greater_than_ema_loop = False
                        if float(market_data.token_dict[self.symbol][strategy_name.DATA.value][
                                     "LP"]) > self.first_candle_high and self.sht == True:
                            # print(
                            #    f'{self.symbol}in float(market_data.token_dict[self.symbol]["LP"]) > self.first_candle_high calling long function')
                            pos_close = None
                            pos_close = self.close_short_pos(self.first_candle_high)
                            # print('closed short pos')
                            if pos_close:
                                while True:
                                    if (datetime.datetime.now(
                                            pytz.timezone('Asia/Kolkata')).minute % 5) == 4 and datetime.datetime.now(
                                        pytz.timezone('Asia/Kolkata')).second == 58:
                                        self.temp_closing_candle_variable = \
                                        market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]
                                        # print(f'{self.symbol}waiting for candle too close')
                                        break

                                if self.temp_closing_candle_variable < self.first_candle_high:
                                    # print(
                                    #    f'{self.symbol}in self.temp_closing_candle_variable < self.first_candle_high:')
                                    # print(f'{self.symbol}calling go short')
                                    self.go_short(self.first_candle_high, "FCH")
                                    break
                                elif self.temp_closing_candle_variable > self.first_candle_high:
                                    # print(
                                    #    f'{self.symbol}in self.temp_closing_candle_variable < self.first_candle_high:')
                                    # print(f'{self.symbol}calling go short')
                                    #self.go_long(self.first_candle_high, "FCH")
                                    break

                        elif float(market_data.token_dict[self.symbol][strategy_name.DATA.value][
                                       "LP"]) < self.first_candle_high and self.lng == True:
                            # print(
                            #    f'{self.symbol}in market_data.token_dict[self.symbol]["LP"]) < self.first_candle_high and self.lng == True:')
                            # print(f'{self.symbol}calling close_long_pos')
                            pos_close = None
                            pos_close = self.close_long_pos(self.first_candle_high)
                            if pos_close:
                                while True:
                                    if (datetime.datetime.now(
                                            pytz.timezone('Asia/Kolkata')).minute % 5) == 4 and datetime.datetime.now(
                                        pytz.timezone('Asia/Kolkata')).second == 58:
                                        self.temp_closing_candle_variable = market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]
                                        #print(f'{self.symbol}waiting for candle to close')
                                        break
                                if self.temp_closing_candle_variable > self.first_candle_high:
                                    # print(f'{self.symbol}in self.temp_closing_candle_variable > self.first_candle_high:')
                                    # print(f'{self.symbol}calling go_long')
                                    #self.go_long(self.first_candle_high, "FCH")
                                    break
                                elif self.temp_closing_candle_variable < self.first_candle_high:
                                    # print(
                                    #    f'{self.symbol}in self.temp_closing_candle_variable < self.first_candle_high:')
                                    # print(f'{self.symbol}calling go_sht')
                                    self.go_short(self.first_candle_high, "FCH")
                                    break




                    elif float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]) < self.ema:
                        # print(f'{self.symbol}in float(market_data.token_dict[self.symbol]["LP"]) < self.ema')
                        if not self.price_less_than_ema_loop:
                            # print(f'{self.symbol}in not self.price_less_than_ema_loop: ')
                            self.price_less_than_ema_loop = True

                            if self.price_greater_than_ema_loop == True and self.price_less_than_ema_loop == True:
                                sleep(4)
                                # print(
                                #    f'{self.symbol}in self.price_greater_than_ema_loop == True and self.price_less_than_ema_loop == True:')
                                if market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"] < self.ema:
                                    # print(f'{self.symbol}in market_data.token_dict[self.symbol]["LP"] < self.ema:')
                                    self.price_crossed_ema = True
                                    self.price = market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]
                                    self.sht_counter = 5
                                    break
                                else:
                                    # print('self.price_less_than_ema_loop = False')
                                    self.price_less_than_ema_loop = False

                        if float(market_data.token_dict[self.symbol][strategy_name.DATA.value][
                                     "LP"]) > self.first_candle_high and self.sht == True:
                            # print(
                            #    f'{self.symbol}in float(market_data.token_dict[self.symbol]["LP"]) > self.first_candle_high calling long function')
                            self.close_short_pos(self.first_candle_high)
                            while True:
                                if (datetime.datetime.now(
                                        pytz.timezone('Asia/Kolkata')).minute % 5) == 4 and datetime.datetime.now(
                                    pytz.timezone('Asia/Kolkata')).second == 58:
                                    self.temp_closing_candle_variable = \
                                    market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]
                                    # print(f'{self.symbol}waiting for candle to close')
                                    break

                            if self.temp_closing_candle_variable < self.first_candle_high:
                                # print(f'{self.symbol}in self.temp_closing_candle_variable < self.first_candle_high:')
                                # print(f'{self.symbol}calling go_sht')
                                self.go_short(self.first_candle_high, "FCH")
                                break
                            elif self.temp_closing_candle_variable > self.first_candle_high:
                                # print(f'{self.symbol}in self.temp_closing_candle_variable < self.first_candle_high:')
                                # print(f'{self.symbol}calling go_sht')
                                #self.go_long(self.first_candle_high, "FCH")
                                break

                        elif float(market_data.token_dict[self.symbol][strategy_name.DATA.value][
                                       "LP"]) < self.first_candle_high and self.lng == True:
                            print(
                                f'{self.symbol}in float(market_data.token_dict[self.symbol]["LP"]) < self.first_candle_high and self.lng == True:')
                            self.close_long_pos(self.first_candle_high)
                            pos_close = None
                            print(f'{self.symbol}close_lng_pos')
                            if pos_close:
                                while True:
                                    if (datetime.datetime.now(
                                            pytz.timezone('Asia/Kolkata')).minute % 5) == 4 and datetime.datetime.now(
                                        pytz.timezone('Asia/Kolkata')).second == 58:
                                        self.temp_closing_candle_variable = market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]
                                        #print(f'{self.symbol}waiting for candle to close')
                                        break
                                if self.temp_closing_candle_variable > self.first_candle_high:
                                    #print(f'{self.symbol}self.temp_closing_candle_variable > self.first_candle_high:')
                                    #print(f'{self.symbol}go_lng')
                                    #self.go_long(self.first_candle_high, "FCH")
                                    break
                                elif self.temp_closing_candle_variable < self.first_candle_high:
                                    #print(f'{self.symbol}self.temp_closing_candle_variable < self.first_candle_high:')
                                    #print(f'{self.symbol}go_sht')
                                    self.go_short(self.first_candle_high, "FCH")
                                    break
                            else:
                                break

                    break

                while self.price_crossed_ema:
                    # print(f'{self.symbol}in while self.price_crossed_ema:')
                    if float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]) > self.ema and self.sht == True:
                        # print(f'{self.symbol}in float(market_data.token_dict[self.symbol]["LP"]) > self.ema: calling long fun')
                        pos_close = None
                        pos_close = self.close_short_pos(self.ema)
                        if pos_close:
                            while True:
                                if (datetime.datetime.now(
                                        pytz.timezone('Asia/Kolkata')).minute % 5) == 4 and datetime.datetime.now(
                                    pytz.timezone('Asia/Kolkata')).second == 58:
                                    self.temp_closing_candle_variable = market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]
                                    # print(f'{self.symbol} waiting for candle to close')
                                    break

                            if self.temp_closing_candle_variable < self.ema:
                                # print(f'{self.symbol}self.temp_closing_candle_variable < self.ema:')
                                # print(f'{self.symbol}go_sht')
                                self.go_short(self.ema, "EMA")
                                break
                        else:
                            break

                    elif float(
                            market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]) < self.ema and self.sht == False:
                        print(f'{self.symbol}in float(market_data.token_dict[self.symbol]["LP"]) < self.ema: calling long fun')
                        # pos_close = None
                        # pos_close = self.close_long_pos(self.ema)
                        print(f'{self.symbol}close_lng_pos')

                        while True:
                            if (datetime.datetime.now(
                                    pytz.timezone('Asia/Kolkata')).minute % 5) == 4 and datetime.datetime.now(
                                pytz.timezone('Asia/Kolkata')).second == 58:
                                self.temp_closing_candle_variable = market_data.token_dict[self.symbol][strategy_name.DATA.value][
                                    "LP"]
                                # print(f'{self.symbol}waiting for candle to close')
                                break
                        if self.temp_closing_candle_variable > self.ema:
                            # print(f'{self.symbol}self.temp_closing_candle_variable > self.ema:')
                            # print(f'{self.symbol}go_lng')
                            #self.go_long(self.ema, "EMA")
                            break
                        elif self.temp_closing_candle_variable < self.ema:
                            # print(f'{self.symbol}self.temp_closing_candle_variable < self.ema:')
                            # print(f'{self.symbol}go_sht')
                            self.go_short(self.ema, "EMA")
                            break
                    else:
                        break

                    '''
                    elif float(market_data.token_dict[self.symbol]["LP"]) > self.ema and self.closing_price[-1] < self.ema:
                        self.close_short_pos(self.ema)
                        break
                    elif float(market_data.token_dict[self.symbol]["LP"]) < self.ema and self.closing_price[-1] < self.ema:
                        # print(f'{self.symbol}in float(market_data.token_dict[self.symbol]["LP"]) < self.ema: calling sht fun')
                        self.go_short(self.ema, "EMA")
                        break
                    elif float(market_data.token_dict[self.symbol]["LP"]) < self.ema and self.closing_price[-1] > self.ema:
                        self.close_long_pos(self.ema)
                        break
                # time_now = (datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour * 60 * 60 + datetime.datetime.now(
                #    pytz.timezone('Asia/Kolkata')).minute * 60 + datetime.datetime.now(
                #    pytz.timezone('Asia/Kolkata')).second)
                '''

    def go_long(self, pivot, reason):
        print(f'{self.symbol}in go long func')
        if (float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]) > pivot) and self.lng == False:
            # print(f'{self.symbol}if (float(market_data.token_dict[self.symbol]["LP"]) > pivot) and self.lng == False:')
            # self.sht_counter = 0
            # sleep(5)
            self.lng_counter = self.lng_counter + 1
            # print(f'{self.symbol}in lng func  {self.lng_counter}')
            if (float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]) > pivot) and self.lng == False:
                # and self.lng_counter == 6:
                # print(f'{self.symbol} in if (float(market_data.token_dict[self.symbol]["LP"]) > pivot) after waiting for 5 secs')
                self.price = float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"])
                self.lng_count = self.lng_count + 1
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["NOE"] = \
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["NOE"] + 1
                self.lng = True
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["POS"] = "LONG"
                # self.sht = False
                self.lng_counter = 0
                print('{} went long at price-{}, time-{}:{}:{}'.format(self.symbol,
                                                                       self.price,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone('Asia/Kolkata')).hour,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone(
                                                                               'Asia/Kolkata')).minute,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone(
                                                                               'Asia/Kolkata')).second))
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['LAST_ENTRY'] = self.price
                self.long_entry_price.append(float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]))
                # self.short_exit_price.append(float(market_data.token_dict[self.symbol]["LP"]))

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
        # print(f'{self.symbol}in sht func')
        if self.first_trade:
            # print(f'{self.symbol}in self.first_trade:')
            self.short_entry_price.append(self.price)
            print('{} went short at price-{}, time-{}:{}:{}'.format(self.symbol,
                                                                    self.price,
                                                                    datetime.datetime.now(
                                                                        pytz.timezone('Asia/Kolkata')).hour,
                                                                    datetime.datetime.now(
                                                                        pytz.timezone('Asia/Kolkata')).minute,
                                                                    datetime.datetime.now(
                                                                        pytz.timezone('Asia/Kolkata')).second))
            self.first_trade = False
            self.sht = True
            market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["POS"] = "SHORT"
            market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["NOE"] = market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["NOE"] + 1
            market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["LAST_ENTRY"] = self.price

            # if len(self.long_entry_price) == len(self.long_exit_price):
            #    self.long_pnl_booked = (self.long_pnl_booked + (
            #            self.long_entry_price[len(self.long_entry_price) - 1] - self.long_exit_price[
            #        len(self.long_exit_price) - 1])) * self.quantity

        if (float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"]) < pivot) and self.sht == False:
            # print(f'{self.symbol}in sht func not first trade')
            self.lng_counter = 0
            # sleep(5)
            self.sht_counter = self.sht_counter + 1
            # print(f'{self.symbol}in sht func not first trade {self.sht_counter}')
            if (market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"] < pivot):
                # and self.sht_counter == 6:
                self.price = float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"])
                self.sht_count = self.sht_count + 1
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["NOE"] = \
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["NOE"] + 1
                self.sht = True
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["POS"] = "SHORT"
                # self.lng = False
                self.sht_counter = 0
                print('{} went short at price-{}, time-{}:{}:{}'.format(self.symbol,
                                                                        self.price,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone('Asia/Kolkata')).hour,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone(
                                                                                'Asia/Kolkata')).minute,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone(
                                                                                'Asia/Kolkata')).second))
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['LAST_ENTRY'] = float(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"])
                # self.long_exit_price.append(float(market_data.token_dict[self.symbol]["LP"]))
                self.short_entry_price.append(float(market_data.token_dict[self.symbol]["LP"]))
                # self.price_crossed_ema = True if reason == "EMA" else False

                # if len(self.long_entry_price) == len(self.long_exit_price):
                #    self.long_pnl_booked = self.long_pnl_booked + ((
                #                                                           self.long_exit_price[
                #                                                               len(self.long_exit_price) - 1] -
                #                                                           self.long_entry_price[
                #                                                               len(self.long_entry_price) - 1]) * self.quantity)

                #            self.long_brokerage = self.long_brokerage + self.calc_brokerage(
                #        self.long_entry_price[len(self.long_entry_price) - 1], self.long_exit_price[
                #            len(self.long_exit_price) - 1], "LONG")

    def close_long_pos(self, pivot):
        # print('in close_long_pos')
        if (market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP'] < pivot) and self.lng == True:

            sleep(6)
            if (market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP'] < pivot) and self.lng == True:

                print('square-off {} at price {}'.format(self.symbol,
                                                         market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP']))
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['POS'] = ' '
                self.long_exit_price.append(market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP'])
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
        # print('in close_short_pos')
        if (market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP'] > pivot) and self.sht == True:
            sleep(6)
            if (market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP'] > pivot) and self.sht == True:
                print('square-off {} at price {}'.format(self.symbol, market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP']))
                market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['POS'] = ' '
                self.short_exit_price.append(market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP'])
                self.sht = False

                if len(self.short_entry_price) == len(self.short_exit_price):
                    self.short_pnl_booked = self.short_pnl_booked + ((
                                                                             self.short_entry_price[
                                                                                 len(self.short_entry_price) - 1] -
                                                                             self.short_exit_price[
                                                                                 len(self.short_exit_price) - 1]) * self.quantity)

                    self.short_brokerage = self.short_brokerage + self.calc_brokerage(
                        self.short_entry_price[len(self.short_entry_price) - 1], self.short_exit_price[
                            len(self.short_exit_price) - 1], "SHORT")
                return True
        return False

    def hedge(self):
        print('HEDGE-{} went long at price-{}, time-{}:{}:{}'.format(self.symbol,
                                                                     self.price,
                                                                     datetime.datetime.now(
                                                                         pytz.timezone('Asia/Kolkata')).hour,
                                                                     datetime.datetime.now(
                                                                         pytz.timezone('Asia/Kolkata')).minute,
                                                                     datetime.datetime.now(
                                                                         pytz.timezone('Asia/Kolkata')).second))
        self.hedge_entry_price.append(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"])
        market_data.token_dict[self.symbol]["NOE"] = 0

        start_time = int(9) * 60 * 60 + int(19) * 60 + int(30)
        time_now = (datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour * 60 * 60 + datetime.datetime.now(
            pytz.timezone('Asia/Kolkata')).minute * 60 + datetime.datetime.now(pytz.timezone('Asia/Kolkata')).second)
        end_time = int(15) * 60 * 60 + int(18) * 60 + int(59)
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['LAST_ENTRY'] = self.price
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["LONG"] = True
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["NOE"] = \
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]["NOE"] + 1
        self.lng = True
        market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['POS'] = 'LONG'

        while start_time <= time_now <= end_time:
            time_now = (datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour * 60 * 60 + datetime.datetime.now(
                pytz.timezone('Asia/Kolkata')).minute * 60 + datetime.datetime.now(
                pytz.timezone('Asia/Kolkata')).second)
            market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP'] = self.price
            if self.lng == True:
                market_data.token_dict[self.symbol][strategy_name.DATA.value]['PNL'] = (
                        (market_data.token_dict[self.symbol][strategy_name.DATA.value]['LP'] -
                         market_data.token_dict[self.symbol][strategy_name.NORMAL.value]['LAST_ENTRY']) * self.quantity)

    def exit_open_positions(self):
        self.current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
        if self.lng:
            self.long_exit_price.append(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"])
            print("exited long - {} at price-{}, time {}:{}:{}".format(self.symbol,
                                                                       market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"],
                                                                       datetime.datetime.now(
                                                                           pytz.timezone('Asia/Kolkata')).hour,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone(
                                                                               'Asia/Kolkata')).minute,
                                                                       datetime.datetime.now(
                                                                           pytz.timezone(
                                                                               'Asia/Kolkata')).second))
            self.lng = False

        if self.sht:
            self.short_exit_price.append(market_data.token_dict[self.symbol][strategy_name.DATA.value]["LP"])
            print("exited short - {} at price-{}, time {}:{}:{}".format(self.symbol,
                                                                        market_data.token_dict[self.symbol][
                                                                            strategy_name.DATA.value]["LP"],
                                                                        datetime.datetime.now(
                                                                            pytz.timezone('Asia/Kolkata')).hour,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone(
                                                                                'Asia/Kolkata')).minute,
                                                                        datetime.datetime.now(
                                                                            pytz.timezone(
                                                                                'Asia/Kolkata')).second))
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
