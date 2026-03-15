from datetime import datetime

def get_satellite_id(cursor, norad_id):
    cursor.execute(
        "SELECT satelite_id FROM satellite WHERE norad_id = %s",
        (norad_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else None

def satellite_exists(cursor, norad_id):
    return get_satellite_id(cursor, norad_id)

def ensure_dataset(cursor, source, name, description, url, frequency):
    cursor.execute(
        "SELECT dataset_id FROM dataset WHERE source = %s LIMIT 1",
        (source,)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    
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

def record_exists(cursor, table, conditions):
    where  = ' AND '.join(f"`{col}` = %s" for col in conditions)
    values = list(conditions.values())
    cursor.execute(
        f"SELECT 1 FROM `{table}` WHERE {where} LIMIT 1",
        values
    )
    return cursor.fetchone() is not None