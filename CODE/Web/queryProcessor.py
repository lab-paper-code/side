from bson.objectid import ObjectId
from haversine import haversine
from pymongo import MongoClient
from requests import post
from time import time

import s2sphere as s2
import pandas as pd
import numpy as np
import operator
import utility
import pickle
import zlib
import json
import re
import os

# User defined Library
import utility




########## MongoDB Access ##########
# Make config file path
def read_config(filename):
    config = {}
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                key, value = map(str.strip, line.split('='))
                config[key] = value
    except FileNotFoundError:
        print(f"Cannot find '{filename}'")
    except Exception as e:
        print(f"Error occur during reading a file: {e}")

    return config


# Read Configuration file
config_directory = os.path.dirname(os.path.realpath(__file__))
config_directory = config_directory.split("/")

conf_path = ""

for i, c in enumerate(config_directory):
    if i != 0:
        if c == "Web":
            conf_path += ("/index/")
        else:
            conf_path += ("/" + c)

conf_path = conf_path + 'config.txt'
config_data = read_config(conf_path)

if config_data:
    ID = config_data.get('ID', '')
    PW = config_data.get('PW', '')
    Index_IP = config_data.get('Index_IP', '')
    Web_IP = config_data.get('Web_IP', '')
    MongoDB_IP = config_data.get('MongoDB_IP', '')
    DB_name = config_data.get('DB_name', '')
    Index_name = config_data.get('Index_name', '')

# Connect to MongoDB
client = MongoClient(MongoDB_IP)
db = client[DB_name]
city_col = db[Index_name]



# Find IoT data from mongodb using matched STC_ID
def find_mongo_stc(stc_list):
    '''
    :param stc_list: list of STC_ID
    :return: list of mongoDB objects matching STC_ID
    '''
    result=[]
    st_len=len(stc_list)
    size = 100000
    num = int(st_len/size)
    for i in range(num+1):
        if i<num:
            query={"STC_ID":{'$in':stc_list[i*size:(i+1)*size]}}
        else:
            query={"STC_ID":{'$in':stc_list[i*size:st_len]}}
        #print(query)
        val=city_col.find(query)
        result.extend(list(val))

    return result


# Find IoT data from mongodb using matched TSC_ID
def find_mongo_tsc(tsc_list):
    '''
    :param tsc_list: dic of TSC info
    :return: list of mongoDB objects matching TSC_ID
    '''
    result=[]
    prior_len = 0
    
    for level, length in zip(tsc_list['level'], tsc_list['length']):
        mongo_tsc_list = tsc_list['TSC_ID'][prior_len:prior_len+length]
        prior_len = prior_len + length

        query_list = []
        if level != 20:
            rest_bit = 44 - (2 * level + 4)
                        
            for tsc_id in mongo_tsc_list:
                pre_tsc_id = ((tsc_id >> rest_bit) - 1) << rest_bit
                post_tsc_id = ((tsc_id >> rest_bit) + 1) << rest_bit

                query = { # MongoDB query
                    "TSC_ID": {"$gte": pre_tsc_id, "$lte": post_tsc_id}
                }
    
                query_list.append(query)
            
            query_all = {"$or" : query_list}
            val=city_col.find(query_all)
            result.extend(list(val))


        else:
            query={"TSC_ID":{'$in':mongo_tsc_list}}
            val=city_col.find(query)
            result.extend(list(val))


    return result
    

# Get web input, parsing and hand over parsed data to index server (in STC)
def get_stc_from_index(query_data):
    '''
    :param
    request: {
        'type' : 0 == circle, 1 == rectangle, 2 == polygon
        'coordinates': [lat, lng, lat, lng, ... ]
        'radius': float (unit: km) if type == 0
        'time': [YY, MM, DD, HH, YY, MM, DD, HH] (start, end)
    }
    :return:
        list of stpt included in spatio-temporal range
    '''
    # parsing
    request=dict()
    request['type'] = query_data['type']
    request['coordinates'] = query_data['coordinates']
    request['time'] = query_data['time']
    if request['type'] == 0:
        request['radius'] = query_data['radius']

    # hand over data to index server
    header = {'Content-Type': 'application/json; charset=utf-8'}
    url = 'http://155.230.35.233:50505'
    try:
        res = post(url, headers=header, data=json.dumps(request),timeout=6000)
        print('res len : ', len(res.json()['STC_ID']))
    except ConnectionError as e:
        print("Connection Error: ", e)
        return []
    
    return res.json()['STC_ID']
    

# Get web input, parsing and hand over parsed data to index server (in TSC)
def get_tsc_from_index(query_data):
    '''
    :param
    request: {
        'type' : 0 == circle, 1 == rectangle, 2 == polygon
        'coordinates': [lat, lng, lat, lng, ... ]
        'radius': float (unit: km) if type == 0
        'time': [YY, MM, DD, HH, YY, MM, DD, HH] (start, end)
    }
    :return:
        list of stpt included in spatio-temporal range
    '''

    # parsing
    request=dict()
    request['type'] = query_data['type']
    request['coordinates'] = query_data['coordinates']
    request['time'] = query_data['time']
    if request['type'] == 0:
        request['radius'] = query_data['radius']

    # hand over data to index server
    header = {'Content-Type': 'application/json; charset=utf-8'}
    url = 'http://155.230.35.233:50505'
    try:
        res = post(url, headers=header, data=json.dumps(request),timeout=6000)
        print('res len : ', len(res.json()['TSC_ID']))
    except ConnectionError as e:
        print("Connection Error: ", e)
        return []
    return res.json()



########## Query Processing ##########
# determine ST or TS from input data from web
def range_query(query_data, index=None):

    if query_data['trie_type'] == 'ST':
        idx = get_stc_from_index(query_data) # stc
        res = find_mongo_stc(idx)
    else:
        idx = get_tsc_from_index(query_data) # tsc
        res = find_mongo_tsc(idx)

    return res


# [Point] - k-NN
def knn_query(query_data):
    dis_dic = {}
    result = []

    center_cor = tuple(query_data['coordinates'])
    k = query_data['k']
    
    # Extract a dictionary of distances between the coordinates in the index_list and the querying range midpoint coordinates.
    if query_data['trie_type'] == 'ST': # ST-Trie
        # get index key(stc)
        index_list = get_stc_from_index(query_data)
        
        for index, stc in enumerate(index_list):
            cellid = stc >> 20
            cellid = cellid << 20
            tuple_cor = utility.get_center_tuple(cellid)  # Extract the midpoint of s2 cell
            distance = haversine(center_cor, tuple_cor, unit='km')  # calcuate herversine
            dis_dic[index] = distance
        # Sorting ascending order
        sdict = sorted(dis_dic.items(), key=operator.itemgetter(1))
        result_stc_list = []
        
        for dic in sdict[:k]:
            result_stc_list.append(index_list[dic[0]])
        
        results = find_mongo_stc(result_stc_list)
        result_dist = {}
        for index, _ in enumerate(results):
            tuple_cor = results[index]['location']['coordinates']
            tuple_cor = (tuple_cor[1], tuple_cor[0])
            distance = haversine(center_cor, tuple_cor, unit='km')  # calcuate herversine
            result_dist[index] = distance
        # Sorting ascending order
        result_dist = sorted(result_dist.items(), key=operator.itemgetter(1))

        for dic in result_dist[:k]:
            result.append(results[dic[0]])

    else: # TS-Trie
        # get index key(tsc)
        index_list = get_tsc_from_index(query_data)
        s2_len_info = index_list['length']

        if sum(s2_len_info) < k:
            print("There is no more than k sensor in your range query!")
            k = sum(s2_len_info)

        
        # Calculate accumulate lengths
        s2_accum_info = [s2_len_info[0]]
        for i in range(1, len(s2_len_info)):
            accumlate = s2_accum_info[i-1] + s2_len_info[i]
            s2_accum_info.append(accumlate)
        
        max_index = -1
        for index, acc_val in enumerate(s2_accum_info):
            if acc_val >= k:
                max_index = index
                break

        new_tsc_list = {}
        new_tsc_list['length'] = index_list['length'][:max_index+1]
        new_tsc_list['level'] = index_list['level'][:max_index+1]

        sum_of_len = sum(new_tsc_list['length'])
        new_tsc_list['TSC_ID'] = index_list['TSC_ID'][:sum_of_len]
    

        # start_querying
        results = find_mongo_tsc(new_tsc_list)
        result_dist = {}
        for index, _ in enumerate(results):
            tuple_cor = results[index]['location']['coordinates']
            tuple_cor = (tuple_cor[1], tuple_cor[0])
            distance = haversine(center_cor, tuple_cor, unit='km')  # calcuate herversine
            result_dist[index] = distance
        # Sorting ascending order
        result_dist = sorted(result_dist.items(), key=operator.itemgetter(1))

        for dic in result_dist[:k]:
            result.append(results[dic[0]])


    return result


# [Point] - Top-k
def topk_query(query_data):
    records = range_query(query_data)

    k = query_data['k']
    # True: Descending, False: Ascending
    method = True
    if query_data['method'] == 'max':
        pass
    elif query_data['method'] == 'min':
        method = False

    records = sorted(records, key=lambda x: x['location']['coordinates'][0], reverse=method)
    res = records[:k]

    return records, res


# [Trajectory] - Spatio-temporal range
def trajectory_range_query(query_data):
    records = range_query(query_data)
    trajectories = dict()

    if len(records) != 0:
        for document in records: # If it is not a trajectory that has been found, add it to the dictionary of trajectories
            if document['Trajectory_ID'] not in trajectories.keys():
                trajectories[document['Trajectory_ID']] = document
    else: # Problem occur
        return None

    return trajectories


# [Trajectory] - Similarity
def trajectory_similarity_query(query_data, query_traj):
    # First, perform a spatiotemporal range query on the trajectory
    # Convert each pair to a tuple of floats
    coord_pairs = query_traj.replace(" ", "").split("),")
    query_traj = [tuple(map(float, pair.replace("(", "").replace(")", "").split(","))) for pair in coord_pairs]
    k = query_data['k']
    distance_type = query_data['distanceMetrics']

    # Execute spatio-temporal range query
    retrived_data = trajectory_range_query(query_data)

    metrics = dict()
    for _, trajectory in retrived_data.items():
        traj_id = trajectory['Trajectory_ID']
        compressed_coor = trajectory['location']['coordinates']
        decompressed_coor = pickle.loads(zlib.decompress(compressed_coor))

        points = [] # points of one trajectory
        for point in decompressed_coor:
            points.append((point['lat'], point['lon']))

        # Trajectory similarity metrics
        if distance_type == 'euclidean': # len(m - n + 1) * len(n) * len(retrived_data) ~ n <= m
            metrics[traj_id] = utility.sliding_euclidean_distance(query_traj, points)
        elif distance_type == 'dtw':
            metrics[traj_id] = utility.dtw_distance(query_traj, points)
        elif distance_type == 'lcss':
            metrics[traj_id] = utility.distance_lcss(query_traj, points, 0.5)
        else:
            raise ValueError("We do not support", distance_type, "type query.")

    # Sorted by metrics value
    sorted_metrics_keys = sorted(metrics, key=metrics.get)[:k]

    # Return result documents
    res = dict()
    for key in sorted_metrics_keys:
        res[key] = retrived_data[key]


    return res




if __name__ == '__main__':
    print('mongodb connector')