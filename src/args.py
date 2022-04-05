import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Find flights between two airports")

    parser.add_argument("filename",
                        type=str,
                        help="CSV file to get flight data from")

    parser.add_argument("origin",
                        type=str,
                        help="3 letter code of the origin airport")

    parser.add_argument("destination",
                        type=str,
                        help="3 letter code of the destination airport")

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
