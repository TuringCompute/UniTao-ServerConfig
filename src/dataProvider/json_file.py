import argparse
import os
import json
from logging import Logger

from shared.entity import DataProvider
from shared.utilities import Util

class JsonFileData(DataProvider):
    @staticmethod
    def parse_args(app_title:str) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=f"{app_title} Operations")
        parser.add_argument("--desired", type=str, help=f"{app_title} desired state request data json file", required=True)
        parser.add_argument("--current", type=str, help=f"{app_title} folder path that store current data json file", required=True)
        args = parser.parse_args()
        return args

    def __init__(self, entity_type: str, logger: Logger):
        self.EntityType = entity_type
        logger.info(f"parse cmd[{entity_type}] arguments")
        self.Args = JsonFileData.parse_args(entity_type)
        self.InventoryPath = self.Args.current
        if not os.path.isdir(self.InventoryPath):
            raise ValueError(f"--current should point to a folder to hold current state json file")
        self.RequestFile = self.Args.desired

    def _get_inventory(self, entity_type: str, entity_id: str) -> dict:
        file_name = f"{entity_id}.json"
        inventory_file = os.path.join(self.InventoryPath, file_name)
        inventory_data = Util.read_json_file(inventory_file) if os.path.exists(inventory_file) else None
        return inventory_data
    
    def _get_request(self, entity_type: str) -> tuple[str, dict]:
        desired_data = Util.read_json_file(self.RequestFile) if os.path.exists(self.Args.desired) else None
        file_name =  os.path.basename(self.RequestFile)
        file_id, file_ext = os.path.splitext(file_name)
        if file_ext != ".json":
            raise ValueError(f"--desired should point to a json file. with extension=[json], got [{file_ext}] instead.")
        return file_id, desired_data

    def _write_inventory(self, entity_type: str, entity_id: str, data: dict) -> bool:
        file_name = f"{entity_id}.json"
        inventory_file = os.path.join(self.InventoryPath, file_name)
        Util.run_command(f"mkdir -p {self.InventoryPath}")
        with open(inventory_file, "w") as fp:
            json.dump(data, fp, indent=4)
