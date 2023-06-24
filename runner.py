from flask import Flask, jsonify, render_template
from pya3 import *
import pandas as pd
import datetime
import pytz
import json
from multiprocessing import Process
from UltraDict import UltraDict
from enum import Enum
import greedy_strategy,normal_strategy
import market_data
import expiry_data

app = Flask(__name__)

# logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w")

# User Credential
user_id = ''
api_key = ''

# Connect and get session Id
alice = Aliceblue(user_id=user_id, api_key=api_key)
print(alice.get_session_id())

sleep(1.5)


class strategy_name(Enum):
    DATA = 0
    NORMAL = 1
    GREEDY = 2


Nifty_spot = 0
BankNifty_spot = 0
nifty_atm = 0
banknifty_atm = 0
# expiry_nifty = []
# expiry_banknifty = []
# expiry_finnifty = []

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


NIFTY_GROSS_PNL_LIST_FOR_GRAPH = []
NIFTY_NET_PNL_LIST_FOR_GRAPH = []
BANKNIFTY_GROSS_PNL_LIST_FOR_GRAPH = []
BANKNIFTY_NET_PNL_LIST_FOR_GRAPH = []

TIME_STAMP_FOR_GRAPH = []


expiry_data.generate_expiry_data()

print('next nifty expiry is on {}'.format(expiry_data.get_nifty_expiry()))
print('next banknifty expiry is on {}'.format(expiry_data.get_banknifty_expiry()))
print('next finnifty expiry is on {}'.format(expiry_data.get_finnifty_expiry()))


market_data.socket(alice)


print(
    "waiting for ATM at 9:20, current time- {}:{}".format(datetime.datetime.now(pytz.timezone('Asia/Kolkata')).hour,
                                                            datetime.datetime.now(
                                                                pytz.timezone('Asia/Kolkata')).minute))


nifty_atm, banknifty_atm, finnifty_atm = market_data.get_atm()

subscribe_list = [alice.get_instrument_by_token('INDICES', 26000),  # nifty spot
                    alice.get_instrument_by_token('INDICES', 26009),  # banknifty spot
                    alice.get_instrument_by_token('INDICES', 26037),  # NSE,NIFTY FIN SERVICE,26037

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm),
                                                is_CE=True),  # change expir
                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm), is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) + 100, is_CE=True),
                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) + 100, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) + 200, is_CE=True),

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) + 200, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) + 300, is_CE=True),

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) + 300, is_CE=False),

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) - 100, is_CE=True),

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) - 100, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) - 200, is_CE=True),

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) - 200, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) - 300, is_CE=True),

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) - 300, is_CE=False),

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) - 600, is_CE=False),
                    # BN Hedge PE

                    alice.get_instrument_for_fno(exch='NFO', symbol='BANKNIFTY', expiry_date=expiry_data.get_banknifty_expiry(),
                                                is_fut=False, strike=int(banknifty_atm) + 600, is_CE=True),
                    # BN Hedge CE

                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm), is_CE=True),  # change expiry
                    #
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm), is_CE=False),

                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) + 100, is_CE=True),
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) + 100, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) + 200, is_CE=True),
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) + 200, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) - 100, is_CE=True),
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) - 100, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) - 200, is_CE=True),
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) - 200, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) - 500, is_CE=False),
                    # #NIFTY Hedge Pe
                    alice.get_instrument_for_fno(exch='NFO', symbol='NIFTY', expiry_date=expiry_data.get_nifty_expiry(),
                                                is_fut=False, strike=int(nifty_atm) + 500, is_CE=True),
                    # #NIFTY Hedge CE
                    alice.get_instrument_for_fno(exch='NFO', symbol='FINNIFTY', expiry_date=expiry_data.get_finnifty_expiry(),
                                                is_fut=False, strike=int(finnifty_atm), is_CE=True),
                    alice.get_instrument_for_fno(exch='NFO', symbol='FINNIFTY', expiry_date=expiry_data.get_finnifty_expiry(),
                                                is_fut=False, strike=int(finnifty_atm), is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='FINNIFTY', expiry_date=expiry_data.get_finnifty_expiry(),
                                                is_fut=False, strike=int(finnifty_atm) + 100, is_CE=True),
                    alice.get_instrument_for_fno(exch='NFO', symbol='FINNIFTY', expiry_date=expiry_data.get_finnifty_expiry(),
                                                is_fut=False, strike=int(finnifty_atm) + 100, is_CE=False),
                    alice.get_instrument_for_fno(exch='NFO', symbol='FINNIFTY', expiry_date=expiry_data.get_finnifty_expiry(),
                                                is_fut=False, strike=int(finnifty_atm) - 100, is_CE=True),
                    alice.get_instrument_for_fno(exch='NFO', symbol='FINNIFTY', expiry_date=expiry_data.get_finnifty_expiry(),
                                                is_fut=False, strike=int(finnifty_atm) - 100, is_CE=False)
                    ]
print("trying to resubcribe")
alice.subscribe(subscribe_list)
sleep(5)


greedy_strategy.execute_greedy_startegy()
normal_strategy.execute_normal_startegy()



@app.route('/_greedy', methods=['GET'])
def greedy():
    NIFTY_TOTAL_PNL_list = []
    NIFTY_TOTAL_BROKERAGE_list = []
    NIFTY_TOTAL_ENTRIES_list = []
    BANKNIFTY_TOTAL_PNL_list = []
    BANKNIFTY_TOTAL_BROKERAGE_list = []
    BANKNIFTY_TOTAL_ENTRIES_list = []
    FINNIFTY_TOTAL_PNL_list = []
    FINNIFTY_TOTAL_BROKERAGE_list = []
    FINNIFTY_TOTAL_ENTRIES_list = []
    global NIFTY_GROSS_PNL_LIST_FOR_GRAPH
    global NIFTY_NET_PNL_LIST_FOR_GRAPH
    global BANKNIFTY_GROSS_PNL_LIST_FOR_GRAPH
    global BANKNIFTY_NET_PNL_LIST_FOR_GRAPH
    global TIME_STAMP_FOR_GRAPH

    # json2html.convert(json=input)
    updated_html = ""

    for x in market_data.token_dict.keys():

        updated_html = updated_html + """
        <tr>
            <td>  {instrument}   </td>
            <td>  {lp}   </td>
            <td>  {pos}   </td>
            <td>  {pnl}   </td>
            <td>  {brokerage}   </td>
            <td>  {last_entry}   </td>
            <td>  {ema}   </td>
            <td>  {fch}   </td>
            <td>  {noe}   </td>
        </tr>
        """.format(instrument=x, lp=round(market_data.token_dict[x][strategy_name.DATA.value]["LP"], 2),
                   pos=market_data.token_dict[x][strategy_name.GREEDY.value]["POS"],
                   pnl=round(market_data.token_dict[x][strategy_name.GREEDY.value]["PNL"], 2), brokerage=round(market_data.token_dict[x][strategy_name.GREEDY.value]["BROKERAGE"], 2),
                   last_entry=round(market_data.token_dict[x][strategy_name.GREEDY.value]["LAST_ENTRY"], 2), ema=round(market_data.token_dict[x][strategy_name.DATA.value]["EMA"], 2),
                   fch=round(market_data.token_dict[x][strategy_name.DATA.value]["FCH"], 2), noe=int(market_data.token_dict[x][strategy_name.GREEDY.value]["NOE"]))

        if x[0] == "N":
            NIFTY_TOTAL_PNL_list.append(market_data.token_dict[x][strategy_name.DATA.value]["PNL"])
            NIFTY_TOTAL_BROKERAGE_list.append(market_data.token_dict[x][strategy_name.GREEDY.value]["BROKERAGE"])
            NIFTY_TOTAL_ENTRIES_list.append(market_data.token_dict[x][strategy_name.GREEDY.value]["NOE"])

        elif x[0] == "B":
            BANKNIFTY_TOTAL_PNL_list.append(market_data.token_dict[x][strategy_name.DATA.value]["PNL"])
            BANKNIFTY_TOTAL_BROKERAGE_list.append(market_data.token_dict[x][strategy_name.GREEDY.value]["BROKERAGE"])
            BANKNIFTY_TOTAL_ENTRIES_list.append(market_data.token_dict[x][strategy_name.GREEDY.value]["NOE"])

        elif x[0] == "F":
            FINNIFTY_TOTAL_PNL_list.append(market_data.token_dict[x][strategy_name.DATA.value]["PNL"])
            FINNIFTY_TOTAL_BROKERAGE_list.append(market_data.token_dict[x][strategy_name.GREEDY.value]["BROKERAGE"])
            FINNIFTY_TOTAL_ENTRIES_list.append(market_data.token_dict[x][strategy_name.GREEDY.value]["NOE"])

    NIFTY_TOTAL_PNL = round(sum(NIFTY_TOTAL_PNL_list), 2)
    NIFTY_NET_PNL = round((sum(NIFTY_TOTAL_PNL_list) - sum(NIFTY_TOTAL_BROKERAGE_list)), 2)
    BANKNIFTY_TOTAL_PNL = round(sum(BANKNIFTY_TOTAL_PNL_list), 2)
    BANKNIFTY_NET_PNL = round((sum(BANKNIFTY_TOTAL_PNL_list) - sum(BANKNIFTY_TOTAL_BROKERAGE_list)), 2)
    FINNIFTY_TOTAL_PNL = round(sum(FINNIFTY_TOTAL_PNL_list), 2)
    FINNIFTY_NET_PNL = round((sum(FINNIFTY_TOTAL_PNL_list) - sum(FINNIFTY_TOTAL_BROKERAGE_list)), 2)

    updated_html2 = """
    <tr>
            <td>  {NIFTY_TOTAL_PNL}   </td>
            <td>  {NIFTY_TOTAL_BROKERAGE}   </td>
            <td>  {NIFTY_NET_PNL}   </td>
            <td>  {NIFTY_TOTAL_ENTRIES}   </td>
            <td>  {BANKNIFTY_TOTAL_PNL}   </td>
            <td>  {BANKNIFTY_TOTAL_BROKERAGE}   </td>
            <td>  {BANKNIFTY_NET_PNL}   </td>
            <td>  {BANKNIFTY_TOTAL_ENTRIES}   </td>
            <td>  {FINNIFTY_TOTAL_PNL}  </td>
            <td>  {FINNIFTY_TOTAL_BROKERAGE}  </td>
            <td>  {FINNIFTY_NET_PNL}  </td>
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
                   )

    html1 = """
        <table class="table table-striped">
            <thead>
                <tr>
                    <td>  <strong> INSTRUMENT  </strong> </td>
                    <td>  <strong> LP  </strong>  </td>
                    <td>  <strong> POS  </strong>  </td>
                    <td>  <strong> PNL  </strong>  </td>
                    <td>  <strong> BROKERAGE  </strong>  </td>
                    <td>  <strong> LAST_ENTRY </strong>   </td>
                    <td>  <strong> EMA </strong>   </td>
                    <td>  <strong> FCH </strong>   </td>
                    <td>  <strong> NOE  </strong>  </td>
                </tr>
            </thead>
            {}
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

    html = {"individual_html": html1, "summary_html": html2}

    # NIFTY_GROSS_PNL_LIST_FOR_GRAPH.append(NIFTY_TOTAL_PNL)
    # NIFTY_NET_PNL_LIST_FOR_GRAPH.append(NIFTY_NET_PNL)
    # BANKNIFTY_GROSS_PNL_LIST_FOR_GRAPH.append(BANKNIFTY_TOTAL_PNL)
    # BANKNIFTY_NET_PNL_LIST_FOR_GRAPH.append(BANKNIFTY_NET_PNL)

    # TIME_STAMP_FOR_GRAPH.append(datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S"))

    return jsonify(result=html)


@app.route('/_normal', methods=['GET'])
def normal():
    NIFTY_TOTAL_PNL_list = []
    NIFTY_TOTAL_BROKERAGE_list = []
    NIFTY_TOTAL_ENTRIES_list = []
    BANKNIFTY_TOTAL_PNL_list = []
    BANKNIFTY_TOTAL_BROKERAGE_list = []
    BANKNIFTY_TOTAL_ENTRIES_list = []
    FINNIFTY_TOTAL_PNL_list = []
    FINNIFTY_TOTAL_BROKERAGE_list = []
    FINNIFTY_TOTAL_ENTRIES_list = []
    global NIFTY_GROSS_PNL_LIST_FOR_GRAPH
    global NIFTY_NET_PNL_LIST_FOR_GRAPH
    global BANKNIFTY_GROSS_PNL_LIST_FOR_GRAPH
    global BANKNIFTY_NET_PNL_LIST_FOR_GRAPH
    global TIME_STAMP_FOR_GRAPH

    # json2html.convert(json=input)
    updated_html = ""

    for x in market_data.token_dict.keys():

        updated_html = updated_html + """
        <tr>
            <td>  {instrument}   </td>
            <td>  {lp}   </td>
            <td>  {pos}   </td>
            <td>  {pnl}   </td>
            <td>  {brokerage}   </td>
            <td>  {last_entry}   </td>
            <td>  {ema}   </td>
            <td>  {fch}   </td>
            <td>  {noe}   </td>
        </tr>
        """.format(instrument=x, lp=round(market_data.token_dict[x][strategy_name.DATA.value]["LP"], 2),
                   pos=market_data.token_dict[x][strategy_name.NORMAL.value]["POS"],
                   pnl=round(market_data.token_dict[x][strategy_name.NORMAL.value]["PNL"], 2), brokerage=round(market_data.token_dict[x][strategy_name.NORMAL.value]["BROKERAGE"], 2),
                   last_entry=round(market_data.token_dict[x][strategy_name.NORMAL.value]["LAST_ENTRY"], 2), ema=round(market_data.token_dict[x][strategy_name.DATA.value]["EMA"], 2),
                   fch=round(market_data.token_dict[x][strategy_name.DATA.value]["FCH"], 2), noe=int(market_data.token_dict[x][strategy_name.NORMAL.value]["NOE"]))

        if x[0] == "N":
            NIFTY_TOTAL_PNL_list.append(market_data.token_dict[x][strategy_name.DATA.value]["PNL"])
            NIFTY_TOTAL_BROKERAGE_list.append(market_data.token_dict[x][strategy_name.NORMAL.value]["BROKERAGE"])
            NIFTY_TOTAL_ENTRIES_list.append(market_data.token_dict[x][strategy_name.NORMAL.value]["NOE"])

        elif x[0] == "B":
            BANKNIFTY_TOTAL_PNL_list.append(market_data.token_dict[x][strategy_name.DATA.value]["PNL"])
            BANKNIFTY_TOTAL_BROKERAGE_list.append(market_data.token_dict[x][strategy_name.NORMAL.value]["BROKERAGE"])
            BANKNIFTY_TOTAL_ENTRIES_list.append(market_data.token_dict[x][strategy_name.NORMAL.value]["NOE"])

        elif x[0] == "F":
            FINNIFTY_TOTAL_PNL_list.append(market_data.token_dict[x][strategy_name.DATA.value]["PNL"])
            FINNIFTY_TOTAL_BROKERAGE_list.append(market_data.token_dict[x][strategy_name.NORMAL.value]["BROKERAGE"])
            FINNIFTY_TOTAL_ENTRIES_list.append(market_data.token_dict[x][strategy_name.NORMAL.value]["NOE"])

    NIFTY_TOTAL_PNL = round(sum(NIFTY_TOTAL_PNL_list), 2)
    NIFTY_NET_PNL = round((sum(NIFTY_TOTAL_PNL_list) - sum(NIFTY_TOTAL_BROKERAGE_list)), 2)
    BANKNIFTY_TOTAL_PNL = round(sum(BANKNIFTY_TOTAL_PNL_list), 2)
    BANKNIFTY_NET_PNL = round((sum(BANKNIFTY_TOTAL_PNL_list) - sum(BANKNIFTY_TOTAL_BROKERAGE_list)), 2)
    FINNIFTY_TOTAL_PNL = round(sum(FINNIFTY_TOTAL_PNL_list), 2)
    FINNIFTY_NET_PNL = round((sum(FINNIFTY_TOTAL_PNL_list) - sum(FINNIFTY_TOTAL_BROKERAGE_list)), 2)

    updated_html2 = """
    <tr>
            <td>  {NIFTY_TOTAL_PNL}   </td>
            <td>  {NIFTY_TOTAL_BROKERAGE}   </td>
            <td>  {NIFTY_NET_PNL}   </td>
            <td>  {NIFTY_TOTAL_ENTRIES}   </td>
            <td>  {BANKNIFTY_TOTAL_PNL}   </td>
            <td>  {BANKNIFTY_TOTAL_BROKERAGE}   </td>
            <td>  {BANKNIFTY_NET_PNL}   </td>
            <td>  {BANKNIFTY_TOTAL_ENTRIES}   </td>
            <td>  {FINNIFTY_TOTAL_PNL}  </td>
            <td>  {FINNIFTY_TOTAL_BROKERAGE}  </td>
            <td>  {FINNIFTY_NET_PNL}  </td>
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
                   )

    html1 = """
        <table class="table table-striped">
            <thead>
                <tr>
                    <td>  <strong> INSTRUMENT  </strong> </td>
                    <td>  <strong> LP  </strong>  </td>
                    <td>  <strong> POS  </strong>  </td>
                    <td>  <strong> PNL  </strong>  </td>
                    <td>  <strong> BROKERAGE  </strong>  </td>
                    <td>  <strong> LAST_ENTRY </strong>   </td>
                    <td>  <strong> EMA </strong>   </td>
                    <td>  <strong> FCH </strong>   </td>
                    <td>  <strong> NOE  </strong>  </td>
                </tr>
            </thead>
            {}
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

    html = {"individual_html": html1, "summary_html": html2}

    # NIFTY_GROSS_PNL_LIST_FOR_GRAPH.append(NIFTY_TOTAL_PNL)
    # NIFTY_NET_PNL_LIST_FOR_GRAPH.append(NIFTY_NET_PNL)
    # BANKNIFTY_GROSS_PNL_LIST_FOR_GRAPH.append(BANKNIFTY_TOTAL_PNL)
    # BANKNIFTY_NET_PNL_LIST_FOR_GRAPH.append(BANKNIFTY_NET_PNL)

    # TIME_STAMP_FOR_GRAPH.append(datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S"))

    return jsonify(result=html)

@app.route('/')
def index():
    return render_template('dy1.html')

if __name__ == '__main__':
    # app.run()
    p = Process(target=app.run(host='0.0.0.0',processes=6))
    p.start()
