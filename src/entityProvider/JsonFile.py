import argparse
import os
import json
from logging import Logger

from typing import Type

from shared.entity import Entity, EntityProvider
from shared.utilities import Util

class JsonFileEntityProvider(EntityProvider):
    @staticmethod
    def parse_args(app_title:str) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=f"{app_title} Operations")
        parser.add_argument("--desired", type=str, help=f"{app_title} desired state data json file", required=True)
        parser.add_argument("--current", type=str, help=f"{app_title} current state data json file", required=True)
        args = parser.parse_args()
        return args

    def __init__(self, app_name: str, entity_class: Type[Entity], log: Logger):
        super().__init__(app_name, entity_class, log)
        args = JsonFileEntityProvider.parse_args(app_name)
        self.Params = args

    def LoadStates(self):
        if self.StateLoaded:
            return
        self.log.info(f"load states from current:[{self.Params.current}], desired:[{self.Params.desired}]")
        desired_data = Util.read_json_file(self.Params.desired) if os.path.exists(self.Params.desired) else None
        current_data = Util.read_json_file(self.Params.current) if os.path.exists(self.Params.current) else None
        self.Desired = self.EntityClass(desired_data) if desired_data is not None else None
        self.Current = self.EntityClass(current_data) if current_data is not None else None
        self.StateLoaded = True

    def SetCurrent(self, new_current: Entity):
        self.log.info(f"Save new_current @[{self.Params.current}]")
        state_file_dir = os.path.dirname(self.Params.current)
        Util.run_command(f"mkdir -p {state_file_dir}")
        current_data = new_current.to_json()
        with open(self.Params.current, "w") as fp:
            json.dump(current_data, fp, indent=4)
        self.Current = new_current
