#!/usr/bin/env python3
from logging import Logger
import os
import copy
from extlib import wget

from shared.utilities import Util
from shared.entity import Entity, Keyword, EntityOp
from src.dataProvider.json_file import JsonFileData
from shared.logger import Log
from typing import List, Callable

from src.shared.data_provider import DataProvider

logger = Log.get_logger("kvm_image")


class KvmImage(Entity):
    class Keyword:
        KvmImage = "kvm_image"
        ImageFormat = "imageFormat"
        ImagePath = "imagePath"
        SizeInGB = "sizeInGB"
        DownloadLink = "downloadLink"
        BaseImagePath = "baseImagePath"
        BaseImageFormat = "baseImageFormat"

        class Format:
            Img = "img"
            QCOW2 = "qcow2"

            @staticmethod
            def list() -> List[str]:
                return [
                    KvmImage.Keyword.Format.Img,
                    KvmImage.Keyword.Format.QCOW2
                ]

    @staticmethod
    def EntityType() -> str:
        return KvmImage.Keyword.KvmImage

    @staticmethod
    def validate_data(data: dict):
        image_format = data.get(KvmImage.Keyword.ImageFormat, None)
        if image_format is None:
            raise ValueError(f"Error: missing field [{KvmImage.Keyword.ImageFormat}] to specify which the file format the image is using")
        if image_format not in KvmImage.Keyword.Format.list():
            raise ValueError(f"Error: Invalid {KvmImage.Keyword.ImageFormat}=[{image_format}, only support{KvmImage.Keyword.Format.list()}")
        image_path = data.get(KvmImage.Keyword.ImagePath, None)
        if image_path is None:
            raise ValueError(f"Error: missing field [{KvmImage.Keyword.ImagePath}] to specify where to hold the image")
        image_size = data.get(KvmImage.Keyword.SizeInGB, None)
        download_link = data.get(KvmImage.Keyword.DownloadLink, None)
        base_image_path = data.get(KvmImage.Keyword.BaseImagePath, None)
        base_image_format = data.get(KvmImage.Keyword.BaseImageFormat, None)
        if download_link is not None:
            # meaning the image file is downloaded from URL. there should be no SizeInGB and BaseImagePath in data
            if image_size is not None:
                raise ValueError(f"Error: since field [{KvmImage.Keyword.DownloadLink}] is not None, field[{KvmImage.Keyword.SizeInGB}] should not exists.")
            
            if base_image_path is not None:
                raise ValueError(f"Error: since field [{KvmImage.Keyword.DownloadLink}] is not None, field[{KvmImage.Keyword.BaseImagePath}] should not exists.")
        else:
            # meaning we need to create the image.
            if image_size is None and base_image_path is None:
                raise ValueError(f"Error: to create image without base, we need to define image size")
            if image_size is not None and type(image_size) is not int:
                raise ValueError(f"Error: invalid value of field [{KvmImage.Keyword.SizeInGB}]={image_size}, expect integer here")
            if base_image_path is not None:
                if base_image_format is None:
                    raise ValueError(f"Error: missing attribute {KvmImage.Keyword.BaseImageFormat} about base image {base_image_path}")
                if base_image_format not in KvmImage.Keyword.Format.list():
                    raise ValueError(f"Error: Invalid {KvmImage.Keyword.BaseImageFormat}=[{base_image_format}, only support {KvmImage.Keyword.Format.list()}")

    def Exists(self) -> bool:
        if self.Data is None:
            return False
        image_path = self.Data.get(KvmImage.Keyword.ImagePath, None)
        if image_path is None:
            return False
        return os.path.exists(image_path)

class KvmImageOp(EntityOp):
    def _process_request(self, entity_id: str, request_data: dict) -> dict:
        request_status = request_data.get(Keyword.Status, Keyword.EntityStatus.Active)
        current_image = KvmImage(self.Current)
        if request_status == Keyword.EntityStatus.Active:
            # create/modify kvm image status=[Active/Error]
            if not current_image.Exists():
                # create kvm image
                self.Create(request_data)
                return request_data
            else:
                # modify kvm image
                for func in [self.ChangeFilePath, self.RebuildImage]:
                    new_data = func(request_data)
                    if new_data is not None:
                        return new_data
        elif request_status == Keyword.EntityStatus.Deleted:
            if current_image.Exists():
                self.log.info(f"kvm image [{entity_id}] exists, Delete")
                # delete kvm image
                self.Destroy()
                self.Current.Data[Keyword.Status] = Keyword.EntityStatus.Deleted
                return self.Current.Data
            self.log.info(f"kvm image [{entity_id}] deleted")
            current_status = current_image.Data.get(Keyword.Status, None) if current_image.Data is not None else None
            if current_status != Keyword.EntityStatus.Deleted:
                self.log.info(f"Sync kvm image data for [{entity_id}]")
                return request_data
        self.log.info("No work to be done.")
        return None

    def ChangeFilePath(self, request_data: dict) -> dict:
        current_image_path = self.Current.Data[KvmImage.Keyword.ImagePath]
        request_image_path = request_data.get(KvmImage.Keyword.ImagePath, None)
        if request_image_path is None:
            return None
        if current_image_path == request_image_path:
            return None
        request_image_folder = os.path.dirname(os.path.abspath(request_image_path))
        Util.run_command(f"mkdir -p {request_image_folder}")
        Util.run_command(f"cp {current_image_path} {request_image_path}")
        Util.run_command(f"rm -f {current_image_path}")
        self.Current.Data[KvmImage.Keyword.ImagePath] = request_image_path
        return self.Current.Data

    def RebuildImage(self, request_data: dict) -> dict:
        for key in [KvmImage.Keyword.ImageFormat, KvmImage.Keyword.BaseImagePath, KvmImage.Keyword.DownloadLink, KvmImage.Keyword.SizeInGB]:
            current_value = self.Current.Data.get(key, None)
            request_value = request_data.get(key, None)
            if current_value != request_value:
                self.Destroy()
                self.Create(request_data)
                return request_data
        return None

    def Create(self, request_data: dict):
        KvmImage.validate_data(request_data)
        image_path = request_data[KvmImage.Keyword.ImagePath]
        image_folder = os.path.dirname(os.path.abspath(image_path))
        Util.run_command(f"mkdir -p {image_folder}")
        download_link = request_data.get(KvmImage.Keyword.DownloadLink, None)
        if download_link is not None:
            self.log.info(f"download as file:{image_path} from {download_link}")
            wget.download(url=download_link, out=image_path)
            return
        image_format = request_data[KvmImage.Keyword.ImageFormat]
        cmd = f"qemu-img create -f {KvmImageOp.ImageFormatCmd(image_format)}"
        base_image_path = request_data.get(KvmImage.Keyword.BaseImagePath, None)
        if base_image_path is not None:
            base_image_format = request_data[KvmImage.Keyword.BaseImageFormat]
            cmd = f"{cmd} -b {base_image_path} -F {KvmImageOp.ImageFormatCmd(base_image_format)}"
        cmd = f"{cmd} {image_path}"
        image_size = request_data.get(KvmImage.Keyword.SizeInGB, None)
        if image_size is not None:
            cmd = f"{cmd} {image_size}G"
        Util.run_command(cmd)

    @staticmethod
    def ImageFormatCmd(image_format):
        if image_format == KvmImage.Keyword.Format.Img:
            return "raw"
        elif image_format == KvmImage.Keyword.Format.QCOW2:
            return "qcow2"

    def Destroy(self):
        image_file_path = self.Current.Data[KvmImage.Keyword.ImagePath]
        Util.run_command(f"rm -rf {image_file_path}")


if __name__ == "__main__":
    logger.info("KVM Image Operation")
    entity_type = KvmImage.EntityType()
    logger.info(f"Create [{entity_type}] data handler from Json File Data Provider")
    data_provider = JsonFileData(entity_type, logger)
    logger.info(f"Create [{entity_type}] Entity Operation Controller")
    image_op = KvmImageOp(KvmImage, logger, data_provider)    
    logger.info("KVM Image Operation Run")
    image_op.Run()

