#!/usr/bin/env python3

#########################################################################################
# Kvm VM utilities
# this will simply translate json data into virt-install command to 
# create/modify KvmVM XML accordingly
# so that we can recreate Kvm VM
#########################################################################################

import argparse
import logging
import os

from shared.logger import Log
from shared.utilities import Util

class KvmVm:
    class Keyword:
        KvmVm = "kvm_vm"

        SMP = "smp"
        RamInGb = "ramInGB"
        Disks = "disks"
        Networks = "networks"
        OsType = "osType"
        OsVariant = "osVariant"
        VmState = "vmState"
        VmPath = "vmPath"
        UseCloudInit = "useCloudInit"
        CIIsoPath = "ciIsoPath"

        class VmStates:
            Running = "running"
            Stopped = "stopped"
            NotExists = "notExists"

            @staticmethod
            def list():
                return [
                    KvmVm.Keyword.VmStates.Running,
                    KvmVm.Keyword.VmStates.Stopped,
                    KvmVm.Keyword.VmStates.NotExists
                ]

    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=f"KVM Vm Operations")
        parser.add_argument("--path", type=str, help=f"Kvm Vm Data Path for Vm Operation", required=True)
        args = parser.parse_args()
        return args

    def __init__(self, logger: logging.Logger):
        self.log = logger
        self.Args = KvmVm.parse_args()
        if not os.path.exists(self.Args.path):
            raise ValueError(f"Invalid path does not exists.[{self.Args.path}]")
        self.VmName = Util.file_data_name(self.Args.path)
        self.VmData = Util.read_json_file(self.Args.path)
        self.Disks = []
        self.Networks = []
        self.Validate()

    def Validate(self):
        if not isinstance(self.VmData, dict):
            raise ValueError(f"Invalid vm data, not dict")
        vm_path = self.VmData.get(self.Keyword.VmPath, None)
        if vm_path is None:
            raise ValueError(f"Missing field [{self.Keyword.VmPath}] in Vm Data")
        if not os.path.isabs(vm_path):
            self.log.info(f"found relative path [{self.Keyword.VmPath}]=[{vm_path}]")
            data_file_path = os.path.dirname(self.Args.path)
            self.log.info(f"create abspath from data file path[{data_file_path}]")
            vm_path = Util.abs_path(data_file_path, vm_path)
            self.log.info(f"Update [{self.Keyword.VmPath}]=[{vm_path}]")
            self.VmData[self.Keyword.VmPath] = vm_path
        if not os.path.isdir(vm_path):
            raise ValueError(f"Invalid value, [{self.Keyword.VmPath}] should point to a folder to hold all file relate to this vm")
        # we do not want to support cpu as it make the system too complicated.
        # for now, we only support cpu=host
        vm_smp= self.VmData.get(self.Keyword.SMP, None)
        if vm_smp is None or not isinstance(vm_smp, int):
            raise ValueError(f"Missing field[{self.Keyword.SMP}] or the vCPU number is not int")
        vm_ram_in_gb = self.VmData.get(self.Keyword.RamInGb, None)
        if vm_ram_in_gb is None or not isinstance(vm_ram_in_gb, int):
            raise ValueError(f"Missing field [{self.Keyword.RamInGb}] or the ram number in GB is not int")
        vm_disks = self.VmData.get(self.Keyword.Disks, None)
        if vm_disks is None or not isinstance(vm_disks, list) or len(vm_disks) == 0:
            raise ValueError(f"Missing field [{self.Keyword.Disks}] or it's value is not a list or the list is empty")
        for disk_path in vm_disks:
            disk_file_path = self.parse_relative_path(disk_path)
            if not os.path.exists(disk_file_path) or not os.path.isfile(disk_file_path):
                raise ValueError(f"Disk File Path does not exists[{disk_file_path}]")
            kvm_disk = KvmDisk(disk_file_path, self.log)
            self.Disks.append(kvm_disk)
        use_cloud_init = self.VmData.get(self.Keyword.UseCloudInit, None)
        if use_cloud_init is None:
            raise ValueError(f"Missing field[{self.Keyword.UseCloudInit}] to specify if vm need to use Cloud Init to boot")
        if use_cloud_init:
            ci_iso_path = self.VmData.get(self.Keyword.CIIsoPath, None)
            if ci_iso_path is None:
                raise ValueError(f"Missing [{self.Keyword.CIIsoPath}] for CloudInit to work")
            real_ci_iso_path = self.parse_relative_path(ci_iso_path)
            if real_ci_iso_path != ci_iso_path:
                self.log.info(f"Update [{self.Keyword.CIIsoPath}] = [{real_ci_iso_path}]")
                self.VmData[self.Keyword.CIIsoPath] = real_ci_iso_path
            if os.path.exists(real_ci_iso_path) and os.path.isdir(real_ci_iso_path):
                raise ValueError(f"expect [{self.Keyword.CIIsoPath}] is a file. found a dir [{real_ci_iso_path}]")
        if not isinstance(use_cloud_init, bool):
            raise ValueError(f"Invalid value for [{self.Keyword.UseCloudInit}], expect bool")
        vm_nets = self.VmData.get(self.Keyword.Networks, None)
        if vm_nets is None or not isinstance(vm_nets, list) or len(vm_nets) == 0:
            raise ValueError(f"Missing field [{self.Keyword.Networks}] or it's value is not a list or the list is empty")
        for net_def_path in vm_nets:
            net_def_path = self.parse_relative_path(net_def_path)
            if not os.path.exists(net_def_path) or not os.path.isfile(net_def_path):
                raise ValueError(f"Disk File Path does not exists[{net_def_path}]")
            kvm_net = KvmNetwork(net_def_path, use_cloud_init , self.log)
            self.Networks.append(kvm_net)
        os_type = self.VmData.get(self.Keyword.OsType, None)
        if os_type is None:
            raise ValueError(f"Missing field[{self.Keyword.OsType}] in Vm Data")
        if os_type != "linux":
            raise ValueError(f"Invalid value[{self.Keyword.OsType}]=[{os_type}], we currently only support [linux]")
        os_variant = self.VmData.get(self.Keyword.OsVariant, None)
        if os_variant is None:
            raise ValueError(f"Missing field[{self.Keyword.OsVariant}] in Vm Data")
        vm_state = self.VmData.get(self.Keyword.VmState, None)
        if vm_state is None:
            raise ValueError(f"Missing field[{self.Keyword.VmState}] to specify desired state for the VM")
        if vm_state not in self.Keyword.VmStates.list():
            raise ValueError(f"Unknown value [{self.Keyword.VmState}]=[{vm_state}], expect value from list [{self.Keyword.VmStates.list()}]")

    def parse_relative_path(self, file_path):
        vm_path = self.VmData[self.Keyword.VmPath]
        vm_path_prefix = f"{{{self.Keyword.VmPath}}}"
        if file_path.startswith(vm_path_prefix):
            return file_path.replace(vm_path_prefix, vm_path, 1)
        if not os.path.isabs(file_path):
            return Util.abs_path(os.path.dirname(self.Args.path), file_path)
        return file_path

    def Process(self):
        if self.VmData[self.Keyword.VmState] == self.Keyword.VmStates.NotExists:
            self.log.info(f"To remove VM: [{self.VmName}]")
            self.delete_vm()
            return
        self.create_vm()
        self.sync_vm_state()
    
    def delete_vm(self):
        cmd_result = Util.run_command("virsh list --name --all")
        if self.VmName not in cmd_result.stdout_lines:
            self.log.info(f"VM[{self.VmName}] not in virsh list. Done")
            return
        self.log.info(f"run virsh to destroy VM[{self.VmName}]")
        Util.run_command(f"virsh destroy {self.VmName}")

    def create_ci_iso(self):
        if not self.VmData[self.Keyword.UseCloudInit]:
            self.log.info("VM not using Cloud Init, return")
            return
        ci_iso_file = self.VmData[self.Keyword.CIIsoPath]
        if os.path.exists(ci_iso_file):
            self.log.info(f"VM Cloud Init iso already exists.return. [{ci_iso_file}]")
            return
        user_data_path = self.create_ci_user_data()
        meta_data_path = self.create_ci_meta_data()
        self.log.info(f"Generate ISO [{ci_iso_file}]")
        iso_gen_cmd = f"genisoimage -output {ci_iso_file} -volid cidata -joliet -rock user-data={user_data_path} meta-data={meta_data_path}"
        iso_gen_sh_path = os.path.join(self.VmData[self.Keyword.VmPath], "gen_cloud_init_iso.sh")
        self.log.info(f"Record Cloud Init iso generate command @[{iso_gen_sh_path}]")
        with open(iso_gen_sh_path, "w") as fp:
            fp.write(iso_gen_cmd)
        self.log.info(f"Run Cloud Init ISO gen command:[{iso_gen_cmd}]")
        Util.run_command(iso_gen_cmd)
    
    def create_ci_user_data(self):
        user_data_path = os.path.join(self.VmData[self.Keyword.VmPath], "user-data.yaml")
        user_data = []
        for net in self.Networks:
            net_user_data = net.ci_user_data()
            user_data.extend(net_user_data)
        with open(user_data_path, "w") as fp:
            fp.writelines(user_data)
        return user_data_path

    def create_ci_meta_data(self):
        meta_data_path = os.path.join(self.VmData[self.Keyword.VmPath], "meta-data.yaml")
        meta_data = []
        for net in self.Networks:
            net_meta_data = net.ci_meta_data()
            meta_data.extend(net_meta_data)
        with open(meta_data_path, "w") as fp:
            fp.writelines(meta_data_path)
        return meta_data_path

    def create_vm(self):
        self.log.info(f"Create VM [{self.VmName}]")
        cmd_result = Util.run_command(f"virsh list --name --all")
        if self.VmName in cmd_result.stdout_lines:
            self.log.info(f"VM[{self.VmName}] already exists.")
            return
        vm_path = self.VmData[self.Keyword.VmPath]
        self.log.info(f"make sure VM path exists.[{vm_path}]")
        Util.run_command(f"mkdir -p {vm_path}")
        self.create_ci_iso()
        vm_create_cmd = self.create_vm_cmd()
        vm_def_create_file = os.path.join(vm_path, f"vm_def_create_{self.VmName}.sh")
        self.log.info(f"Create bash file that can create vm definition XML file. {vm_def_create_file}")
        with open(vm_def_create_file, "w") as fp:
            fp.write(vm_create_cmd)
        self.log.info("vm def creation bash created.")
        vm_def_file = os.path.join(vm_path, f"vm_def_{self.VmName}.xml")
        self.log.info(f"Run def creation command to generate VM definition XML file. [{vm_def_file}]")
        cmd_result = Util.run_command(vm_create_cmd)
        with open(vm_def_file, "w") as fp:
            fp.writelines(cmd_result.stdout_lines)
        self.log.info(f"VM definition file created")
        self.log.info(f"Create vm [{self.VmName}] using definition XML. [{vm_def_file}]")
        Util.run_command(f"virsh define {vm_def_file}")
        self.log.info(f"VM [{self.VmName}] created.")

    def create_vm_cmd(self) -> str:
        ram_in_mb= self.VmData[self.Keyword.RamInGb] * 1024
        vm_create_cmd = f"""virt-install --print-xml --name {self.VmName} \n
                            --os-type {self.VmData[self.Keyword.OsType]} \n
                            --os-variant {self.VmData[self.Keyword.OsVariant]} \n
                            --ram {ram_in_mb} \n
                            --vcpus {self.VmData[self.Keyword.SMP]}"""
        for disk in self.Disks:
            vm_create_cmd = f"""{vm_create_cmd} \n
                                --disk {disk.disk_cmd()}"""
        for net in self.Networks:
            vm_create_cmd = f"""{vm_create_cmd} \n
                                --network {net.net_cmd()}"""
        if self.VmData[self.Keyword.UseCloudInit]:
            vm_create_cmd = f"""{vm_create_cmd} \n
                                --cdrom={self.VmData[self.Keyword.CIIsoPath]}"""
        vm_create_cmd = f"""{vm_create_cmd} \n
                            --graphics none --console pty,target_type=serial"""
        return vm_create_cmd

    def vm_running(self) -> bool:
        cmd_result = Util.run_command("virsh list --name")
        return self.VmName in cmd_result.stdout_lines

    def sync_vm_state(self):
        if self.vm_running():
            self.log.info(f"VM[{self.VmName}] is running")
            if self.VmData[self.Keyword.VmState] == self.Keyword.VmStates.Stopped:
                self.log.info(f"stop VM[{self.VmName}]")
                Util.run_command(f"virsh shutdown {self.VmName}")
            return
        if self.VmData[self.Keyword.VmState] == self.Keyword.VmStates.Running:
            self.log.info(f"VM[{self.VmName}] is not running, start it.")
            Util.run_command(f"virsh start {self.VmName}")

class KvmDisk:
    class Keyword:
        DiskPath = "diskPath"

    def __init__(self, data_path: str, logger: logging.Logger):
        self.log = logger
        self.DataFile = data_path
        self.DiskData = Util.read_json_file(data_path)
        self.Validate()
    
    def Validate(self):
        if not isinstance(self.DiskData, dict):
            raise ValueError(f"Invalid disk data, not dict. data file = [{self.DataFile}]")
        disk_file = self.DiskData.get(self.Keyword.DiskPath, None)
        if disk_file is None:
            raise ValueError(f"Missing field[{self.Keyword.DiskPath}]")
        disk_file_real_path = Util.abs_path(os.path.dirname(self.DataFile), disk_file)
        if not os.path.exists(disk_file_real_path) or not os.path.isfile(disk_file_real_path):
            raise ValueError(f"invalid disk file, Not exists or not a file. [{disk_file_real_path}]")
        if disk_file_real_path != disk_file:
            self.DiskData[self.Keyword.DiskPath] = disk_file_real_path

    def disk_cmd(self) -> str:
        return f"path={self.DiskData[self.Keyword.DiskPath]}"

class KvmNetwork:
    class Keyword:
        IfaceType = "ifaceType"
        BridgeName = "bridgeName"
        TapSource = "tapSource"
        TapMode = "tapMode"
        MacAddress = "macAddress"

        MacAddress = "macAddress"
        UseDHCP4 = "useDHCP4"
        IPv4 = "ip4"
        Gateway4 = "gateway4"

        class TapModes:
            Bridge = "bridge"
            Private = "private"
            VEPA = "vepa"
            PassThru = "passthru"


        class InterfaceTypes:
            Bridge = "bridge"
            MacVTap = "macvtap"

            @staticmethod
            def list():
                return [
                    KvmNetwork.Keyword.InterfaceTypes.Bridge,
                    KvmNetwork.Keyword.InterfaceTypes.MacVTap
                ]

    def __init__(self, data_path: str, use_ci: bool, logger: logging.Logger):
        self.log = logger
        self.UseCI = use_ci
        self.DataFile = data_path
        self.NetData = Util.read_json_file(data_path)
        self.Validate()

    def Validate(self):
        iface_type = self.NetData.get(self.Keyword.IfaceType, None)
        if iface_type is None:
            raise ValueError(f"Missing attribute=[{self.Keyword.IfaceType}]")
        if iface_type not in self.Keyword.InterfaceTypes.list():
            raise ValueError(f"Invalid [{self.Keyword.IfaceType}]=[{iface_type}], expect value from list [{self.Keyword.InterfaceTypes.list()}]")
        if iface_type == self.Keyword.InterfaceTypes.Bridge:
            self.validate_bridge()
        if iface_type == self.Keyword.InterfaceTypes.MacVTap:
            self.validate_macvtap()
        mac_address = self.NetData.get(self.Keyword.MacAddress, None)
        if mac_address is not None:
            Util.parse_mac_address(mac_address)
        if not self.UseCI:
            self.log.info(f"[{KvmVm.Keyword.UseCloudInit}]==False, ignore CloudInit data check")
            return
        if mac_address is None:
            raise ValueError(f"Invalid data, CI need mac_address to config IP for each network interface")
        use_dhcp4 = self.NetData.get(self.Keyword.UseDHCP4, None)
        if use_dhcp4 is None:
            raise ValueError(f"Missing field[{self.Keyword.DHCP4}] to specify DHCP4 enable or not")
        if not isinstance(use_dhcp4, bool):
            raise ValueError(f"Invalid value[{self.Keyword.DHCP4}] need to be an bool value")
        if use_dhcp4:
            self.log.info(f"[{self.Keyword.UseDHCP4}] == True, Ignore check on IP configuraiton")
            return
        ipv4 = self.NetData.get(self.Keyword.IPv4, None)
        if ipv4 is None:
            raise ValueError(f"Missing field[{self.Keyword.IPv4}]")
        self.validate_ipv4_address(ipv4)
        gateway = self.NetData.get(self.Keyword.Gateway4, None)
        if gateway is None:
            raise ValueError(f"Missing field[{self.Keyword.Gateway4}]")
        self.validate_ipv4(gateway)

    def validate_bridge(self):
        device_name = self.NetData.get(self.Keyword.BridgeName, None)
        if device_name is None:
            raise ValueError(f"Missing field[{self.Keyword.BridgeName}] for [{self.Keyword.InterfaceTypes.Bridge}] interface")

    def validate_macvtap(self):
        tap_source = self.NetData.get(self.Keyword.TapSource, None)
        if tap_source is None:
            raise ValueError(f"Missing field [{self.Keyword.TapSource}] for [{self.Keyword.InterfaceTypes.MacVTap}] interface")
        tap_src_mode = self.NetData.get(self.Keyword.TapMode, None)
        if tap_src_mode is not None and tap_src_mode != self.Keyword.TapModes.Bridge:
            raise ValueError(f"For MacVTap mode,  Not support[{self.Keyword.TapMode}] =[{tap_src_mode}], only support [{self.Keyword.TapModes.Bridge}]")
        device_name = self.NetData.get(self.Keyword.BridgeName, None)
        if device_name is None:
            raise ValueError(f"Missing field[{self.Keyword.BridgeName}] for {self.Keyword.TapMode} = [{self.Keyword.TapModes}]")

    def validate_ipv4_address(self, ipv4):
        net_mask_parts = ipv4.split("/")
        if len(net_mask_parts)!=2:
            raise ValueError(f"Invalid IPv4[{ipv4}], missing net mask after [/], expect x.x.x.x/x")
        if not Util.is_int_str(net_mask_parts[1]):
            raise ValueError(f"Invalid IPv4[{ipv4}], netmask [{net_mask_parts[1]}] is not int")
        self.validate_ipv4(net_mask_parts[0])
    
    def validate_ipv4(self, ipv4):
        ip_parts = ipv4.split(".")
        if len(ip_parts)!=4:
            raise ValueError(f"Invalid IPv4[{ipv4}], expect 4 segments(x.x.x.x) for ip[{net_mask_parts[0]}]")
        for part in ip_parts:
            if not Util.is_int_str(part):
                raise ValueError(f"Invalid IPv4[{ipv4}], expect all segment are int. found non-int[{part}]")

    def net_cmd(self) -> str:
        if self.NetData[self.Keyword.IfaceType] == self.Keyword.InterfaceTypes.Bridge:
            return f"{self.Keyword.InterfaceTypes.Bridge}={self.NetData[self.Keyword.BridgeName]},model=virtio"
        if self.NetData[self.Keyword.IfaceType] == self.Keyword.InterfaceTypes.MacVTap:
            return f"type=direct,source={self.NetData[self.Keyword.BridgeName]},source_mode={self.Keyword.TapModes.Bridge},model=virtio"

    def generate_meta(self) -> list:
        meta_lines = []
        return meta_lines

    def generate_userdata(self) -> list:
        user_data = []
        return user_data


if __name__ == "__main__":
    logger = Log.get_logger("KvmImage")
    logger.info("Create Kvm VM")
    vm = KvmVm(logger)
    vm.Process()
