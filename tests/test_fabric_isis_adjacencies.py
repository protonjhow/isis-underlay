#!/usr/bin/env python3
import requests
import json

DEFAULT_CRED = ("admin", "NokiaSrl1!")
TOPOLOGY_NAME = "isis-underlay"
DEVICE_LIST = [
    f"clab-{TOPOLOGY_NAME}-spine1",
    f"clab-{TOPOLOGY_NAME}-spine2",
]
VRF = "default"
ISIS_INSTANCE = "underlay"
NEIGHBOUR_DICT = {
    "ethernet-1/1.0": {
        "neighbor-hostname": "leaf1",
        "neighbor-ipv4": "169.254.1.1",
        "area-address": ["49.1001"],
    },
    "ethernet-1/2.0": {
        "neighbor-hostname": "leaf2",
        "neighbor-ipv4": "169.254.1.2",
        "area-address": ["49.1002"],
    },
    "ethernet-1/3.0": {
        "neighbor-hostname": "leaf3",
        "neighbor-ipv4": "169.254.1.3",
        "area-address": ["49.1003"],
    },
    "ethernet-1/4.0": {
        "neighbor-hostname": "leaf4",
        "neighbor-ipv4": "169.254.1.4",
        "area-address": ["49.1004"],
    },
    "system0.0": {},
}


def build_rpc_request(path: str, datastore: str) -> str:
    """build an RPC required to Nokia JSONRPC endpoint

    Args:
        path (str): the JSONRPC path tho query
        datastore (str): the JSONRPC datastore to query from

    Returns:
        str: JSONRPC body string for a requests payload
    """
    body = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "get",
        "params": {"commands": [{"path": path, "datastore": datastore}]},
    }
    return body


def fetch_device_data(device: str) -> requests.models.Response:
    """Make a solo query to a device JSONRPC endpoint for data and return a requests response object

    Args:
        device (str): device hostname

    Returns:
        requests.models.Response: dataset obtained from the device
    """
    jsonrpc_path = "/jsonrpc"
    headers = {"Content-type": "application/json"}
    url = f"https://{device}{jsonrpc_path}"
    response = requests.post(
        url,
        data=json.dumps(
            build_rpc_request(
                path=f"/network-instance[name={VRF}]/protocols/isis/instance[name={ISIS_INSTANCE}]",
                datastore="state",
            )
        ),
        headers=headers,
        auth=requests.auth.HTTPBasicAuth(*DEFAULT_CRED),
        verify=f"clab-{TOPOLOGY_NAME}/.tls/ca/ca.pem",
    )
    return response


def assert_isis_neighbour_status(interface: dict, expected: dict) -> tuple:
    """Parse the response from a subset of a JSONRPC request and look for things we like about the output.

    Args:
        interface (dict): Response from JSONRPC request on IS-IS state
        expected (dict): Interface to query for status within IS-IS protocol

    Returns:
        tuple: state and feedback
    """
    # init
    state_bool = True
    state_str = "default"
    if not interface["oper-state"] == "up":
        state_bool = False
        state_str = f"IS-IS on interface {interface['interface-name']} is oper-down!"
    else: 
        for adjacency in interface["adjacency"]:
            if adjacency['neighbor-hostname'] == expected['neighbor-hostname']:
                print(f"\U00002705 Neighbor Hostname: {expected['neighbor-hostname']}")
                state_bool = True
                state_str = f"IS-IS on interface {interface['interface-name']} has correct peer hostname"
            else: 
                print(f"\U0000274C Neighbor Hostname: {adjacency['neighbor-hostname']} / Expected: {expected['neighbor-hostname']}")
                state_bool = False
                state_str = f"IS-IS on interface {interface['interface-name']} has incorrect peer hostname"
            if adjacency['neighbor-ipv4'] == expected['neighbor-ipv4']:
                print(f"\U00002705 Neighbor loopback IP: {expected['neighbor-ipv4']}")
                state_bool = True
                state_str = f"IS-IS on interface {interface['interface-name']} has correct peer ipv4"
            else: 
                print(f"\U0000274C Neighbor loopback IP: {adjacency['neighbor-ipv4']} / expected {expected['neighbor-ipv4']}")
                state_bool = False
                state_str = f"IS-IS on interface {interface['interface-name']} has incorrect peer ipv4"
    return (state_bool, state_str)


if __name__ == "__main__":
    """
    main cli entrypoint
    """
    for device in DEVICE_LIST:
        response = fetch_device_data(device).json()["result"][0]
        if not response["oper-state"] == "up":
            success = False
            result = "is-is is oper-down"
        else:
            success = True
            result = "is-is is oper-up"
            for interface in response["interface"]:
                if not interface['passive']:
                    expected_dict = NEIGHBOUR_DICT[interface["interface-name"]]
                    success, result = assert_isis_neighbour_status(interface, expected_dict)
                    if success:
                        print(f"\U00002705 {device}: {ISIS_INSTANCE}: {interface['interface-name']}")
                    else:
                        print(f"\U0000274C {device}: {ISIS_INSTANCE}: {interface['interface-name']}")
                else: 
                    pass
