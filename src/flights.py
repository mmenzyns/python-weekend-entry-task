from dataclasses import dataclass
from datetime import datetime, timedelta
import copy
from typing import Iterator, List

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
    def from_row(row) -> "Flight":
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

    def can_be_succeeded(self, departure: "Flight", layover: bool) -> bool:
        delta = self.departure - departure
        if delta.days != 0:
            return False
        hours = delta.seconds / 3600

        if layover:
            return 1 < hours and hours < 6
        else:
            return 1 < hours


class FlightsDataset:

    def __init__(self, reader, args):
        self.flights = [Flight.from_row(row) for row in reader]
        self.bags_required = args.bags
        self.return_required = args.returning

    def filter_by_origin_departure(self, departure: datetime, layover: bool, origin: str) -> Iterator[Flight]:
        for flight in self.flights:
            if origin is None:
                yield flight
            if flight.origin != origin or self.bags_required > flight.bags_allowed:
                continue
            if departure is not None:
                if not flight.can_be_succeeded(departure, layover):
                    continue
            yield flight


class FlightsPath:
    origin: str = None
    destination: str = None

    def __init__(self, args):
        self.flights = []

        self.bags_allowed = None
        self.bags_count = args.bags
                
        self.origin = args.origin
        self.destination = args.destination

        self.total_price = 0
        self.travel_time = timedelta(0)

        self.returning = False
        self.airports = []


    def copy(self):
        return copy.deepcopy(self)

    def first_flight(self):
        return self.flights[0]

    def last_flight(self):
        return self.flights[-1]

    def not_empty(self) -> bool:
        return bool(self.flights)

    def add_flight(self, flight: Flight):
        self.flights.append(flight)

        if self.bags_allowed is None or self.bags_allowed > flight.bags_allowed:
            self.bags_allowed = flight.bags_allowed

        self.travel_time = flight.arrival - self.first_flight().departure

        self.total_price += flight.base_price
        self.total_price += flight.bag_price * self.bags_count

    def add_airport(self, airport: str):
        self.airports.append(airport)

    def clear_airports(self):
        self.airports = []

