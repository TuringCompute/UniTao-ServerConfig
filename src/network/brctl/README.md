# BRCTL Command
operate on linux bridges

### Description
 - brctl_br.py: operate on linux bridge, check_exists/create/destroy
 - brctl_if.py: operate device on linux bridge, check_exists/create/destroy


### Base on command:
 - brctl addbr {bridge}
 - brctl delbr {bridge}
 - brctl addif {bridge} {device}
 - brctl delif {bridged} {device}

### data schema
```jsonc
{
    "state": "make",               // make or break for create or destroy the entity
    "type": "LinuxBridge",      // LinuxBridge for brctl operation
    "name": "bridge name",      // LinuxBridge name to be created
    "interfaces": []                 // list of link to be add to this bridge
}
```

