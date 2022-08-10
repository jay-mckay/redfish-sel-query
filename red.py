import requests
from argparse import ArgumentParser

class RedfishConnection():
    def __init__(self, remote, user, password):
        self.root = 'https://' + remote
        self.session = requests.sessions.Session()
        self.session.auth = (user, password)
        self.session.verify = False

    def get(self, resource):
        response = self.session.get(self.root + resource)
        if not response.ok:
            return "unable to fetch from " + resource
        return response.json()

def get_manager_addresses(redfishconnection):
    response = redfishconnection.get('/redfish/v1/Managers/')
    addresses = [m.get('@odata.id') for m in response.get('Members')]
    return addresses

def get_service_address(redfishconnection, manager_location):
    response = redfishconnection.get(manager_location)
    address = response.get('LogServices').get('@odata.id')
    return address

def get_log_addresses(redfishconnection, service_location):
    response = redfishconnection.get(service_location)
    addresses = [s.get('@data.id') for s in response.get('Members')]

def query(remote, user, password):
    redfish = RedfishConnection(remote, user, password)
    manager_addresses = get_manager_addresses(redfish)
    service_addresses = [get_service_address(redfish, address) for address in manager_addresses]
    log_addresses = [get_log_addresses(redfish, address) for address in service_addresses]
    for l in log_addresses:
        print(l)

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
    query(args.remote, args.user, args.password)

if __name__ == "__main__":
    main()
