from rest_framework.throttling import UserRateThrottle

class CelesTrakThrottle(UserRateThrottle):
    scope = 'celestrak'

class PositionsThrottle(UserRateThrottle):
    scope = 'positions'