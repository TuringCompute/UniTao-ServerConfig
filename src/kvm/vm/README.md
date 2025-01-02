# VM utility for KVM
Create vm using qemu utilities base on given json model attributes.

### Description
This utilities will use all the resource and attribute given by json file and create a VM using qemu tool.

### schema
 ```jsonc
{vm_name}.json
{
    "vmPath": "{path}",     // path to store VM data and file
    "smp": 2,               // number of CPUs assigned to this VM, [Symmetric Multi-Processing]
    "ramInGB": 2,           // number GB of memory to be assigned to this VM
    "disks": [],            // list of path to vm disk definition json file, path can use {vmPath} as reference for relative path
    "networks": [],         // list of path to vm network definition json file, path can use {vmPath} as reference for relative path
    "vmState": "running",   // desired vm state. running, stopped, notExists
    "vmDefPath": "{path}"   // folder that can store Vm Definition creation script and Vm definition XML file    
}

example.json
{
    "vmPath": "../",
    "smp": 2,
    "ramInGB": 2,
    "disks":[
       "{vmPath}/data/wireguard_os.json"
    ],
    "networks": [
       "{vmPath}/data/local_bridge.json"
    ],
    "vmState": "running",
    "vmDefPath": "{vmPath}"
}

{disk_name}.json
{
    "diskPath": "path"      // path that link to the disk image file. path can be relative path to the disk data file
}

{network_name}.json
{
    "ifaceType": "bridge",      // VM net interface type. bridge/macvtap
    "BridgeName": "ext_net"     // bridge the vm net interface to connect with
}

{
    "ifaceType": "macvtap",                  // VM net interface type. bridge/macvtap
    "TapSource": "{ext iface/bridge name}",  // the network interface on host for this vm interface to tap into
    "TapMode": "{tap mode value}"            // define how vm interface is tapping into host net interface
                                             // possible values [bridge, private, vepa, passthru]
}

 ```