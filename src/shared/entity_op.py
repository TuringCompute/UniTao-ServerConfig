from shared.entity import Entity, EntityProvider, Keyword

from typing import Type


class EntityOp:
    @staticmethod
    def SyncCurrent(current_entity: Entity):
        raise NotImplemented("Error: method SyncCurrent not implemented")

    @classmethod
    def MakeEntity(cls, current_entity: Entity, desired_entity: Entity) -> Entity:
        if current_entity is None or current_entity.Status != Keyword.EntityStatus.Active:
            return cls.CreateEntity(desired_entity)
        if cls.__compare_and_change(current_entity, desired_entity):
            return current_entity
        return None
    
    @staticmethod
    def CreateEntity(desired_entity: Entity) -> Entity:
        raise NotImplemented("Error: method CreateEntity not implemented")

    @classmethod
    def BreakEntity(cls, current_entity: Entity):
        if current_entity is None:
            raise ValueError(f"data [current] is empty")
        if current_entity.Status == Keyword.EntityStatus.Active:
            cls.DestroyEntity(current_entity)

    @staticmethod
    def DestroyEntity(current_entity: Entity):
        raise NotImplemented("Error: method BreakEntity not implemented")
    
    @classmethod
    def __compare_and_change(cls, current_entity: Entity, desired_entity: Entity) -> Entity:
        for change_func in cls.ChangeFunctions():
            if change_func(current_entity, desired_entity):
                return True
        return False

    @classmethod
    def ChangeFunctions(cls) -> list[callable[Entity, Entity]]:
        raise NotImplemented("Error: Method ChangeFunctions not implemented")

    @classmethod
    def Run(cls, current: Entity, desired: Entity) -> Entity:
        if current is not None:
            cls.SyncCurrent(current)
        if desired is None:            
            cls.BreakEntity(current)
        else:
            new_entity = cls.MakeEntity(current, desired)
            if new_entity is not None:
                return new_entity
        return current
    
class EntityOpRunner:
    def __init__(self, entity_class: Type[Entity], entity_op_class: Type[EntityOp], state_provider: EntityProvider):
        self.cls_entity = entity_class
        self.cls_entity_op = entity_op_class
        self.entity_op = self.cls_entity_op()
        self.state_provider = state_provider

    def Run(self):
        while True:
            current, desired = self.state_provider.GetStates()
            if current is None and desired is None:
                break
            new_current = self.entity_op.Run(current, desired)
            self.state_provider.SetCurrent(new_current)
            