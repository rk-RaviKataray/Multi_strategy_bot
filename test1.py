import datetime
import pytz
import os
import time


N_pnl_list_for_dynamic_graph = [0,1,2,3,4,5,6,7]


if not os.path.exists("./instrument_data/BANKNIFTY"):
    os.makedirs("./instrument_data/BANKNIFTY")


with open("./instrument_data/BANKNIFTY/candle_data.jsonl", 'a') as N_candle_data_file:
        N_time_ = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%s')
        N_open_ = N_pnl_list_for_dynamic_graph[0]
        N_high_ = max(N_pnl_list_for_dynamic_graph)
        N_low_= min(N_pnl_list_for_dynamic_graph)
        N_close_ = int(NIFTY_NET_PNL)
        N_pnl_list_for_dynamic_graph.clear()
        N_candle_data_to_append = {"time": int(N_time_)+19800, "open": N_open_, "high": N_high_, "low":N_low_, "close": N_close_}
        json.dump(N_candle_data_to_append, N_candle_data_file)
        N_candle_data_file.write('\n')
        N_candle_data_file.flush()
        os.fsync(N_candle_data_file)
        sleep(0.3)

     