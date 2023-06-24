
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