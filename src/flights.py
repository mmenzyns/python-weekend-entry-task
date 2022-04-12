from dataclasses import dataclass
from datetime import datetime, timedelta
import copy
from typing import Iterator, List


@dataclass
class Flight:
    flight_no: str # flight number
    origin: str # origin airport code
    destination: str # destination airport code
    departure: datetime # flight departure date and time
    arrival: datetime # flight arrival date and time
    base_price: float # price for the ticket
    bag_price: float # price for one piece of baggage
    bags_allowed: int # number of allowed pieces of baggage for the flight

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
        """Returns bool whether departure provided in parameters matches the conditions for transfer from last flight in instance's route.
        There has to be at least 1 hour gap between the flights. If layover is true, then the time gap cannot be larger than 6 hours
        """
        delta = self.departure - departure
        if delta.days != 0:
            return False
        hours = delta.seconds / 3600

        if layover:
            return 1 < hours and hours < 6
        else:
            return 1 < hours


class FlightsDataset:
    """ A class for a dataset of all possible flights and user's requirements"""

    def __init__(self, reader, args):
        self.flights = [Flight.from_row(row) for row in reader]
        self.bags_required = args.bags
        self.return_required = args.returning

    def get_filtered_flights(self, departure: datetime, layover: bool, origin: str) -> Iterator[Flight]:
        """This function goes through all flight in the dataset. And yields flights according to conditions in parameter.
        If origin is provided, only flights from selected airports are yielded.
        If departure is provided, only flights that departure at least 1 hour after departure time in parameters.
        If layover is provided together with departure, only flights departuring less then 6 hours after are yielded.
        """
        for flight in self.flights:
            if origin is None:
                yield flight
            if flight.origin != origin or self.bags_required > flight.bags_allowed:
                continue
            if departure is not None and not flight.can_be_succeeded(departure, layover):
                continue
            yield flight


class FlightsRoute:
    """A class for a series of consecutive flights for a flight route between multiple airports"""
    origin: str = None
    destination: str = None

    def __init__(self, args):
        self.flights = [] # list of flights in the trip

        self.bags_allowed = None # number of allowed bags for the trip
        self.bags_count = args.bags # searched number of bags
        self.origin = args.origin # origin airport for the trip
        self.destination = args.destination # destination airport for the trip

        self.total_price = 0 # total price for the trip
        self.travel_time = timedelta(0) # total travel time for the trip
        self.stay_length = timedelta(0) # time between first trip and return trip

        # Which way is the route being searched. Either towards destination => false or towards origin => true
        self.returning = False
        
        self.visited_airports = [] # airports already visited for either direction

    def copy(self):
        """Returns a deep copy of the instance"""
        return copy.deepcopy(self)

    def last_flight(self):
        assert(len(self.flights) > 0)
        return self.flights[-1]

    def not_empty(self) -> bool:
        return bool(self.flights)

    def add_flight(self, flight: Flight):
        """Add flight to the route and update few route info such as bags, price and travel_time"""
        if self.returning and len(self.visited_airports) == 0:
            self.stay_length = flight.departure - self.last_flight().arrival

        self.flights.append(flight)

        if self.bags_allowed is None or flight.bags_allowed < self.bags_allowed:
            self.bags_allowed = flight.bags_allowed

        total_time = flight.arrival - self.flights[0].departure
        # Stay time between both direction doesn't count into travel_time
        self.travel_time = total_time - self.stay_length

        self.total_price += flight.base_price
        self.total_price += flight.bag_price * self.bags_count

    def visit_airport(self, airport: str):
        self.visited_airports.append(airport)

    def clear_airports(self):
        self.visited_airports.clear()
