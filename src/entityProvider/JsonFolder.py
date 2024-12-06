import argparse

from logging import Logger
from typing import Type
import os

from shared.entity import Entity, EntityProvider, Keyword
from shared.utilities import Util

class JsonFolderEntityProvider(EntityProvider):
    @staticmethod
    def parse_args(app_title:str) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=f"{app_title} Operations")
        parser.add_argument(f"--path", type=str, help=f"{app_title} entity state json data folder path", required=True)
        args = parser.parse_args()
        return args

    def __init__(self, app_name: str, entity_class: Type[Entity], log: Logger):
        super().__init__(app_name, entity_class, log)
        args = JsonFolderEntityProvider.parse_args(app_name)
        self.Params = args
        self.EntityPath = None
        self.StateLoaded = False

    def LoadStates(self):
        if self.StateLoaded:
            return
        self.log.info(f"load entity state from Json folder [{self.Params.path}]")
        self.EntityPath = self.Params.path
        self.CurrentPath = os.path.join(self.EntityPath, Keyword.States.Current)
        Util.run_command(f"mkdir -p {self.CurrentPath}")
        self.DesiredPath = os.path.join(self.EntityPath, Keyword.States.Desired)
        Util.run_command(f"mkdir -p {self.DesiredPath}")
        self.Current = self.EntityClass(self.EntityPath, Keyword.States.Current)
        self.Desired = self.EntityClass(self.EntityPath, Keyword.States.Desired)
        self.StateLoaded = True
    
    def SetCurrent(self, new_current: Entity):
        new_current.save()
        

