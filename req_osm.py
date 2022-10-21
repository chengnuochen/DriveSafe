import random
from overpy import Element 
import requests as req
import global_params as gp


def check_key_exist(dict, key): 
    try: 
        value = dict[key]
        return True
    except KeyError:
        return False 


def get_bbox(city='Irvine', state='ca', country='usa'): 
    """
    returns a bbox of a certain area (bbox of Irvine, CA by default) \\
    bbox is the bounding box arranged in [minLat, maxLat, minLon, maxLon] order \\
    user can pass different parameters to get wanted bbox 
    """
    req_params = {'city':city, 'state':state, 'country':country, 'format':'jsonv2'}
    url = 'https://nominatim.openstreetmap.org/search.php'
    out = req.get(url, params=req_params)
    js = out.json()
    return (js[0])['boundingbox'] # a list with 4 strings 

def gen_rand_loc(bbox): 
    """
    return the [lat,lon] of a random location within the bbox \\
    Eg: generate a random location on the world: gen_rand_loc([-90, 90, -180, 180])
    """
    minLat = float(bbox[0]) 
    maxLat = float(bbox[1])
    minLon = float(bbox[2])
    maxLon = float(bbox[3])
    latRange = maxLat - minLat
    latMid = (maxLat+minLat) / 2
    lonRange = maxLon - minLon
    lonMid = (maxLon+minLon) / 2
    lat = random.random()*latRange - latRange/2 + latMid
    lon = random.random()*lonRange - lonRange/2 + lonMid
    return [lat, lon]

    
def get_osm_id(lat, lon):
    """
    return the osm_id according to the given [lat,lon]
    """
    osm_type = ''
    osm_id = 0
    req_params = {'lat':lat, 'lon':lon, 'zoom':18,'format':'jsonv2'}
    # req_params = {'format':'json', 'lat':MYLAT, 'lon':MYLON, 'zoom':18}
    # req_params = {'format':'json', 'lat':lat, 'lon':lon, 'zoom':18}
    url = 'https://nominatim.openstreetmap.org/reverse.php'
    out = req.get(url, params=req_params)
    js = out.json()
    # print(js)
    if(check_key_exist(js, 'osm_type')):
        if(js['osm_type'] == 'way'):
            # print(out.url)
            # print(js)
            osm_type = js['osm_type']
            osm_id = js['osm_id']
            # print(osm_id)
    return osm_type, osm_id 


def get_roads_query(osm_type, osm_id):
    """
    return a "way" query for overpass API based on the osm_id (method 1); 
    need to get the osm_id first 
    """
    head = """[out:json][timeout:50];""" 
    body = osm_type + "(" + str(osm_id)
    tail = """);out;""" 
    built_query = head + body + tail
    # print(built_query)
    return built_query 

def get_way_around_query(lat, lon): 
    """
    return a "way around" query for overpass API based on the [lat,lon] (method 2)
    """
    radius = 20 # unit: meter 
    head = """[out:json][timeout:50];way[highway](around:""" 
    body =  str(radius) + "," + str(lat) + "," + str(lon)
    tail = """);out;""" 
    built_query = head + body + tail
    # print(built_query)
    return built_query 


def get_maxspeed(lat, lon):
    status_code = 999 
    url_overpass = 'http://overpass-api.de/api/interpreter'
    while (status_code >= 400):  # try again if client/server error
        # osm_id = 0 
        # osm_type = '' 
        # # osm_id = 173862443 
        # while(osm_id == 0 and (not osm_type == 'way')): 
        #     # [lat, lon] = gen_rand_loc(get_bbox())
        #     [osm_type, osm_id] = get_osm_id(lat, lon)
        # built_query = get_roads_query(osm_type, osm_id) # use osm_id 

        built_query = get_way_around_query(lat, lon) # use [lat,lon]
        
        out = req.get(url_overpass, params={'data':built_query})
        status_code = out.status_code
    # print(out.url)
    # print(out.content)
    js = out.json() # this json file is complex, not simply dict 
    
    road_name = ''
    maxspeed = -1 
    try: 
        e = (js['elements'])[0]
        # print(e)
        if(check_key_exist(e['tags'], 'name')): # 
            road_name = (e['tags'])['name']
        if(check_key_exist(e['tags'], 'maxspeed')): # if maxspeed exist, use this value 
            maxSpeedStr = ((e['tags'])['maxspeed']).split()
            # gp.maxSpeed = maxSpeedStr[0]
            # return int(maxSpeedStr[0])
            maxspeed = int(maxSpeedStr[0])
        elif(check_key_exist(e['tags'], 'highway')): # else if maxspeed not exist 
            way_type = (e['tags'])['highway']
            # refer to https://wiki.openstreetmap.org/wiki/Key:highway for different kinds of road (3.1.1) 
            # refer to https://en.wikipedia.org/wiki/Speed_limits_in_the_United_States for general speed limitation (see CA)
            if(way_type in ['motorway', 'trunk']): 
                # gp.maxSpeed = 65
                # return 65
                maxspeed = 65
            elif(way_type == 'residential'):
                # gp.maxSpeed = 25
                maxspeed = 25
            elif(way_type in ['primary', 'secondary', 'tertiary', 'unclassified']):
                # gp.maxSpeed = 55
                maxspeed = 55
            else: 
                print("highway type not specified")
                # maxspeed = None 
        else:
            print("not a highway")
            # maxspeed = None # use the current speed limit 
        return [road_name, maxspeed]
    except IndexError: # when use "way around" query, the js["elements"] may be empty 
        print('no way around found')
        return [road_name, maxspeed]
        


if __name__=="__main__": 
    # simulate the route from my home to UCI (route data in .csv)
    # fetch real-time max_speed 
    route_file = open('./home2uci_route.csv', 'r')
    for line in route_file.readlines():
        [lat, lon] = line.strip('\n').split(',')
        gp.maxSpeed = get_maxspeed(gp.lat, gp.lon)
        print('[lat, lon] = [' + lat + ',' + lon + '], current_max_speed = ' + gp.maxSpeed)

