# connection and api imports, jwt, and hashing imports
import bcrypt
from django.db import connection, transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from backend.throttles import RegisterThrottle

# check password method
def check_password(plain, hashed):
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
        cursor.execute(f"SELECT username FROM {table} WHERE username = %s", (username,))
        if cursor.fetchone():
            return role
    return None

# login view class to log the user in and generate the JWT token
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Username and password required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with connection.cursor() as cursor:
            # Get user
            cursor.execute(
                "SELECT username, password, full_name, level_access FROM user WHERE username = %s",
                (username,)
            )
            row = cursor.fetchone()

            if not row:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            db_username, db_password, full_name, level_access = row

            # Check password
            if not check_password(password, db_password):
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
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

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': username,
            'full_name': full_name,
            'role': role,
            'level_access': level_access,
        })

# create account view to create a users account and check for conflicts
class CreateAccountView(APIView):
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
            return Response(
                {'error': 'Username, full name and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with connection.cursor() as cursor:
            # check for deuplicate username
            cursor.execute("SELECT username FROM user WHERE username = %s", (username, ))
            if cursor.fetchone():
                return Response(
                    {'error': 'Username already taken'},
                    status=status.HTTP_409_CONFLICT
                )
            
            # hash the pasword to insert into the database
            hashed = bcrypt.hashpw(
                password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')

            cursor.execute(
                "INSERT INTO user (username, password, full_name, level_access) VALUES (%s, %s, %s, %s)",
                (username, hashed, full_name, 1)
            )
            
            # insert the new user
            cursor.execute("INSERT INTO amateur (username, interests) VALUES (%s, %s)", (username, None))


        return Response(
            {'message': 'Account Created Successfully'},
            status=status.HTTP_201_CREATED
        )
    
class GetUsers(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
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
        return Response(data)
    
class GetUserProfile(APIView):
    def get(self, request, username):
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

        if not row:
            return Response({'error': 'user not found'}, status=404)
        
        return Response(dict(zip(columns, row)))
    
class ModifyUser(APIView):
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
        original_username = request.data.get('original_username')
        level_access      = request.data.get('level_access')
        user_type         = request.data.get('user_type')

        if not original_username:
            return Response({'error': 'original_username is required'}, status=400)

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

        return Response({'message': 'User updated successfully'})


class DeleteUser(APIView):
    def delete(self, request, username):
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SELECT username FROM user WHERE username = %s", [username])
            if not cursor.fetchone():
                return Response({'error': 'User not found'}, status=404)

            # clear dependent records before removing subtype rows
            cursor.execute("DELETE FROM reviews WHERE reviewed_by = %s", [username])
            cursor.execute("DELETE FROM uploads WHERE uploaded_by = %s", [username])

            # remove from all subtype tables
            for table in ['administrator', 'data_analyst', 'scientist', 'amateur']:
                cursor.execute(f"DELETE FROM {table} WHERE username = %s", [username])

            cursor.execute("DELETE FROM user WHERE username = %s", [username])

        return Response({'message': 'User deleted successfully'})