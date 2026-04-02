# imports
from math import pi, degrees, sqrt, atan2, sin, cos
from datetime import datetime, timedelta, timezone
from sgp4.api import Satrec, jday
from sgp4.omm import initialize

# constants
HISTORY_DAYS     = 7
INTERVAL_MINUTES = 5

# build sat record method
def build_sat_record(satellite_data):
    satellite_record = Satrec()
    initialize(satellite_record, satellite_data)
    return satellite_record

# conversion function to go from ecef to geodetic
def ecef_to_geodetic(x, y, z):
    a = 6378.137
    f = 1 / 298.257223563
    e2 = 2 * f - f ** 2
    lon = degrees(atan2(y, x))
    p = sqrt(x**2 + y**2)
    lat = degrees(atan2(z, p * (1 - e2)))
    for i in range(10):
        lat_rad = lat * pi / 180
        N = a / sqrt(1 - e2 * sin(lat_rad)**2)
        lat = degrees(atan2(z + e2 * N * sin(lat_rad), p))
    lat_rad = lat * pi / 180
    N = a / sqrt(1 - e2 * sin(lat_rad)**2)
    alt = p / cos(lat_rad) - N if abs(lat) <= 89.9 else abs(z) / sin(lat_rad) - N * (1 - e2)
    return round(lat, 6), round(lon, 6), round(alt, 4)

# compute velocity function
def compute_velocity(mean_motion_rad_per_sec):
    GM = 398600.4418
    n = mean_motion_rad_per_sec
    sma = (GM / (n**2)) ** (1/3)
    return round(sqrt(GM / sma), 4)

# build timestamp function
def build_timestamps():
    now_utc = datetime.now(timezone.utc)
    start = now_utc - timedelta(days=HISTORY_DAYS)
    return [
        start + timedelta(minutes=m)
        for m in range(0, HISTORY_DAYS * 24 * 60, INTERVAL_MINUTES)
    ]