#!/usr/bin/python3

import pytest
import requests

from rfsq import *

# @pytest.fixture
# def redfish_connection():
#     return RedfishConnection()

def test_correct_inputs():
    connection = RedfishConnection("notch220-ipmi", "root", "Ak15halfTB")
    connection.get_single_id("/redfish/v1/Managers", "LogServices")


def test_correct_output_on_bad_credentials(capsys):
    logs = []
    with pytest.raises(requests.exceptions.HTTPError) as excep_info:
        logs = query_logs("notch220-ipmi", "root", "blahblah")

    captured = capsys.readouterr()
    assert captured.out == "Bad username or password. Try again.\n"


def test_correct_output_when_no_critical_logs(capsys):
    logs = query_logs("notch409-ipmi", "root", "Ak15halfTB")
    with pytest.raises(SystemExit) as excep_info:
        print_logs(logs, False)

    captured = capsys.readouterr()
    assert captured.out == "There are no critical-level logs available for this host\n"

    