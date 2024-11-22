# VM utility for KVM
Create vm using qemu utilities base on given json model attributes.

### Description
This utilities will use all the resource and attribute given by json file and create a VM using qemu tool.

### schema
 ```jsonc
vm_{vm_name}.json
{
    "name": "vm name",      // name of the VM in host
    "cpu": "host",          // optional, type of cpu for the VM .
                            // host: follow means same cpu as vm host
                            // other values: x86、x86_64、ARM、MIPS、PowerPC、SPARC、RISC-V
                            // set to host to follow host cpu type by default
    "smp": 2,               // number of CPUs assigned to this VM, [Symmetric Multi-Processing]
    "ramInGB": 2048,        // number GB of memory to be assigned to this VM
    "osDrive": "",          // Drive id to be OS Drive, 
    "drives": [],           // list of Drive Id to be retrieved from Inventory.
    "networks": [],         // list of id to retrieve network config JSON data file for each nic in VM
}

drive_{driveIdx}.json
{
    "id": "driveIdx",       // Drive id for each drive
    "linkType": "file",     // Which way to find the drive record, list of ways: [file]
    "recordFilePath": ""    // Drive Record Path
}

net_{netIdx}.json
{
    "id": "networkIdx",     // Id of the net adapter for the vm
    "bridgeName": "bridge"  // Bridge name to be linked by VM net adapter
}
 ```