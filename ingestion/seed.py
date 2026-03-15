# imports
from datetime import datetime
import celestrak
from config import get_connection
from db_helpers import record_exists, get_satellite_id


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

# data insertion functions

# seed the owners table
def seed_owners(cursor):
    print("[Seed] Inserting satellite owners...")
    for owner in OWNERS:
        if record_exists(cursor, 'satellite_owner', {'owner_name': owner['owner_name']}):
            print(f"[Seed] Owner {owner['owner_name']} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO satellite_owner (
                owner_name, owner_phone, owner_address,
                country, operator, owner_type
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                owner['owner_name'],
                owner['owner_phone'],
                owner['owner_address'],
                owner['country'],
                owner['operator'],
                owner['owner_type'],
            )
        )
        print(f"[Seed] Inserted owner {owner['owner_name']}")

# seed the launch sites table
def seed_launch_sites(cursor):
    print("[Seed] Inserting launch sites...")
    for site in LAUNCH_SITES:
        if record_exists(cursor, 'launch_site', {'site_name': site['site_name']}):  # ← site_name not location
            print(f"[Seed] Launch site {site['site_name']} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO launch_site (location, climate, site_name, country)
            VALUES (%s, %s, %s, %s)
            """,
            (site['location'], site['climate'], site['site_name'], site['country'])
        )
        print(f"[Seed] Inserted launch site {site['site_name']}")

# seed the launch vehicles table
def seed_launch_vehicles(cursor):
    print("[Seed] Inserting launch vehicles...")
    for vehicle in LAUNCH_VEHICLES:
        if record_exists(cursor, 'launch_vehicle', {'vehicle_name': vehicle['vehicle_name']}):
            print(f"[Seed] Vehicle {vehicle['vehicle_name']} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO launch_vehicle (
                vehicle_name, manufacturer, reusable,
                country, payload_capacity
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (
                vehicle['vehicle_name'],
                vehicle['manufacturer'],
                vehicle['reusable'],
                vehicle['country'],
                vehicle['payload_capacity'],
            )
        )
        print(f"[Seed] Inserted vehicle {vehicle['vehicle_name']}")

# seed the users table
def seed_users(cursor):
    print("[Seed] Inserting users...")
    for user in USERS:
        if record_exists(cursor, 'user', {'username': user['username']}):
            print(f"[Seed] User {user['username']} already exists — skipping")
            continue

        cursor.execute(
            """
            INSERT INTO user (username, password, full_name, level_access)
            VALUES (%s, %s, %s, %s)
            """,
            (user['username'], user['password'], user['full_name'], user['level_access'])
        )

        if user['type'] == 'administrator':
            cursor.execute(
                "INSERT INTO administrator (username, employee_id) VALUES (%s, %s)",
                (user['username'], user['employee_id'])
            )
        elif user['type'] == 'data_analyst':
            cursor.execute(
                "INSERT INTO data_analyst (username, employee_id) VALUES (%s, %s)",
                (user['username'], user['employee_id'])
            )
        elif user['type'] == 'scientist':
            cursor.execute(
                "INSERT INTO scientist (username, profession) VALUES (%s, %s)",
                (user['username'], user['profession'])
            )
        elif user['type'] == 'amateur':
            cursor.execute(
                "INSERT INTO amateur (username, interests) VALUES (%s, %s)",
                (user['username'], user['interests'])
            )

        print(f"[Seed] Inserted user {user['username']} ({user['type']})")

# seed the communication stations table
def seed_communication_stations(cursor):
    print("[Seed] Inserting communication stations...")
    for station in COMMUNICATION_STATIONS:
        if record_exists(cursor, 'communication_station', {'location': station['location']}):
            print(f"[Seed] Station {station['name']} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO communication_station (
                location, name
            ) VALUES (%s, %s)
            """,
            (station['location'], station['name'])
        )
        print(f"[Seed] Inserted station {station['name']}")

# resolve the foreign keys for satellite owners in satellite
def seed_satellite_owners(cursor):
    print("[Seed] Resolving satellite owner foreign keys...")
    for norad_id, owner_name in SATELLITE_OWNER_MAP.items():

        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping owner update")
            continue

        cursor.execute(
            "SELECT owner_id FROM satellite_owner WHERE owner_name = %s",
            (owner_name,)
        )
        row = cursor.fetchone()
        if not row:
            print(f"[Seed] Owner {owner_name} not found — skipping")
            continue

        owner_id = row[0]
        cursor.execute(
            "UPDATE satellite SET owner_id = %s WHERE satellite_id = %s",
            (owner_id, satellite_id)
        )
        print(f"[Seed] Linked {norad_id} to {owner_name}")

# seed the launched from table
def seed_launched_from(cursor):
    print("[Seed] Inserting launched_from records...")
    for norad_id, data in DEPLOYS_PAYLOAD_MAP.items():

        # get vehicle_id
        cursor.execute(
            "SELECT vehicle_id FROM launch_vehicle WHERE vehicle_name = %s",
            (data['vehicle'],)
        )
        row = cursor.fetchone()
        if not row:
            print(f"[Seed] Vehicle {data['vehicle']} not found — skipping")
            continue
        vehicle_id = row[0]

        # check if already exists
        if record_exists(cursor, 'launched_from', {
            'vehicle_id':  vehicle_id,
            'site_name':   data['site_name'],
            'launch_date': data['date'],
        }):
            print(f"[Seed] launched_from {norad_id} already exists — skipping")
            continue

        cursor.execute(
            """
            INSERT INTO launched_from (vehicle_id, site_name, launch_date)
            VALUES (%s, %s, %s)
            """,
            (vehicle_id, data['site_name'], data['date'])
        )
        print(f"[Seed] Inserted launched_from for {norad_id}")

# seed the deploys payload table
def seed_deploys_payload(cursor):
    print("[Seed] Inserting deploys_payload records...")
    for norad_id, data in DEPLOYS_PAYLOAD_MAP.items():

        # get vehicle_id
        cursor.execute(
            "SELECT vehicle_id FROM launch_vehicle WHERE vehicle_name = %s",
            (data['vehicle'],)
        )
        row = cursor.fetchone()
        if not row:
            print(f"[Seed] Vehicle {data['vehicle']} not found — skipping")
            continue
        vehicle_id = row[0]

        # get satellite_id
        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping")
            continue

        # check if already exists
        if record_exists(cursor, 'deploys_payload', {
            'vehicle_id':   vehicle_id,
            'satellite_id': satellite_id,
        }):
            print(f"[Seed] deploys_payload {norad_id} already exists — skipping")
            continue

        cursor.execute(
            """
            INSERT INTO deploys_payload (vehicle_id, satellite_id, deploy_date_time)
            VALUES (%s, %s, %s)
            """,
            (vehicle_id, satellite_id, f"{data['date']} 00:00:00")
        )
        print(f"[Seed] Inserted deploys_payload for {norad_id}")

# seed the communicates_with table
def seed_communicates_with(cursor):
    print("[Seed] Inserting communicates_with records...")
    for norad_id, data in COMMUNICATES_WITH_MAP.items():

        # get location from communication_station
        cursor.execute(
            "SELECT location FROM communication_station WHERE location = %s",
            (data['location'],)
        )
        row = cursor.fetchone()
        if not row:
            print(f"[Seed] Communication Station {data['location']} not found — skipping")
            continue
        location = row[0]

        # get satellite_id
        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping")
            continue

        # check if already exists
        if record_exists(cursor, 'communicates_with', {
            'location':     location,
            'satellite_id': satellite_id,
        }):
            print(f"[Seed] communicates_with {norad_id} already exists — skipping")
            continue

        cursor.execute(
            """
            INSERT INTO communicates_with (location, satellite_id, communication_frequency)
            VALUES (%s, %s, %s)
            """,
            (location, satellite_id, data['frequency'])
        )
        print(f"[Seed] Inserted communicates_with for {norad_id}")

# main run method
def run():
    # track the straci time
    start = datetime.now()

    print("========================================")
    print("  SatTrack — Database Seed")
    print("========================================")

    # test DB connection
    print("\n[Seed] Testing database connection...")
    try:
        conn = get_connection()
        conn.close()
        print("[Seed] Database connection successful")
    except Exception as e:
        print(f"[Seed] Database connection failed: {e}")
        return

    # open connection for static data
    conn   = get_connection()
    cursor = conn.cursor()

    # seed the owners
    print("\n[1/10] Seeding satellite owners...")
    seed_owners(cursor)
    conn.commit()

    # seed the launch sites
    print("\n[2/10] Seeding launch sites...")
    seed_launch_sites(cursor)
    conn.commit()

    # seed the launch vehicles
    print("\n[3/10] Seeding launch vehicles...")
    seed_launch_vehicles(cursor)
    conn.commit()

    # seed the users
    print("\n[4/10] Seeding users...")
    seed_users(cursor)
    conn.commit()

    # seed the communication
    print("\n[5/10] Seeding communication stations...")
    seed_communication_stations(cursor)
    conn.commit()

    cursor.close()
    conn.close()

    # seed the celestrak data for all satellites and create their trajectories
    print("\n[6/10] Running CelesTrak ingestion...")
    celestrak.run()

    # reopen connection after celestrak finishes
    conn   = get_connection()
    cursor = conn.cursor()

    # resolve the satellite owner foreign keys
    print("\n[7/10] Resolving satellite owner foreign keys...")
    seed_satellite_owners(cursor)
    conn.commit()

    # seed the launch from table
    print("\n[8/10] Inserting launched_from records...")
    seed_launched_from(cursor)
    conn.commit()

    # seed the deploys payload table
    print("\n[9/10] Inserting deploys_payload records...")
    seed_deploys_payload(cursor)
    conn.commit()

    print("\n[10/10] Inserting communicates_with records...")
    seed_communicates_with(cursor)
    conn.commit()

    cursor.close()
    conn.close()

    # compute the seed time and end the seed function
    elapsed = (datetime.now() - start).seconds
    print(f"\n========================================")
    print(f"  Seed complete in {elapsed}s")
    print(f"========================================")


if __name__ == "__main__":
    run()