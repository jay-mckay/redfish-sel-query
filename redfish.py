import requests
import sys
from argparse import ArgumentParser
        
def parse_args():
    parser = ArgumentParser(description="SEL collector via Redfish")
    arguments = parser.add_argument_group(title="mandatory arguments")
    arguments.add_argument("-r", "--remote", help="the remote bmc to query", required=True)
    arguments.add_argument("-u", "--user", help="the login username", required=True)
    arguments.add_argument("-p", "--password", help="the login password", required=True)
    args = parser.parse_args()
    return args

def query_node(remote, user, password):

    root = 'https://' + remote
    with requests.sessions.Session() as session: 
        session.auth = (user, password)
        session.verify = False

        # find paths to system managers
        managers = []
        response = session.get(root + '/redfish/v1/Managers/', verify=False)
        if not response.ok:
            print("Cannot reach /redfish/v1/Managers/: " + response.reason)
        else:
            data = response.json()
            managers = [m.get('@odata.id') for m in data.get('Members')]

        # find paths to systems
        systems = []
        response = session.get(root + '/redfish/v1/Systems/', verify=False)
        if not response.ok:
            print("Cannot reach /redfish/v1/Systems/: " + response.reason)
        else:
            data = response.json()
            systems = [s.get('@odata.id') for s in data.get('Members')]

        services = []
        # on each manager and system page, find the path to log services
        for page in managers + systems:
            response = session.get(root + page + '/LogServices/', verify=False)
            if not response.ok:
                print("Cannot reach " + page + "/LogServices/: " + response.reason)
            else:
                data = response.json()
                for service in data.get('Members'):
                    services.append(service.get('@odata.id'))
        
        logs = []
        for page in services: 
            response = session.get(root + page + "/Entries/", verify=False)
            if not response.ok:
                print("Cannot reach events: " + response.reason)
            data = response.json()
            entries = [data.get(e.get('Message') for e in data.get('Members')]
            if entries:
                logs.append(entries)

        return logs
                
def main():
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    args = parse_args()
    collections = query_node(args.remote, args.user, args.password)
    for collection in collections:
        for item in collection:
            print(item)
            
if __name__ == "__main__":
    main()           
