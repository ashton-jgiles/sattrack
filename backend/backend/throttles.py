# api throttling imports
from rest_framework.throttling import UserRateThrottle

# create classes for our most expensive apis being the retrive from celestrak and retrive all positional data for the globe
class CelesTrakThrottle(UserRateThrottle):
    scope = 'celestrak'

class PositionsThrottle(UserRateThrottle):
    scope = 'positions'