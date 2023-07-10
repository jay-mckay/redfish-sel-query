import requests
from argparse import ArgumentParser

def HttpRequest (url):
    print (requests.get(url).text)

def parse_args():
    parser = ArgumentParser(description="Http Requester")
    mandatoryArgs = parser.add_argument_group(title="Mandatory argument")
    mandatoryArgs.add_argument("-u", "--url", help="The URL for the HTTP request", required=True)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    HttpRequest(args.url)


if __name__ == "__main__":
    main()

