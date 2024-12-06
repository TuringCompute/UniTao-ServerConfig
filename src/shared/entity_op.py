import logging
from shared.entity import Entity, EntityProvider, Keyword

from typing import Type, Callable, List


class EntityOp:
    class Keyword:
        CheckStatus = "checkStatus"
        CreateEntity = "createEntity"
        DestroyEntity = "destroyEntity"
        NoAction = "noAction"           # No action needed. when no need for further decision
        NoDecision = "noDecision"       # No decision made, Need inherit class to make decision


    def __init__(self, entity_name: str, log: logging.Logger):
        self.log = log
        self.Name = entity_name

    # sync record with reality, 
    #    if changed, return False
    #    if no change made, return True
    def SyncCurrent(self, state_provider: EntityProvider) -> bool:
        self.log.info("EntityOp root level: no data to sync")
        return False

    def NextAction(self, state_provider: EntityProvider) -> str:
        if state_provider.Current is None or state_provider.Current.Status == Keyword.EntityStatus.Deleted:
            self.log.info(f"Current does not exists.")
            if state_provider.Desired is None or state_provider.Desired.Status == Keyword.EntityStatus.Deleted:
                self.log.info(f"No Action - Desired does not exists either.")
                return EntityOp.Keyword.NoAction
            self.log.info(f"Next Action=[{EntityOp.Keyword.CreateEntity}], Current [{self.Name}] does not exists")
            return EntityOp.Keyword.CreateEntity
        if state_provider.Current.Status == Keyword.EntityStatus.Processing:
            self.log.info(f"Next Action=[{EntityOp.Keyword.CheckStatus}], current [{self.Name}] @[{Keyword.EntityStatus.Processing}]")
            return EntityOp.Keyword.CheckStatus
        if state_provider.Desired.Status == Keyword.EntityStatus.Deleted:
            return EntityOp.Keyword.DestroyEntity
        return EntityOp.Keyword.NoDecision
    
    @staticmethod
    def CreateEntity(desired_entity: Entity) -> Entity:
        raise NotImplemented("Error: method CreateEntity not implemented")

    @staticmethod
    def DestroyEntity(current_entity: Entity):
        raise NotImplemented("Error: method BreakEntity not implemented")

    # get action function from key, if don't recognize the key, then return None
    def GetAction(self, action_key) -> Callable[[Entity, Entity]]:
        return None

    # return true so the outside loop continue
    # return false the outside loop will break
    def Run(self, state_provider: EntityProvider) -> bool:
        next_action = self.NextAction(state_provider)
        if next_action == EntityOp.Keyword.NoAction:
            self.log.info("No more work left")
            return False
        if next_action == EntityOp.Keyword.NoDecision:
            self.log.info("Wait 1 second and try to make decision again")
            return True
        action = self.GetAction(next_action)
        action(state_provider)
        return True
    
class EntityOpRunner:
    def __init__(self, entity_op_class: Type[EntityOp], state_provider: EntityProvider):
        self.EntityOpClass = entity_op_class
        self.entity_op = self.EntityOpClass(state_provider.AppName, state_provider.log)
        self.state_provider = state_provider

    def Run(self):
        self.state_provider.LoadStates()
        while True:
            if self.entity_op.SyncCurrent(self.state_provider.Current):
                self.state_provider.SetCurrent(new_current)
                continue
            self.state_provider.log.info("Run Entity Op from current -> desired")
            new_current = self.entity_op.Run(self.state_provider)
            
            