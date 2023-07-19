#!/usr/bin/python3
"""
    Simple program to query redfish thermal data resources of BMCs

    Redfish specification at
    https://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.17.0.pdfi

    Authors - J. Jay McKay & Leonardo Leano
"""


import requests
import json
from datetime import datetime
from argparse import ArgumentParser
from getpass import getpass


# hardcoded locations within redfish
THERMAL_PATH = "/redfish/v1/Chassis/System.Embedded.1/Thermal#/"


# 
ID = "@odata.id"
TEMPERATURES = "Temperatures"

class RedfishConnection():
    """
    Small object to store information about
    a redfish connection
    """

    def __init__(self, remote, user, password):
        self.root = 'https://' + remote
        self.session = requests.sessions.Session()
        self.session.auth = (user, password)
        self.session.verify = False


    def __request(self, location):
        """
        makes an http request and returns the result as a JSON object
        """
        response = self.session.get(self.root + location)
        response.raise_for_status()
        return response.json()


    def get_many_id(self, location, resource_collection):
        """
        returns the IDs of the items in a resource collection,
        or None if collection cannot be found
        """
        response = self.__request(location)
        collection = response.get(resource_collection)
        if collection is None:
            return None
        return[x.get(ID) for x in collection]


    def get_single_id(self, location, resource):
        """
        returns the ID of a resource, or None if
        resource cannot be found
        """
        response = self.__request(location)
        item = response.get(resource)
        if item is None:
            return None
        return item.get(ID)


    def get_resource(self, location, resource):
        """
        returns a redfish resource, or None if
        resource is not found
        """
        response = self.__request(location)
        items = response.get(resource)
        return items


def flatten(thelist):
    return [item for sublist in thelist for item in sublist]


def query_thermals(remote, user, password):
    """
    attempts to get thermal data from a redfish resource locatated at remote
    """

    # initialize the connection
    connection = RedfishConnection(remote, user, password)

    # get the thermal data
    temperature_locations = connection.get_many_id(THERMAL_PATH, TEMPERATURES)

    temperatures = connection.get_resource(THERMAL_PATH, TEMPERATURES)
    #temperatures = flatten(temperatures)

    return temperatures


def parse_args():
    parser = ArgumentParser(description="Thermal Data collector via Redfish")
    parser.add_argument("-v", "--verbose", action = 'store_const',
                        const=True, default=False, dest='verbose',
                        help='display detailed log information')
    arguments = parser.add_argument_group(title="mandatory arguments")
    arguments.add_argument("-r", "--remote", help="the remote bmc to query", required=True)
    arguments.add_argument("-u", "--user", help="the login username", required=True)
    args = parser.parse_args()
    return args

def print_thermals(thermals, verbose):
    show = []
    for t in thermals:
        name = t.get("Name")
        temperatureCelsius = t.get("ReadingCelsius")
        formatted = name + ": " + str(temperatureCelsius) + " C"
        show.append(formatted)
    for s in show:
        print(s)

def main():
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    args = parse_args()
    try:
        password = getpass()
        thermals = query_thermals(args.remote, args.user, password)
        print_thermals(thermals, args.verbose)
    except requests.exceptions.RequestException as e:
        print(args.remote + ' : ' + e)

if __name__ == "__main__":
    main()
