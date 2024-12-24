import logging

from typing import Type

class Keyword:
    Data = "data"
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
    @staticmethod
    def ProviderName() -> str:
        raise NotImplemented("Method Provider Name not implemented")

    # state: load data from state(current/desired)
    #   Current: is the current state
    def GetInventory(self, entity_type:str, entity_id: str) -> dict:
        raise NotImplemented(f"Method GetInventory is not implemented")        

    # list request id of entity type
    def ListRequests(self, entity_type) -> list[str]:
        raise NotImplemented(f"Method ListRequests is not implemented")

    # get request data
    # first level is the record info: id/type/subtype and so on
    def GetRequest(self, entity_type, entity_id) -> dict:
        raise NotImplemented(f"Method GetRequest is not implemented")

    def WriteInventory(self, entity_type:str, entity_id:str, entity_data: dict):
        raise NotImplemented(f"Method WriteData is not implemented") 

class EntityOp:
    def __init__(self, log: logging.Logger, data_handler: DataProvider):
        self.log = log
        self.data_handler = data_handler

    def ProcessRequest(self, request_data: dict):
        while True:
            current_data = self._get_current(request_data)
            new_current = self._process_request(current_data, request_data)
            if new_current is None:
                self.log.info("Request processed, exit.")
                break
            self.log.info("Entity data changed, save.")
            self._write_current(new_current)
            self.log.info("Inventory data change saved.")

    def _process_request(self, inv_record: dict, req_record: dict) -> dict:
        raise NotImplemented(f"Method _process_request is not implemented")

    # pull relative info from request record
    # use the info to query and retrieve current data
    def _get_current(self, request_record) -> dict:
        raise NotImplemented(f"method _get_current is not implemented")
    
    def _write_current(self, current_data):
        raise NotImplemented(f"method _write")

