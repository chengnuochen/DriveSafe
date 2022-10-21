import threading 
import time 
import os 
from datetime import datetime as dt
import sys 
import requests

import global_params as gp 
import record as rec
import monitor_sleepy
import monitor_speed
import get_loc_speed as gls


def driveSafeSystem(): 
    # os.system('clear')
    t_get_loc_speed = threading.Thread(target=gls.get_from_gps, args=())
    # t_get_loc_speed = threading.Thread(target=gls.get_from_route, args=())
    t_monitor_sleepy = threading.Thread(target=monitor_sleepy.monitor_sleepy, args=())
    t_monitor_speed = threading.Thread(target=monitor_speed.monitor_speeding, args=())
    t_status = threading.Thread(target=gp.print_status, args=())
    t_warning = threading.Thread(target=gp.warning, args=())

    t_get_loc_speed.daemon = True
    t_monitor_speed.daemon = True
    t_status.daemon = True
    t_warning.daemon = True 

    try: 
        rec.create_record() 
        t_monitor_sleepy.start()
        t_monitor_speed.start()
        t_status.start()
        t_get_loc_speed.start()
        t_warning.start()
    except KeyboardInterrupt:
        print("Killing all threads ... ")
        # t_monitor_sleepy.kill_received = True
        # t_monitor_speed.kill_received = True
        # t_status.kill_received = True
        # t_get_loc_speed.kill_received = True
        print('End of journey, Here is the data report:')
        print('Please refer to \"./data/{0}\" for details'.format(gp.fname))
        exit(0)



if __name__=="__main__":
    # sys.argv[1] 
    driveSafeSystem() 
    while True: 
        if gp.arriveDest: 
            break 

    # sent ifttt 
    tripTime = str(dt.now()-gp.tripStartTime)
    # payload = { 'value1' : tripTime, 'value2' : gp.rec_num, 'value3' : '5:41'}
    payload = { 'value1' : gp.tripStartTime.strftime("%H:%M:%S"), 'value2' : dt.now().strftime('%H:%M:%S'), 'value3' : gp.rec_num}
    requests.post("https://maker.ifttt.com/trigger/trip_end/with/key/dF2Lt3x9C_s_KEMcpvPc4w", data=payload)
    os.system('espeak "This is the end of the trip, see you next time"')
    print("[INFO] This is the end of the trip")
    print("[INFO] sending IFTTT notification")
    print("[INFO] exiting ... ")
    
        


