#!/usr/bin/env python3

import numbers
import time

from shared.logger import Log
from shared.utilities import Util

from shared.entity import Entity, EntityOp, Keyword
from dataProvider.json_folder import JsonFolderData



# Need to use JsonFolderProvider
class KvmVm(Entity):
    class Keyword:
        KvmVM = "kvm_vm"
        Drive = "drive"
        VmName = "vmName",
        VmState = "vmState"
        CPU = "cpu"
        SMP = "smp"
        RamInGb = "ramInGB"
        OsDrive = "osDrive"
        Drives = "drives"
        Networks = "networks"

        class VmStates:
            Running = "running"
            Stopped = "stopped"
            NotExists = "notExists"
    
            def List() -> list[str]:
                return [KvmVm.Keyword.VmStates.Running, KvmVm.Keyword.VmStates.Stopped, KvmVm.Keyword.VmStates.NotExists]
    @staticmethod
    def EntityType() -> str:
        return KvmVm.Keyword.KvmVM
    
    def Exists(self)-> bool:
        if self.Data is None:
            return False
        current_data = self.Data.get(Keyword.States.Current, {})
        vm_name = current_data.get(KvmVm.Keyword.VmName, None)
        if vm_name is None:
            return False
        return KvmVmOp.VmExists(vm_name)
    
    # validate date to see if request data is good to create VM
    @staticmethod
    def ValidateRequest(request_data: dict):
        vm_name = request_data.get(KvmVm.Keyword.VmName, None)
        if vm_name is None:
            raise ValueError(f"missing field {KvmVm.Keyword.VmName} from {self.EntityType()} data")
        vm_state = request_data.get(KvmVm.Keyword.VmState, None)
        if vm_state not in KvmVm.Keyword.VmStates.List():
            raise ValueError(f"missing field {KvmVm.Keyword.VmState}, or bad value no from list {KvmVm.Keyword.VmStates.List()}")
        vm_cpu =  request_data.get(KvmVm.Keyword.CPU, "host")
        if vm_cpu is None or vm_cpu == "":
            raise ValueError(f"Error: field [{self.Keyword.CPU}] cannot by None or '', 
                             please specify a valid value or remove it to use default value [host]")
        vm_smp = request_data.get(self.Keyword.SMP, None)
        if vm_smp is None or not isinstance(vm_smp, int):
            raise ValueError(f"Error: field[{self.Keyword.SMP}] cannot be None and type to be int")
        vm_ram = request_data.get(self.Keyword.RamInGb, None)
        if vm_ram is None or not isinstance(vm_ram, numbers.Number):
            raise ValueError(f"Error: field[{self.Keyword.RamInGb}] cannot be None and type to be number")
        vm_osdrive = request_data.get(self.Keyword.OsDrive, None)
        if vm_osdrive is None or not isinstance(vm_osdrive, str):
            raise ValueError(f"Error: field[{self.Keyword.OsDrive}] cannot be None and type to be str")
        vm_drives = request_data.get(self.Keyword.Drives, [])
        if vm_drives is None or not isinstance(vm_drives, list):
            raise ValueError(f"Error: field[{self.Keyword.Drives}] cannot be None, It's type should be list of str")
        if len(vm_drives) ==0:
            raise ValueError(f"Error: field[{self.Keyword.Drives}] cannot be empty list, VM need at least 1 drive to run")
        for driveIdx in vm_drives:
            if not isinstance(driveIdx, str) or driveIdx.strip() == "":
                raise ValueError(f"Error: drive[{driveIdx}] @field[{self.Keyword.Drives}] is not string or is empty")
        if vm_osdrive not in vm_drives:
            raise ValueError(f"Error: OS drive[{self.OsDrive}] not in field[{self.Keyword.Drives}]")
        vm_networks = request_data.get(self.Keyword.Networks, [])
        if vm_networks is None or not isinstance(vm_networks, list):
            raise ValueError(f"Error: field[{self.Keyword.Networks}] cannot be None, It's type should be list of str")

class KvmVmOp(EntityOp):
    def __init__(self, log, data_handler):
        super().__init__(log, data_handler)
        self.EntityType = KvmVm.EntityType()

    def list_request(self):
        return self.data_handler.ListRequests(self.EntityType)

    def process_vm_request(self, vm_id):
        request_data = {}
        vm_request = self.data_handler.GetRequest(self.EntityType, vm_id)
        request_data[self.EntityType] = {
            Keyword.Id:vm_id,
            Keyword.Data: vm_request
        }
        # collect other request info


    def __get_vm_data(self, vm_id) -> dict:
        pass

    def _process_request(self, entity_id, request_data):
        request_status = request_data.get(Keyword.Status, Keyword.EntityStatus.Active)
        KvmVm.ValidateRequest(request_data)
        
        current_vm = KvmVm(entity_id, self.Current.Data)
        if request_status == Keyword.EntityStatus.Active:
            # create/modify kvm image status=[Active/Error]
            if not current_vm.Exists():
                # create kvm image
                self.Create(request_data)
                return request_data

    # create vm using request data, 
    def Create(self, request_data: dict):
        pass

    @staticmethod
    def VmExists(vm_name: str)-> bool:
        result = Util.run_command("virsh list --all --name")
        if vm_name in result.stdout_lines:
            return True
        return False
    
    @staticmethod
    def VmUp(vm_name: str) -> bool:
        result = Util.run_command(f"virsh list --name")
        if vm_name in result.stdout_lines:
            return True
        return False

if __name__ == "__main__":
    entity_type = KvmVm.EntityType()
    log = Log.get_logger(entity_type)
    log.info(f"{entity_type} Operations")
    log.info(f"Create [{entity_type}] data handler from {JsonFolderData.ProviderName()}")
    data_provider = JsonFolderData(entity_type, log)
    log.info(f"Create [{entity_type}] Entity Operation Controller")
    vm_op = KvmVmOp(log, data_provider)
    vm_list= vm_op.List_Requests()
    log.info(f"Got [{len(vm_list)}] VMs to process")
    for vm_id in vm_list:
        log.info(f"process {vm_op.EntityType}=[{vm_id}]")
        vm_op.process_vm_request(vm_id)
    log.info(f"All VMs processed")
