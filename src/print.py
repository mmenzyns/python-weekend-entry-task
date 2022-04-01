import json

from datetime import datetime, timedelta
from flights import Flight, FlightsPath

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    if isinstance(x, timedelta):
        return str(x)
    if isinstance(x, FlightsPath):
        return x.__dict__
    if isinstance(x, Flight):
        return x.__dict__
    raise TypeError("Unknown type {}".format(type(x)))

def print_json(paths: list[FlightsPath]):

    # dicts = [[flight.__dict__ for flight in flight_path.flights] for flight_path in paths]
    # print(dicts)
    print(json.dumps(paths, default=datetime_handler))