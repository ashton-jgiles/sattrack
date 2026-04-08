# django auth imports
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.db import connection


class SimpleUser:
    """Lightweight user object returned by CustomJWTAuthentication.

    Replaces Django's full User model. Only carries the fields the API
    actually needs: username, level_access, is_authenticated, and pk.
    """
    def __init__(self, username, level_access):
        self.username = username
        self.level_access = level_access
        self.is_authenticated = True
        self.pk = username


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # try cookie first, fall back to Authorization header
        raw_token = request.COOKIES.get('access_token')
        if raw_token:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except Exception:
                pass
        # fall back to Authorization: Bearer header
        return super().authenticate(request)

    def get_user(self, validated_token):
        username = validated_token.get('username')
        if not username:
            raise InvalidToken('Token has no username')

        with connection.cursor() as cursor:
            cursor.execute("SELECT username, level_access FROM user WHERE username = %s", [username])
            row = cursor.fetchone()

        if not row:
            raise InvalidToken('User not found')

        return SimpleUser(row[0], row[1])
