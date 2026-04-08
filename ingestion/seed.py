# imports
from datetime import datetime
import celestrak
from config import get_connection
from db_helpers import record_exists, get_satellite_id
import bcrypt

# import the static data
from config import (
    OWNERS,
    LAUNCH_SITES,
    LAUNCH_VEHICLES,
    USERS,
    COMMUNICATION_STATIONS,
    SATELLITE_OWNER_MAP,
    DEPLOYS_PAYLOAD_MAP,
    COMMUNICATES_WITH_MAP,
    EARTH_SCIENCE_DATA,
    OCEANIC_SCIENCE_DATA,
    WEATHER_DATA,
    RESEARCH_DATA,
    INTERNET_DATA,
    NAVIGATION_DATA
)
# data insertion functions

# hash password function
def hash_password(plain_password):
    return bcrypt.hashpw(
        plain_password.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')


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
            "INSERT INTO user (username, password, full_name, level_access) VALUES (%s, %s, %s, %s)",
            (user['username'], hash_password(user['password']), user['full_name'], user['level_access'])
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

# seed the earth science table
def seed_earth_science(cursor):
    print("[Seed] Inserting earth_science records...")
    for norad_id, data in EARTH_SCIENCE_DATA.items():
        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping")
            continue
        if record_exists(cursor, 'earth_science', {'satellite_id': satellite_id}):
            print(f"[Seed] earth_science {norad_id} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO earth_science (
                satellite_id, instrument, data_measured,
                wavelength_band, resolution_m, data_archive_url, mission_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (satellite_id, data['instrument'], data['data_measured'],
             data['wavelength_band'], data['resolution_m'],
             data['data_archive_url'], data['mission_status'])
        )
        print(f"[Seed] Inserted earth_science for {norad_id}")

# seed the oceanic science table
def seed_oceanic_science(cursor):
    print("[Seed] Inserting oceanic_science records...")
    for norad_id, data in OCEANIC_SCIENCE_DATA.items():
        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping")
            continue
        if record_exists(cursor, 'oceanic_science', {'satellite_id': satellite_id}):
            print(f"[Seed] oceanic_science {norad_id} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO oceanic_science (
                satellite_id, instrument, data_measured,
                wavelength_band, resolution_m, data_archive_url, mission_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (satellite_id, data['instrument'], data['data_measured'],
             data['wavelength_band'], data['resolution_m'],
             data['data_archive_url'], data['mission_status'])
        )
        print(f"[Seed] Inserted oceanic_science for {norad_id}")

# seed the weather table
def seed_weather(cursor):
    print("[Seed] Inserting weather records...")
    for norad_id, data in WEATHER_DATA.items():
        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping")
            continue
        if record_exists(cursor, 'weather', {'satellite_id': satellite_id}):
            print(f"[Seed] weather {norad_id} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO weather (
                satellite_id, instrument, data_measured, coverage_region,
                imaging_channels, repeat_cycle_min, data_archive_url, mission_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (satellite_id, data['instrument'], data['data_measured'],
             data['coverage_region'], data['imaging_channels'],
             data['repeat_cycle_min'], data['data_archive_url'], data['mission_status'])
        )
        print(f"[Seed] Inserted weather for {norad_id}")

# seed the research table
def seed_research(cursor):
    print("[Seed] Inserting research records...")
    for norad_id, data in RESEARCH_DATA.items():
        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping")
            continue
        if record_exists(cursor, 'research', {'satellite_id': satellite_id}):
            print(f"[Seed] research {norad_id} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO research (
                satellite_id, instrument, data_measured, research_field,
                wavelength_band, data_archive_url, mission_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (satellite_id, data['instrument'], data['data_measured'],
             data['research_field'], data['wavelength_band'],
             data['data_archive_url'], data['mission_status'])
        )
        print(f"[Seed] Inserted research for {norad_id}")

# seed the internet table
def seed_internet(cursor):
    print("[Seed] Inserting internet records...")
    for norad_id, data in INTERNET_DATA.items():
        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping")
            continue
        if record_exists(cursor, 'internet', {'satellite_id': satellite_id}):
            print(f"[Seed] internet {norad_id} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO internet (
                satellite_id, coverage, frequency_band,
                service_type, throughput_gbps, altitude_km
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (satellite_id, data['coverage'], data['frequency_band'],
             data['service_type'], data['throughput_gbps'], data['altitude_km'])
        )
        print(f"[Seed] Inserted internet for {norad_id}")

# seed the navigation table
def seed_navigation(cursor):
    print("[Seed] Inserting navigation records...")
    for norad_id, data in NAVIGATION_DATA.items():
        satellite_id = get_satellite_id(cursor, norad_id)
        if not satellite_id:
            print(f"[Seed] Satellite {norad_id} not found — skipping")
            continue
        if record_exists(cursor, 'navigation', {'satellite_id': satellite_id}):
            print(f"[Seed] navigation {norad_id} already exists — skipping")
            continue
        cursor.execute(
            """
            INSERT INTO navigation (
                satellite_id, constellation, signal_type,
                accuracy_m, orbital_slot, clock_type
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (satellite_id, data['constellation'], data['signal_type'],
             data['accuracy_m'], data['orbital_slot'], data['clock_type'])
        )
        print(f"[Seed] Inserted navigation for {norad_id}")

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
    print("\n[1/16] Seeding satellite owners...")
    seed_owners(cursor)
    conn.commit()

    # seed the launch sites
    print("\n[2/16] Seeding launch sites...")
    seed_launch_sites(cursor)
    conn.commit()

    # seed the launch vehicles
    print("\n[3/16] Seeding launch vehicles...")
    seed_launch_vehicles(cursor)
    conn.commit()

    # seed the users
    print("\n[4/16] Seeding users...")
    seed_users(cursor)
    conn.commit()

    # seed the communication
    print("\n[5/16] Seeding communication stations...")
    seed_communication_stations(cursor)
    conn.commit()

    cursor.close()
    conn.close()

    # seed the celestrak data for all satellites and create their trajectories
    print("\n[6/16] Running CelesTrak ingestion...")
    celestrak.run()

    # reopen connection after celestrak finishes
    conn   = get_connection()
    cursor = conn.cursor()

    # resolve the satellite owner foreign keys
    print("\n[7/16] Resolving satellite owner foreign keys...")
    seed_satellite_owners(cursor)
    conn.commit()

    # seed the launch from table
    print("\n[8/16] Inserting launched_from records...")
    seed_launched_from(cursor)
    conn.commit()

    # seed the deploys payload table
    print("\n[9/16] Inserting deploys_payload records...")
    seed_deploys_payload(cursor)
    conn.commit()

    print("\n[10/16] Inserting communicates_with records...")
    seed_communicates_with(cursor)
    conn.commit()


    print("\n[11/16] Inserting earth_science records...")
    seed_earth_science(cursor)
    conn.commit()

    print("\n[12/16] Inserting oceanic_science records...")
    seed_oceanic_science(cursor)
    conn.commit()

    print("\n[13/16] Inserting weather records...")
    seed_weather(cursor)
    conn.commit()

    print("\n[14/16] Inserting research records...")
    seed_research(cursor)
    conn.commit()

    print("\n[15/16] Inserting internet records...")
    seed_internet(cursor)
    conn.commit()

    print("\n[16/16] Inserting navigation records...")
    seed_navigation(cursor)
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
    