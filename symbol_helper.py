import expiry_data


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


def get_fch_and_first_candle_closing(symbol):
    strike = int(symbol[-5:])

    if symbol[0] == "B":
        symbol_ = 'BANKNIFTY'
        expiry_date_ = expiry_data.get_banknifty_expiry()
    elif symbol[0] == "N":
        symbol_ = 'NIFTY'
        expiry_date_ = expiry_data.get_nifty_expiry()
    elif symbol[0] == "F":
        symbol_ = 'FINNIFTY'
        expiry_date_ = expiry_data.get_finnifty_expiry()

    is_CE = True if symbol[-6] == "C" else False

    instrument = alice.get_instrument_for_fno(exch='NFO', symbol=symbol_, expiry_date=expiry_date_,
                                                is_fut=False, strike=strike,
                                                is_CE=is_CE)

    from_datetime = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).replace(hour=9,
                                                                                    minute=14)
    to_datetime = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))

    interval = "1"  # ["1", "D"]
    indices = False  # For Getting index data
    df_ = alice.get_historical(instrument, from_datetime, to_datetime, interval, indices)
    first_candle_high = max(df_.head(15)['high'])
    return first_candle_high, df_['close'][14]