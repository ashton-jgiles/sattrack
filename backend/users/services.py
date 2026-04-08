# bcrypt import for password hashing
import bcrypt


def check_password(plain, hashed):
    """Return True if the plain-text password matches the bcrypt hash."""
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8'),
    )


def get_user_role(cursor, username):
    """
    Determine a user's role by checking each subclass table in priority order.
    Returns the role string ('administrator', 'data_analyst', 'scientist', 'amateur')
    or None if the user is not found in any subclass table.
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
    return None
