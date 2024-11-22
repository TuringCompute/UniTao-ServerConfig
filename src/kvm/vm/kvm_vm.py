#!/usr/bin/env python3

import numbers

from shared.utilities import Util
from shared.logger import Log

from shared.entity import Entity, ParamEntityProvider, Keyword

logger = Log.get_logger("kvm_vm")

class KvmVm(Entity):
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
            
        })
        return super().to_json(json_data)
