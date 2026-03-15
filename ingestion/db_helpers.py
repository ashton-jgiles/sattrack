# import date time
from datetime import datetime

# get satellite method
def get_satellite_id(cursor, norad_id):
    # select the satellite id where the norad id equals the passed in id
    cursor.execute(
        "SELECT satellite_id FROM satellite WHERE norad_id = %s",
        (norad_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else None

# satellite exists function
def satellite_exists(cursor, norad_id):
    # return if there is a satellite at the norad id
    return get_satellite_id(cursor, norad_id)

# ensure dataset method
def ensure_dataset(cursor, source, name, description, url, frequency):
    # select the dataset id from the source
    cursor.execute(
        "SELECT dataset_id FROM dataset WHERE source = %s LIMIT 1",
        (source,)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # insert into the dataset an approved status
    cursor.execute(
        """
        INSERT INTO dataset (
            dataset_name,
            description,
            creation_date,
            source,
            source_url,
            pull_frequency,
            review_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            name,
            description,
            datetime.now().date(),
            source,
            url,
            frequency,
            'approved'
        )
    )
    return cursor.lastrowid

# record exists function
def record_exists(cursor, table, conditions):
    # check if a reocrd exists in a table
    where = ' AND '.join(f"`{col}` = %s" for col in conditions)
    values = list(conditions.values())
    cursor.execute(
        f"SELECT 1 FROM `{table}` WHERE {where} LIMIT 1",
        values
    )
    return cursor.fetchone() is not None