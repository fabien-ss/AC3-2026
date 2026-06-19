import networkx as nx

class Variable:
    def __init__(self, name, domain):
        self.name = name
        self.domain = set(domain)


class Constraint:
    def __init__(self, var1: Variable, var2: Variable, condition):
        self.var1 = var1
        self.var2 = var2
        self.condition = condition

    def is_satisfied(self, value1, value2):
        return self.condition(value1, value2)

class CSP:
    def __init__(self):
        self.variables = {}
        self.constraints = []

    def add_variable(self, variable):
        self.variables[variable.name] = variable

    def add_constraint(self, constraint):
        self.constraints.append(constraint)

    def get_arc_queue(self):
        queue = []
        for constraint in self.constraints:
            queue.append((constraint.var1, constraint.var2))
            queue.append((constraint.var2, constraint.var1))
        
        return queue

    def get_neighbors(self, x):
        """Return list of arcs (z, x) for every variable z that shares a constraint with x."""
        neighbors = []
        for constraint in self.constraints:
            if constraint.var1 == x:
                neighbors.append((constraint.var2, constraint.var1))
            elif constraint.var2 == x:
                neighbors.append((constraint.var1, constraint.var2))
        return neighbors


def build_graph(csp):
    G = nx.Graph()

    for variable in csp.variables.values():
        G.add_node(variable.name)

    for constraint in csp.constraints:
        G.add_edge(
            constraint.var1.name,
            constraint.var2.name
        )

    return G