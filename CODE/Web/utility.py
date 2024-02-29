from collections import Counter
from pymongo import MongoClient
from haversine import haversine

import numpy as np
import s2sphere
import s2cell
import pickle
import zlib
import re



########## Convert Form input into Json format ##########
def input_parser(form):
    data = {}
    # date time from user input
    s_date, s_hour, e_date, e_hour = form['start_date'], form['start_hour'], form['end_date'], form['end_hour']
    s_date = s_date.split('-')
    e_date = e_date.split('-')
    
    if 'trie_type' in form.keys():
        data['trie_type'] = form['trie_type']
        
    # form : [YY, MM, DD, HH, YY, MM, DD, HH]
    data['time'] = [int(s_date[0][2:]), int(s_date[1]), int(s_date[2]), int(s_hour),
                  int(e_date[0][2:]), int(e_date[1]), int(e_date[2]), int(e_hour)]
    # k value for k-NN, Top-k query
    if 'k' in form.keys():
        data['k'] = int(form['k'])
    if 'method' in form.keys():
        data['method'] = form['method']
    # Trajectory distance metrics
    if 'distanceMetrics' in form.keys():
        data['distanceMetrics'] = form['distanceMetrics']
    # area type check
    if 'type' in form.keys():
        if form['type'] == 'CIRCLE':
            data['type'] = 0
            # form of points: (lat, lng), radius
            point = list(map(float, re.findall(r'[-*0-9.0-9]+',form['points'])))

            data['coordinates'] = point[:2]
            # the unit of radius is 'km'
            data['radius'] = point[-1] / 1000

        elif form['type'] == 'RECTANGLE':
            data['type'] = 1
            data['coordinates'] = list(map(float, re.findall(r'[-*0-9.0-9]+', form['points'])))

        elif form['type'] == 'POLYGON':
            data['type'] = 2
            data['coordinates'] = list(map(float, re.findall(r'[-*0-9.0-9]+', form['points'])))


    return data



########## Return center coordinate of S2 cell ##########
def get_center_tuple(cell_id):
    cent_point = s2sphere.Cell(s2sphere.CellId(cell_id)).get_center()
    cor = s2sphere.LatLng(0, 0).from_point(cent_point)
    split_cor = str(cor).split(' ')[1].split(',')
    split_float = list(map(float, split_cor))
    tuple_cor = tuple(split_float)

    return tuple_cor



########## Trajectory Similarity Metrics 
def sliding_euclidean_distance(T1, T2):
    """
    Compute the Euclidean distance between two trajectories using a sliding window approach.

    Reference:
    A survey of trajectory distance measures and performance evaluation (VLDB'20)

    Parameters:
    T1 (list of tuples): Trajectory 1, where each tuple is a point (e.g., (x, y)).
    T2 (list of tuples): Trajectory 2, where each tuple is a point (e.g., (x, y)).

    Returns:
    float: The minimum average Euclidean distance between the trajectories over all window positions.
    """
    n = len(T1)
    m = len(T2)

    # Ensure that n <= m
    if n > m:
        temp = T2
        T2 = T1
        T1 = temp

    min_distance = float('inf')

    # Slide the window of size n over T2
    for j in range(m - n + 1):
        distance_sum = 0
        for i in range(n):
            distance_sum += np.linalg.norm(np.array(T1[i]) - np.array(T2[i + j]))
        average_distance = distance_sum / n
        min_distance = min(min_distance, average_distance)

    return min_distance


def dtw_distance(T1, T2):
    """
    Compute the Dynamic Time Warping (DTW) distance between two trajectories.

    Reference:
    A survey of trajectory distance measures and performance evaluation (VLDB'20)

    Parameters:
    T1 (list of tuples): Trajectory 1, where each tuple represents a point (e.g., (x, y)).
    T2 (list of tuples): Trajectory 2, where each tuple represents a point (e.g., (x, y)).

    Returns:
    float: The DTW distance between the two trajectories.
    """
    n, m = len(T1), len(T2)
    dtw_matrix = np.full((n+1, m+1), np.inf)
    dtw_matrix[0, 0] = 0

    for i in range(1, n+1):
        for j in range(1, m+1):
            cost = np.linalg.norm(np.array(T1[i-1]) - np.array(T2[j-1]))
            dtw_matrix[i, j] = cost + min(dtw_matrix[i-1, j],    # Insertion
                                          dtw_matrix[i, j-1],    # Deletion
                                          dtw_matrix[i-1, j-1])  # Match

    return dtw_matrix[n, m]


def lcss(T1, T2, eps):
    """
    Compute the LCSS (Longest Common Subsequence) distance between two trajectories using the Haversine distance.

    Parameters:
    t1 (list of tuples): Trajectory 1, where each tuple represents a geographic point (latitude, longitude).
    t2 (list of tuples): Trajectory 2, where each tuple represents a geographic point (latitude, longitude).

    Returns:
    float: The LCSS distance between the two trajectories.
    """
    n, m = len(T1), len(T2)

    if n == 0 or m == 0:
        return 0
    elif haversine(T1[0], T2[0]) <= eps:
        return lcss(T1[1:], T2[1:], eps) + 1
    else:
        return max(lcss(T1, T2[1:], eps), lcss(T1[1:], T2, eps))
    

# LCSS distance simply counts the number of match pairs between T1 and T2
# We consider the larger normalize distance_lcss then both T1 and T2 are similar
def distance_lcss(t1, t2, eps):
    return 1- (lcss(t1, t2, eps) / (len(t1) + len(t2) - lcss(t1, t2, eps)))



########## Visualization ##########
# Extract S2 cell corner coordinates
def extractCoordinate(keyType, s2cell_id, level=0):

    center_lat, center_lon = s2cell.cell_id_to_lat_lon(s2cell_id)
    s2cell_id = s2sphere.CellId.from_lat_lng(s2sphere.LatLng.from_degrees(center_lat,center_lon)).parent(level)
    
    vertices = [s2sphere.LatLng.from_point(s2sphere.Cell(s2cell_id).get_vertex(i)) for i in range(4)]
    vertices.append(s2sphere.LatLng.from_point(s2sphere.Cell(s2cell_id).get_vertex(0)))
    polygon = [[[v.lng().degrees, v.lat().degrees] for v in vertices]]
    

    return polygon


# Point visualization (ST-Trie and TS-Trie)
def s2CellPointJson(keyType, indexKey, query_data):

    res = 'var s2cell = [\n'
    if keyType == 'stc':
        check_leadingBit = s2cell.lat_lon_to_cell_id((query_data['coordinates'][0]+query_data['coordinates'][2])/2, (query_data['coordinates'][1]+query_data['coordinates'][3])/2, 20)
        if (check_leadingBit & (1 << 63)) != 0: # If leading bit is 1, then we should change from 1 to 0 because MongoDB cannot save the number which bigger than 1000 ... 00 (64 bits)
            indexKey = np.array(indexKey, dtype=np.uint64) + 9223372036854775808

        indexKey = np.right_shift(indexKey, 20)
        indexKey = np.left_shift(indexKey, 20) # Extract S2 Cell ID
        indexKey = set(indexKey)
        for cellID in indexKey:
            cellID = cellID.item()
            geo_dict = {"type":"Feature", "properties": {"status": "retrieved"}, "geometry": {"type": "Polygon"}}
            geo_dict["geometry"]["coordinates"] = extractCoordinate(keyType, cellID, 20)
            res = res + '     ' + str(geo_dict) + ",\n"
    else: # tsc
        new_indexKey = {}
        new_indexKey['TSC_ID'] = indexKey['TSC_ID']
        new_indexKey['TSC_ID'] = np.bitwise_and(new_indexKey['TSC_ID'], (1 << 44) - 1)
        new_indexKey['TSC_ID'] = np.left_shift(new_indexKey['TSC_ID'], 20) # Extract S2 Cell ID
        new_indexKey['level'] = []
        for iter, _ in enumerate(indexKey['level']):
            new_indexKey['level'].extend([indexKey['level'][iter]]*indexKey['length'][iter])
            
        paired_elements = set(zip(new_indexKey['TSC_ID'], new_indexKey['level']))
        id_level_pair = list(paired_elements)

        for cellID, level in id_level_pair:
            cellID = cellID.item()
            geo_dict = {"type":"Feature", "properties": {"status": "retrieved"}, "geometry": {"type": "Polygon"}}
            geo_dict["geometry"]["coordinates"] = extractCoordinate(keyType, cellID, level)
            res = res + '     ' + str(geo_dict) + ",\n"
                

    # Retrieved space
    left_bottom = [query_data['coordinates'][1], query_data['coordinates'][0]]
    left_upper = [query_data['coordinates'][3], query_data['coordinates'][0]]
    right_bottom = [query_data['coordinates'][1], query_data['coordinates'][2]]
    right_upper = [query_data['coordinates'][3], query_data['coordinates'][2]]

    querying_space = {"type":"Feature", "properties": {"status": "querying"}, "geometry": {"type": "Polygon"}}
    
    if query_data['type'] == 1: # Rectangle
        querying_space['geometry']['coordinates'] = [[left_upper, left_bottom, right_bottom, right_upper, left_upper]]

    res = res + '     ' + str(querying_space) + "\n"
    res = res + '\n];'

    return res


# Trajectory visualization
def s2CellTrajJson(retrived_data, query_data):

    res = 'var s2cell = [\n'
    
    for _, trajectory in retrived_data.items():
        geo_dict = {"type":"Feature", "properties": {"status": "retrieved"}, "geometry": {"type": "LineString"}}

        compressed_coor = trajectory['location']['coordinates']
        decompressed_coor = pickle.loads(zlib.decompress(compressed_coor))

        points = []
        for point in decompressed_coor:
            points.append([point['lon'], point['lat']])
    
        geo_dict["geometry"]["coordinates"] = points
        res = res + '     ' + str(geo_dict) + ",\n"


    # Retrieved space
    left_bottom = [query_data['coordinates'][1], query_data['coordinates'][0]]
    left_upper = [query_data['coordinates'][3], query_data['coordinates'][0]]
    right_bottom = [query_data['coordinates'][1], query_data['coordinates'][2]]
    right_upper = [query_data['coordinates'][3], query_data['coordinates'][2]]

    querying_space = {"type":"Feature", "properties": {"status": "querying"}, "geometry": {"type": "Polygon"}}
    
    if query_data['type'] == 1: # Rectangle
        querying_space['geometry']['coordinates'] = [[left_upper, left_bottom, right_bottom, right_upper, left_upper]]

    res = res + '     ' + str(querying_space) + "\n"
    res = res + '\n];'

    return res


# Make a.js file forS2Cell Map Visualization
def S2CellMapJS(keyType, indexKey, query_data, data_type="Point", retrived_data=None):

    view_center_lat = (query_data['coordinates'][0] + query_data['coordinates'][2]) / 2
    view_center_lon = (query_data['coordinates'][1] + query_data['coordinates'][3]) / 2

    javascript_code = f"""
    // We use the leaflet library
    var map = L.map('map').setView([{view_center_lat}, {view_center_lon}], 13); """
    
    javascript_code = javascript_code + """
    var coordinate_meta;

    // Open street map tile
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    """
    if data_type == 'Point':
        s2cellGeo = s2CellPointJson(keyType, indexKey, query_data)
    elif data_type == 'Trajectory':
        s2cellGeo = s2CellTrajJson(retrived_data, query_data)
        

    javascript_code = javascript_code + s2cellGeo
    javascript_code = javascript_code + """

    L.geoJSON(s2cell, {
        style: function(feature) {
            switch (feature.properties.status) {
                case 'querying': return {color: "#ff0000"};  // Entire querying space
                case 'retrieved': return {color: "#0000ff"}; // retrived space
            }
        }
    }).addTo(map);
    """

    # Write the JavaScript code to a file
    with open('./static/result_map.js', 'w') as js_file:
        js_file.write(javascript_code)
    print("Generating Map is done!")