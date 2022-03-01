import os
import sys
sys.path.append(os.path.abspath('..'))
from Utils.Gcj02ToWgs84 import getwgs84
from DataClean.Cleaner import get_clean_data
import osmnx as ox
from leuvenmapmatching.map.inmem import InMemMap
import pandas as pd
from leuvenmapmatching.matcher.distance import DistanceMatcher
import numpy as np



def get_graph(path):
    '''
    获取路网数据
    :param path:
    :return:graph, data
    '''
    data = getwgs84(path)
    data.to_csv('../data/data_84.csv')
    print('原始数据长度 = ' + str(len(data)))
    data = get_clean_data(data)
    data.to_csv('../data/data_clean.csv')
    print('清洗后数据长度 = ' + str(len(data)))
    track = np.array(list(zip(data['latitude'], data['longitude'])))
    lat = track[:, 0]
    lon = track[:, 1]
    graph = ox.graph_from_bbox(
        np.max(lat) + .001, np.min(lat) - 0.001,
        np.max(lon) + .001, np.min(lon) - 0.001,
        simplify=False,
        retain_all=True,
        network_type='all')
    return graph, data


def get_map_con(path):
    '''
    获取map_con对象
    :param path:
    :return:
    '''
    graph, data = get_graph(path)
    # Creation of the Leuven Map object from the OSM network
    map_con = InMemMap("myosm", use_latlon=True, use_rtree=True, index_edges=True)
    # Add the OSM network into the Leuven Map object
    nodes_id = list(graph.nodes)
    for node in nodes_id:
        lat = graph.nodes[node]['y']
        lon = graph.nodes[node]['x']
        map_con.add_node(node, (lat, lon))
    edges_id = list(graph.edges)
    for edge in edges_id:
        node_a, node_b = edge[0], edge[1]
        map_con.add_edge(node_a, node_b)
        map_con.add_edge(node_b, node_a)
    return map_con, data

def get_proj_data(path):
    '''
    获取投影后的数据
    :param path:
    :return:
    '''
    map_con, data = get_map_con(path)
    track = list(zip(data['latitude'], data['longitude']))
    map_con.purge()
    matcher = DistanceMatcher(
        map_con,  # Map object to connect to map database
        max_dist=2000,  # 与路径的最大距离
        max_dist_init=500,  # Maximum distance from start location (if not given, uses max_dist)距起始位置的最大距离
        min_prob_norm=0.001,  # Minimum normalized probability of observations (ema)
        non_emitting_length_factor=0.95,  # 降低非发射状态序列
        obs_noise=100,  # Standard deviation of noise噪音的标准差，表示数学期望之间的偏离程度
        #   obs_noise_ne=100,  # Standard deviation of noise for non-emitting states#非发射状态的噪音标准差
        dist_noise=100,  # meter
        max_lattice_width=100,
        non_emitting_edgeid=True
    )
    matcher.match(track)
    print("映射后的数据长度" + str(len(matcher.path_pred_onlynodes)))
    lat_corr, lon_corr, stime = [], [], []
    lat_nodes = matcher.lattice_best
    for idx, m in enumerate(lat_nodes):
        lat, lon = m.edge_m.pi[:2]
        my_index = m.edge_m.my_index
        lat_corr.append(lat)
        lon_corr.append(lon)
        stime.append(data['time'][my_index])

    proj_node = list(zip(lat_corr, lon_corr, stime))
    proj_data = pd.DataFrame(proj_node, columns=['latitude', 'longitude', 'time'])
    return proj_data


def write_tack(path):
    '''
    保存输出数据data_time.csv和json.js中
    :param path:
    :return:
    '''
    proj_data = get_proj_data(path)
    # proj_data = get_clean_data(proj_data)
    proj_data.to_csv('../data/2022-02-07鲸云纠正数据_time.csv')
    z = proj_data[['longitude','latitude']].values
    with open(r"D:\学习\论文\交通路网拟合\轨迹地图\轨迹\json.js", 'w+', encoding='utf-8') as f:
        f.write('var data3 = [')
        for row in z:
            f.write(str('[' + str(row[0]) + ',' + str(row[1]) + ']') + ",")
        f.write(']')

# path = r'D:\学习\论文\交通路网拟合\轨迹数据\轨迹数据\2022-01-30鲸云纠正数据.txt'
path = r'D:\学习\论文\交通路网拟合\轨迹数据\轨迹数据\2022-02-07鲸云纠正数据.txt'
# path = r'D:\学习\论文\交通路网拟合\轨迹数据\轨迹数据\郭鑫02-14鲸云.txt'
# path = r'D:\学习\论文\交通路网拟合\轨迹数据\轨迹数据\李岩02-19鲸云.txt'
# path = r'D:\学习\论文\交通路网拟合\轨迹数据\轨迹数据\李岩02-19.txt'

write_tack(path)




