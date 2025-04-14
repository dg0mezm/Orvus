#!/usr/bin/env python

import argparse
from src.Orvus import Orvus


def parse_arguments():
    parser = argparse.ArgumentParser(description="Orvus: Tool to automate the initial scans.")
    parser.add_argument("-i", "--ip", type=str, required=True, help="Target IP Address")
    parser.add_argument("--ignore-ping", type=bool, default=False, help="Indicates if ignore initial ping.")
    parser.add_argument("--debug", type=bool, default=False, help="Toggle debug mode")
    return parser.parse_args()


def main():
    args = parse_arguments()
    Orvus(args)


if __name__ == '__main__':
    main()
