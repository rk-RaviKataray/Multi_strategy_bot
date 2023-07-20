from UltraDict import UltraDict

def socket():


    global token_dict
    global LTP
    global socket_opened
    global subscribe_flag
    global subscribe_list

    LTP = 0
    token_dict = UltraDict(recurse=True, name='token_dict')
    token_dict['NIFTY_SPOT'] = [
        {"TOKEN": 0, "LP": 0.0, "EMA": 0, "FCH": 0},
        {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "NOE": 0, "BROKERAGE": 0},
        {"POS": "", "PNL": 0.0, "LAST_ENTRY": 0, "EMA": 0, "FCH": 0, "NOE": 0, "BROKERAGE": 0}
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

def get_token_dict():
    return token_dict

socket()
print(token_dict.name)
