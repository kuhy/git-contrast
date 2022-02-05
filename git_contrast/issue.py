class Issue:

    def __init__(self, symbolic_name: str, linter: str, category: str):
        self.symbolic_name = symbolic_name
        self.linter = linter
        self.category = category

    def __eq__(self, other):
        return (self.symbolic_name == other.symbolic_name and
                self.linter == other.linter and
                self.category == other.category)

    def __hash__(self):
        # TODO: do this properly
        return self.symbolic_name.__hash__().__xor__(self.linter.__hash__())
