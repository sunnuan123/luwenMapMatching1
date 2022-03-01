import os
import sys

import pandas as pd

sys.path.append(os.path.abspath('..'))
from Utils.Gcj02ToWgs84 import getwgs84
from DataClean.Cleaner import get_clean_data
import matplotlib.pyplot as plt
import osmnx as ox
from leuvenmapmatching.map.inmem import InMemMap
from leuvenmapmatching.matcher.distance import DistanceMatcher
import numpy as np
from leuvenmapmatching import visualization as mmviz


def get_graph(path):
    '''
    获取路网数据
    :param path:
    :return:graph, data
    '''
    data = getwgs84(path)
    data.to_csv('../data/raw_84.csv')
    print('原始数据长度 = ' + str(len(data)))
    data = get_clean_data(data)
    print('清洗后数据长度 = ' + str(len(data)))
    track = np.array(list(zip(data['latitude'], data['longitude'], data['time'])))
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

def get_matcher(path):
    '''
    获取投影后的数据
    :param path:
    :return:
    '''
    map_con, data = get_map_con(path)
    # track = list(zip(data['latitude'], data['longitude'], data['time']))
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
    states, _ = matcher.match(track)
    pd.DataFrame(states).to_csv("../data/states.csv")
    nodes = matcher.path_pred_onlynodes
    pd.DataFrame(nodes).to_csv("../data/nodes.csv")
    print("映射后的数据长度" + str(len(nodes)))
    return matcher, map_con


def get_pic(map_con, matcher):
    mmviz.plot_map(map_con, matcher=matcher,
                   show_labels=True, show_matching=True, show_graph=False)
    plt.show()
path = r'D:\学习\论文\交通路网拟合\轨迹数据\轨迹数据\李岩02-19鲸云.txt'
matcher, map_con = get_matcher(path)
get_pic(map_con, matcher)



