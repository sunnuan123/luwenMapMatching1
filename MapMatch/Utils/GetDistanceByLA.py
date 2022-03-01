from math import sin, asin, cos, radians, fabs, sqrt


def geodistance(lng1,lat1,lng2,lat2):
    '''
    #通过经纬度公式计算两点间距离（m）
    :param lng1:
    :param lat1:
    :param lng2:
    :param lat2:
    :return:
    '''
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
    dlon=lng2-lng1
    dlat=lat2-lat1
    a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance=2*asin(sqrt(a))*6378.138*1000 # 地球平均半径，6371km
    # distance=round(distance/1000,3)

    # 6378.138 * 2 * asin(sqrt(np.power(sin((lat1*np.pi/180-lat2*np.pi/180)/2),2)+
    #                          cos(lat1*np.pi()/180)*cos(lat2*np.pi/180)*np.power(sin((lng1*np.pi/180-lng2*np.pi/180)/2),2)))*1000


    return distance



