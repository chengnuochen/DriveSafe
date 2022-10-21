from datetime import datetime as dt 
import os 

import global_params as gp

ext = '.csv'

def create_record(): # every trip create a top directory to store the data 
    gp.fname = dt.now().strftime('%Y-%m-%d_%H-%M-%S')
    gp.DATA_PATH = gp.DATA_PATH + gp.fname + "/"
    os.mkdir(gp.DATA_PATH, mode=0o755, dir_fd=None)

    # f_rec_top is the top table of the records 
    gp.rec_top = gp.DATA_PATH + gp.fname + ext
    top = open(gp.rec_top, 'w')
    top.write('number,behavior_type,start_time,end_time,duration,route\n')
    top.close() 
    

def write_record(entryName, behavior_type, startTime, endTime, duration, route):
    rec_entry = gp.DATA_PATH + entryName

    entry = open(rec_entry + ext, 'w')
    if (behavior_type == "speed"):
        entry.write('time,latitude,longitude,road_name,nowSpeed,maxSpeed\n')
        for pt in route: 
            entry.write(str(pt[0]) + ',' + str(pt[1]) + ',' + str(pt[2]) + ',' + str(pt[3]) + ',' + str(pt[4]) + ',' + str(pt[5]) + '\n')
    else: 
        entry.write('time,latitude,longitude,road_name\n')
        for pt in route: 
            entry.write(str(pt[0]) + ',' + str(pt[1]) + ',' + str(pt[2]) + ',' + str(pt[3]) + '\n')
    entry.close() 

    top = open(gp.rec_top, 'a')
    record = str(gp.rec_num) + "," + behavior_type + "," + startTime + "," + endTime + "," + duration + "," + rec_entry + "\n"
    top.write(record)
    top.close()

    print('Write a new record:', entryName)


if __name__=="__main__": 
    create_record() 
    # write_record("speeding", "2021-11-11 20:10:02", "2021-11-11 20:11:02", "00:01:00", [[1,2],[3,4],[5,6]])

