from pyproj import Geod
import pandas as pd
import numpy as np
import math

def get_edges_nodes(data):
    '''
    获取边的节点
    :param data:
    :return:
    '''
    track = list(zip(data['latitude'], data['longitude']))
    n = len(track)
    nodes = pd.DataFrame()
    nodes['node1'] = track[:(n - 2)]
    nodes['node2'] = track[1:(n - 1)]
    nodes['node3'] = track[2:n]
    return nodes




def get_angle(data):
    '''
    根据获取的点求三角形边长和角度
    :param nodes:
    :return:
    '''
    nodes = get_edges_nodes(data)#获取三个点
    geod = Geod(ellps='WGS84')
    d = []
    for index, row in nodes.iterrows():
        _, _, edge12 =  geod.inv(row[0][1], row[0][0], row[1][1],row[1][0])
        _, _, edge23 =  geod.inv(row[1][1], row[1][0], row[2][1],row[2][0])
        _, _, edge13 =  geod.inv(row[0][1], row[0][0], row[2][1],row[2][0])
        d.append([edge12, edge23, edge13])
    distances = pd.DataFrame(d, columns=['d12', 'd23', 'd13'])
    distances['node2'] = nodes['node2']
    distances = distances[(distances['d12'] != 0) & (distances['d23'] != 0)]
    angs = []
    for index, row in distances.iterrows():
        z = (row[0] ** 2 + row[1] ** 2 - row[2] ** 2) / (2 * row[0] * row[1])
        ang = math.acos(round(z, 8)) * 180 / np.pi
        angs.append(ang)
    distances['angle'] = angs

    distances['latitude'] = distances['node2'].apply(lambda d: d[0])
    distances['longitude'] = distances['node2'].apply(lambda d: d[1])
    # 加上第一个经纬度点和最后一个经纬度点
    dist = distances.values.tolist()
    dist.insert(0, [np.nan, np.nan, np.nan, np.nan, np.nan, data['latitude'][0], data['longitude'][0]])
    dist.append([np.nan, np.nan, np.nan, np.nan, np.nan, data['latitude'].values[-1], data['longitude'].values[-1]])
    distances = pd.DataFrame(dist, columns=distances.columns)
    distances['time'] = data['time']
    return distances

def get8to20(data):
    '''
    取在8-20之间的数据
    :param data:
    :return:
    '''
    data['hour'] = [h.hour for h in data['time']]
    data = data[(data['hour'] > 8) & (data['hour'] < 20)]
    data = data.drop('hour', axis=1).reset_index(drop=True)
    return data

def cleanAfterProj(proj_data):
    pass







def get_clean_data(data):
    '''
    选取合适角度范围内的数据和边长的数据
    :param data:
    :return:
    '''
    # data = get8to20(data)
    data = get_angle(data)
    # data = data[(data['angle']>10) & (20 < data['d12']) & (data['d12'] < 2000)]
    # data = data[(data['angle']>0)]
    return data




