# VETH Command
operate on veth ip link pair

### Description

translate veth data into real entity
based on command:
    ip link add {veth0} type veth peer name {veth1}
    ip link delete veth0

to detect if veth link pair exists.
    detect if link name {veth0}@{veth1} and {veth1}@{veth0} exists in the output of ip link command

### Schema
```jsonc
{
    "op": "make",             // value [make, break]
    "veth0": "veth-if01",     // name of 1st end of veth link
    "veth1": "veth-br01"      // name of 2nd end of veth link 
}
```