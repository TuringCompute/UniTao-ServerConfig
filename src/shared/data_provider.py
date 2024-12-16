from shared.entity import Keyword

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
        if Keyword.Entity not in data:
            raise ValueError(f"missing main key [{Keyword.Entity}] for main record")
        self._write_inventory(entity_type, entity_id, data)
    
    def _write_inventory(self, entity_type:str, entity_id: str, data: dict):
        raise NotImplemented(f"Method _write_inventory is not implemented") 
