import csv
from datetime import datetime

from flights import FlightsDataset, FlightsPath, Flight
from args import parse_args
from print import print_json


def expand_node(dataset: FlightsDataset, base_path: FlightsPath):
    new_paths: list[FlightsPath] = []
    valid_paths: list[FlightsPath] = []

    target = base_path.destination if not base_path.returning else base_path.origin
    airport_to_expand = base_path.last_flight(
    ).destination if base_path.not_empty() else base_path.origin
    departure = base_path.last_flight().arrival if base_path.not_empty() else None
    layover = False if not base_path._airports and base_path.returning else True

    flights = list(dataset.filter_by_origin_departure(
        departure, layover, origin=airport_to_expand))

    for flight in flights:
        path = base_path.copy()
        path.add_flight(flight)
        path.add_airport(flight.origin)

        if flight.destination == target:
            # If user specified return ticket then continue to find a path back, but first check
            #  if return ticket wasn't already searched for right now
            if dataset.return_required and target == path.destination:
                path._airports.clear()  # Now finding return route, so old airports don't matter
                path.returning = True
                new_paths.append(path)
            else:
                valid_paths.append(path)
        elif flight.destination not in path._airports:
            new_paths.append(path)

    return valid_paths, new_paths


def find_flights(dataset: FlightsDataset, args):

    (valid_paths, paths) = expand_node(dataset, FlightsPath(args))

    while paths:
        next_depth_paths = []
        for path in paths:
            (ret_valid, ret_new) = expand_node(dataset, path)
            next_depth_paths.extend(ret_new)
            valid_paths.extend(ret_valid)
        paths = next_depth_paths

    return valid_paths


if __name__ == "__main__":

    args = parse_args()

    with open(args.filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        dataset = FlightsDataset(reader, args)

    flights = find_flights(dataset, args)

    print_json(flights)
