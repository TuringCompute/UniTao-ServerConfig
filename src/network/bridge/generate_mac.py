#!/usr/bin/env python3

#########################################################################################
# Linux Mac Address Generator
# this will generate a mac address
#########################################################################################

import random

def generate_mac():
    mac = [random.randint(0, 255) for _ in range(5)]
    mac_address ='0e:' + ':'.join(f'{num:02X}' for num in mac)
    return mac_address

print(generate_mac())
