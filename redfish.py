import requests
import sys
import time
import re
from requests.auth import HTTPBasicAuth
from requests.packages import urllib3
from requests.exceptions import ReadTimeout, HTTPError, ConnectionError
from argparse import ArgumentParser

class Connection:
    def __init__(self, remote, user, password):
        self.base = "https://" + remote
        self.auth = HTTPBasicAuth(user, password)
    def request(self, path):
        return requests.get(self.base + path, auth=self.auth, verify=False, timeout=15)
            
class Entry:
    def __init__(self, data):
        self.etype = data.get("EntryType")
        self.snumber = data.get("SensorNumber")
        self.stype = data.get("SensorType")
        self.ecode = data.get("EntryCode")
        self.message = data.get("Message") if data.get("Message") is not None else ""
        self.severity = data.get("Severity") if data.get("Severity") is not None else self.etype
        self.date = data.get("Created")[0:10]
    def __str__(self):
        s = "["+ self.date + " " + self.severity.rjust(8, ' ') + "] " + self.message
        return s

def parse_args():
    parser = ArgumentParser(description="SEL collector via Redfish")
    mandatory = parser.add_argument_group(title="mandatory arguments")
    mandatory.add_argument("-r", "--remote", help="the remote bmc to query", required=True)
    mandatory.add_argument("-u", "--user", help="the login username", required=True)
    mandatory.add_argument("-p", "--password", help="the login password", required=True)
    mandatory.add_argument("-e", "--events", help="show events only", action='store_true', required=False)
    args = parser.parse_args()
    return args

def query_node(remote, user, password):

    # initial connection information 
    c = Connection(remote, user, password)
    
    # find the location of the system managers
    response = c.request("/redfish/v1/Managers/")
    response.raise_for_status()
    data = response.json()
    managers = [m.get("@odata.id") for m in data.get("Members")]

    # find the location of the system
    response = c.request("/redfish/v1/Systems/")
    response.raise_for_status()
    data = response.json()
    systems = [s.get("@odata.id") for s in data.get("Members")]

    # for each manager, find the log services attached to it
    services = []
    for m in managers:
        response = c.request(m).json()
        location = response.get("LogServices").get("@odata.id")
        response = c.request(location).json()
        members = [s.get("@odata.id") for s in response.get("Members")]
        services.extend(members)
    
    # for each system, see if there exists log services attached to it
    for m in systems:
        response = c.request(m).json()
        location = response.get("LogServices")
        if location is not None:
            location = location.get("@odata.id")
            response = c.request(location).json()
            members = [s.get("@odata.id") for s in response.get("Members")]
            services.extend(members)


    # for each log service, find log locations
    logs = []
    for s in services:
        response = c.request(s).json()
        log = response.get("Entries")
        if log is not None:
            log = log.get("@odata.id")
            logs.append(log)

    # for each log, get all entries
    entries = []
    for l in logs:
        response = c.request(l).json()
        members = response.get("Members")
        for m in members:
            e = Entry(m)
            if e.severity != "OK":
                entries.append(e)

    # NOTE: if we want to "deassert" some of the messages, keep a dict with
    # the sensor numbers as keys
            
    # return our list of errors sorted by newest date
    return sorted(entries, key=lambda e: e.date, reverse=True)

def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    args = parse_args()
    try:
        warnings = query_node(args.remote, args.user, args.password)
        for w in warnings:
            if args.events:
                print(w) 
            else:
                print(w)
    except (ReadTimeout, HTTPError, ConnectionError) as e:
        print(e)
            
if __name__ == "__main__":
    main()           
