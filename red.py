import requests
from argparse import ArgumentParser

class RedfishConnection():
    def __init__(self, remote, user, password):
        self.root = 'https://' + remote
        self.session = requests.sessions.Session()
        self.session.auth = (user, password)
        self.session.verify = False

    def get_many_id(self, location, resource):
        response = self.session.get(self.root + location)
        if not response.ok:
            return []
        response = response.json()
        items = [x.get('@odata.id') for x in response.get(resource)]
        return items

    def get_single_id(self, location, resource):
        response = self.session.get(self.root + location)
        if not response.ok:
            return []
        response = response.json()
        item = response.get(resource).get('@odata.id')
        return item

    def get_entry(self, location, resource):
        response = self.session.get(self.root + location)
        if not response.ok:
            return []
        response = response.json()
        items = response.get('Members')
        return items

def flatten(thelist):
    return [item for sublist in thelist for item in sublist]

def query_logs(remote, user, password, severity):
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
        if entry.get('Severity') == severity:
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
    for i in range(100, 199):
        remote = '10.241.15.' + str(i)
        print("Remote: " + remote)
        print(len(query_logs(remote, args.user, args.password, 'OK')))

if __name__ == "__main__":
    main()
