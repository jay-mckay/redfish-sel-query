#!/usr/bin/python3

import pytest
import requests

from rfsq import RedfishConnection

# @pytest.fixture
# def redfish_connection():
#     return RedfishConnection()

def test_nonsense_bmc_host():
    connection = RedfishConnection("notch220-ipmi", "root", "Ak15halfTB")
    connection.get_single_id("/redfish/v1/Managers", "LogServices")