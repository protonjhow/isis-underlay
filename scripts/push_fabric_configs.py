#!/usr/bin/env python3
# coding: utf-8

# Modules
from nornir.init_nornir import InitNornir
from nornir.core.filter import F
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from nornir_pygnmi.tasks import gnmi_set
from ruamel.yaml import YAML


# Statics
NORNIR_CONFIG = "./config.yaml"


def read_yaml_config(yaml_file):
    yaml = YAML(typ="safe")

    with open(f"configs/{yaml_file}.yaml", "r") as file:
        content = yaml.load(file)

    config_msg = [
        (
            "/",
            content,
        )
    ]
    return config_msg


def send_config_to_group(run_name, config_name, nornir_group):
    config_msg = read_yaml_config(config_name)
    # change it
    update_request = nornir_group.run(
        name=run_name, task=gnmi_set, encoding="json_ietf", update=config_msg
    )
    print_result(update_request)
    # if update_request['response'][0]['op'] == 'UPDATE':
    #     print_result("OK!")
    # else:
    #     print_result(update_request)


# Body
if __name__ == "__main__":
    # Initialise Nornir
    nr = InitNornir(config_file=NORNIR_CONFIG)

    # make filters up front
    spines = nr.filter(F(groups__contains="spine"))
    leaves = nr.filter(F(groups__contains="leaf"))
    spine1 = nr.filter(F(name__endswith="spine1"))
    spine2 = nr.filter(F(name__endswith="spine2"))
    leaf1 = nr.filter(F(name__endswith="leaf1"))
    leaf2 = nr.filter(F(name__endswith="leaf2"))
    leaf3 = nr.filter(F(name__endswith="leaf3"))
    leaf4 = nr.filter(F(name__endswith="leaf4"))

    # order of things
    send_config_to_group(
        run_name="Configure spine1 local items",
        config_name="spine1",
        nornir_group=spine1,
    )
    send_config_to_group(
        run_name="Configure spine2 local items",
        config_name="spine2",
        nornir_group=spine2,
    )
    send_config_to_group(
        run_name="Configure leaf1 local items",
        config_name="leaf1",
        nornir_group=leaf1,
    )
    send_config_to_group(
        run_name="Configure leaf2 local items",
        config_name="leaf2",
        nornir_group=leaf2,
    )
    send_config_to_group(
        run_name="Configure leaf3 local items",
        config_name="leaf3",
        nornir_group=leaf3,
    )
    send_config_to_group(
        run_name="Configure leaf4 local items",
        config_name="leaf4",
        nornir_group=leaf4,
    )
    send_config_to_group(
        run_name="Configure generic spine items",
        config_name="spine",
        nornir_group=spines,
    )
    send_config_to_group(
        run_name="Configure generic leaf items",
        config_name="leaf",
        nornir_group=leaves,
    )
