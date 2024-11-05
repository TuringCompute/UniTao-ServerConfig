import logging
from shared.entity import Entity, EntityProvider, Keyword

from typing import Type, Callable, List



class EntityOp:
    def __init__(self, log: logging.Logger, entity_name: str):
        self.log = log
        self.Name = entity_name

    # sync record with reality, 
    #    if changed, return False
    #    if no change made, return True
    @staticmethod
    def SyncCurrent(current_entity: Entity) -> Entity:
        return current_entity

    def MakeEntity(self, current_entity: Entity, desired_entity: Entity) -> Entity:
        self.log.info("Make Mode")
        if current_entity is None or current_entity.Status != Keyword.EntityStatus.Active:
            self.log.info("Create Mode")
            if current_entity is not None and current_entity.Status == Keyword.EntityStatus.Error:
                self.log.info(f"{self.Name} in error state, delete current as clean up.")
                self.DestroyEntity(current_entity)
                return current_entity
            self.log.info(f"Create {self.Name} as desired")
            return self.CreateEntity(desired_entity)
        self.log.info("Change Mode")
        if self.__compare_and_change(current_entity, desired_entity):
            return current_entity
        return None
    
    @staticmethod
    def CreateEntity(desired_entity: Entity) -> Entity:
        raise NotImplemented("Error: method CreateEntity not implemented")

    def BreakEntity(self, current_entity: Entity):
        if current_entity is None:
            raise ValueError(f"data [current] is empty")
        self.log.info(f"Break Mode")
        if current_entity.Status != Keyword.EntityStatus.Deleted:
            self.log.info(f"Destroy")
            self.DestroyEntity(current_entity)

    @staticmethod
    def DestroyEntity(current_entity: Entity):
        raise NotImplemented("Error: method BreakEntity not implemented")
    
    def __compare_and_change(self, current_entity: Entity, desired_entity: Entity) -> Entity:
        self.log.info(f"Compare {self.Name} and change desired to be current")
        for change_func in self.ChangeFunctions():
            if change_func(current_entity, desired_entity):
                return True
        return False

    def ChangeFunctions(self) -> List[Callable[[Entity, Entity], Entity]]:
        raise NotImplemented("Error: Method ChangeFunctions not implemented")

    def Run(self, current: Entity, desired: Entity) -> Entity:
        self.log.info("Sync current record with reality")
        real_current = self.SyncCurrent(current)
        if real_current is not None:
            self.log.info(f"Current record is off, updata Current record")
            return real_current
        if desired is None or desired.Status == Keyword.EntityStatus.Deleted:
            self.BreakEntity(current)
        else:
            new_entity = self.MakeEntity(current, desired)
            if new_entity is not None:
                return new_entity
        return current
    
class EntityOpRunner:
    def __init__(self, entity_op_class: Type[EntityOp], state_provider: EntityProvider):
        self.EntityOpClass = entity_op_class
        self.entity_op = self.EntityOpClass(state_provider.log)
        self.state_provider = state_provider

    def Run(self):
        while True:
            current, desired = self.state_provider.GetStates()
            if current is None and desired is None:
                self.state_provider.log.info("No more work left, exit loop")
                break
            self.state_provider.log.info("Run Entity Op from current -> desired")
            new_current = self.entity_op.Run(current, desired)
            self.state_provider.SetCurrent(new_current)
            