#!/bin/env python

import csv
import argparse
from typing import Tuple, List
from flights import FlightsDataset, FlightsRoute
from args import parse_args
from print import print_json


def expand_node(dataset: FlightsDataset, base_route: FlightsRoute) -> Tuple[List[FlightsRoute], List[FlightsRoute]]:
    """Takes last flight in base_path, and expands this path with every valid flight that the path can be continued upon.
    Returns expanded paths in "expanded_paths". If any expanded path is a complete path, returns it in "new_paths".
    """
    completed_routes: list[FlightsRoute] = []
    expanded_routes: list[FlightsRoute] = []

    if base_route.not_empty():
        # Select the last airport in path to be expanded
        airport_to_expand: str = base_route.last_flight().destination
        # Select the arrival to latest airport
        arrival_to_airport = base_route.last_flight().arrival
    else:
        # Select the origin to be expanded, since there is no path yet
        airport_to_expand: str = base_route.origin
        # There is no time requirement for first flight in path
        arrival_to_airport = None

    # If this is first flight in either direction, there is no layover time
    layover: bool = len(base_route.visited_airports) != 0
    # Target is the final airport in either direction
    target_airport: str = base_route.destination if not base_route.returning else base_route.origin

    for flight in dataset.get_filtered_flights(arrival_to_airport, layover, origin=airport_to_expand):
        # Prepare new route object for expanded route
        route = base_route.copy()
        route.add_flight(flight)
        route.visit_airport(flight.origin)

        if flight.destination == target_airport:
            assert(dataset.return_required or target_airport ==
                   route.destination)
            # The route is completed in all cases except when route found is towards destination, and return flight is required
            if dataset.return_required and target_airport == route.destination:
                # Return route is required, clear airports because airports cannot be visited multiple times in each direction
                route.visited_airports.clear()
                route.returning = True
                expanded_routes.append(route)
            else:
                completed_routes.append(route)
        elif flight.destination not in route.visited_airports:
            # Airport wasn't yet visited, expand by this flight
            expanded_routes.append(route)

    return completed_routes, expanded_routes


def find_flights(dataset: FlightsDataset, args: argparse.Namespace) -> List[FlightsRoute]:
    """Searches the dataset using BFS. Returns routes matching the search
    """
    (valid_paths, paths) = expand_node(dataset, FlightsRoute(args))

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

    with open(args.dataset, newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        dataset = FlightsDataset(reader, args)

    flights = find_flights(dataset, args)

    flights.sort(key=lambda x: x.total_price)

    print_json(flights)
