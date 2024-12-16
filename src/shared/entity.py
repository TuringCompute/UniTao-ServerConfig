import logging

from typing import Type

from shared.data_provider import DataProvider



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

    