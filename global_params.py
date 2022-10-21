# global fname, datapath, projpath, rec_num 
# global latitude, longitude 
# global nowSpeed, maxSpeed 

import os 
import time 
from datetime import datetime as dt 
import pyrebase

DEST_LAT = 33.7175098
DEST_LON = -117.748628

DELTA = 0.5 # time interval of each operation 

locspdReady = False # locspdReady means the lat/lon and speed data ready
cameraReady = False
networkReady = False # TODO try to know how to test network status  
allReady = False 

PROJ_PATH = '/home/pi/drive_safe/'
DATA_PATH = '/home/pi/drive_safe/data/'
fname = ''
rec_top = ''
# rec_entry = ''
rec_num = 0

tripStartTime = dt.now() 
lat = 0
lon = 0
road_name = ''

nowSpeed = 0 # set a initial value 
maxSpeed = 10 # initial maxspeed is 10 mph 

dozeFlag = False 
yawnFlag = False 
spdFlag = False 

arriveDest = False 

DOZE_WARN = 'dozing!'
YAWN_WARN = 'yawning!'
SPD_WARN = 'speeding!'

# Firebase config
config = {
    "apiKey": "XzM90nMlLSdkeA5WWnsxvMzDEjatnEa90Cxyr7pk",
    "authDomain": "drivesaferpi.firebaseapp.com",
    "databaseURL": "https://drivesaferpi-default-rtdb.firebaseio.com/",
    "storageBucket": "drivesaferpi.appspot.com"
}

def check_arriveDest(): 
    global arriveDest
    if abs(lat-DEST_LAT)<0.0001 and abs(lon-DEST_LON)<0.0001:
        arriveDest = True 
    

def update_allReady(): 
    global allReady, locspdReady, cameraReady
    allReady = (locspdReady and cameraReady)

def check_allReady(): 
    while True: 
        if allReady:
            tripStartTime = dt.now()
            break 

def warning(): 
    check_allReady()

    while not arriveDest: 
        
        if dozeFlag:
            os.system('espeak "{0}"'.format(DOZE_WARN))   
            print("DANGEROUS!")
            print("[WANRING] " + DOZE_WARN)
        if yawnFlag: 
            os.system('espeak "{0}"'.format(YAWN_WARN))   
            print("DANGEROUS!")
            print("[WANRING] " + YAWN_WARN)
        if spdFlag: 
            os.system('espeak "{0}"'.format(SPD_WARN))
            print("DANGEROUS!")
            print("[WANRING] " + SPD_WARN)
        # time.sleep(0.1)

    

def print_status(): 
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
    print("[INFO] firebase connection ready")    
    check_allReady()
    # init firebase connection 
    while not arriveDest: 
        os.system('clear')
        print("Current Status Dashboard")
        print("[TIME] {0}".format(dt.now().strftime('%Y-%m-%d %H:%M:%S')))
        print("[GPS ] lat,lon = [{0},{1}]; road_name = {2}".format(lat, lon, road_name))
        print("[SPED] now = {0}; max = {1}".format(nowSpeed, maxSpeed))
        print("[FLAG] dozeFlag = {0}; yawnFlag = {1}; speedFlag = {2}".format(dozeFlag, yawnFlag, spdFlag))
        print("Dangerous behavior count: {0}".format(rec_num))
        print("Destination: [{0},{1}]; if arrived: {2}".format(DEST_LAT, DEST_LON, arriveDest))
        print() 
        # warning()
        # upload to firebase 
        data = {
            "lat": lat,
            "lon": lon,
            "road_name": road_name, 
            "nowSpeed": nowSpeed,
            "maxSpeed": maxSpeed,
            "dozeFlag": dozeFlag,
            "yawnFlag": yawnFlag,
            "spdFlag": spdFlag,
            "risky behavior count": rec_num,
            "DEST_LAT": DEST_LAT,
            "DEST_LON": DEST_LON,
        }
        db.child("dashboard").set(data)

        time.sleep(0.25)
