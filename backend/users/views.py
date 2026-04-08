# connection and api imports, jwt, hashing, and rate limiting imports
import bcrypt
import logging
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from backend.throttles import RegisterThrottle

logger = logging.getLogger('sattrack')

# check password method
def check_password(plain, hashed):
    # check the password to see if they match
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8')
    )

# get user role method to get the role subclass of a user
def get_user_role(cursor, username):
    # Check each sub-table to determine role
    for role, table in [
        ('administrator', 'administrator'),
        ('data_analyst', 'data_analyst'),
        ('scientist', 'scientist'),
        ('amateur', 'amateur'),
    ]:
        # get the username from the database
        cursor.execute(f"SELECT username FROM {table} WHERE username = %s", [username])
        # if there is a username return the role of the user
        if cursor.fetchone():
            return role
    # other wise nothing is returned
    return None

# login view class to log the user in and generate the JWT token
class LoginView(APIView):
    # setup the auth and permission classes
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        # get the username and password
        username = request.data.get('username')
        password = request.data.get('password')

        # check both values exists
        if not username or not password:
            # if not return an error response
            return Response(
                {'error': 'Username and password required'},
                status=400
            )

        with connection.cursor() as cursor:
            # Get user from the database
            cursor.execute("SELECT username, password, full_name, level_access FROM user WHERE username = %s", [username])
            row = cursor.fetchone()

            # if now user exists in the database
            if not row:
                logger.info(f"[Auth] Failed login attempt for unknown user '{username}'")
                # return an error response for invalid credentials
                return Response(
                    {'error': 'Invalid credentials'},
                    status=401
                )

            # create
            retrived_username, retrived_password, full_name, level_access = row

            # Check password
            if not check_password(password, retrived_password):
                logger.info(f"[Auth] Failed login attempt for user '{username}' (bad password)")
                # if the password is incorrect return an error response
                return Response(
                    {'error': 'Invalid credentials'},
                    status=401
                )

            # Get role from sub-tables
            role = get_user_role(cursor, username)

        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.contrib.auth.models import User as DjangoUser

        # Create a simple token payload without Django's User model
        refresh = RefreshToken()
        refresh['username'] = username
        refresh['role'] = role
        refresh['level_access'] = level_access
        refresh['full_name'] = full_name

        logger.info(f"[Auth] User '{username}' logged in successfully (role={role})")

        # set tokens as httpOnly cookies — not readable by JavaScript
        # secure=False is acceptable for local/Docker dev; set True when serving over HTTPS
        response = Response({
            'username': username,
            'full_name': full_name,
            'role': role,
            'level_access': level_access,
        })
        response.set_cookie(
            'access_token', str(refresh.access_token),
            max_age=30 * 60,
            httponly=True,
            samesite='Lax',
            secure=False,
        )
        response.set_cookie(
            'refresh_token', str(refresh),
            max_age=7 * 24 * 60 * 60,
            httponly=True,
            samesite='Lax',
            secure=False,
        )
        return response

# create account view to create a users account and check for conflicts
class CreateAccountView(APIView):
    # create the authentication classes
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        # key values to insert into the users table
        username = request.data.get('username')
        full_name = request.data.get('full_name')
        password = request.data.get('password')

        # check for missing fields
        if not username or not full_name or not password:
            # return an error response for username and password being required
            return Response(
                {'error': 'Username, full name and password are required'},
                status=400
            )

        # enforce minimum password length (same requirement as ChangePassword)
        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=400)

        with connection.cursor() as cursor:
            # check for deuplicate username
            cursor.execute("SELECT username FROM user WHERE username = %s", [username])
            # if the usename is a duplicated return a conflict error response
            if cursor.fetchone():
                return Response(
                    {'error': 'Username already taken'},
                    status=409
                )
            
            # hash the pasword to insert into the database
            hashed = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            # insert the user into the database
            cursor.execute(
                "INSERT INTO user (username, password, full_name, level_access) VALUES (%s, %s, %s, %s)",
                [username, hashed, full_name, 1]
            )
            
            # insert the new user subclass entry
            cursor.execute("INSERT INTO amateur (username, interests) VALUES (%s, %s)", [username, None])


        logger.info(f"[Auth] New account registered: '{username}'")
        # return a success response
        return Response(
            {'message': 'Account Created Successfully'},
            status=201
        )
    
class GetUsers(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            # get all the users and their subclass type as a column
            cursor.execute("""
                SELECT 
                    u.full_name, 
                    u.username, 
                    u.level_access,
                    CASE
                        WHEN ad.username IS NOT NULL THEN 'Administrator'
                        WHEN am.username IS NOT NULL THEN 'Amateur'
                        WHEN da.username IS NOT NULL THEN 'Data Analyst'
                        WHEN s.username IS NOT NULL THEN 'Scientist'
                        ELSE 'Unknown'
                    END AS user_type
                FROM user u
                    LEFT JOIN administrator ad ON u.username = ad.username
                    LEFT JOIN amateur am ON u.username = am.username
                    LEFT JOIN data_analyst da ON u.username = da.username
                    LEFT JOIN scientist s ON u.username = s.username
                """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        # return the user data
        return Response(data)
    
class GetUserProfile(APIView):
    def get(self, request, username):
        with connection.cursor() as cursor:
            # select a specific user name and their user type from the database
            cursor.execute("""
                SELECT
                    u.username,
                    u.full_name,
                    u.level_access,
                    CASE
                        WHEN ad.username IS NOT NULL THEN 'Administrator'
                        WHEN am.username IS NOT NULL THEN 'Amateur'
                        WHEN da.username IS NOT NULL THEN 'Data Analyst'
                        WHEN s.username IS NOT NULL THEN 'Scientist'
                        ELSE 'Unknown'
                    END AS user_type
                FROM user u
                    LEFT JOIN administrator ad ON u.username = ad.username
                    LEFT JOIN amateur am ON u.username = am.username
                    LEFT JOIN data_analyst da ON u.username = da.username
                    LEFT JOIN scientist s ON u.username = s.username
                WHERE u.username = %s""", [username])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

            # if no user is found return an error response
            if not row:
                return Response({'error': 'user not found'}, status=404)

            data = dict(zip(columns, row))

            # Fetch subtype-specific fields
            subtype_data = {}
            user_type = data['user_type']
            if user_type in ('Administrator', 'Data Analyst'):
                table = 'administrator' if user_type == 'Administrator' else 'data_analyst'
                cursor.execute(f"SELECT employee_id FROM {table} WHERE username = %s", [username])
                r = cursor.fetchone()
                if r:
                    subtype_data['employee_id'] = r[0]
            elif user_type == 'Scientist':
                cursor.execute("SELECT profession FROM scientist WHERE username = %s", [username])
                r = cursor.fetchone()
                if r:
                    subtype_data['profession'] = r[0]
            elif user_type == 'Amateur':
                cursor.execute("SELECT interests FROM amateur WHERE username = %s", [username])
                r = cursor.fetchone()
                if r:
                    subtype_data['interests'] = r[0]

        data['subtype_data'] = subtype_data
        # return the user data and subtype data
        return Response(data)

# modify user class to change an existing users data 
class ModifyUser(APIView):
    # create a table map
    TYPE_TABLE_MAP = {
        'Administrator': 'administrator',
        'Data Analyst':  'data_analyst',
        'Scientist':     'scientist',
        'Amateur':       'amateur',
    }
    # default values for NOT NULL columns when inserting into a new type table
    TYPE_INSERT = {
        'administrator': ("INSERT INTO administrator (username, employee_id) VALUES (%s, %s)", 0),
        'data_analyst':  ("INSERT INTO data_analyst (username, employee_id) VALUES (%s, %s)", 0),
        'scientist':     ("INSERT INTO scientist (username, profession) VALUES (%s, %s)", ''),
        'amateur':       ("INSERT INTO amateur (username, interests) VALUES (%s, %s)", None),
    }

    def post(self, request):
        # get the original values from the request
        original_username = request.data.get('original_username')
        level_access = request.data.get('level_access')
        user_type = request.data.get('user_type')
        subtype_data = request.data.get('subtype_data', {})

        # check to see that the user sent their original usename and return an error response if they didnt
        if not original_username:
            return Response({'error': 'original_username is required'}, status=400)

        # check the user type is valid
        new_table = self.TYPE_TABLE_MAP.get(user_type)
        if not new_table:
            return Response({'error': 'Invalid user_type'}, status=400)

        # get the original username actually exists in the database
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SELECT username FROM user WHERE username = %s", [original_username])
            if not cursor.fetchone():
                return Response({'error': 'User not found'}, status=404)

            # update the access level of the user
            cursor.execute(
                "UPDATE user SET level_access = %s WHERE username = %s",
                [level_access, original_username]
            )

            # find current subtype table
            current_table = None
            for table in ['administrator', 'data_analyst', 'scientist', 'amateur']:
                cursor.execute(f"SELECT username FROM {table} WHERE username = %s", [original_username])
                if cursor.fetchone():
                    current_table = table
                    break

            if current_table != new_table:
                if current_table:
                    cursor.execute(f"DELETE FROM {current_table} WHERE username = %s", [original_username])
                sql, default_val = self.TYPE_INSERT[new_table]
                cursor.execute(sql, [original_username, default_val])

            # Update subtype-specific fields if provided
            if new_table in ('administrator', 'data_analyst') and 'employee_id' in subtype_data:
                cursor.execute(
                    f"UPDATE {new_table} SET employee_id = %s WHERE username = %s",
                    [subtype_data['employee_id'], original_username]
                )
            elif new_table == 'scientist' and 'profession' in subtype_data:
                cursor.execute(
                    "UPDATE scientist SET profession = %s WHERE username = %s",
                    [subtype_data['profession'], original_username]
                )

        logger.info(f"[Auth] User '{original_username}' updated (type={user_type}, level={level_access})")
        # return a success response if the user is updated successfully
        return Response({'message': 'User updated successfully'})


# update own profile class to change just a specific user that only the user can access
class UpdateOwnProfile(APIView):
    def post(self, request):
        # get the current values from the request
        current_username = request.user.username
        new_username = request.data.get('username', '').strip()
        full_name = request.data.get('full_name', '').strip()
        subtype_data = request.data.get('subtype_data', {})

        # check all values exists
        if not full_name:
            return Response({'error': 'full_name is required'}, status=400)
        if not new_username:
            return Response({'error': 'username is required'}, status=400)

        # check the user that the usernames do not match so its a real change
        username_changed = new_username != current_username

        with transaction.atomic(), connection.cursor() as cursor:
            # Check new username isn't already taken
            if username_changed:
                cursor.execute("SELECT username FROM user WHERE username = %s", [new_username])
                if cursor.fetchone():
                    return Response({'error': 'Username already taken'}, status=409)

            # update the username if its not taken
            cursor.execute(
                "UPDATE user SET full_name = %s WHERE username = %s",
                [full_name, current_username]
            )

            # check if the username is changed
            if username_changed:
                # Temporarily disable FK checks so we can rename the PK
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute(
                    "UPDATE user SET username = %s WHERE username = %s",
                    [new_username, current_username]
                )
                # update the subclass tables
                for table in ['administrator', 'data_analyst', 'scientist', 'amateur']:
                    cursor.execute(
                        f"UPDATE {table} SET username = %s WHERE username = %s",
                        [new_username, current_username]
                    )
                # update the revies table
                cursor.execute(
                    "UPDATE reviews SET reviewed_by = %s WHERE reviewed_by = %s",
                    [new_username, current_username]
                )
                # update the uploads table
                cursor.execute(
                    "UPDATE uploads SET uploaded_by = %s WHERE uploaded_by = %s",
                    [new_username, current_username]
                )
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            # Determine user's current subtype table (use new_username after rename)
            active_username = new_username if username_changed else current_username
            user_type = None
            for role, table in [
                ('Administrator', 'administrator'),
                ('Data Analyst',  'data_analyst'),
                ('Scientist',     'scientist'),
                ('Amateur',       'amateur'),
            ]:
                cursor.execute(f"SELECT username FROM {table} WHERE username = %s", [active_username])
                if cursor.fetchone():
                    user_type = role
                    break

            # Update subtype-specific fields
            if user_type in ('Administrator', 'Data Analyst'):
                table = 'administrator' if user_type == 'Administrator' else 'data_analyst'
                if 'employee_id' in subtype_data:
                    cursor.execute(
                        f"UPDATE {table} SET employee_id = %s WHERE username = %s",
                        [subtype_data['employee_id'], active_username]
                    )
            elif user_type == 'Scientist' and 'profession' in subtype_data:
                cursor.execute(
                    "UPDATE scientist SET profession = %s WHERE username = %s",
                    [subtype_data['profession'], active_username]
                )
            elif user_type == 'Amateur' and 'interests' in subtype_data:
                cursor.execute(
                    "UPDATE amateur SET interests = %s WHERE username = %s",
                    [subtype_data['interests'], active_username]
                )

        # return the success response
        return Response({
            'message': 'Profile updated successfully',
            'full_name': full_name,
            'username': new_username,
            'username_changed': username_changed,
        })


# change password class to change a users account password
class ChangePassword(APIView):
    def post(self, request):
        # user and a password passed by the request
        username = request.user.username
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        # check that all fields are present
        if not old_password or not new_password:
            return Response({'error': 'Both old and new passwords are required'}, status=400)

        # maintain password length requirement
        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=400)

        with connection.cursor() as cursor:
            # get the user this password belongs to
            cursor.execute("SELECT password FROM user WHERE username = %s", [username])
            row = cursor.fetchone()
            # make sure the user exists
            if not row:
                return Response({'error': 'User not found'}, status=404)

            # check the password is correct
            if not check_password(old_password, row[0]):
                return Response({'error': 'Current password is incorrect'}, status=400)

            # hash the new password
            hashed = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            # update the users password in the database
            cursor.execute(
                "UPDATE user SET password = %s WHERE username = %s",
                [hashed, username]
            )

        logger.info(f"[Auth] User '{username}' changed their password")
        # return a success response
        return Response({'message': 'Password changed successfully'})


# delete user class to remove a user from the database 
class DeleteUser(APIView):
    def delete(self, request, username):
        with transaction.atomic(), connection.cursor() as cursor:
            # get the user from the database and make sure it exists
            cursor.execute("SELECT username FROM user WHERE username = %s", [username])
            if not cursor.fetchone():
                return Response({'error': 'User not found'}, status=404)

            # clear dependent records before removing subtype rows
            cursor.execute("DELETE FROM reviews WHERE reviewed_by = %s", [username])
            cursor.execute("DELETE FROM uploads WHERE uploaded_by = %s", [username])

            # remove from all subtype tables
            for table in ['administrator', 'data_analyst', 'scientist', 'amateur']:
                cursor.execute(f"DELETE FROM {table} WHERE username = %s", [username])

            # delete the user from the database
            cursor.execute("DELETE FROM user WHERE username = %s", [username])

        logger.info(f"[Auth] User '{username}' deleted")
        # return success response
        return Response({'message': 'User deleted successfully'})


# refresh token view reads the httpOnly refresh cookie and issues a new access cookie
class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'No refresh token'}, status=401)

        try:
            token = JWTRefreshToken(refresh_token)
            new_access = str(token.access_token)
        except Exception:
            return Response({'error': 'Invalid or expired refresh token'}, status=401)

        response = Response({'message': 'Token refreshed'})
        response.set_cookie(
            'access_token', new_access,
            max_age=30 * 60,
            httponly=True,
            samesite='Lax',
            secure=False,
        )
        return response


# logout view clears the httpOnly auth cookies
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({'message': 'Logged out successfully'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        logger.info("[Auth] User logged out")
        return response
    