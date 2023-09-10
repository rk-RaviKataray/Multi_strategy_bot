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
from multiprocessing import Process
from UltraDict import UltraDict
import retrying
from flask_cors import CORS


def is_current_date_greater_than_latest_expiry(string_input_with_date):
    # string_input_with_date = "2023-08-03"
    past = datetime.datetime.strptime(string_input_with_date, "%Y-%m-%d")
    present = datetime.datetime.now()
    return past.date() < present.date()


# User Credential
user_id = '771791'
api_key = 'jOf1uqDV2objI4Obj33QuoTN4Iz7qXD0mW5X0WgupaH8k9NvWV0hqifsdN6Rf1vmEmGEbHJsLq448Kkt6tU7u5qocJyOTQOYJAxxcq1dyqHzs1br5IGFnpsQrPUATctt'


# Connect and get session Id
alice = Aliceblue(user_id=user_id, api_key=api_key)
print(alice.get_session_id())
# if os.path.exists("//home/ravik/Desktop/Dynamic Update/NFO.csv"):
#   os.remove("/home/ravik/Desktop/Dynamic Update/NFO.csv")
alice.get_contract_master("INDICES")
# pathlib.Path('/home/ravik/Desktop/Dynamic Update/NFO.csv').rename('/home/ravik/Desktop/Dynamic Update/NFO.csv')
print("master contract downloaded")
sleep(1.5)

df = pd.read_csv('BFO.csv')
expiry_sensex_df = df[df['Symbol'] == 'SENSEX']


expiry_sensex = expiry_sensex_df['Expiry Date'].sort_values().drop_duplicates().reset_index(drop=True)


expiry_sensex = expiry_sensex[1] if is_current_date_greater_than_latest_expiry(expiry_sensex[0]) else expiry_sensex[0]



print('next sensex expiry is on {}'.format(expiry_sensex))
