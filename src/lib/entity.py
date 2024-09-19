class Keyword:
    OP = "op"
    MAKE = "make"
    BREAK = "break"

class EntityOp:
    def make_entity(self, entity_data):
        if not self.EntityExists(entity_data):
            self.CreateEntity(entity_data)

    def break_entity(self, entity_data):
        if self.EntityExists(entity_data):
            self.DestroyEntity(entity_data)

    def EntityExists(entity_data):
        raise NotImplementedError("Op.EntityExists method is not defined")

    def CreateEntity(entity_data):
        raise NotImplementedError("Op.CreateEntity method is not defined")

    def DestroyEntity(entity_data):
        raise NotImplementedError("Op.DestroyEntity method is not defined")

    def Run(self, op_data: dict):
        if Keyword.OP not in op_data:
            raise Exception(f"Error: field [{Keyword.OP}] is required.")
        op_type = op_data.get(Keyword.OP, None)
        if op_type == Keyword.MAKE:
            self.make_entity(op_data)
        elif op_type == Keyword.BREAK:
            self.break_entity(op_data)
        else:
            raise Exception(f"Error: unknown [{Keyword.OP}]='{op_type}'")
        