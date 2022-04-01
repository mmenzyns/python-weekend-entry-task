from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Flight:
    flight_no: str
    origin: str
    destination: str
    departure: datetime
    arrival: datetime
    base_price: float
    bag_price: float
    bags_allowed: float

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
            float(row["bags_allowed"]),
        )

    def covers_layover_time(self, departure: Flight) -> bool:
        delta = self.departure - departure
        hours = delta.seconds / 3600
        return 1 < hours and hours < 6


class FlightsDataset():

    def __init__(self, reader, args):
        self.flights = [Flight.from_row(row) for row in reader]
        self.bags_required = args.bags
        self.return_required = args.returning

    def filter_by_origin_departure(self, departure: datetime, layover: bool, origin: str) -> list[Flight]:
        if layover is None or departure is None:
            return [
                flight for flight in self.flights
                if flight.origin == origin and flight.bags_allowed >= self.bags_required
            ]
        if layover == False:
            return [
                flight for flight in self.flights
                if flight.origin == origin
                and flight.bags_allowed >= self.bags_required
                and flight.departure >= departure
            ]
        if layover == True:
            return [
                flight for flight in self.flights
                if flight.origin == origin
                and flight.bags_allowed >= self.bags_required
                and flight.covers_layover_time(departure)
            ]


class FlightsPath():
    origin: str = None
    destination: str = None

    def __init__(self, args, flights: list[Flight] = []):
        self.flights = flights
                
        self.origin = args.origin
        self.destination = args.destination

        self.total_price = 0
        self.travel_time = timedelta()
        self.returning = False
        self._airports = []


    def copy(self):
        return FlightsPath(self.flights.copy())

    def last_flight(self):
        return self.flights[-1]

    def add_flight(self, flight: Flight):
        self.flights.append(flight)

    def add_airport(self, airport: str):
        self._airports.append(airport)

    def clear_airports(self):
        self._airports = []

    def count_price(self, bags: int):
        price = 0
        for flight in self:
            price += flight.base_price
            price += flight.bag_price * bags

        return price
