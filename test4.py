from UltraDict import UltraDict


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

delta_dict_expected = UltraDict(recurse=True,create=True)
delta_dict_expected['NIFTY'] = {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}
delta_dict_expected['BANKNIFTY'] =   {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}
delta_dict_expected['FINNIFTY'] =   {0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}