import argparse

class Keyword:
    Name = "name"
    State = "state"
    Status = "status"
    MAKE = "make"
    BREAK = "break"

    class EntityStatus:
        Active = "active"
        Deleted = "deleted"
        Error = "error"


class Entity:
    def __init__(self, entity_data: dict):
        if Keyword.State not in entity_data:
            raise ValueError(f"Error: field [{Keyword.State}] is required. to specify the intended state")
        self.State = entity_data.get(Keyword.State, None)
        if self.State not in [Keyword.MAKE, Keyword.BREAK]:
            raise ValueError(f"Error: field [{Keyword.State}] has invalid value [{self.State}], expect [{Keyword.MAKE} or {Keyword.BREAK}]")
        self.Status = entity_data.get(Keyword.Status, Keyword.EntityStatus.Active)
        

class EntityOp:
    @staticmethod
    def parse_args(app_title:str) -> argparse.Namespace:
        parser = argparse.ArgumentParser(description=f"{app_title} Operations")
        parser.add_argument("--desired", type=str, help=f"{app_title} desired state data json file", required=True)
        parser.add_argument("--current", type=str, help=f"{app_title} current state data json file", required=True)
        args = parser.parse_args()
        return args

    def __init__(self, current: Entity=None):
        self.current = current
        if self.current is not None:
            self.SyncCurrent()

    def SyncCurrent(self):
        raise NotImplemented("Error: method SyncCurrent not implemented")

    def MakeEntity(self, entity):
        raise NotImplemented("Error: method MakeEntity not implemented ")

    def BreakEntity(self, entity):
        raise NotImplemented("Error: method BreakEntity not implemented ")

    def Run(self, desired: Entity, current: Entity=None):
        if current is not None:
            current = self.SyncCurrentState(current)
        if desired.Status != Keyword.EntityStatus.Active:
            return
        if desired.State == Keyword.MAKE:
            self.MakeEntity(current)
            return
        self.BreakEntity(current)
        