class Command:
    def execute(self):
        pass
    def undo(self):
        pass

class CommandStack:
    def __init__(self, max_size=50):
        self.stack = []
        self.redo_stack = []
        self.max_size = max_size

    def push(self, command):
        command.execute()
        self.stack.append(command)
        self.redo_stack.clear()
        if len(self.stack) > self.max_size:
            self.stack.pop(0)

    def undo(self):
        if self.stack:
            command = self.stack.pop()
            command.undo()
            self.redo_stack.append(command)

    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.stack.append(command)

class PlaceTileCommand(Command):
    def __init__(self, grid, r, c, old_val, new_val):
        self.grid = grid
        self.r = r
        self.c = c
        self.old_val = old_val
        self.new_val = new_val

    def execute(self):
        self.grid[self.r][self.c] = self.new_val

    def undo(self):
        self.grid[self.r][self.c] = self.old_val

class PlaceEntityCommand(Command):
    def __init__(self, entities_list, entity_data, is_add=True):
        self.entities_list = entities_list
        self.entity_data = entity_data # dict: {type, x, y, properties}
        self.is_add = is_add

    def execute(self):
        if self.is_add:
            self.entities_list.append(self.entity_data)
        else:
            # Remove by finding matching data (simple match)
            if self.entity_data in self.entities_list:
                self.entities_list.remove(self.entity_data)

    def undo(self):
        if self.is_add:
            if self.entity_data in self.entities_list:
                self.entities_list.remove(self.entity_data)
        else:
            self.entities_list.append(self.entity_data)

class BulkTileCommand(Command):
    def __init__(self, grid, changes):
        """changes: list of (r, c, old, new)"""
        self.grid = grid
        self.changes = changes

    def execute(self):
        for r, c, old, new in self.changes:
            self.grid[r][c] = new

    def undo(self):
        for r, c, old, new in self.changes:
            self.grid[r][c] = old
