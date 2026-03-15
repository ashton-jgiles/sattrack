# imports
import os
import MySQLdb
from dotenv import load_dotenv
from pathlib import Path

# load the environment variables
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# create the database connection for ingestion
def get_connection():
    return MySQLdb.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        passwd=os.environ.get('DB_PASSWORD', ''),
        db=os.environ.get('DB_NAME', 'sattrack'),
        port=int(os.environ.get('DB_PORT', 3306)),
        charset='utf8mb4'
    )

# constants
HISTORY_DAYS = 30
INTERVAL_HOURS = 2

# CelesTrak Datasource URLS
CELESTRAK_SOURCES = [
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=json',
        'source':      'CelesTrak Starlink',
        'name':        'CelesTrak Starlink Satellites',
        'description': 'TLE orbital elements for Starlink satellites',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=gps-ops&FORMAT=json',
        'source':      'CelesTrak GPS',
        'name':        'CelesTrak GPS Operational Satellites',
        'description': 'TLE orbital elements for GPS operational satellites',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=galileo&FORMAT=json',
        'source':      'CelesTrak Galileo',
        'name':        'CelesTrak Galileo Satellites',
        'description': 'TLE orbital elements for Galileo navigation satellites',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=science&FORMAT=json',
        'source':      'CelesTrak Science',
        'name':        'CelesTrak Science Satellites',
        'description': 'TLE orbital elements for Science satellites',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=noaa&FORMAT=json',
        'source':      'CelesTrak NOAA',
        'name':        'CelesTrak NOAA Satellites',
        'description': 'TLE orbital elements for NOAA satellites',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=goes&FORMAT=json',
        'source':      'CelesTrak GOES',
        'name':        'CelesTrak GOES Satellites',
        'description': 'TLE orbital elements for GOES satellites',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=json',
        'source':      'CelesTrak Weather',
        'name':        'CelesTrak Weather Satellites',
        'description': 'TLE orbital elements for Wheather satellites',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=resource&FORMAT=json',
        'source':      'CelesTrak Earth and Ocean',
        'name':        'CelesTrak Earth and Ocean Satellites',
        'description': 'TLE orbital elements for Earth and Ocean satellites',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=json',
        'source':      'CelesTrak Space Stations',
        'name':        'CelesTrak Space Stations',
        'description': 'TLE orbital elements for Space Stations',
        'frequency':   '6h',
    },
    {
        'url':         'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json',
        'source':      'CelesTrak Active',
        'name':        'CelesTrak Miscellaneous Satellites',
        'description': 'TLE orbital elements for Miscellaneous Satellites',
        'frequency':   '6h',
    },


]

# create the list of urls
CELESTRAK_URLS = [s['url'] for s in CELESTRAK_SOURCES]

# target satellites list
TARGET_SATELLITES = {
 
    'earth_science': [
        {'norad_id': '25994', 'orbit_type': 'LEO', 'name': 'TERRA'},
        {'norad_id': '27424', 'orbit_type': 'LEO', 'name': 'AQUA'},
        {'norad_id': '39084', 'orbit_type': 'LEO', 'name': 'LANDSAT 8'},
        {'norad_id': '49260', 'orbit_type': 'LEO', 'name': 'LANDSAT 9'},
        {'norad_id': '41335', 'orbit_type': 'LEO', 'name': 'SENTINEL-3A'},
        {'norad_id': '43437', 'orbit_type': 'LEO', 'name': 'SENTINEL-3B'},
        {'norad_id': '39574', 'orbit_type': 'LEO', 'name': 'GPM-CORE'},
        {'norad_id': '43476', 'orbit_type': 'LEO', 'name': 'GRACE-FO 1'},
        {'norad_id': '43613', 'orbit_type': 'LEO', 'name': 'ICESAT-2'},
    ],
 
    'oceanic_science': [
        {'norad_id': '38771', 'orbit_type': 'LEO', 'name': 'METOP-B'},
        {'norad_id': '43013', 'orbit_type': 'LEO', 'name': 'NOAA 20 (JPSS-1)'},
        {'norad_id': '41240', 'orbit_type': 'LEO', 'name': 'JASON-3'},
        {'norad_id': '46984', 'orbit_type': 'LEO', 'name': 'SENTINEL-6A'},
        {'norad_id': '66514', 'orbit_type': 'LEO', 'name': 'SENTINEL-6B'},
        {'norad_id': '38337', 'orbit_type': 'LEO', 'name': 'GCOM-W1 (SHIZUKU)'},
    ],
 
    'research': [
        {'norad_id': '20580', 'orbit_type': 'LEO', 'name': 'HST'},
        {'norad_id': '43435', 'orbit_type': 'HEO', 'name': 'TESS'},
        {'norad_id': '25544', 'orbit_type': 'LEO', 'name': 'ISS (ZARYA)'},
        {'norad_id': '28376', 'orbit_type': 'LEO', 'name': 'AURA'},
        {'norad_id': '66303', 'orbit_type': 'LEO', 'name': 'STARCLOUD-1'},
        {'norad_id': '65616', 'orbit_type': 'LEO', 'name': 'CYGNUS NG-23'},
    ],
 
    'internet': [
        {'norad_id': '68125', 'orbit_type': 'LEO', 'name': 'STARLINK-36839'},
        {'norad_id': '68124', 'orbit_type': 'LEO', 'name': 'STARLINK-36938'},
        {'norad_id': '68123', 'orbit_type': 'LEO', 'name': 'STARLINK-36922'},
        {'norad_id': '68122', 'orbit_type': 'LEO', 'name': 'STARLINK-36366'},
        {'norad_id': '68121', 'orbit_type': 'LEO', 'name': 'STARLINK-36855'},
        {'norad_id': '68097', 'orbit_type': 'LEO', 'name': 'STARLINK-36853'},
        {'norad_id': '68096', 'orbit_type': 'LEO', 'name': 'STARLINK-36328'},
        {'norad_id': '68095', 'orbit_type': 'LEO', 'name': 'STARLINK-36790'},
        {'norad_id': '68094', 'orbit_type': 'LEO', 'name': 'STARLINK-36787'},
        {'norad_id': '68093', 'orbit_type': 'LEO', 'name': 'STARLINK-36251'},
    ],
 
    'weather': [
        {'norad_id': '41866', 'orbit_type': 'GEO', 'name': 'GOES 16'},
        {'norad_id': '51850', 'orbit_type': 'GEO', 'name': 'GOES 18'},
        {'norad_id': '41836', 'orbit_type': 'GEO', 'name': 'HIMAWARI-9'},
        {'norad_id': '38552', 'orbit_type': 'GEO', 'name': 'Meteosat-10 (MSG-3)'},
        {'norad_id': '40732', 'orbit_type': 'GEO', 'name': 'Meteosat-11 (MSG-4)'},
        {'norad_id': '65159', 'orbit_type': 'LEO', 'name': 'Metop-SGA1'},
        {'norad_id': '54234', 'orbit_type': 'LEO', 'name': 'NOAA 21 (JPSS-2)'},
        {'norad_id': '37849', 'orbit_type': 'LEO', 'name': 'SUOMI NPP'},
    ],
 
    'navigation': [
        {'norad_id': '24876', 'orbit_type': 'MEO', 'name': 'GPS BIIR-2  (PRN 13)'},
        {'norad_id': '26407', 'orbit_type': 'MEO', 'name': 'GPS BIIR-5  (PRN 22)'},
        {'norad_id': '27663', 'orbit_type': 'MEO', 'name': 'GPS BIIR-8  (PRN 16)'},
        {'norad_id': '28190', 'orbit_type': 'MEO', 'name': 'GPS BIIR-11 (PRN 19)'},
        {'norad_id': '28474', 'orbit_type': 'MEO', 'name': 'GPS BIIR-13 (PRN 02)'},
        {'norad_id': '28874', 'orbit_type': 'MEO', 'name': 'GPS BIIRM-1 (PRN 17)'},
        {'norad_id': '37846', 'orbit_type': 'MEO', 'name': 'GSAT0101 (GALILEO-PFM)'},
        {'norad_id': '37847', 'orbit_type': 'MEO', 'name': 'GSAT0102 (GALILEO-FM2)'},
        {'norad_id': '38857', 'orbit_type': 'MEO', 'name': 'GSAT0103 (GALILEO-FM3)'},
        {'norad_id': '40128', 'orbit_type': 'MEO', 'name': 'GSAT0201 (GALILEO 5)'},
        {'norad_id': '40129', 'orbit_type': 'MEO', 'name': 'GSAT0103 (GALILEO 6)'},
        {'norad_id': '40544', 'orbit_type': 'MEO', 'name': 'GSAT0201 (GALILEO 7)'},
    ],
}

# create flat lookups

# flat list of all NORAD IDs
ALL_NORAD_IDS = [
    sat['norad_id']
    for sats in TARGET_SATELLITES.values()
    for sat in sats
]
 
# orbit type by norad_id
ORBIT_TYPE_MAP = {
    sat['norad_id']: sat['orbit_type']
    for sats in TARGET_SATELLITES.values()
    for sat in sats
}
 
# subclass type by norad_id
SUBCLASS_MAP = {
    sat['norad_id']: subclass
    for subclass, sats in TARGET_SATELLITES.items()
    for sat in sats
}
 
# name by norad_id
NAME_MAP = {
    sat['norad_id']: sat['name']
    for sats in TARGET_SATELLITES.values()
    for sat in sats
}