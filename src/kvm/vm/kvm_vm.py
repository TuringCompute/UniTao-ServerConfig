#!/usr/bin/env python3

import numbers
import os

from shared.utilities import Util
from shared.logger import Log

from shared.entity import Entity, EntityProvider, Keyword
from shared.entity_op import EntityOp

logger = Log.get_logger("kvm_vm")

# Need to use JsonFolderProvider
class KvmVm(Entity):
    class Keyword:
        Drive = "drive"
        Vm = "vm",
        VmInfo = "vminfo",
        VmInfoPath = "vmInfoPath"
        VmState = "vmState"

        class VmStates:
            Running = "running"
            Stopped = "stopped"
            NotExists = "notExists"
    
    def __init__(self, entity_data: dict):
        super().__init__(entity_data)
        self.Name = entity_data.get(Keyword.Name, None)
        if self.Name is None:
            raise ValueError(f"Error: field [{Keyword.Name}] cannot be None or ''")
        self.InfoPath = entity_data.get(self.Keyword.VmInfoPath, None)
        self.VmState = entity_data.get(self.Keyword.VmState, None)
    
    def to_json(self, data: dict = None) -> dict:
        json_data = data if data is not None else {}
        json_data.update({
            Keyword.Name: self.Name,
            self.Keyword.VmInfoPath: self.InfoPath,
            self.Keyword.VmState: self.VmState
        })
        return super().to_json(json_data)


class KvmVmInfo(Entity):
    class Keyword:
        CPU = "cpu"
        SMP = "smp"
        RamInGb = "ramInGB"
        OsDrive = "osDrive"
        Drives = "drives"
        Networks = "networks"

    def __init__(self, entity_data: dict):
        super().__init__(entity_data)
        self.CPU = entity_data.get(self.Keyword.CPU, "host")
        if self.CPU is None or self.CPU == "":
            raise ValueError(f"Error: field [{self.Keyword.CPU}] cannot by None or '', 
                             please specify a valid value or remove it to use default value [host]")
        self.SMP = entity_data.get(self.Keyword.SMP, None)
        if self.SMP is None or not isinstance(self.SMP, int):
            raise ValueError(f"Error: field[{self.Keyword.SMP}] cannot be None and type to be int")
        self.Ram = entity_data.get(self.Keyword.RamInGb, None)
        if self.RAM is None or not isinstance(self.Ram, numbers.Number):
            raise ValueError(f"Error: field[{self.Keyword.RamInGb}] cannot be None and type to be number")
        self.OsDrive = entity_data.get(self.Keyword.OsDrive, None)
        if self.OsDrive is None or not isinstance(self.OsDrive, str):
            raise ValueError(f"Error: field[{self.Keyword.OsDrive}] cannot be None and type to be str")
        self.Drives = entity_data.get(self.Keyword.Drives, [])
        if self.Drives is None or not isinstance(self.Drives, list):
            raise ValueError(f"Error: field[{self.Keyword.Drives}] cannot be None, It's type should be list of str")
        if len(self.Drives) ==0:
            raise ValueError(f"Error: field[{self.Keyword.Drives}] cannot be empty list, VM need at least 1 drive to run")
        for driveIdx in self.Drives:
            if not isinstance(driveIdx, str) or driveIdx.strip() == "":
                raise ValueError(f"Error: drive[{driveIdx}] @field[{self.Keyword.Drives}] is not string or is empty")
        if self.OsDrive not in self.Drives:
            raise ValueError(f"Error: OS drive[{self.OsDrive}] not in field[{self.Keyword.Drives}]")
        self.Networks = entity_data.get(self.Keyword.Networks, [])
        if self.Networks is None or not isinstance(self.Networks, list):
            raise ValueError(f"Error: field[{self.Keyword.Networks}] cannot be None, It's type should be list of str")
        
    def to_json(self, data: dict=None) -> dict:
        json_data = data if data is not None else {}
        json_data.update({
            Keyword.Name: self.Name,
            self.Keyword.CPU: self.CPU,
            self.Keyword.SMP: self.SMP,
            self.Keyword.RamInGb: self.Ram,
            self.Keyword.OsDrive: self.OsDrive,
            self.Keyword.Drives: self.Drives
        })
        return super().to_json(json_data)


class KvmVmOp(EntityOp):
    @staticmethod
    def SyncCurrent(vm_state: EntityProvider) -> bool:
         if super().SyncCurrent(vm_state):
             return True
         if vm_state.Current is None:
             return False 
         current_state = KvmVmOp.query_vm_state(vm_state.Current.Name)                                                                                                                                                                                                                        
         if current_state != vm_state.Current.VmState:
             vm_state.Current.VmState = current_state
             return True
         return False
         
    @staticmethod
    def query_vm_state(vm_name: str) -> str:
        qry_result = Util.run_command("virsh list --name")
        if vm_name in qry_result.stdout_lines:
            return KvmVm.Keyword.VmStates.Running
        qry_result = Util.run_command("virsh list --all --name")
        if vm_name in qry_result.stdout_lines:
            return KvmVm.Keyword.VmStates.Stopped
        return KvmVm.Keyword.VmStates.NotExists
    