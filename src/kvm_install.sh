#!/bin/bash

# install all related software
sudo apt-get install -y qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virt-manager

# enable local user able to manage kvm without sudo
# need reboot to take effect
sudo adduser $USER kvm
sudo adduser $USER libvirt

# install pip and update to latest
sudo apt-get install -y python3-pip
   