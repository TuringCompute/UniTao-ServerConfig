#!/bin/bash

# install all related software
apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager

# enable local user able to manage kvm without sudo
# need reboot to take effect
adduser $USER kvm
adduser $USER libvirt

# install pip and update to latest
apt-get install -y python3-pip

# install genisoimage for Cloud-init install 
apt-get install -y genisoimage

apt-get install -y openvswitch-switch
