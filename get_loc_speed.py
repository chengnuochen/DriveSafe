#! /usr/bin/python
import os
from gps import *
from time import *
import time
import sys 
import random 

import global_params as gp 

def gen_nowSpeed(seed): 
    gp.nowSpeed = 35+25*random.random()
    # gp.nowSpeed = 60*abs(math.cos(0.1*math.pi*seed))


# method 1: get loc and speed from GPS module 
def get_from_gps():
    # gp.gpsReady = False
    gpsd = gps(mode=WATCH_ENABLE)
    i=0
    try:
        while not gp.arriveDest: 
            gpsd.next()
            # print("gp.gpsReady =",gp.gpsReady)
            if not (gpsd.fix.mode is 1): 
                if not gp.locspdReady: 
                    print("[INFO] GPS module ready")
                    gp.locspdReady = True
                gp.lat = gpsd.fix.latitude
                gp.lon = gpsd.fix.longitude
                gp.nowSpeed = int(gpsd.fix.speed * 2.237) # meter per second to mph
                # gp.nowSpeed = gen_nowSpeed(i)
                gp.check_arriveDest()
                i += 1
            else: 
                gp.locspdReady = False 
            gp.update_allReady() 
            time.sleep(0.1) # get gps data every 1 sec 

    except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
        print ("[GPS] Exiting.")
    
# method 2: get loc from iPhone SSH command 
loc_file_path = gp.PROJ_PATH + 'loc.csv'
def save_iphone_gps(string): 
    f = open(loc_file_path, 'w')
    f.write(string)
    f.close()

def get_from_iphone(): 
    i = 0 
    print("[INFO] locspeed from iPhone ready")
    gp.locspdReady = True
    gp.update_allReady()
    while True: 
        f = open(loc_file_path, 'r')
        for line in f.readlines(): 
            [gp.lat, gp.lon] = line.split(',')
        print(gp.lat, gp.lon)
        gen_nowSpeed(i)
        i += 1
        time.sleep(gp.DELTA)


# method 3: get loc from route file 
def get_from_route(): 
    i = 0 
    home2uci_route_file = open('./home2uci_route.csv', 'r')
    print("[INFO] Route file ready")
    gp.locspdReady = True
    gp.update_allReady()
    for line in home2uci_route_file.readlines():
        [lat, lon] = line.strip('\n').split(',')
        [gp.lat, gp.lon] = [float(lat), float(lon)]
        gen_nowSpeed(i) 
        i = i+1
        gp.check_arriveDest() 
        # time.sleep(gp.DELTA)


if __name__=="__main__": 
    debug = 1 
    if debug == 1: 
        get_from_gps()
    elif debug == 2: 
        string = str(sys.argv[1]) + ',' + str(sys.argv[2])
        save_iphone_gps(string) 
    elif debug == 3: 
        get_from_route() 
    else: 
        print("debug = 1/2/3")



