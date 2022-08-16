import requests
from datetime import datetime
from argparse import ArgumentParser

class RedfishConnection():
    def __init__(self, remote, user, password):
        self.root = 'https://' + remote
        self.session = requests.sessions.Session()
        self.session.auth = (user, password)
        self.session.verify = False

    def get(self, location):
        response = self.session.get(self.root + location)
        response.raise_for_status()
        return response.json()

    def get_many_id(self, location, resource):
        response = self.get(location)
        items = [x.get('@odata.id') for x in response.get(resource)]
        return items

    def get_single_id(self, location, resource):
        response = self.get(location)
        item = response.get(resource).get('@odata.id')
        return item

    def get_entry(self, location, resource):
        response = self.get(location)
        items = response.get('Members')
        return items

def flatten(thelist):
    return [item for sublist in thelist for item in sublist]

# currently only queries the managers (BMC)
# NOTE: does not query more than on page of logs currently
def query_logs(remote, user, password):
    connection = RedfishConnection(remote, user, password)
    manager_locations = connection.get_many_id('/redfish/v1/Managers/', 'Members')
    service_locations = [connection.get_single_id(location, 'LogServices') for location in manager_locations]
    log_locations = [connection.get_many_id(location, 'Members') for location in service_locations]
    log_locations = flatten(log_locations)
    entry_locations = [connection.get_single_id(location, 'Entries') for location in log_locations]
    entries = [connection.get_entry(location, 'Members') for location in entry_locations]
    entries = flatten(entries)
    logs = []
    for entry in entries:
        severity = entry.get('Severity')
        if severity != "OK":
            logs.append(entry)
    return logs

def parse_args():
    parser = ArgumentParser(description="SEL collector via Redfish")
    arguments = parser.add_argument_group(title="mandatory arguments")
    arguments.add_argument("-r", "--remote", help="the remote bmc to query", required=True)
    arguments.add_argument("-u", "--user", help="the login username", required=True)
    arguments.add_argument("-p", "--password", help="the login password", required=True)
    args = parser.parse_args()
    return args

def main():
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    args = parse_args()
    remote = '{:*^20}'.format(args.remote)
    print(remote)
    try:
        logs = query_logs(args.remote, args.user, args.password)
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
    except requests.exceptions.RequestException as e:
        print("Unable to fetch logs:" +  str(e))

if __name__ == "__main__":
    main()
