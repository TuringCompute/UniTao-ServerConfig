#!/usr/bin/env python3
import sys

from lib.utilities import Util
from lib.entity import EntityOp

def veth_set(veth_data):
    veth0 = veth_data.get("veth0", None)
    veth1 = veth_data.get("veth1", None)
    if veth0 is None or veth1 is None:
        print("Error: missing field [veth0] or [veth1] from veth_data")
        sys.exit(-6)
    if veth0 == veth1:
        print("Error: veth0 and veth1 cannot be the same name")
        sys.exit(-7)
    if not veth_exists(veth0, veth1):
        veth_create(veth0, veth1)
        print("Successfully created veth pair")
        return
    print("veth [{0}, {1}] already exists".format(veth0, veth1))


def veth_exists(veth0, veth1):
    veth_name1 = "{0}@{1}".format(veth0, veth1)
    veth_name2 = "{0}@{1}".format(veth1, veth0)
    result = Util.run_command(['ip', 'link'])
    output = result.stdout
    if veth_name1 in output and veth_name2 in output:
        return True
    else:
        return False
    

def veth_create(veth0, veth1):
    iplink_cmd = ['ip', 'link', 'add', veth0, 'type', 'veth', 'peer', 'name', veth1]
    Util.run_command(iplink_cmd)


def veth_delete(veth_data):
    veth0 = veth_data.get("veth0", None)
    veth1 = veth_data.get("veth1", None)
    if veth0 is None or veth1 is None:
        print("Error: missing field [veth0] or [veth1] from veth_data")
        sys.exit(-6)
    if not veth_exists(veth0, veth1):
        print("Veth pair [{0}, {1}] does not exists".format(veth0, veth1))
        return
    veth_destroy(veth0)


def veth_destroy(veth0):
    iplink_cmd = ['ip', 'link', 'delete', veth0]
    Util.run_command(iplink_cmd)

def init_veth_op() -> EntityOp:
    veth_op = EntityOp()
    veth_op.EntityExists = veth_exists
    veth_op.CreateEntity = veth_create
    veth_op.DestroyEntity = veth_delete
    return veth_op

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: veth.py < <json_file_path>")
        sys.exit(-1)
    file_path = sys.argv[1]
    veth_op = init_veth_op()
    json_data = Util.read_json_file(file_path)
    veth_op.Run(json_data)
    

