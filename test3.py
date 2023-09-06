#from UltraDict import UltraDict
#other = UltraDict(recurse = True, name='ravi_',create=False,auto_unlink=False)
#other['nested']['counter'] += 1

#print(other)

#secret!!!!!!!!!!!!

delta_dict_expected = {'NIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}, 
            'BANKNIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}, 
            'FINNIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}},
}

def update_delta_dict_expected(base_symbol, target_delta):
    global token_dict
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

if __name__ == "__main__":
    num_processes = 3
    global delta_dict_expected

    with multiprocessing.Pool(processes=num_processes) as pool:
        # Create a list of (base_symbol, delta) pairs
        pairs = [(base_symbol, delta) for base_symbol in delta_dict_expected.keys() for delta in delta_dict_expected[base_symbol].keys()]
        
        # Use the map function to apply the update_delta_dict_expected function
        pool.starmap(update_delta_dict_expected, pairs)
        
        print("Updated delta_dict_expected:", delta_dict_expected)