#!/usr/bin/env python3
import sys
import json
import subprocess

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(-2)
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON file.")
        sys.exit(-3)


def run_command(command: list[str]):
    cmd_str = " ".join(command)
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error: command [{0}] run failed with error:{1}".format(cmd_str, result.stderr))
            sys.exit(-9)
        return result
    except Exception as e:
        print(f"Error: Command [{0}] got an error: {1}".format(cmd_str, e))
        sys.exit(-8)


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
    result = run_command(['ip', 'link'])
    output = result.stdout
    if veth_name1 in output and veth_name2 in output:
        return True
    else:
        return False
    

def veth_create(veth0, veth1):
    iplink_cmd = ['ip', 'link', 'add', veth0, 'type', 'veth', 'peer', 'name', veth1]
    run_command(iplink_cmd)


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
    run_command(iplink_cmd)


if __name__ == "main":
    if len(sys.argv) < 2:
        print("Usage: veth.py < <json_file_path>")
        sys.exit(-1)

    file_path = sys.argv[1]
    json_data = read_json_file(file_path)
    veth_op(json_data)

