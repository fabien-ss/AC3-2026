class State:
    def __init__(self, domains, queue, current_arc=None, removed=None, message=""):
        self.domains = domains
        self.queue = queue
        self.current_arc = current_arc
        self.removed = removed if removed else {}
        # list of reinserted arcs as tuples of variable names, e.g. [("X","Y"), ...]
        self.reinserted = []
        self.message = message