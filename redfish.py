import requests
import sys
from argparse import ArgumentParser
            
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
    arguments = parser.add_argument_group(title="mandatory arguments")
    arguments.add_argument("-r", "--remote", help="the remote bmc to query", required=True)
    arguments.add_argument("-u", "--user", help="the login username", required=True)
    arguments.add_argument("-p", "--password", help="the login password", required=True)
    args = parser.parse_args()
    return args

def query_node(remote, user, password):

    root = 'https://' + remote + '/redfish/v1/'
    session = requests.Session()
    session.auth = (user, password)
    
    # find paths to system managers
    response = session.get(root + 'Managers/')
    if not response.ok:
        print("No path to systems: " + response.reason)
    else:
        data = response.json()
        managers = [m.get("@odata.id") for m in data.get("Members")]

    # find paths to systems
    response = session.get(root + 'Systems/')
    if not response.ok:
        print("No path to managers:" + response.reason)
    else:
        data = response.json()
        systems = [s.get("@odata.id") for s in data.get("Members")]

    if not managers and not systems:
        print("Could not collect events")
        sys.exit()

    services = []
    # on each manager and system page, find the path to log services
    for page in managers + systems:
        response = session.get(page)
        data = response.json()
        location = data.get("LogServices").get("@odata.id")
        response = session.get(location).json()
        members = [s.get("@odata.id") for s in response.get("Members")]
        services.extend(members)
    
    # for each log service, find log locations
    # logs = []
    # for s in services:
    #     response = c.request(s).json()
    #     log = response.get("Entries")
    #     if log is not None:
    #         log = log.get("@odata.id")
    #         logs.append(log)

    # for each log, get all entries of interest
    # entries = []
    # for l in logs:
    #     response = c.request(l).json()
    #     members = response.get("Members")
    #     for m in members:
    #         e = Entry(m)
    #         if e.severity != "OK":
    #             entries.append(e)

    # # NOTE: if we want to "deassert" some of the messages, keep a dict with
    # # the sensor numbers as keys
            
    # # return our list of errors sorted by newest date
    # return sorted(entries, key=lambda e: e.date, reverse=True)
    
    session.close()
    return services

def main():
    args = parse_args()
    warnings = query_node(args.remote, args.user, args.password)
    for w in warnings:
        print(w)
            
if __name__ == "__main__":
    main()           
