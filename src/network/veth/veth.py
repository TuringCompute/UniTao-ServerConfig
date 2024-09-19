#!/usr/bin/env python3
import sys

from lib.utilities import Util
from lib.entity import EntityOp

def parse_data(veth_data):
    veth0 = veth_data.get("veth0", None)
    veth1 = veth_data.get("veth1", None)
    if veth0 is None or veth1 is None:
        raise ValueError("Error: missing field [veth0] or [veth1] from veth_data")
    if veth0 == veth1:
        raise ValueError("Error: veth0 and veth1 cannot be the same name")
    return veth0, veth1

def veth_exists(veth_data):
    veth0, veth1 = parse_data(veth_data)
    veth_name1 = "{0}@{1}".format(veth0, veth1)
    veth_name2 = "{0}@{1}".format(veth1, veth0)
    result = Util.run_command(f"ip link")
    output = result.stdout
    if veth_name1 in output and veth_name2 in output:
        return True
    else:
        return False

def veth_create(veth_data):
    Util.run_command(f"ip link add {veth_data["veth0"]} type veth peer name {veth_data["veth1"]}")
    Util.run_command(f"ip link set {veth_data["veth0"]} up")
    Util.run_command(f"ip link set {veth_data["veth1"]} up")

def veth_destroy(veth_data):
    Util.run_command(f"ip link delete {veth_data["veth0"]}")

def init_veth_op() -> EntityOp:
    veth_op = EntityOp()
    veth_op.EntityExists = veth_exists
    veth_op.CreateEntity = veth_create
    veth_op.DestroyEntity = veth_destroy
    return veth_op

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: veth.py < <json_file_path>")
        sys.exit(-1)
    file_path = sys.argv[1]
    veth_op = init_veth_op()
    json_data = Util.read_json_file(file_path)
    veth_op.Run(json_data)
    

