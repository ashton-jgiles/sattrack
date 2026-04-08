# bcrypt import for password hashing
import bcrypt
import logging

# create the logger
logger = logging.getLogger('sattrack')

# check password function to check if the users password is correct
def check_password(plain, hashed):
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8'),
    )

# get user role function to get the subclass type of the user
def get_user_role(cursor, username):
    for role, table in [
        ('administrator', 'administrator'),
        ('data_analyst',  'data_analyst'),
        ('scientist',     'scientist'),
        ('amateur',       'amateur'),
    ]:
        # get the username from the associated subclass table
        cursor.execute(f"SELECT username FROM {table} WHERE username = %s", [username])
        if cursor.fetchone():
            return role

    # warning for if use has not subclass
    logger.warning(f"[Auth] No subtype row found for user '{username}' — data integrity issue")
    return None
