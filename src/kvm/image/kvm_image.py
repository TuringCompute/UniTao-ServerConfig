#!/usr/bin/env python3

#########################################################################################
# Kvm Image Utility
#
# Create image for local Kvm usage.
#########################################################################################

import argparse
import logging
import os
from extlib import wget

from shared.utilities import Util
from shared.logger import Log

class KvmImage:
    class Keyword:
        ImageFormat = "imageFormat"
        ImageSource = "imageSource"
        ImagePath = "imagePath"
        DownloadLink = "downloadLink"
        SizeInGB   = "sizeInGB"
        BaseImagePath = "baseImagePath"
        BaseImageFormat = "baseImageFormat"

        class Source:
            Remote = "remote"
            Local = "local"

            @staticmethod
            def list():
                return [
                    KvmImage.Keyword.Source.Remote,
                    KvmImage.Keyword.Source.Local
                ]

        class Formats:
            QCOW2 = "qcow2"
            IMG = "img"

            @staticmethod
            def list():
                return [
                    KvmImage.Keyword.Formats.QCOW2, 
                    KvmImage.Keyword.Formats.IMG
                ]

    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=f"KVM Image Operations")
        parser.add_argument("--path", type=str, help=f"Kvm Image Data Path for Image Creation", required=True)
        args = parser.parse_args()
        return args

    @staticmethod
    def ImageFormatCmd(image_format):
        if image_format == KvmImage.Keyword.Format.Img:
            return "raw"
        elif image_format == KvmImage.Keyword.Format.QCOW2:
            return "qcow2"

    def __init__(self, logger: logging.Logger):
        self.log = logger
        self.Args = KvmImage.parse_args()
        if not os.path.exists(self.Args.path):
            raise ValueError(f"Invalid path does not exists.[{self.Args.path}]")
        file_name = os.path.basename(self.Args.path)
        self.ImagName, file_ext = os.path.splitext(file_name)
        if file_ext!=".json":
            raise ValueError(f"Invalid path, data file should be an json file. got [{file_name}] instead")
        self.ImageData = Util.read_json_file(self.Args.path)
        if not isinstance(self.ImageData):
            raise ValueError(f"Invalid image data, not dict")
    
    def Validate(self):
        image_path = self.ImageData.get(self.Keyword.ImagePath, None)
        if image_path is None:
            raise ValueError(f"Missing field [{self.Keyword.ImagePath}] in Image Data")
        image_file_name = os.path.basename(image_path)
        image_name, file_ext = os.path.splitext(image_file_name)
        if image_name != self.ImagName:
            raise ValueError(f"Image data file name should match image name. [{self.ImagName}]!=[{image_name}]")
        image_format = self.ImageData.get(self.Keyword.ImageFormat, None)
        if image_format is None:
            raise ValueError(f"Missing field [{self.Keyword.ImageFormat}] to specify image format")
        if image_format not in self.Keyword.Formats.list():
            raise ValueError(f"Invalid [{self.Keyword.ImageFormat}]=[{image_format}], expect [{self.Keyword.Formats.list()}]")
        image_source = self.ImageData.get(self.Keyword.ImageSource, None)
        if image_source is None:
            raise ValueError(f"Missing field [{self.Keyword.ImageSource}] to specify image source")
        if image_source not in self.Keyword.Source.list():
            raise ValueError(f"Invalid [{self.Keyword.ImageSource}]=[{image_source}], expect [{self.Keyword.Source.list()}]")
        if image_source == self.Keyword.Source.Remote:
            download_link = self.ImageData.get(self.Keyword.DownloadLink, None)
            if download_link is None:
                raise ValueError(f"Invalid data, missing field=[{self.Keyword.DownloadLink}]")
        elif image_source == self.Keyword.Source.Local:
            image_size = self.ImageData.get(self.Keyword.SizeInGB, None)
            if image_size is not None and not isinstance(image_size, int):
                raise ValueError(f"Invalid value, [{self.Keyword.SizeInGB}]=image_size, expect int")
            base_image_path = self.ImageData.get(self.Keyword.BaseImagePath, None)
            if base_image_path is not None:
                if not os.path.exists(base_image_path):
                    raise ValueError(f"Invalid value [{self.Keyword.BaseImagePath}] does not exists. [{base_image_path}]")
                base_image_format = self.ImageData.get(self.Keyword.BaseImageFormat, None)
                if base_image_format is None:
                    raise ValueError(f"Missing value [{self.Keyword.BaseImageFormat}]")
                if base_image_format not in self.Keyword.Formats.list():
                    raise ValueError(f"Invalid value [{self.Keyword.BaseImageFormat}]=[{base_image_format}], expect [{self.Keyword.Formats.list()}]")
                
    def Create(self):
        if os.path.exists(self.ImageData[self.Keyword.ImagePath]):
            self.log.info(f"Image already exists. [{self.ImageData[self.Keyword.ImagePath]}]")
            return
        self.DownloadImage()
        self.BuildImage()

    def DownloadImage(self):
        if self.ImageData[self.Keyword.ImageSource] != self.Keyword.Source.Remote:
            return
        image_path = self.ImageData[self.Keyword.ImagePath]
        download_link = self.ImageData[self.Keyword.DownloadLink]
        self.log.info(f"Download image [{image_path}] from [{download_link}]")
        wget.download(url=download_link, out=image_path)

    def BuildImage(self):
        if self.ImageData[self.Keyword.ImageSource] != self.Keyword.Source.Local:
            return
        image_path = self.ImageData[self.Keyword.ImagePath]
        image_format = self.ImageData[self.Keyword.ImageFormat]
        cmd = f"qemu-img create -f {KvmImage.ImageFormatCmd(image_format)}"
        base_image_path = self.ImageData.get(self.Keyword.BaseImagePath, None)
        if base_image_path is not None:
            self.log.info(f"Create image {image_path} from {base_image_path}")
            base_image_format = self.ImageData[self.Keyword.BaseImageFormat]
            cmd = f"{cmd} -b {base_image_path} -F {KvmImage.ImageFormatCmd(base_image_format)}"
        cmd = f"{cmd} {image_path}"
        image_size = self.ImageData.get(self.Keyword.SizeInGB, None)
        if image_size is not None:
            self.log.info(f"Define image size to {image_size}G")
            cmd = f"{cmd} {image_size}G"
        self.log.info(f"run command [{cmd}]")
        Util.run_command(cmd)

if __name__ == "__main__":
    logger = Log.get_logger(KvmImage.Keyword.KvmImage)
    logger.info("Create Kvm Image")
    image = KvmImage(logger)
    image.Create()
