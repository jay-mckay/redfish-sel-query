#!/usr/bin/python3
"""
    Simple program to query redfish logs resources of BMCs

    Redfish specification at
    https://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.17.0.pdfi

    Authors - J. Jay McKay
"""


import requests
import json
from datetime import datetime
from argparse import ArgumentParser
import getpass


# hardcoded locations within redfish
MANAGER_PATH = "/redfish/v1/Managers/"
SYSTEM_PATH = "/redfish/v1/Systems/"
CHASSIS_PATH = "/redfish/v1/Chassis/"


# 
ID = "@odata.id"
MEMBERS = "Members"
ENTRIES = "Entries"
LOG_SERVICES = "LogServices"

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


# NOTE: does not query more than on page of logs currently
def query_logs(remote, user, password):
    """
    attempts to get logs from a redfish resource locatated at remote
    """

    # initialize the connection
    connection = RedfishConnection(remote, user, password)

    # get locations where logs could be
    manager_locations = connection.get_many_id(MANAGER_PATH, MEMBERS)
    system_locations = connection.get_many_id(SYSTEM_PATH, MEMBERS)
    chassis_locations = connection.get_many_id(CHASSIS_PATH, MEMBERS)

    locations = manager_locations + system_locations + chassis_locations

    # get locations of services
    service_locations = []
    for loc in locations:
        sl = connection.get_single_id(loc, LOG_SERVICES)
        if sl is not None:
            service_locations.append(sl)

    # get locations of logs
    log_locations = [connection.get_many_id(location, MEMBERS) for location in service_locations]
    log_locations = flatten(log_locations)

    # get locations of entries
    entry_locations = [connection.get_single_id(location, ENTRIES) for location in log_locations]

    # collect the entries
    entries = [connection.get_resource(location, MEMBERS) for location in entry_locations]
    entries = flatten(entries)

    return entries


def parse_args():
    parser = ArgumentParser(description="SEL collector via Redfish")
    arguments = parser.add_argument_group(title="mandatory arguments")
    arguments.add_argument("-r", "--remote", help="the remote bmc to query", required=True)
    arguments.add_argument("-u", "--user", help="the login username", required=True)
    args = parser.parse_args()
    return args


def print_logs(logs):
    for l in logs:
        message = l.get("Message")
        if message is None: message = "None"
        severity = l.get("Severity")
        if severity is None: severity = "None"
        fseverity = '[{:^8}]'.format(severity)
        datestring = l.get("Created")[0:19]
        if datestring is None: datestring = "0000-00-00T00:00:00"
        date = datetime.strptime(datestring, '%Y-%m-%dT%H:%M:%S')
        datestring = datetime.strftime(date,'%b %d %Y, %T')
        print(fseverity + " " + datestring + ": " + message)

# Get password
def get_password():
    password = getpass.getpass(prompt="Enter the password: ")
    return password


def main():
    try:
        password = get_password()
    except: print("\nyour password is wrong. bye.\n")
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    args = parse_args()
    remote = '{:*^20}'.format(args.remote)
    try:
        logs = query_logs(args.remote, args.user, password)
        print_logs(logs)
    except requests.exceptions.RequestException as e:
        print(remote + ": Unable to make request", e)

if __name__ == "__main__":
    main()
