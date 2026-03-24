import bcrypt
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

def check_password(plain, hashed):
    return bcrypt.checkpw(
        plain.encode('utf-8'),
        hashed.encode('utf-8')
    )

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

class LoginView(APIView):
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