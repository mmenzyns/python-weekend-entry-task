from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import copy
import sys

@dataclass
class Flight:
    flight_no: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    base_price: float
    bag_price: float
    bags_allowed: int

    @staticmethod
    def from_row(row) -> Flight:
        return Flight(
            row["flight_no"],
            row["origin"],
            row["destination"],
            datetime.fromisoformat(row["departure"]),
            datetime.fromisoformat(row["arrival"]),
            float(row["base_price"]),
            float(row["bag_price"]),
            int(row["bags_allowed"]),
        )

    def covers_layover_time(self, departure: Flight) -> bool:
        delta = self.departure - departure
        if delta.days != 0:
            return False
        hours = delta.seconds / 3600
        return 1 < hours and hours < 6


class FlightsDataset():

    def __init__(self, reader, args):
        self.flights = [Flight.from_row(row) for row in reader]
        self.bags_required = args.bags
        self.return_required = args.returning

    def filter_by_origin_departure(self, departure: datetime, layover: bool, origin: str) -> list[Flight]:
        for flight in self.flights:
            if origin is None:
                yield flight
            if flight.origin != origin or self.bags_required > flight.bags_allowed:
                continue
            if departure is not None:
                if layover and not flight.covers_layover_time(departure) or not flight.departure >= departure:
                    continue
            yield flight


class FlightsPath():
    origin: str = None
    destination: str = None

    def __init__(self, args, flights: list[Flight] = []):
        self.flights = flights

        self.bags_allowed = 0
        self.bags_count = args.bags
                
        self.origin = args.origin
        self.destination = args.destination

        self.total_price = 0
        self.travel_time = timedelta()

        self.returning = False
        self._airports = []


    def copy(self):
        return copy.deepcopy(self)

    def last_flight(self):
        return self.flights[-1]

    def not_empty(self) -> bool:
        return bool(self.flights)

    def add_flight(self, flight: Flight):
        self.flights.append(flight)
        self.update_prices_and_bags()

    def add_airport(self, airport: str):
        self._airports.append(airport)

    def clear_airports(self):
        self._airports = []

    def update_prices_and_bags(self):
        price = 0
        bags = None

        for flight in self.flights:
            if bags is None or flight.bags_allowed < bags:
                bags = flight.bags_allowed
                
            price += flight.base_price
            price += flight.bag_price * self.bags_count

        self.bags_allowed = bags
        self.total_price = price