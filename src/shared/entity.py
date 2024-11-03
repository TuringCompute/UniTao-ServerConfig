import argparse
import os
import json

from shared.utilities import Util


class Keyword:
    Name = "name"
    State = "state"
    Status = "status"

    class EntityStatus:
        Active = "active"
        Deleted = "deleted"
        Error = "error"


class Entity:
    def __init__(self, entity_data: dict):
        if Keyword.State not in entity_data:
            raise ValueError(f"Error: field [{Keyword.State}] is required. to specify the intended state")
        self.Status = entity_data.get(Keyword.Status, Keyword.EntityStatus.Active)

    def to_json(self) -> dict:
        raise NotImplemented(f"Error: method [to_json] not implemented for class {self.__class__.__name__}")

class EntityProvider:
    def __init__(self, app_name: str):
        self.AppName = app_name
        pass

    def GetStates(self) -> tuple[Entity, Entity]:
        raise NotImplemented(f"Method GetState is not implemented")
    
    def SetCurrent(self, new_current: Entity):
        raise NotImplemented(f"Method SetCurrent is not implemented")
    
    @staticmethod
    def MatchStates(current: Entity, desired: Entity) -> bool:
        current_data = current.to_json()
        desired_data = desired.to_json()
        for key in desired_data.keys():
            if current_data[key] != desired_data[key]:
                return False
        return True

class ParamEntityProvider(EntityProvider):
    @staticmethod
    def parse_args(app_title:str) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=f"{app_title} Operations")
        parser.add_argument("--desired", type=str, help=f"{app_title} desired state data json file", required=True)
        parser.add_argument("--current", type=str, help=f"{app_title} current state data json file", required=True)
        args = parser.parse_args()
        return args

    def __init__(self, app_name: str):
        super().__init__(app_name)
        args = ParamEntityProvider.parse_args(app_name)
        self.Params = args
        self.Current = None
        self.Desired = None
        self.StateLoaded = False

    def LoadStates(self):
        if self.StateLoaded:
            return
        desired_data = Util.read_json_file(self.Params.desired)
        current_data = Util.read_json_file(self.Params.current) if os.path.exists(self.Params.current) else None
        self.Desired = self.cls_entity(desired_data)
        self.Current = self.cls_entity(current_data) if current_data is not None else None
        self.StateLoaded = True

    def GetStates(self) -> tuple[Entity, Entity]:
        self.LoadStates()
        if not self.MatchStates(self.Current, self.Desired):
            return self.Current, self.Desired
        return None, None

    def SetCurrent(self, new_current: Entity):
        state_file_dir = os.path.dirname(self.Params.current)
        Util.run_command(f"mkdir -p {state_file_dir}")
        current_data = new_current.to_json()
        with open(self.Params.current, "w") as fp:
            json.dump(current_data, fp, indent=4)
        self.Current = new_current
