#!/usr/bin/env python3
import argparse

from lib.utilities import Util
from lib.entity import Entity, EntityOp

class Veth(Entity):
    def __init__(self, entity_data: dict):
        super().__init__(entity_data)
        self.Veth0 = entity_data.get("veth0", None)
        self.Veth1 = entity_data.get("veth1", None)
        if self.Veth0 is None or self.Veth1 is None:
            raise ValueError("Error: missing field [veth0] or [veth1] from veth_data")
        if self.Veth0 == self.Veth1:
            raise ValueError("Error: veth0 and veth1 cannot be the same name")

    def Exists(self):
        veth_name1 = "{0}@{1}".format(self.Veth0, self.Veth1)
        veth_name2 = "{0}@{1}".format(self.Veth1, self.Veth0)
        result = Util.run_command(f"ip link")
        output = result.stdout
        if veth_name1 in output and veth_name2 in output:
            return True
        else:
            return False


class VethOP(EntityOp):
    def MakeEntity(self, veth: Veth):
        if not veth.Exists():
            VethOP.Create(veth)
    
    def BreakEntity(self, veth: Veth):
        if veth.Exists():
            VethOP.Destroy(veth)

    @staticmethod
    def Create(veth: Veth):
        Util.run_command(f"ip link add {veth.Veth0} type veth peer name {veth.Veth1}")
        Util.run_command(f"ip link set {veth.Veth0} up")
        Util.run_command(f"ip link set {veth.Veth1} up")

    @staticmethod
    def Destroy(veth: Veth):
        Util.run_command(f"ip link delete {veth.Veth0}")


def parse_args():
    parser = argparse.ArgumentParser(description="Create Veth Link Interfaces.")
    parser.add_argument("--data", type=str, help="veth data in json format", required=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    json_data = Util.read_json_file(args.data)
    veth_op = VethOP()
    
    veth = Veth(json_data)
    veth_op.Run(veth)
    

