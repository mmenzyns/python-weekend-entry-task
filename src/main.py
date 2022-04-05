import csv

from typing import Tuple, List

from flights import FlightsDataset, FlightsPath, Flight
from args import parse_args
from print import print_json
import argparse

def expand_node(dataset: FlightsDataset, base_path: FlightsPath) -> Tuple[List[FlightsPath], List[FlightsPath]]:
    
    new_paths: list[FlightsPath] = []
    valid_paths: list[FlightsPath] = []

    if base_path.not_empty():
        airport_to_expand: str = base_path.last_flight().destination
        departure = base_path.last_flight().arrival
    else:
        airport_to_expand: str = base_path.origin
        departure = None

    layover: bool = base_path.not_empty and not base_path.returning
    target: str = base_path.destination if not base_path.returning else base_path.origin

    flights = dataset.filter_by_origin_departure(departure, layover, origin=airport_to_expand)

    for flight in flights:
        path = base_path.copy()
        path.add_flight(flight)
        path.add_airport(flight.origin)

        if flight.destination == target:
            # If user specified return ticket then continue to find a path back, but first check
            #  if return ticket wasn't already searched for right now
            if dataset.return_required and target == path.destination:
                path.airports.clear()  # Now finding return route, so old airports don't matter
                path.returning = True
                new_paths.append(path)
            else:
                valid_paths.append(path)
        elif flight.destination not in path.airports:
            new_paths.append(path)

    return valid_paths, new_paths


def find_flights(dataset: FlightsDataset, args: argparse.Namespace) -> List[FlightsPath]:

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
