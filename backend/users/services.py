# bcrypt import for password hashing
import bcrypt
import logging

logger = logging.getLogger('sattrack')


def check_password(plain, hashed):
    """Return True if the plain-text password matches the bcrypt hash."""
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8'),
    )


def get_user_role(cursor, username):
    """
    Determine a user's role by checking each subclass table in priority order.
    Returns the table/role key ('administrator', 'data_analyst', 'scientist', 'amateur')
    or None if the user has no subtype row.

    A None return indicates a data integrity issue (user exists in `user` table
    but has no matching subtype row). This is logged as a warning so it surfaces
    in the logs without crashing the caller.
    """
    for role, table in [
        ('administrator', 'administrator'),
        ('data_analyst',  'data_analyst'),
        ('scientist',     'scientist'),
        ('amateur',       'amateur'),
    ]:
        cursor.execute(f"SELECT username FROM {table} WHERE username = %s", [username])
        if cursor.fetchone():
            return role

    logger.warning(f"[Auth] No subtype row found for user '{username}' — data integrity issue")
    return None
