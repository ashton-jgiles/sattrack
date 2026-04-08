# connection and api imports, jwt, and rate limiting imports
import bcrypt
import logging
from django.conf import settings
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from backend.throttles import RegisterThrottle
from users.services import check_password, get_user_role

logger = logging.getLogger('sattrack')

# maps get_user_role() return values (table names) to display names
ROLE_DISPLAY_MAP = {
    'administrator': 'Administrator',
    'data_analyst':  'Data Analyst',
    'scientist':     'Scientist',
    'amateur':       'Amateur',
}


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
            return Response(
                {'error': 'Username and password required'},
                status=400
            )

        with connection.cursor() as cursor:
            # get user from the database
            cursor.execute("SELECT username, password, full_name, level_access FROM user WHERE username = %s", [username])
            row = cursor.fetchone()

            # if no user exists in the database
            if not row:
                logger.info(f"[Auth] Failed login attempt for unknown user '{username}'")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=401
                )

            retrieved_username, retrieved_password, full_name, level_access = row

            # check password
            if not check_password(password, retrieved_password):
                logger.info(f"[Auth] Failed login attempt for user '{username}' (bad password)")
                return Response(
                    {'error': 'Invalid credentials'},
                    status=401
                )

            # get role from sub-tables
            role = get_user_role(cursor, username)

        # generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken

        # create a simple token payload without Django's User model
        refresh = RefreshToken()
        refresh['username'] = username
        refresh['role'] = role
        refresh['level_access'] = level_access
        refresh['full_name'] = full_name

        logger.info(f"[Auth] User '{username}' logged in successfully (role={role})")

        # set tokens as httpOnly cookies — not readable by JavaScript
        # secure follows DEBUG: False in dev, True when served over HTTPS in production
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
            secure=not settings.DEBUG,
        )
        response.set_cookie(
            'refresh_token', str(refresh),
            max_age=7 * 24 * 60 * 60,
            httponly=True,
            samesite='Lax',
            secure=not settings.DEBUG,
        )
        return response


# create account view to create a users account and check for conflicts
class CreateAccountView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def post(self, request):
        username = request.data.get('username')
        full_name = request.data.get('full_name')
        password = request.data.get('password')

        # check for missing fields
        if not username or not full_name or not password:
            return Response(
                {'error': 'Username, full name and password are required'},
                status=400
            )

        # enforce minimum password length
        if len(password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=400)

        # wrap both inserts in a transaction so a failed amateur insert doesn't leave an orphaned user row
        with transaction.atomic(), connection.cursor() as cursor:
            # check for duplicate username
            cursor.execute("SELECT username FROM user WHERE username = %s", [username])
            if cursor.fetchone():
                return Response(
                    {'error': 'Username already taken'},
                    status=409
                )

            # hash the password before storing
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
        return Response(
            {'message': 'Account Created Successfully'},
            status=201
        )


# get users view to list all users — requires level 3+
class GetUsers(APIView):
    def get(self, request):
        if getattr(request.user, 'level_access', 0) < 3:
            return Response({'error': 'Insufficient permissions'}, status=403)

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
                        WHEN s.username  IS NOT NULL THEN 'Scientist'
                        ELSE 'Unknown'
                    END AS user_type
                FROM user u
                    LEFT JOIN administrator ad ON u.username = ad.username
                    LEFT JOIN amateur       am ON u.username = am.username
                    LEFT JOIN data_analyst  da ON u.username = da.username
                    LEFT JOIN scientist     s  ON u.username = s.username
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(data)


# get user profile view to fetch a single user — requires level 3+
class GetUserProfile(APIView):
    def get(self, request, username):
        if getattr(request.user, 'level_access', 0) < 3:
            return Response({'error': 'Insufficient permissions'}, status=403)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    u.username,
                    u.full_name,
                    u.level_access,
                    CASE
                        WHEN ad.username IS NOT NULL THEN 'Administrator'
                        WHEN am.username IS NOT NULL THEN 'Amateur'
                        WHEN da.username IS NOT NULL THEN 'Data Analyst'
                        WHEN s.username  IS NOT NULL THEN 'Scientist'
                        ELSE 'Unknown'
                    END AS user_type
                FROM user u
                    LEFT JOIN administrator ad ON u.username = ad.username
                    LEFT JOIN amateur       am ON u.username = am.username
                    LEFT JOIN data_analyst  da ON u.username = da.username
                    LEFT JOIN scientist     s  ON u.username = s.username
                WHERE u.username = %s
            """, [username])
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()

            if not row:
                return Response({'error': 'user not found'}, status=404)

            data = dict(zip(columns, row))

            # fetch subtype-specific fields
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
        return Response(data)


# modify user class to change an existing user's role, level, and subtype data — requires level 4
class ModifyUser(APIView):
    # maps display name to table name
    TYPE_TABLE_MAP = {
        'Administrator': 'administrator',
        'Data Analyst':  'data_analyst',
        'Scientist':     'scientist',
        'Amateur':       'amateur',
    }
    # default values for NOT NULL columns when inserting into a new type table
    TYPE_INSERT = {
        'administrator': ("INSERT INTO administrator (username, employee_id) VALUES (%s, %s)", 0),
        'data_analyst':  ("INSERT INTO data_analyst  (username, employee_id) VALUES (%s, %s)", 0),
        'scientist':     ("INSERT INTO scientist      (username, profession)  VALUES (%s, %s)", ''),
        'amateur':       ("INSERT INTO amateur        (username, interests)   VALUES (%s, %s)", None),
    }

    def post(self, request):
        if getattr(request.user, 'level_access', 0) < 4:
            return Response({'error': 'Insufficient permissions'}, status=403)

        original_username = request.data.get('original_username')
        level_access = request.data.get('level_access')
        user_type = request.data.get('user_type')
        subtype_data = request.data.get('subtype_data', {})

        if not original_username:
            return Response({'error': 'original_username is required'}, status=400)

        # validate level_access is a recognised access level
        if level_access not in (1, 2, 3, 4):
            return Response({'error': 'level_access must be 1, 2, 3, or 4'}, status=400)

        new_table = self.TYPE_TABLE_MAP.get(user_type)
        if not new_table:
            return Response({'error': 'Invalid user_type'}, status=400)

        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SELECT username FROM user WHERE username = %s", [original_username])
            if not cursor.fetchone():
                return Response({'error': 'User not found'}, status=404)

            cursor.execute(
                "UPDATE user SET level_access = %s WHERE username = %s",
                [level_access, original_username]
            )

            # use the shared service helper instead of reimplementing the lookup
            current_table = get_user_role(cursor, original_username)

            if current_table != new_table:
                if current_table:
                    cursor.execute(f"DELETE FROM {current_table} WHERE username = %s", [original_username])
                sql, default_val = self.TYPE_INSERT[new_table]
                cursor.execute(sql, [original_username, default_val])

            # update subtype-specific fields if provided
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

        logger.info(f"[Auth] User '{original_username}' updated by '{request.user.username}' (type={user_type}, level={level_access})")
        return Response({'message': 'User updated successfully'})


# update own profile — allows the authenticated user to change their own username, name, and subtype fields
class UpdateOwnProfile(APIView):
    def post(self, request):
        current_username = request.user.username
        new_username = request.data.get('username', '').strip()
        full_name = request.data.get('full_name', '').strip()
        subtype_data = request.data.get('subtype_data', {})

        if not full_name:
            return Response({'error': 'full_name is required'}, status=400)
        if not new_username:
            return Response({'error': 'username is required'}, status=400)

        username_changed = new_username != current_username

        with transaction.atomic(), connection.cursor() as cursor:
            if username_changed:
                cursor.execute("SELECT username FROM user WHERE username = %s", [new_username])
                if cursor.fetchone():
                    return Response({'error': 'Username already taken'}, status=409)

            cursor.execute(
                "UPDATE user SET full_name = %s WHERE username = %s",
                [full_name, current_username]
            )

            if username_changed:
                # FK checks are disabled then immediately re-enabled in a try/finally
                # to guarantee they're restored even if an exception is raised mid-rename.
                # Note: FOREIGN_KEY_CHECKS is a session variable and is NOT rolled back by
                # the transaction — the finally block is the only reliable way to restore it.
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                try:
                    cursor.execute(
                        "UPDATE user SET username = %s WHERE username = %s",
                        [new_username, current_username]
                    )
                    for table in ['administrator', 'data_analyst', 'scientist', 'amateur']:
                        cursor.execute(
                            f"UPDATE {table} SET username = %s WHERE username = %s",
                            [new_username, current_username]
                        )
                    cursor.execute(
                        "UPDATE reviews SET reviewed_by = %s WHERE reviewed_by = %s",
                        [new_username, current_username]
                    )
                    cursor.execute(
                        "UPDATE uploads SET uploaded_by = %s WHERE uploaded_by = %s",
                        [new_username, current_username]
                    )
                finally:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            # use new_username after rename; current_username otherwise
            active_username = new_username if username_changed else current_username

            # use the shared service helper instead of reimplementing the subtype lookup
            role_table = get_user_role(cursor, active_username)
            user_type = ROLE_DISPLAY_MAP.get(role_table)

            # update subtype-specific fields if provided
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

        return Response({
            'message': 'Profile updated successfully',
            'full_name': full_name,
            'username': new_username,
            'username_changed': username_changed,
        })


# change password class to change a users account password
class ChangePassword(APIView):
    def post(self, request):
        username = request.user.username
        old_password = request.data.get('old_password', '')
        new_password = request.data.get('new_password', '')

        if not old_password or not new_password:
            return Response({'error': 'Both old and new passwords are required'}, status=400)

        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters'}, status=400)

        with connection.cursor() as cursor:
            cursor.execute("SELECT password FROM user WHERE username = %s", [username])
            row = cursor.fetchone()
            if not row:
                return Response({'error': 'User not found'}, status=404)

            if not check_password(old_password, row[0]):
                return Response({'error': 'Current password is incorrect'}, status=400)

            hashed = bcrypt.hashpw(
                new_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            cursor.execute(
                "UPDATE user SET password = %s WHERE username = %s",
                [hashed, username]
            )

        logger.info(f"[Auth] User '{username}' changed their password")
        return Response({'message': 'Password changed successfully'})


# delete user class to remove a user from the database — requires level 4
class DeleteUser(APIView):
    def delete(self, request, username):
        if getattr(request.user, 'level_access', 0) < 4:
            return Response({'error': 'Insufficient permissions'}, status=403)

        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SELECT username FROM user WHERE username = %s", [username])
            if not cursor.fetchone():
                return Response({'error': 'User not found'}, status=404)

            # clear dependent records before removing subtype rows
            cursor.execute("DELETE FROM reviews WHERE reviewed_by = %s", [username])
            cursor.execute("DELETE FROM uploads WHERE uploaded_by = %s", [username])

            for table in ['administrator', 'data_analyst', 'scientist', 'amateur']:
                cursor.execute(f"DELETE FROM {table} WHERE username = %s", [username])

            cursor.execute("DELETE FROM user WHERE username = %s", [username])

        logger.info(f"[Auth] User '{username}' deleted by '{request.user.username}'")
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
            secure=not settings.DEBUG,
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
        # attempt to extract the username from the access token cookie for audit logging
        try:
            from rest_framework_simplejwt.tokens import UntypedToken
            raw = request.COOKIES.get('access_token')
            if raw:
                token = UntypedToken(raw)
                logger.info(f"[Auth] User '{token.get('username', 'unknown')}' logged out")
            else:
                logger.info("[Auth] User logged out (no token present)")
        except Exception:
            logger.info("[Auth] User logged out")
        return response
