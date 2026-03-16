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

# static data
OWNERS = [
    {
        'owner_name':    'NASA',
        'owner_phone':   '1-202-358-0000.',
        'owner_address': 'Mary W. Jackson NASA Headquarters, 300 E Street SW, Washington, DC 20546-0001',
        'country':       'United States',
        'operator':      'NASA',
        'owner_type':    'government',
    },
    {
        'owner_name':    'SpaceX',
        'owner_phone':   '1-310-363-6000',
        'owner_address': '1 Rocket Road, Hawthorne, California, 90250, USA',
        'country':       'United States',
        'operator':      'SpaceX',
        'owner_type':    'commercial',
    },
    {
        'owner_name':    'ESA',
        'owner_phone':   '33-1-53-69-76-54',
        'owner_address': 'ESA HQ Mario Nikis, 8-10 rue Mario Nikis, CS 45741, 75738 Paris Cedex 15, France',
        'country':       'France',
        'operator':      'ESA',
        'owner_type':    'government',
    },
    {
        'owner_name':    'NOAA',
        'owner_phone':   '1-301-713-0500',
        'owner_address': '1315 East-West Highway, Silver Spring, Maryland 20910',
        'country':       'United States',
        'operator':      'NOAA',
        'owner_type':    'government',
    },
    {
        'owner_name':    'USAF',
        'owner_phone':   'None',
        'owner_address': 'The Pentagon, Arlington County, Virginia, U.S',
        'country':       'United States',
        'operator':      'United States Space Force',
        'owner_type':    'military',
    },
    {
        'owner_name':    'EUMETSAT',
        'owner_phone':   '49-6151-807-7',
        'owner_address': 'Eumetsat Allee 1, D-64295 Darmstadt, Germany',
        'country':       'Germany',
        'operator':      'EUMETSAT',
        'owner_type':    'government',
    },
    {
        'owner_name':    'JAXA',
        'owner_phone':   '81-3-5289-3650',
        'owner_address': '7-44-1 Jindaji Higashi-machi, Chofu-shi, Tokyo 182-8522, Japan',
        'country':       'Japan',
        'operator':      'JAXA',
        'owner_type':    'government',
    },
    {
        'owner_name':    'USGS',
        'owner_phone':   '1-888-275-8747',
        'owner_address': 'John W. Powell National Center, 12201 Sunrise Valley Dr, Reston, VA 20192, USA',
        'country':       'United States',
        'operator':      'USGS',
        'owner_type':    'government',
    },
    {
        'owner_name':    'Northrop Grumman Corporation',
        'owner_phone':   '+1 703-280-2900',
        'owner_address': 'John W. Powell National Center, 12201 Sunrise Valley Dr, Reston, VA 20192, USA',
        'country':       'United States',
        'operator':      'JAXA',
        'owner_type':    'commercial',
    },
    {
        'owner_name':    'INTERNATIONAL',
        'owner_phone':   'None',
        'owner_address': 'None',
        'country':       'Multiple',
        'operator':      'INTL',
        'owner_type':    'government',
    },
]

LAUNCH_SITES = [
    {
        'location':  'Vandenberg Space Force Base, CA',
        'climate':   'Temperate',
        'site_name': 'SLC-3E',
        'country':   'United States',
    },
    {
        'location':  'Vandenberg Space Force Base, CA',
        'climate':   'Temperate',
        'site_name': 'SLC-2W',
        'country':   'United States',
    },
    {
        'location':  'Vandenberg Space Force Base, CA',
        'climate':   'Temperate',
        'site_name': 'SLC-4E',
        'country':   'United States',
    },
    {
        'location':  'Kennedy Space Center, FL',
        'climate':   'Temperate',
        'site_name': 'LC-39B',
        'country':   'United States',
    },
    {
        'location':  'Cape Canaveral, FL',
        'climate':   'Temperate',
        'site_name': 'SLC-40',
        'country':   'United States',
    },
    {
        'location':  'Cape Canaveral, FL',
        'climate':   'Temperate',
        'site_name': 'SLC-41',
        'country':   'United States',
    },
    {
        'location':  'Cape Canaveral, FL',
        'climate':   'Temperate',
        'site_name': 'SLC-17A',
        'country':   'United States',
    },
    {
        'location':  'Cape Canaveral, FL',
        'climate':   'Temperate',
        'site_name': 'SLC-17B',
        'country':   'United States',
    },
    {
        'location':  'Plesetsk Cosmodrome',
        'climate':   'Continental',
        'site_name': 'Site 133/3',
        'country':   'Russia',
    },
    {
        'location':  'Baikonur Cosmodrome',
        'climate':   'Dry',
        'site_name': 'Site 31/6',
        'country':   'Kazakhstan',
    },
    {
        'location':  'Baikonur Cosmodrome',
        'climate':   'Dry',
        'site_name': 'Site 81/23',
        'country':   'Kazakhstan',
    },
    {
        'location':  'Tanegashima Space Center',
        'climate':   'Temperate',
        'site_name': 'LA-Y1',
        'country':   'Japan',
    },
    {
        'location':  'Guiana Space Centre',
        'climate':   'Tropical',
        'site_name': 'ELS (Soyuz)',
        'country':   'French Guiana',
    },
    {
        'location':  'Guiana Space Centre',
        'climate':   'Tropical',
        'site_name': 'ELA-3',
        'country':   'French Guiana',
    },
    {
        'location':  'Guiana Space Centre',
        'climate':   'Tropical',
        'site_name': 'ELA-4',
        'country':   'French Guiana',
    },
]

LAUNCH_VEHICLES = [
    {
        'vehicle_name':     'Atlas IIAS',
        'manufacturer':     'Lockheed Martin',
        'reusable':         False,
        'country':          'United States',
        'payload_capacity': '8,600 kg to LEO',
    },
    {
        'vehicle_name':     'Delta II 7920',
        'manufacturer':     'Boeing',
        'reusable':         False,
        'country':          'United States',
        'payload_capacity': '6,100 kg to LEO',
    },
    {
        'vehicle_name':     'Delta II 7925',
        'manufacturer':     'Boeing',
        'reusable':         False,
        'country':          'United States',
        'payload_capacity': '4,800 kg to LEO',
    },
    {
        'vehicle_name':     'Delta II 7420',
        'manufacturer':     'Boeing',
        'reusable':         False,
        'country':          'United States',
        'payload_capacity': '3,100 kg to LEO',
    },
    {
        'vehicle_name':     'Atlas V 401',
        'manufacturer':     'ULA',
        'reusable':         False,
        'country':          'United States',
        'payload_capacity': '12,500 kg to LEO',
    },
    {
        'vehicle_name':     'Atlas V 541',
        'manufacturer':     'ULA',
        'reusable':         False,
        'country':          'United States',
        'payload_capacity': '17,410 kg to LEO',
    },
    {
        'vehicle_name':     'Rockot',
        'manufacturer':     'Eurockot / Khrunichev',
        'reusable':         False,
        'country':          'Russia',
        'payload_capacity': '1,900 kg to LEO',
    },
    {
        'vehicle_name':     'H-IIA 202',
        'manufacturer':     'Mitsubishi Heavy Industries',
        'reusable':         False,
        'country':          'Japan',
        'payload_capacity': '10,000 kg to LEO',
    },
    {
        'vehicle_name':     'Falcon 9',
        'manufacturer':     'SpaceX',
        'reusable':         True,
        'country':          'United States',
        'payload_capacity': '22,800 kg to LEO',
    },
    {
        'vehicle_name':     'Soyuz 2.1a',
        'manufacturer':     'Roscosmos / TsSKB-Progress',
        'reusable':         False,
        'country':          'Russia',
        'payload_capacity': '7,600 kg to LEO',
    },
    {
        'vehicle_name':     'Soyuz ST-B',
        'manufacturer':     'Roscosmos / TsSKB-Progress',
        'reusable':         False,
        'country':          'Russia',
        'payload_capacity': '7,600 kg to LEO',
    },
    {
        'vehicle_name':     'Space Shuttle',
        'manufacturer':     'Rockwell / Lockheed Martin',
        'reusable':         True,
        'country':          'United States',
        'payload_capacity': '24,000 kg to LEO',
    },
    {
        'vehicle_name':     'Proton-K',
        'manufacturer':     'Khrunichev',
        'reusable':         False,
        'country':          'Russia',
        'payload_capacity': '21,000 kg to LEO',
    },
    {
        'vehicle_name':     'Ariane 5 ECA',
        'manufacturer':     'ArianeGroup',
        'reusable':         False,
        'country':          'France',
        'payload_capacity': '10,300 kg to LEO',
    },
    {
        'vehicle_name':     'Ariane 6',
        'manufacturer':     'ArianeGroup',
        'reusable':         False,
        'country':          'France',
        'payload_capacity': '21,600 kg to LEO',
    },
]

USERS = [
    {
        'username':     'admin01',
        'password':     'admin123',
        'full_name':    'Admin User',
        'level_access': 4,
        'type':         'administrator',
        'employee_id':  1,
    },
    {
        'username':     'analyst01',
        'password':     'analyst123',
        'full_name':    'Analyst User',
        'level_access': 3,
        'type':         'data_analyst',
        'employee_id':  2,
    },
    {
        'username':     'scientist01',
        'password':     'scientist123',
        'full_name':    'Scientist User',
        'level_access': 2,
        'type':         'scientist',
        'profession':   'Astrophysicist',
    },
    {
        'username':     'amateur01',
        'password':     'amateur123',
        'full_name':    'Amateur User',
        'level_access': 1,
        'type':         'amateur',
        'interests':    'Satellite tracking and astronomy',
    },
]

COMMUNICATION_STATIONS = [
    {
        'location':                'White Sands, New Mexico, USA',
        'name':                    'White Sands Complex',
    },
    {
        'location':                'Redmond, Washington',
        'name':                    'Starcloud Mission Control',
    },
    {
        'location':                'International (Sioux Falls, SD, USA, Gilmore Creek, AK, USA, Svalbard, Norway, Neustrelitz, Germany, Alice Springs, Australia)',
        'name':                    'USGS Ground Network',
    },
    {
        'location':                'Svalbard, Norway',
        'name':                    'Svalbard Satellite Station',
    },
    {
        'location':                'Greenbelt, Maryland, USA',
        'name':                    'Goddard Space Flight Center',
    },
    {
        'location':                'Antartica',
        'name':                    'McMurdo Station',
    },
    {
        'location':                'Fairbanks, Alaska',
        'name':                    'NOAA Ground Station',
    },
    {
        'location':                'Wallops, Virginia, USA',
        'name':                    'NOAA Ground Station',
    },
    {
        'location':                'Global Gateways',
        'name':                    'Starlink Gateways',
    },
    {
        'location':                'Wallops Island, Virginia, USA',
        'name':                    'Wallops Command & Data Aquisition',
    },
    {
        'location':                'Tokyo, Japan',
        'name':                    'Kanto Region Station',
    },
    {
        'location':                'Colorado Springs, CO, USA',
        'name':                    'Schriever Space Force Base',
    },
    {
        'location':                'Oberpfaffenhofen, Germany',
        'name':                    'German Space Operation Center',
    },
    {
        'location':                'Darmstadt, Germany',
        'name':                    'European Organization for the Explotation of Meterological Satellites',
    },
    {
        'location':                'Northrop Grumman, Dulles, Virginia, USA',
        'name':                    'Mission Operations Center',
    },
    {
        'location':                'Houston, Texas, USA',
        'name':                    'Johnson Space Center',
    },
    {
        'location':                'Okinawa, Japan',
        'name':                    'Japan Aerospace Exploration Agency',
    },
]

# maps norad_id to owner_name
SATELLITE_OWNER_MAP = {
    # NASA
    '25994': 'NASA',    # Terra
    '27424': 'NASA',    # Aqua
    '20580': 'NASA',    # Hubble
    '43435': 'NASA',    # TESS
    '28376': 'NASA',    # Aura
    '39574': 'NASA',    # GPM Core
    '43476': 'NASA',    # GRACE-FO 1
    '43613': 'NASA',    # ICESat-2
    '66303': 'NASA',    # STARCLOUD-1

    #International
    '25544': 'INTERNATIONAL',    # ISS

    # USGS
    '39084': 'USGS',    # Landsat 8
    '49260': 'USGS',    # Landsat 9

    # Northrop Grumman
    '65616': 'Northrop Grumman Corporation',    # CYGNUS NG-23

    # NOAA
    '43013': 'NOAA',    # NOAA-20
    '41240': 'NOAA',    # Jason-3
    '54234': 'NOAA',    # NOAA-21
    '41866': 'NOAA',    # GOES-16
    '51850': 'NOAA',    # GOES-18

    # ESA
    '41335': 'ESA',     # Sentinel-3A
    '43437': 'ESA',     # Sentinel-3B
    '46984': 'ESA',     # Sentinel-6A
    '66514': 'ESA',     # Sentinel-6B
    '40732': 'ESA',     # Meteosat-11
    '37846': 'ESA',     # Galileo-PFM
    '37847': 'ESA',     # Galileo-FM2
    '38857': 'ESA',     # Galileo-FM3
    '40128': 'ESA',     # Galileo-5
    '40129': 'ESA',     # Galileo-6
    '40544': 'ESA',     # Galileo-7

    # EUMETSAT
    '38771': 'EUMETSAT', # Metop-B
    '38552': 'EUMETSAT', # Meteosat-10
    '65159': 'EUMETSAT', # Metop-SGA1
    '37849': 'EUMETSAT', # Suomi NPP

    # SpaceX Starlink
    '68125': 'SpaceX',
    '68124': 'SpaceX',
    '68123': 'SpaceX',
    '68122': 'SpaceX',
    '68121': 'SpaceX',
    '68097': 'SpaceX',
    '68096': 'SpaceX',
    '68095': 'SpaceX',
    '68094': 'SpaceX',
    '68093': 'SpaceX',

    # USAF / Space Force GPS
    '24876': 'USAF',
    '26407': 'USAF',
    '27663': 'USAF',
    '28190': 'USAF',
    '28474': 'USAF',
    '28874': 'USAF',

    # JAXA
    '38337': 'JAXA',    # GCOM-W1
    '41836': 'JAXA',    # Himawari-9
}

# naps norad_id to vehicle name site name and creates the launch date
DEPLOYS_PAYLOAD_MAP = {
    '25994': {
        'vehicle':    'Atlas IIAS',
        'site_name':  'SLC-3E',
        'date':       '1999-12-18',
    },
    '27424': {
        'vehicle':    'Delta II 7920',
        'site_name':  'SLC-2W',
        'date':       '2002-05-04',
    },
    '39084': {
        'vehicle':    'Atlas V 401',
        'site_name':  'SLC-3E',
        'date':       '2013-02-11',
    },
    '49260': {
        'vehicle':    'Atlas V 401',
        'site_name':  'SLC-3E',
        'date':       '2021-09-27',
    },
    '41335': {
        'vehicle':    'Rockot',
        'site_name':  'Site 133/3',
        'date':       '2016-02-16',
    },
    '43437': {
        'vehicle':    'Rockot',
        'site_name':  'Site 133/3',
        'date':       '2018-04-25',
    },
    '39574': {
        'vehicle':    'H-IIA 202',
        'site_name':  'LA-Y1',
        'date':       '2014-02-27',
    },
    '43476': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2018-05-22',
    },
    '43613': {
        'vehicle':    'Delta II 7420',
        'site_name':  'SLC-2W',
        'date':       '2018-09-15',
    },
    '38771': {
        'vehicle':    'Soyuz 2.1a',
        'site_name':  'Site 31/6',
        'date':       '2012-09-17',
    },
    '43013': {
        'vehicle':    'Delta II 7920',
        'site_name':  'SLC-2W',
        'date':       '2017-11-18',
    },
    '41240': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2016-01-17',
    },
    '46984': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2020-11-21',
    },
    '66514': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2025-11-17',
    },
    '38337': {
        'vehicle':    'H-IIA 202',
        'site_name':  'LA-Y1',
        'date':       '2012-05-17',
    },
    '20580': {
        'vehicle':    'Space Shuttle',
        'site_name':  'LC-39B',
        'date':       '1990-04-24',
    },
    '43435': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-40',
        'date':       '2018-04-18',
    },
    '25544': {
        'vehicle':    'Proton-K',
        'site_name':  'Site 81/23',
        'date':       '1998-11-20',
    },
    '28376': {
        'vehicle':    'Delta II 7920',
        'site_name':  'SLC-2W',
        'date':       '2004-07-15',
    },
    '66303': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-40',
        'date':       '2025-11-02',
    },
    '65616': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-40',
        'date':       '2025-09-14',
    },
    '41866': {
        'vehicle':    'Atlas V 541',
        'site_name':  'SLC-41',
        'date':       '2016-11-19',
    },
    '51850': {
        'vehicle':    'Atlas V 541',
        'site_name':  'SLC-41',
        'date':       '2022-03-01',
    },
    '41836': {
        'vehicle':    'H-IIA 202',
        'site_name':  'LA-Y1',
        'date':       '2016-11-02',
    },
    '38552': {
        'vehicle':    'Ariane 5 ECA',
        'site_name':  'ELA-3',
        'date':       '2012-07-04',
    },
    '40732': {
        'vehicle':    'Ariane 5 ECA',
        'site_name':  'ELA-3',
        'date':       '2015-07-15',
    },
    '65159': {
        'vehicle':    'Ariane 6',
        'site_name':  'ELA-4',
        'date':       '2025-08-13',
    },
    '54234': {
        'vehicle':    'Atlas V 401',
        'site_name':  'SLC-3E',
        'date':       '2022-11-10',
    },
    '37849': {
        'vehicle':    'Delta II 7920',
        'site_name':  'SLC-2W',
        'date':       '2011-10-28',
    },
    '24876': {
        'vehicle':    'Delta II 7925',
        'site_name':  'SLC-17A',
        'date':       '1997-07-23',
    },
    '26407': {
        'vehicle':    'Delta II 7925',
        'site_name':  'SLC-17A',
        'date':       '2000-07-16',
    },
    '27663': {
        'vehicle':    'Delta II 7925',
        'site_name':  'SLC-17B',
        'date':       '2003-01-29',
    },
    '28190': {
        'vehicle':    'Delta II 7925',
        'site_name':  'SLC-17B',
        'date':       '2004-03-20',
    },
    '28474': {
        'vehicle':    'Delta II 7925',
        'site_name':  'SLC-17B',
        'date':       '2004-11-06',
    },
    '28874': {
        'vehicle':    'Delta II 7925',
        'site_name':  'SLC-17A',
        'date':       '2005-09-26',
    },
    '37846': {
        'vehicle':    'Soyuz ST-B',
        'site_name':  'ELS (Soyuz)',
        'date':       '2011-10-21',
    },
    '37847': {
        'vehicle':    'Soyuz ST-B',
        'site_name':  'ELS (Soyuz)',
        'date':       '2011-10-21',
    },
    '38857': {
        'vehicle':    'Soyuz ST-B',
        'site_name':  'ELS (Soyuz)',
        'date':       '2012-10-12',
    },
    '40128': {
        'vehicle':    'Soyuz ST-B',
        'site_name':  'ELS (Soyuz)',
        'date':       '2014-08-22',
    },
    '40129': {
        'vehicle':    'Soyuz ST-B',
        'site_name':  'ELS (Soyuz)',
        'date':       '2014-08-22',
    },
    '40544': {
        'vehicle':    'Soyuz ST-B',
        'site_name':  'ELS (Soyuz)',
        'date':       '2015-03-27',
    },
    '68125': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-40',
        'date':       '2025-12-12',
    },
    '68124': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-40',
        'date':       '2025-12-12',
    },
    '68123': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-40',
        'date':       '2025-12-12',
    },
    '68122': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-40',
        'date':       '2025-12-12',
    },
    '68121': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-40',
        'date':       '2025-12-12',
    },
    '68097': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2025-12-05',
    },
    '68096': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2025-12-05',
    },
    '68095': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2025-12-05',
    },
    '68094': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2025-12-05',
    },
    '68093': {
        'vehicle':    'Falcon 9',
        'site_name':  'SLC-4E',
        'date':       '2025-12-05',
    },
}

COMMUNICATES_WITH_MAP = {
    '25994': {
        'location':   'Greenbelt, Maryland, USA',
        'frequency':  'Once per orbit (16 orbits)',
    },
    '27424': {
        'location':   'Greenbelt, Maryland, USA',
        'frequency':  'Once per orbit (16 orbits)',
    },
    '39084': {
        'location':   'International (Sioux Falls, SD, USA, Gilmore Creek, AK, USA, Svalbard, Norway, Neustrelitz, Germany, Alice Springs, Australia)',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '49260': {
        'location':   'International (Sioux Falls, SD, USA, Gilmore Creek, AK, USA, Svalbard, Norway, Neustrelitz, Germany, Alice Springs, Australia)',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '41335': {
        'location':   'Svalbard, Norway',
        'frequency':  'Once per orbit (15 orbits)',
    },
    '43437': {
        'location':   'Svalbard, Norway',
        'frequency':  'Once per orbit (15 orbits)',
    },
    '39574': {
       'location':   'White Sands, New Mexico, USA',
        'frequency':  'Continuous',
    },
    '43476': {
        'location':   'Oberpfaffenhofen, Germany',
        'frequency':  'Once per orbit (15 orbits)',
    },
    '43613': {
        'location':   'Antartica',
        'frequency':  'Once per orbit (15 orbits)',
    },
    '38771': {
        'location':   'Svalbard, Norway',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '43013': {
        'location':   'Fairbanks, Alaska',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '41240': {
        'location':   'Fairbanks, Alaska',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '46984': {
        'location':   'Fairbanks, Alaska',
        'frequency':  'Once per orbit (13 orbits)',
    },
    '66514': {
        'location':   'Fairbanks, Alaska',
        'frequency':  'Once per orbit (13 orbits)',
    },
    '38337': {
        'location':   'Okinawa, Japan',
        'frequency':  'Once per orbit (15 orbits)',
    },
    '20580': {
        'location':   'White Sands, New Mexico, USA',
        'frequency':  'Near Continuous',
    },
    '43435': {
        'location':   'Northrop Grumman, Dulles, Virginia, USA',
        'frequency':  'Once every 14 days',
    },
    '25544': {
        'location':   'Houston, Texas, USA',
        'frequency':  'Near Continuous',
    },
    '28376': {
        'location':   'Antartica',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '66303': {
        'location':   'Redmond, Washington', 
        'frequency':  'Periodic over groundstation',
    },
    '65616': {
        'location':    'Northrop Grumman, Dulles, Virginia, USA',
        'frequency':  'Periodic over groundstation',
    },
    '41866': {
        'location':   'Wallops Island, Virginia, USA',
        'frequency':  'Continuous',
    },
    '51850': {
        'location':   'Wallops Island, Virginia, USA',
        'frequency':  'Continuous',
    },
    '41836': {
        'location':   'Tokyo, Japan',
        'frequency':  'Continuous',
    },
    '38552': {
        'location':   'Darmstadt, Germany',
        'frequency':  'Continuous',
    },
    '40732': {
        'location':   'Darmstadt, Germany',
        'frequency':  'Continuous',
    },
    '65159': {
        'location':   'Darmstadt, Germany',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '54234': {
        'location':   'Svalbard, Norway',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '37849': {
        'location':   'Svalbard, Norway',
        'frequency':  'Once per orbit (14 orbits)',
    },
    '24876': {
        'location':   'Colorado Springs, CO, USA',
        'frequency':  '2 per day',
    },
    '26407': {
        'location':   'Colorado Springs, CO, USA',
        'frequency':  '2 per day',
    },
    '27663': {
        'location':   'Colorado Springs, CO, USA',
        'frequency':  '2 per day',
    },
    '28190': {
        'location':   'Colorado Springs, CO, USA',
        'frequency':  '2 per day',
    },
    '28474': {
        'location':   'Colorado Springs, CO, USA',
        'frequency':  '2 per day',
    },
    '28874': {
       'location':   'Colorado Springs, CO, USA',
        'frequency':  '2 per day',
    },
    '37846': {
        'location':   'Oberpfaffenhofen, Germany',
        'frequency':  '2 per day',
    },
    '37847': {
        'location':   'Oberpfaffenhofen, Germany',
        'frequency':  '2 per day',
    },
    '38857': {
        'location':   'Oberpfaffenhofen, Germany',
        'frequency':  '2 per day',
    },
    '40128': {
        'location':   'Oberpfaffenhofen, Germany',
        'frequency':  '2 per day',
    },
    '40129': {
        'location':   'Oberpfaffenhofen, Germany',
        'frequency':  '2 per day',
    },
    '40544': {
        'location':   'Oberpfaffenhofen, Germany',
        'frequency':  '2 per day',
    },
    '68125': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68124': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68123': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68122': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68121': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68097': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68096': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68095': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68094': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
    '68093': {
        'location':   'Global Gateways',
        'frequency':  'Continuous',
    },
}

EARTH_SCIENCE_DATA = {
    '25994': {  # TERRA
        'instrument':      'MODIS',
        'data_measured':   'Land Surface Temperature, Vegetation Index, Aerosol Optical Depth',
        'wavelength_band': 'Visible / Thermal IR',
        'resolution_m':    250,
        'data_archive_url': 'https://lpdaac.usgs.gov/products/mod11a1v061/',
        'mission_status':  'active',
    },
    '27424': {  # AQUA
        'instrument':      'MODIS / AIRS',
        'data_measured':   'Land Surface Temperature, Atmospheric Temperature, Water Vapour',
        'wavelength_band': 'Visible / Thermal IR / Microwave',
        'resolution_m':    250,
        'data_archive_url': 'https://lpdaac.usgs.gov/products/myd11a1v061/',
        'mission_status':  'active',
    },
    '39084': {  # LANDSAT 8
        'instrument':      'OLI / TIRS',
        'data_measured':   'Land Surface Temperature, Land Cover, Surface Reflectance',
        'wavelength_band': 'Visible / Near-IR / Thermal IR',
        'resolution_m':    30,
        'data_archive_url': 'https://www.usgs.gov/landsat-missions/landsat-8',
        'mission_status':  'active',
    },
    '49260': {  # LANDSAT 9
        'instrument':      'OLI-2 / TIRS-2',
        'data_measured':   'Land Surface Temperature, Land Cover, Surface Reflectance',
        'wavelength_band': 'Visible / Near-IR / Thermal IR',
        'resolution_m':    30,
        'data_archive_url': 'https://www.usgs.gov/landsat-missions/landsat-9',
        'mission_status':  'active',
    },
    '41335': {  # SENTINEL-3A
        'instrument':      'SLSTR / OLCI',
        'data_measured':   'Land Surface Temperature, Ocean Colour, Fire Radiative Power',
        'wavelength_band': 'Visible / Near-IR / Thermal IR',
        'resolution_m':    300,
        'data_archive_url': 'https://browser.dataspace.copernicus.eu/',
        'mission_status':  'active',
    },
    '43437': {  # SENTINEL-3B
        'instrument':      'SLSTR / OLCI',
        'data_measured':   'Land Surface Temperature, Ocean Colour, Fire Radiative Power',
        'wavelength_band': 'Visible / Near-IR / Thermal IR',
        'resolution_m':    300,
        'data_archive_url': 'https://browser.dataspace.copernicus.eu/',
        'mission_status':  'active',
    },
    '39574': {  # GPM-CORE
        'instrument':      'GMI / DPR',
        'data_measured':   'Precipitation Rate, Snow Water Equivalent, Latent Heat',
        'wavelength_band': 'Microwave / Ka-Ku Band Radar',
        'resolution_m':    5000,
        'data_archive_url': 'https://gpm.nasa.gov/data',
        'mission_status':  'active',
    },
    '43476': {  # GRACE-FO 1
        'instrument':      'MWI / LRI',
        'data_measured':   'Terrestrial Water Storage, Ice Sheet Mass, Gravity Anomaly',
        'wavelength_band': 'Microwave / Laser Ranging',
        'resolution_m':    300000,
        'data_archive_url': 'https://gracefo.jpl.nasa.gov/data/grace-fo-data/',
        'mission_status':  'active',
    },
    '43613': {  # ICESAT-2
        'instrument':      'ATLAS',
        'data_measured':   'Ice Sheet Elevation, Sea Ice Thickness, Vegetation Canopy Height',
        'wavelength_band': 'Green Laser (532nm)',
        'resolution_m':    17,
        'data_archive_url': 'https://icesat-2.gsfc.nasa.gov/data',
        'mission_status':  'active',
    },
}

OCEANIC_SCIENCE_DATA = {
    '38771': {  # METOP-B
        'instrument':      'AVHRR/3 / ASCAT',
        'data_measured':   'Sea Surface Temperature, Ocean Wind Speed and Direction',
        'wavelength_band': 'Visible / Thermal IR / Microwave',
        'resolution_m':    1100,
        'data_archive_url': 'https://www.eumetsat.int/metop',
        'mission_status':  'active',
    },
    '43013': {  # NOAA-20
        'instrument':      'VIIRS / CrIS / ATMS',
        'data_measured':   'Sea Surface Temperature, Ocean Colour, Chlorophyll Concentration',
        'wavelength_band': 'Visible / Near-IR / Thermal IR / Microwave',
        'resolution_m':    375,
        'data_archive_url': 'https://www.star.nesdis.noaa.gov/jpss/NOAA20.php',
        'mission_status':  'active',
    },
    '41240': {  # JASON-3
        'instrument':      'Poseidon-3B / AMR-2',
        'data_measured':   'Sea Level Anomaly, Significant Wave Height, Ocean Circulation',
        'wavelength_band': 'Ku / C Band Radar',
        'resolution_m':    300000,
        'data_archive_url': 'https://www.eumetsat.int/jason-3',
        'mission_status':  'active',
    },
    '46984': {  # SENTINEL-6A
        'instrument':      'Poseidon-4 / AMR-C',
        'data_measured':   'Sea Level Anomaly, Significant Wave Height, Sea Surface Temperature',
        'wavelength_band': 'Ku / C Band Radar / Microwave',
        'resolution_m':    300000,
        'data_archive_url': 'https://browser.dataspace.copernicus.eu/',
        'mission_status':  'active',
    },
    '66514': {  # SENTINEL-6B
        'instrument':      'Poseidon-4 / AMR-C',
        'data_measured':   'Sea Level Anomaly, Significant Wave Height, Sea Surface Temperature',
        'wavelength_band': 'Ku / C Band Radar / Microwave',
        'resolution_m':    300000,
        'data_archive_url': 'https://browser.dataspace.copernicus.eu/',
        'mission_status':  'active',
    },
    '38337': {  # GCOM-W1
        'instrument':      'AMSR2',
        'data_measured':   'Sea Surface Temperature, Soil Moisture, Snow Water Equivalent, Precipitation',
        'wavelength_band': 'Microwave (6.9–89 GHz)',
        'resolution_m':    3500,
        'data_archive_url': 'https://gportal.jaxa.jp/gpr/',
        'mission_status':  'active',
    },
}

WEATHER_DATA = {
    '41866': {  # GOES-16
        'instrument':      'ABI / GLM',
        'data_measured':   'Cloud Cover, Precipitation Rate, Lightning, Wildfire Detection',
        'coverage_region': 'Americas & Atlantic',
        'imaging_channels': 16,
        'repeat_cycle_min': 10,
        'data_archive_url': 'https://www.ncei.noaa.gov/products/goes',
        'mission_status':  'active',
    },
    '51850': {  # GOES-18
        'instrument':      'ABI / GLM',
        'data_measured':   'Cloud Cover, Precipitation Rate, Lightning, Wildfire Detection',
        'coverage_region': 'Americas & Pacific',
        'imaging_channels': 16,
        'repeat_cycle_min': 10,
        'data_archive_url': 'https://www.ncei.noaa.gov/products/goes',
        'mission_status':  'active',
    },
    '41836': {  # HIMAWARI-9
        'instrument':      'AHI',
        'data_measured':   'Cloud Cover, Rainfall Rate, SST, Dust and Smoke Detection',
        'coverage_region': 'Asia-Pacific',
        'imaging_channels': 16,
        'repeat_cycle_min': 10,
        'data_archive_url': 'https://www.data.jma.go.jp/mscweb/en/himawari89/',
        'mission_status':  'active',
    },
    '38552': {  # METEOSAT-10
        'instrument':      'SEVIRI',
        'data_measured':   'Cloud Top Temperature, Water Vapour, SST, Vegetation',
        'coverage_region': 'Europe & Africa',
        'imaging_channels': 12,
        'repeat_cycle_min': 15,
        'data_archive_url': 'https://www.eumetsat.int/meteosat',
        'mission_status':  'active',
    },
    '40732': {  # METEOSAT-11
        'instrument':      'SEVIRI',
        'data_measured':   'Cloud Top Temperature, Water Vapour, SST, Vegetation',
        'coverage_region': 'Europe & Africa (Rapid Scan)',
        'imaging_channels': 12,
        'repeat_cycle_min': 5,
        'data_archive_url': 'https://www.eumetsat.int/meteosat',
        'mission_status':  'active',
    },
    '65159': {  # METOP-SGA1
        'instrument':      'METimage / IASI-NG / ASCAT',
        'data_measured':   'Atmospheric Temperature, Humidity Profile, Ocean Wind, Cloud Properties',
        'coverage_region': 'Global (Polar)',
        'imaging_channels': 20,
        'repeat_cycle_min': 101,
        'data_archive_url': 'https://www.eumetsat.int/metop-sg',
        'mission_status':  'active',
    },
    '54234': {  # NOAA-21
        'instrument':      'VIIRS / CrIS / ATMS',
        'data_measured':   'Cloud Properties, Precipitation, Atmospheric Temperature and Humidity',
        'coverage_region': 'Global (Polar)',
        'imaging_channels': 22,
        'repeat_cycle_min': 101,
        'data_archive_url': 'https://www.star.nesdis.noaa.gov/jpss/',
        'mission_status':  'active',
    },
    '37849': {  # SUOMI NPP
        'instrument':      'VIIRS / CrIS / ATMS / OMPS',
        'data_measured':   'Cloud Properties, Ozone, Atmospheric Temperature, Night Lights',
        'coverage_region': 'Global (Polar)',
        'imaging_channels': 22,
        'repeat_cycle_min': 101,
        'data_archive_url': 'https://www.star.nesdis.noaa.gov/jpss/NPP.php',
        'mission_status':  'active',
    },
}

RESEARCH_DATA = {
    '20580': {  # HST
        'instrument':      'WFC3 / COS / ACS / STIS',
        'data_measured':   'Deep Field Imaging, UV Spectroscopy, Exoplanet Atmospheres',
        'research_field':  'Astrophysics',
        'wavelength_band': 'UV / Visible / Near-IR',
        'data_archive_url': 'https://archive.stsci.edu/hst/',
        'mission_status':  'active',
    },
    '43435': {  # TESS
        'instrument':      'Wide-Field Camera Array',
        'data_measured':   'Stellar Photometry, Exoplanet Transit Detection',
        'research_field':  'Exoplanet Detection',
        'wavelength_band': 'Visible / Near-IR (600–1000nm)',
        'data_archive_url': 'https://archive.stsci.edu/tess/',
        'mission_status':  'active',
    },
    '25544': {  # ISS
        'instrument':      'Multiple Payloads (ECOSTRESS, EMIT, NICER, etc.)',
        'data_measured':   'Multi-discipline — Earth Observation, Biology, Physics, Materials',
        'research_field':  'Microgravity / Multi-discipline',
        'wavelength_band': 'Multiple',
        'data_archive_url': 'https://www.nasa.gov/international-space-station/',
        'mission_status':  'active',
    },
    '28376': {  # AURA
        'instrument':      'MLS / OMI / HIRDLS / TES',
        'data_measured':   'Ozone, NO2, SO2, Aerosols, Atmospheric Chemistry Profiles',
        'research_field':  'Atmospheric Chemistry',
        'wavelength_band': 'UV / Visible / IR / Microwave',
        'data_archive_url': 'https://aura.gsfc.nasa.gov/data.html',
        'mission_status':  'active',
    },
    '66303': {  # STARCLOUD-1
        'instrument':      'Multi-Spectral Cloud Imager',
        'data_measured':   'Cloud Microphysics, Optical Depth, Droplet Size Distribution',
        'research_field':  'Cloud Physics',
        'wavelength_band': 'Visible / Near-IR',
        'data_archive_url': 'None',
        'mission_status':  'active',
    },
    '65616': {  # CYGNUS NG-23
        'instrument':      'Cargo Manifest',
        'data_measured':   'ISS Resupply — no independent sensing payload',
        'research_field':  'Logistics / ISS Support',
        'wavelength_band': 'None',
        'data_archive_url': 'None',
        'mission_status':  'active',
    },
}

INTERNET_DATA = {
    '68125': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68124': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68123': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68122': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68121': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68097': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68096': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68095': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68094': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
    '68093': {'coverage': 'Global', 'frequency_band': 'Ku / Ka', 'service_type': 'Broadband Internet', 'throughput_gbps': 20.00, 'altitude_km': 550},
}

NAVIGATION_DATA = {
    '24876': {'constellation': 'GPS',     'signal_type': 'L1 C/A, L2P',       'accuracy_m': 3.00, 'orbital_slot': 'Plane D, Slot 4',  'clock_type': 'Rubidium / Caesium'},
    '26407': {'constellation': 'GPS',     'signal_type': 'L1 C/A, L2P',       'accuracy_m': 3.00, 'orbital_slot': 'Plane E, Slot 1',  'clock_type': 'Rubidium / Caesium'},
    '27663': {'constellation': 'GPS',     'signal_type': 'L1 C/A, L2P',       'accuracy_m': 3.00, 'orbital_slot': 'Plane B, Slot 1',  'clock_type': 'Rubidium / Caesium'},
    '28190': {'constellation': 'GPS',     'signal_type': 'L1 C/A, L2P',       'accuracy_m': 3.00, 'orbital_slot': 'Plane D, Slot 2',  'clock_type': 'Rubidium / Caesium'},
    '28474': {'constellation': 'GPS',     'signal_type': 'L1 C/A, L2P',       'accuracy_m': 3.00, 'orbital_slot': 'Plane A, Slot 2',  'clock_type': 'Rubidium / Caesium'},
    '28874': {'constellation': 'GPS',     'signal_type': 'L1 C/A, L2C, L2M',  'accuracy_m': 2.50, 'orbital_slot': 'Plane F, Slot 2',  'clock_type': 'Rubidium'},
    '37846': {'constellation': 'Galileo', 'signal_type': 'E1, E5a, E5b, E6',  'accuracy_m': 1.00, 'orbital_slot': 'Plane A, Slot 1',  'clock_type': 'Passive Hydrogen Maser'},
    '37847': {'constellation': 'Galileo', 'signal_type': 'E1, E5a, E5b, E6',  'accuracy_m': 1.00, 'orbital_slot': 'Plane B, Slot 1',  'clock_type': 'Passive Hydrogen Maser'},
    '38857': {'constellation': 'Galileo', 'signal_type': 'E1, E5a, E5b, E6',  'accuracy_m': 1.00, 'orbital_slot': 'Plane C, Slot 1',  'clock_type': 'Passive Hydrogen Maser'},
    '40128': {'constellation': 'Galileo', 'signal_type': 'E1, E5a, E5b, E6',  'accuracy_m': 1.00, 'orbital_slot': 'Plane A, Slot 2',  'clock_type': 'Passive Hydrogen Maser'},
    '40129': {'constellation': 'Galileo', 'signal_type': 'E1, E5a, E5b, E6',  'accuracy_m': 1.00, 'orbital_slot': 'Plane B, Slot 2',  'clock_type': 'Passive Hydrogen Maser'},
    '40544': {'constellation': 'Galileo', 'signal_type': 'E1, E5a, E5b, E6',  'accuracy_m': 1.00, 'orbital_slot': 'Plane C, Slot 2',  'clock_type': 'Passive Hydrogen Maser'},
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