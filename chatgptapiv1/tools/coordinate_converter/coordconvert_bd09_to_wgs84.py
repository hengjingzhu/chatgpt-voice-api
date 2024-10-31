import math

# 定定义常量
PI = math.pi
X_PI = PI * 3000.0 / 180.0
A = 6378245.0  # 长半轴
EE = 0.00669342162296594323  # 偏心率平方

def bd09_to_gcj02(bd_lon, bd_lat):
    """
    BD-09 转 GCJ-02
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * X_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * X_PI)
    gcj_lon = z * math.cos(theta)
    gcj_lat = z * math.sin(theta)
    return gcj_lon, gcj_lat

def gcj02_to_wgs84(gcj_lon, gcj_lat):
    """
    GCJ-02 转 WGS-84
    """
    if out_of_china(gcj_lon, gcj_lat):
        return gcj_lon, gcj_lat
    dlat = transform_lat(gcj_lon - 105.0, gcj_lat - 35.0)
    dlng = transform_lon(gcj_lon - 105.0, gcj_lat - 35.0)
    radlat = gcj_lat / 180.0 * PI
    magic = math.sin(radlat)
    magic = 1 - EE * magic * magic
    sqrt_magic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((A * (1 - EE)) / (magic * sqrt_magic) * PI)
    dlng = (dlng * 180.0) / (A / sqrt_magic * math.cos(radlat) * PI)
    wgs_lon = gcj_lon - dlng
    wgs_lat = gcj_lat - dlat
    return wgs_lon, wgs_lat

def transform_lat(x, y):
    """
    转换纬度
    """
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + \
          0.1 * x * y + 0.2 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 *
            math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(y * PI) + 40.0 *
            math.sin(y / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * math.sin(y / 12.0 * PI) + 320 *
            math.sin(y * PI / 30.0)) * 2.0 / 3.0
    return ret

def transform_lon(x, y):
    """
    转换经度
    """
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x + \
          0.1 * x * y + 0.1 * math.sqrt(abs(x))
    ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 *
            math.sin(2.0 * x * PI)) * 2.0 / 3.0
    ret += (20.0 * math.sin(x * PI) + 40.0 *
            math.sin(x / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * math.sin(x / 12.0 * PI) + 300.0 *
            math.sin(x / 30.0 * PI)) * 2.0 / 3.0
    return ret

def out_of_china(lon, lat):
    """
    判断是否在中国境外
    """
    if lon < 72.004 or lon > 137.8347:
        print("在中国境外")
        return True
    if lat < 0.8293 or lat > 55.8271:
        print("在中国境外")
        return True
    return False

def bd09_to_wgs84(bd_lon, bd_lat):
    """
    BD-09 转 WGS-84
    """

    gcj_lon, gcj_lat = bd09_to_gcj02(bd_lon, bd_lat)
    if not (73.66 < gcj_lon < 135.05 and 3.86 < gcj_lat < 53.55):
        print("在中国境外")
        return bd_lon, bd_lat
    wgs_lon, wgs_lat = gcj02_to_wgs84(gcj_lon, gcj_lat)
    return wgs_lon, wgs_lat


if __name__ == "__main__":
    
    bd09_longitude = 121.45137537780776
    bd09_latitude = 31.246174201475053
    
    wgs84_longitude, wgs84_latitude = bd09_to_wgs84(bd09_longitude, bd09_latitude)
    print(f"WGS84 坐标：经度={wgs84_longitude}, 纬度={wgs84_latitude}")
