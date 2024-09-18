#!/usr/bin/env python3
import sys

from lib.util import Util


def veth_op(veth_data):
    op = veth_data.get("op", None)
    if op == "set":
        veth_set(veth_data)
    elif op == "delete":
        veth_delete(veth_data)
    elif op is None:
        print("Error: Missing field [op] from JSON data")
        sys.exit(-4)
    else:
        print("Error: Expect op in [set, delete], got {0} instead".format(op))
        sys.exit(-5)


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


if __name__ == "main":
    if len(sys.argv) < 2:
        print("Usage: veth.py < <json_file_path>")
        sys.exit(-1)

    file_path = sys.argv[1]
    json_data = Util.read_json_file(file_path)
    veth_op(json_data)

