import json
from datetime import datetime, timedelta
from flights import Flight, FlightsRoute


def handler(x):
    """Handler function for print_json to help the function with unrecognized objects
    """
    if isinstance(x, datetime):
        return x.isoformat()
    if isinstance(x, timedelta):
        return str(x)
    if isinstance(x, FlightsRoute):
        # Select only desired attributes from FlightsRoute object.
        print_keys = ["flights", "bags_allowed", "bags_count",
                      "origin", "destination", "total_price", "travel_time"]
        d = {}
        for key in print_keys:
            d[key] = x.__dict__[key]
        return d
    if isinstance(x, Flight):
        return x.__dict__
    raise TypeError("Unknown type {}".format(type(x)))


def print_json(paths):
    """Print paths using json module"""
    print(json.dumps(paths, default=handler))
