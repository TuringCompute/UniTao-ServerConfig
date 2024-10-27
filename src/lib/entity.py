class Keyword:
    State = "state"
    Status = "status"
    MAKE = "make"
    BREAK = "break"

class Status:
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
        self.Status = entity_data.get(Keyword.Status, Status.Active)
        


class EntityOp:
    def MakeEntity(self, entity):
        raise NotImplemented("Error: method make_entity not implemented ")

    def BreakEntity(self, entity):
        raise NotImplemented("Error: method break_entity not implemented ")

    def Run(self, entity: Entity):
        if entity.State == Keyword.MAKE:
            self.MakeEntity(entity)
            return
        self.BreakEntity(entity)
        