import json

from datetime import datetime, timedelta
from flights import Flight, FlightsPath
from collections import OrderedDict

#>>> d = {1:2, 3:4, 5:6, 7:8}
# >>> l = {1, 5}
# >>> {key: d[key] for key in d.viewkeys() & l}
# {1: 2, 5: 6}

def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    if isinstance(x, timedelta):
        return str(x)
    if isinstance(x, FlightsPath):
        print_keys = ["flights", "bags_allowed", "bags_count", "origin", "destination", "total_price", "travel_time"]
        d = {}
        for key in print_keys:
            d[key] = x.__dict__[key]
        return d
    if isinstance(x, Flight):
        return x.__dict__
    raise TypeError("Unknown type {}".format(type(x)))

def print_json(paths):
    
    print(json.dumps(paths, default=datetime_handler))


        