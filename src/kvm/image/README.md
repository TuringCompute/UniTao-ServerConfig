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
    "id": "image_id",                   // id of the image to be identified
    "entityType": "kvm_image",          // Entity Data Type
    "current": {
        "imageFormat": "{qcow2/img}",       // the image file type  
        "sizeInGB": 30,                     // optional, only use to create a new image with size requirement
        "downloadLink": "",                 // optional, only use when need to download the image file from remote location
        "baseImagePath": "",                // optional, only use when need to create a new image with a baseline image
        "baseImageFormat": "{qcow2/img}",
        "imagePath": "",                    // image file path to store the image
        "exists": true,                     // whether or not image exists 
    },
    "desired": {}                           // changes to be made to current data
}
 ```