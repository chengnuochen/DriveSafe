from datetime import datetime as dt 
import req_osm 
import record as rec 
import global_params as gp 
import time 



def check_spd(now, max): 
    if now > max: 
        # print('nowSpeed = ' + str(now) + ' > ' + 'maxSpeed = ' +str(max))
        return True 
    else: 
        # print('nowSpeed = ' + str(now) + ' <= ' + 'maxSpeed = ' +str(max))
        return False 

def monitor_speeding(): 
    # spdFlag = False # initially not speeding 
    spdSttTime = 0 
    spdRoute = [] 
    spdEntryName = ''
    while True:
        if gp.allReady:
            break   
    while not gp.arriveDest: 
        [name, max] = req_osm.get_maxspeed(gp.lat, gp.lon)
        if max != -1: 
            gp.maxSpeed = max 
        if name is not '':
            gp.road_name = name
        if (gp.spdFlag is not check_spd(gp.nowSpeed, gp.maxSpeed)):
            if(gp.spdFlag == False): # speeding on 
                gp.spdFlag = True 
                spdSttTime = dt.now() # speeding start time  
                gp.rec_num += 1
                spdEntryName = "{0}__{1}_speed".format(gp.fname, gp.rec_num)
                spdRoute.append([spdSttTime.strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon, gp.road_name, gp.nowSpeed, gp.maxSpeed])
            else: # speeding off 
                spdEndTime = dt.now() 
                spdDurTime = spdEndTime - spdSttTime
                spdSttStr = spdSttTime.strftime('%Y-%m-%d %H:%M:%S')
                spdEndStr = spdEndTime.strftime('%Y-%m-%d %H:%M:%S')
                spdRoute.append([spdEndTime.strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon, gp.road_name, gp.nowSpeed, gp.maxSpeed])
                rec.write_record(spdEntryName, behavior_type="speed", startTime=spdSttStr, endTime=spdEndStr, duration=str(spdDurTime), route=spdRoute)
                spdRoute = [] 
                gp.spdFlag = False 
        else: 
            if(gp.spdFlag == True): 
                spdRoute.append([dt.now().strftime('%Y-%m-%d %H:%M:%S.%f'), gp.lat, gp.lon, gp.road_name, gp.nowSpeed, gp.maxSpeed])
        time.sleep(gp.DELTA)


if __name__=="__main__": 
    rec.create_record() 
    monitor_speeding() 

            