import logging

from typing import Type

class Keyword:
    Id = "id"
    EntityData = "entityData"
    EntityType = "entityType"
    Status = "status"

    class States:
        Current = "current"
        Desired = "desired"

    class EntityStatus:
        Active = "active"
        Processing = "processing"       # middle status of operation. need to wait and check result
        Deleted = "deleted"
        Error = "error"


# root data class for Entity. contain basic Data structure of each Entity
class Entity:
    @staticmethod
    def EntityType() -> str:
        raise NotImplemented("Method [_type_name] not implemented")

    def __init__(self, entity_id: str, entity_data: dict):
        self.ID = entity_id
        self.Data = entity_data

# class to provide stored data for 2 states(current/desired)
# the data only reflect the last stored one, not necessarily reflect the truth
# for source of truth, we need to rely on Entity class that load data and collect information from real world
class DataProvider:
    # state: load data from state(current/desired)
    #   Current: is the current state
    def GetInventory(self, entity_type:str, entity_id: str) -> dict:
        return self._get_inventory(entity_type, entity_id)
    
    def _get_inventory(self, entity_type:str, entity_id: str) -> dict:
        raise NotImplemented(f"Method _get_inventory is not implemented")

    def GetRequest(self, entity_type:str) -> tuple[str, dict]:
        return self._get_request(entity_type)
        
    def _get_request(self, entity_type:str) -> tuple[str, dict]:
        raise NotImplemented(f"Method _get_request is not implemented")   

    def WriteData(self, entity_type:str, entity_id: str, data: dict):
        self._write_inventory(entity_type, entity_id, data)
    
    def _write_inventory(self, entity_type:str, entity_id: str, data: dict):
        raise NotImplemented(f"Method _write_inventory is not implemented") 

class EntityOp:
    def __init__(self, entity_class: Type[Entity], log: logging.Logger, data_handler: DataProvider):
        self.log = log
        self.EntityClass = entity_class
        self.EntityType = entity_class.EntityType()
        self.data_handler = data_handler

    def Run(self):
        entity_id, request_data = self.data_handler.GetRequest(self.EntityType)
        self.Current = self.EntityClass(entity_id, None)
        while True:
            self.Current.Data = self.data_handler.GetInventory(self.EntityType, entity_id)
            new_inventory = self._process_request(entity_id, request_data)
            if new_inventory is None:
                self.log.info("Request processed, exit.")
                break
            self.log.info("Inventory data changed, save.")
            self.data_handler._write_inventory(self.EntityType, entity_id, new_inventory)
            self.log.info("Inventory data change saved.")

    def _process_request(self, entity_id: str, request_data: dict) -> dict:
        raise NotImplemented(f"Method _process_request is not implemented")


