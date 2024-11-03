# Image utility of KVM
Operate on image for vm

### Description
This Image utility can be used to
 - Download image from link
 - Create image with specified format and size
 - Create image from base image

 ### Based on commands
 - wget to download image from remote link
 - qemu-img to create new image with baseline, size and format


 ### schema

 ```jsonc
{
    "imageFormat": "{qcow2/img}",       // the image file type  
    "name": "",                         // the image name, the file name will be defined as {name}.{imageFormat}
    "sizeInGB": 30,                     // optional, only use to create a new image with size requirement
    "downloadLink": "",                 // optional, only use when need to download the image file from remote location
    "baseImagePath": "",                // optional, only use when need to create a new image with a baseline image
    "imagePath": ""                     // folder or path to store the image file
}
 ```