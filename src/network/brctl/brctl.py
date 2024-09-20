#!/usr/bin/env python3

import argparse


from lib.utilities import Util
from lib.entity import EntityOp, Entity


class LinuxBridge(Entity):
    def __init__(self, br_data: dict):
        super().__init__(br_data)
        self.Type = br_data.get("type", None)
        if self.Type is None:
            raise ValueError("Error: missing field [type] to specify bridge type. expected [LinuxBridge, OVSBridge]")
        if self.Type != "LinuxBridge":
            raise ValueError(f"Error: invalid bridge type={self.Type}. expected [LinuxBridge, OVSBridge]")
        self.Name = br_data.get("name", None)
        if self.Name is None:
            raise ValueError("Error: missing field [name] to specify bridge name.")
        self.Interfaces = br_data.get("interfaces", None)
        if self.Interfaces is None:
            raise ValueError("Error: missing field [interfaces] to specify links to be add to the bridge")
        if not isinstance(self.Interfaces, list):
            raise ValueError(f"Error: invalid value for links={self.Interfaces}, expect a list of link names")


class BrCtlOp(EntityOp):
    def MakeEntity(self, br_entity: LinuxBridge):
        br_list = BrCtlOp.ListBridge()
        if br_entity.Name not in br_list:
            BrCtlOp.CreateLinuxBridge(br_entity.Name)
        BrCtlOp.SetInterfaces(br_entity.Name, br_entity.Interfaces)


    def BreakEntity(self, br_entity: LinuxBridge):
        br_list = BrCtlOp.ListBridge()
        if br_entity.Name in br_list:
            BrCtlOp.DestroyLinuxBridge(br_entity.Name)


    @staticmethod
    def ListBridge():
        result = Util.run_command("brctl show")
        # Parse the output and print bridge names
        lines = result.stdout.splitlines()[1:]  # Skip the header line
        bridges = [line.split()[0] for line in lines if line]  # Get the first column (bridge name)
        return bridges


    @staticmethod
    def CreateLinuxBridge(br_name: str):
        Util.run_command(f"brctl addbr {br_name}")


    @staticmethod
    def DestroyLinuxBridge(br_name: str):
        Util.run_command(f"brctl delbr {br_name}")


    @staticmethod
    def SetInterfaces(br_name: str, interfaces: list[str]):
        current_ifaces = BrCtlOp.__list_interface(br_name)
        for iface in current_ifaces:
            if iface not in interfaces:
                BrCtlOp.__remove_interface(br_name, iface)

        for iface in interfaces:
            if iface not in current_ifaces:
                BrCtlOp.__add_interface(br_name, iface)


    @staticmethod
    def __remove_interface(br_name, iface):
        Util.run_command(f"brctl delif {br_name} {iface}")


    @staticmethod
    def __add_interface(br_name, iface):
        Util.run_command(f"brctl addif {br_name} {iface}")


    @staticmethod
    def __list_interface(br_name: str):
        result = Util.run_command(f"brctl show {br_name}")
        lines = result.stdout.splitlines()
        interfaces = []
        # Skip the header line
        for line in lines[1:]:
            parts = line.split()
            # If the line starts with the bridge name, it has the interfaces
            if parts[0] == br_name:
                # The first interface is in the 4th column, subsequent interfaces are on following lines
                interfaces.append(parts[3])
            else:
                interfaces.append(parts[0])
        return interfaces


def parse_args():
    parser = argparse.ArgumentParser(description="Linux Bridge Control [brctl] Operations")
    parser.add_argument("--data", type=str, help="Linux Bridge data to make in json format", required=True)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    json_data = Util.read_json_file(args.data)
    brctl_data = LinuxBridge(json_data)
    brctl_op = BrCtlOp()
    brctl_op.Run(brctl_data)
