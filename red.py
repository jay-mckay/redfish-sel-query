import requests

class RedfishConnection():
    def __init__(self, remote, user, password):
        self.remote = remote
        self.password = password
        self.user = user
        self.root = 'https//' + remote
        self.session = requests.sessions.Session()
        session.auth = (user, password)
        session.verify = False

    def get(resource):
        return session.get(root + resource)
        
def query(remote, user, password):
    redfish = RedfishConnection(remote, user, password)
    response = redfish.get('/Managers/')
    print(response)

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
    query(args.remote, arges.user, args.password)
            
if __name__ == "__main__":
    main()           