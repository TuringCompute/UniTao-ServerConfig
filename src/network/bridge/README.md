# BRCTL Command
operate on linux bridges

### Description
use brctl.py to operate linux bridge utility to create/enable/disable/delete LinuxBridge

### Base on command:
 - brctl addbr {bridge}
 - brctl delbr {bridge}
 - brctl addif {bridge} {device}
 - brctl delif {bridged} {device}

### data schema
```jsonc
{
    "bridgeType": "[linuxBridge, ovsBridge]",   // specify bridge name so different commands will be used for operation
    "macAddress": "d6:60:50:0b:83:10",          // specify mac address for the bridge
    "interfaces": []                            // list of link to be add to this bridge
}
```

