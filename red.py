import requests
from argparse import ArgumentParser

class RedfishConnection():
    def __init__(self, remote, user, password):
        self.remote = remote
        self.password = password
        self.user = user
        self.root = 'https://' + remote + '/redfish/v1/'
        self.session = requests.sessions.Session()
        self.session.auth = (user, password)
        self.session.verify = False

    def get(self, resource):
        response = self.session.get(self.root + resource)
        if not response.ok:
            return "unable to fetch from " + resource
        return response.json()
        
def query(remote, user, password):
    redfish = RedfishConnection(remote, user, password)
    data = redfish.get('Managers/')
    managers = [m.get('@odata.id') for m in data.get('Members')]

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
