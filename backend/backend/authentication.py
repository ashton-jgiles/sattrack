# django auth imports
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.db import connection

# create simple user class to handle auth
class SimpleUser:
    def __init__(self, username, level_access):
        self.username = username
        self.level_access = level_access
        self.is_authenticated = True
        self.pk = username

# JWT authentication class to create our cookie and authenticate
class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # try cookie first, fall back to Authorization header
        raw_token = request.COOKIES.get('access_token')
        if raw_token:
            # Token is present — validate it and let any exception propagate.
            # This ensures an expired/invalid cookie returns a 401 so the
            # client can refresh, rather than silently falling back to anonymous.
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        # No cookie — fall back to Authorization: Bearer header (or anonymous)
        return super().authenticate(request)

    # get user to check token status and verify user details
    def get_user(self, validated_token):
        # get the username of the token
        username = validated_token.get('username')
        # check for the username
        if not username:
            raise InvalidToken('Token has no username')

        with connection.cursor() as cursor:
            # get the user from the database using the username
            cursor.execute("SELECT username, level_access FROM user WHERE username = %s", [username])
            row = cursor.fetchone()

        # check the user exists
        if not row:
            raise InvalidToken('User not found')

        # create a simple user object
        return SimpleUser(row[0], row[1])
