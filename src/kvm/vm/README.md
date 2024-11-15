# VM utility for KVM
Create vm using qemu utilities base on given json model attributes.

### Description
This utilities will use all the resource and attribute given by json file and create a VM using qemu tool.

### schema
 ```jsonc
{
    "name": "vm name",      // name of the VM in host
    "cpu": "host",          // type of cpu for the VM 
                            // host: follow means same cpu as vm host
                            // other values: x86、x86_64、ARM、MIPS、PowerPC、SPARC、RISC-V
    "smp": 2,               // number of CPUs assigned to this VM
    "ramInGB": 2048,        // number GB of memory to be assigned to this VM
    "osDrive": "",          // path to KVM OS image JSON data file to read image information
    "drives": [],           // list of id to retrieve image JSON data file to read image information and fill in command
    "networks": [],         // list of id to retrieve network config JSON data file for each nic in VM
}
 ```