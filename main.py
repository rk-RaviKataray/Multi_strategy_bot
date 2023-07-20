import subprocess
import time
import datetime



list_files = subprocess.run(["pip", "install", '-r','requirements.txt'])

print('************************************All required libraries installed!!!!!**************************************')
time.sleep(2)



download_ema_data = subprocess.run(["python3", "EMA_DATA.py"])
print('*************************************EMA DATA DOWNLOAD COMPLETE!!!!!!!!!**************************************')

time.sleep(2)


print('**************************************STARTING STRATEGY!!!!!!!!!**************************************')
run_strategy = subprocess.run(["python3", "bot.py"])
