# from UltraDict import UltraDict


# ultra = UltraDict(recurse = True, name='ravi_',create=False,auto_unlink=False)
# #ultra['nested'] = { 'counter': 0 }


# print(ultra)
import multiprocessing

from multiprocessing import Process

quantity_dic = {'NIFTY':1000,'BANKNIFTY':750, 'FINNIFTY':400}
global token_dict

token_dict = {'NIFTYC': {'DELTA':  0.55}, 'NIFTY1C': {'DELTA':  0.52},
              'NIFTY2C': {'DELTA':  0.49},
               'NIFTYP': {'DELTA':  -0.55}, 'NIFTY1P': {'DELTA':  -0.52},
              'NIFTY2P': {'DELTA':  -0.49},

'BANKNIFTYC': {'DELTA':  0.55}, 'BANKNIFTY1C': {'DELTA':  0.52},
              'BANKNIFTY2C': {'DELTA':  0.49},
               'BANKNIFTYP': {'DELTA':  -0.55}, 'BANKNIFTY1P': {'DELTA':  -0.52},
              'BANKNIFTY2P': {'DELTA':  -0.49},


'FINNIFTYC': {'DELTA':  0.55}, 'FINNIFTY1C': {'DELTA':  0.52},
              'FINNIFTY2C': {'DELTA':  0.49},
               'FINNIFTYP': {'DELTA':  -0.55}, 'FINNIFTY1P': {'DELTA':  -0.52},
              'FINNIFTY2P': {'DELTA':  -0.49},

              }

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
        #print(delta_dict_expected)  

        for i in range(len(check_entries.instances)):

            if check_entries.instances[i].symbol == closest_key:
                delta_dict_expected[base_symbol][abs(target_delta)][option_type] = check_entries.instances[i]    
                return    

        obj = check_entries(closest_key , quantity=quantity_dic[base_symbol],is_hedge=False)
        delta_dict_expected[base_symbol][abs(target_delta)][option_type] = obj
        obj.start()

global delta_dict_expected

delta_dict_current = {'NIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}, 
            'BANKNIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}, 
            'FINNIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}},
}
            

delta_dict_expected = {'NIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}, 
            'BANKNIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}}, 
            'FINNIFTY':{0.3:{'CALL':None, 'PUT':None}, 0.2:{'CALL':None, 'PUT':None}, 0.1:{'CALL':None, 'PUT':None}},
}


def get_delta_neutral_strikes(delta, base_symbol):

    return delta_dict_expected[base_symbol][delta]

def get_current_short_strikes(base_symbol,delta):


    return delta_dict_current[base_symbol][delta]



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


                if isinstance(current_call_strike, check_entries):
                    current_call_strike.close_short_pos()

                expected_call_strike_obj.go_short()

                delta_dict_current[self.base_symbol][self.delta]['CALL'] = expected_call_strike_obj

            if expected_put_strike != current_put_strike:

                if isinstance(current_put_strike, check_entries):
                    current_put_strike.close_short_pos()

                expected_put_strike_obj.go_short()
                delta_dict_current[self.base_symbol][self.delta]['PUT'] = expected_put_strike_obj

            sleep(5)
        




for key, value in delta_dict_expected.items():
    for x in list(value.keys()):
        update_delta_dict_expected(key, x)
        update_delta_dict_expected(key, -x)



if __name__ == "__main__":
    num_processes = 3
    
    pairs = [(base_symbol, delta) for base_symbol in delta_dict_expected.keys() for delta in delta_dict_expected[base_symbol].keys()]


    processes = []

    pairs = [(base_symbol,delta) for base_symbol in delta_dict_expected.keys() for delta in
             delta_dict_expected[base_symbol].keys()]

    with multiprocessing.Pool(processes=num_processes) as pool:
        # Create a list of (base_symbol, delta) pairs
        
        
        # Use the map function to apply the update_delta_dict_expected function
        pool.starmap(update_delta_dict_expected, pairs)
        
        #print("Updated delta_dict_expected:", delta_dict_expected)

    # for pair in pairs:
    #     process = delta_neutral(pair[0],pair[1])
    #     processes.append(process)
    #     process.start()
    print("Updated delta_dict_expected:", delta_dict_expected)
    