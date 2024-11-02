#!/usr/bin/env python3
import os
from extlib import wget

from shared.utilities import Util
from shared.entity import Entity, EntityOp, Keyword
from shared.logger import Log


logger = Log.get_logger("kvm_image")


class KvmImage(Entity):
    class Keyword:
        ImageFormat = "imageFormat"
        ImagePath = "imagePath"
        SizeInGB = "sizeInGB"
        DownloadLink = "downloadLink"
        BaseImagePath = "baseImagePath"

        class Format:
            Img = "img"
            QCOW2 = "qcow2"

    def __init__(self, entity_data: dict):
        super().__init__(entity_data)
        self.ImageFormat = entity_data.get(self.Keyword.ImageFormat, None)
        if self.ImageFormat is None:
            raise ValueError(f"Error: missing field [{self.Keyword.ImageFormat}] to specify which the file format the image is using")
        if self.ImageFormat not in [self.Keyword.Format.Img, self.Keyword.Format.QCOW2]:
            raise ValueError(f"Error: Invalid {self.Keyword.ImageFormat}=[{self.ImageFormat}, only support[{self.Keyword.Format.Img}, {self.Keyword.Format.QCOW2}]")
        self.Name = entity_data.get(Keyword.Name, None)
        if self.Name is None:
            raise ValueError(f"Error: missing field [{Keyword.Name}] for the image")
        self.ImagePath = entity_data.get(self.Keyword.ImagePath, None)
        if self.ImagePath is None:
            raise ValueError(f"Error: missing field [{self.Keyword.ImagePath}] to specify where to hold the image")
        self.ImageSize = entity_data.get(self.Keyword.SizeInGB, None)
        self.DownloadLink = entity_data.get(self.Keyword.DownloadLink, None)
        self.BaseImage = entity_data.get(self.Keyword.BaseImagePath, None)
        if self.DownloadLink is not None:
            # meaning the image file is downloaded from URL. there should be no SizeInGB and BaseImagePath in data
            if self.ImageSize is not None:
                raise ValueError(f"Error: since field [{self.Keyword.DownloadLink}] is not None, field[{self.Keyword.SizeInGB}] should not exists.")
            
            if self.BaseImage is not None:
                raise ValueError(f"Error: since field [{self.Keyword.DownloadLink}] is not None, field[{self.Keyword.BaseImagePath}] should not exists.")
        else:
            # meaning we need to create the image.
            if self.ImageSize is None and self.BaseImage is None:
                raise ValueError(f"Error: to create image without base, we need to define image size")
            if self.ImageSize is not None and type(self.ImageSize) is not int:
                raise ValueError(f"Error: invalid value of field [{self.Keyword.SizeInGB}]={self.ImageSize}, expect integer here")


    def Exists(self):
        return os.path.exists(self.FilePath())
        
    def __filename(self):
        return f"{self.Name}.{self.ImageFormat}"
    
    def FilePath(self):
        return os.path.join(self.ImagePath, self.__filename())


class KvmImageOp(EntityOp):
    def MakeEntity(self, image: KvmImage):
        if not image.Exists():
            logger.info("Image does not exists. Create one")
            KvmImageOp.Create(image)
    
    def BreakEntity(self, image: KvmImage):
        if image.Exists():
            KvmImageOp.Destroy(image)

    @staticmethod
    def Create(image: KvmImage):
        if image.DownloadLink is not None:
            KvmImageOp.DownloadImage(image)
            return

    @staticmethod
    def GenerateImage(image: KvmImage):
        cmd = f"qemu-img create {KvmImageOp.FormatCmd(image.ImageFormat)}"
        if image.BaseImage is not None:
            cmd = f"{cmd} -b {image.BaseImage}"
        cmd = f"{cmd} {image.FilePath()}"
        if image.ImageSize is not None:
            cmd = f"{cmd} {image.ImageSize}G"
        Util.run_command(cmd)

    @staticmethod
    def ImageFormatCmd(image_format):
        if image_format == KvmImage.Keyword.Format.Img:
            return "-f raw"
        elif image_format == KvmImage.Keyword.Format.QCOW2:
            return "-f qcow2"

    @staticmethod
    def DownloadImage(image: KvmImage):
        file_path = image.FilePath()
        logger.info(f"download as file:{file_path} from {image.DownloadLink}")
        wget.download(url=image.DownloadLink, out=image.FilePath())


    @staticmethod
    def Destroy(image: KvmImage):
        image_file_path = image.FilePath()
        Util.run_command(f"rm -rf {image_file_path}")


if __name__ == "__main__":
    args = EntityOp.parse_args("KVM Image")
    desired_data = Util.read_json_file(args.desired)
    current_data = Util.read_json_file(args.current) if args.current is not None else None
    image_op = KvmImageOp()

    desired_state = KvmImage(desired_data)
    current_state = KvmImage(current_data) if current_data is not None else None
    image_op.Run(desired_state, current_state)
