from logging import Logger

from typing import Type

class Keyword:
    Name = "name"
    Status = "status"

    class States:
        Current = "current"
        Desired = "desired"

    class EntityStatus:
        Active = "active"
        Processing = "processing"       # middle status of operation. need to wait and check result
        Deleted = "deleted"
        Error = "error"


class Entity:
    def __init__(self, entity_data: dict):
        self.Status = entity_data.get(Keyword.Status, Keyword.EntityStatus.Active)

    def to_json(self, data: dict=None) -> dict:
        if data is not None:
            data[Keyword.Status] = self.Status
            return data
        raise NotImplemented(f"Error: method [to_json] not implemented for class {self.__class__.__name__}")
    
    def __eq__(self, other):
        raise NotImplemented(f"Error: method [__eq__] not implemented for class {self.__class__.__name__}")
    
    def save(self):
        raise NotImplemented(f"Error: method [save] not implemented for class {self.__class__.__name__}")

class EntityProvider:
    def __init__(self, app_name: str, entity_class: Type[Entity], log: Logger):
        self.log = log
        self.AppName = app_name
        self.EntityClass = entity_class
        self.Current = None
        self.Desired = None
        self.StateLoaded = False
        self.Changed = False

    def LoadStates(self):
        raise NotImplemented(f"Method LoadStates is not implemented")
    
    def SetCurrent(self, new_current: Entity):
        self.Current = new_current
    
    @staticmethod
    def MatchStates(current: Entity, desired: Entity) -> bool:
        if current is None:
            return False
        if desired is None and current.Status==Keyword.EntityStatus.Deleted:
            return True
        current_data = current.to_json()
        desired_data = desired.to_json()
        
