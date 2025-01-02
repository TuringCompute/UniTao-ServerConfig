#!/usr/bin/env python3

#########################################################################################
# Linux Network Bridge utilities
# this will use network bridge json data and use different command base on bridge type to
# - Create/Delete bridge
# - Add/remove network interfaces to/from specified bridge
#########################################################################################

import argparse
import logging
import os

from shared.logger import Log
from shared.utilities import Util


class NetBridge:
    class Keyword:
        BridgeType = "bridgeType"
        Interfaces = "interfaces"
        MacAddress = "macAddress"

        class BridgeTypes:
            LinuxBridge = "linuxBridge"
            OvsBridge   = "ovsBridge"

            @staticmethod
            def list():
                return [
                    NetBridge.Keyword.BridgeTypes.LinuxBridge,
                    NetBridge.Keyword.BridgeTypes.OvsBridge                
                ]
    
    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=f"Linux Network Bridge Operations")
        parser.add_argument("--path", type=str, help=f"Linux Network Bridge Data Path for Vm Operation", required=True)
        args = parser.parse_args()
        return args

    def __init__(self, logger: logging.Logger):
        self.log = logger
        self.Args = NetBridge.parse_args()
        if not os.path.exists(self.Args.path):
            raise ValueError(f"Invalid path does not exists.[{self.Args.path}]")
        self.BridgeName = Util.file_data_name(self.Args.path)
        self.BrData = Util.read_json_file(self.Args.path)

    def Validate(self):
        br_type = self.BrData.get(self.Keyword.BridgeType, None)
        if br_type is None:
            raise ValueError(f"Error: Missing field[{self.Keyword.BridgeType}] or value is None")
        if br_type not in self.Keyword.BridgeTypes.list():
            raise ValueError(f"Error: invalid [{self.Keyword.BridgeType}]=[{br_type}], supported values[{self.Keyword.BridgeTypes.list()}]")
        iface_list = self.BrData.get(self.Keyword.Interfaces, None)
        if iface_list is None:
            raise ValueError(f"Error: Missing field[{self.Keyword.Interfaces}] or value is None")
        if not isinstance(iface_list, list):
            raise ValueError(f"Error: field[{self.Keyword.Interfaces}] needs to be a list of interface names")

