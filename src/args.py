import argparse


def parse_args():
    """Parse arguments using argparse module
    """
    parser = argparse.ArgumentParser(
        description="This script is a submission for a task for Kiwi.com birthday Python weekend in Brno. From given data in a form if 'csv' file, the script prints out a list of all flight combinations for a selected route, sorted by the total price for the trip.")

    parser.add_argument("dataset",
                        type=str,
                        help="A path to a CSV file containing flight data")

    parser.add_argument("origin",
                        type=str,
                        help="3-letter code of the origin airport")

    parser.add_argument("destination",
                        type=str,
                        help="3-letter code of the destination airport")

    parser.add_argument("--bags",
                        type=int,
                        default=0,
                        help="Number of requested bags")

    parser.add_argument("--return",
                        dest="returning",
                        action="store_true",
                        default=False,
                        help="Does user want a return flight?")

    return parser.parse_args()
