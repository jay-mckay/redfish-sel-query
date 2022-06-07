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
        response = session.get(root + '/redfish/v1/Managers/', verify=False)
        if not response.ok:
            print("No path to systems: " + response.reason)
        else:
            data = response.json()
            managers = [m.get("@odata.id") for m in data.get("Members")]

        # find paths to systems
        response = session.get(root + '/redfish/v1/Systems/')
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
            response = session.get(root + page)
            data = response.json()
            location = data.get("LogServices").get("@odata.id")
            response = session.get(location).json()
            members = [s.get("@odata.id") for s in response.get("Members")]
            services.extend(members)

        return services

def main():
    args = parse_args()
    warnings = query_node(args.remote, args.user, args.password)
    for w in warnings:
        print(w)
            
if __name__ == "__main__":
    main()           
