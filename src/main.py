import csv
from datetime import datetime

from flights import FlightsDataset, FlightsPath, Flight
from args import parse_args
from print import print_json


def explore_node(dataset: FlightsDataset, base_path: FlightsPath, destination: str, departure: datetime = None):
    new_paths = list[FlightsPath]
    valid_paths = list[FlightsPath]

    if base_path.returning:
        dataset.filter_by_origin_departure(False, departure, origin=base_path.last_flight().destination)

    for flight in :
        path = base_path.copy()
        path.add_flight(flight)
        path.add_airport(flight.origin)

        if flight.destination == destination:
            # If user specified return ticket then continue to find a path back, but first check
            #  if return ticket wasn't already searched for right now
            if path.returning and destination != path.origin: 
                path._airports.clear() # Now finding return route, so old airports don't matter
                path.returning = True
                new_paths.append(path)
            else:
                valid_paths.append(path)

        if flight.destination not in path._airports:
            new_paths.append(path)

    return valid_paths, new_paths

def find_flights(dataset: FlightsDataset, args):

    (valid_paths, new_paths) = explore_node(dataset, FlightsPath(args), args.destination)

    while new_paths:
        for path in new_paths:
            


if __name__ == "__main__":

    args = parse_args()

    with open(args.filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        dataset = FlightsDataset(reader, args)

    start_flights = dataset.filter_by_origin_departure(args.origin)
    result = find_flights_recursively(
        start_flights, dataset, FlightsPath(args))

    print_json(result)
    print("hh")


# def find_flights_recursively(flights: list[Flight], dataset: FlightsDataset, base_path: FlightsPath, destination: str):
#     valid_paths: list[FlightsPath] = []

#     for flight in flights:
#         path = base_path.copy()
#         path.add_flight(flight)
#         path.add_airport(flight.origin)

#         if flight.destination == destination:
#             if path.returning and destination != path.origin:
#                 next_flights = dataset.filter_by_origin_departure(
#                     origin=destination, departure=flight.arrival, layover=False)
#                 path._airports.clear()
#                 valid_paths.extend(find_flights_recursively(
#                     next_flights, dataset, path, destination=path.origin))
#             else:
#                 valid_paths.append(path)

#             continue

#         if flight.destination not in path._airports:
#             next_flights = dataset.filter_by_origin_departure(
#                 origin=flight.destination, departure=flight.arrival, layover=True)
#             valid_paths.extend(find_flights_recursively(
#                 next_flights, dataset, path, destination))

#     return valid_paths