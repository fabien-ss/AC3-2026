from state import State

def ac3(csp):
    Q = list(set(csp.get_arc_queue()))

    print("Initial arc queue:")
    for x, y in Q:
        print(f"{x.name} → {y.name}")

    states = []

    # Initial snapshot
    states.append(
        State(
            domains={v.name: set(v.domain) for v in csp.variables.values()},
            queue=[(a, b) for a, b in Q],
            current_arc=None,
            removed={},
            message="Initial state"
        )
    )

    while Q:
        x, y = Q.pop(0)

        # Snapshot: arc extracted
        states.append(
            State(
                domains={v.name: set(v.domain) for v in csp.variables.values()},
                queue=[(a, b) for a, b in Q],
                current_arc=(x, y),
                removed={},
                message=f"Processing {x.name} → {y.name}"
            )
        )

        revised, removed_vals = revise(x, y, csp)

        # Snapshot: after revise shows removed values (if any)
        states.append(
            State(
                domains={v.name: set(v.domain) for v in csp.variables.values()},
                queue=[(a, b) for a, b in Q],
                current_arc=(x, y),
                removed={x.name: removed_vals} if removed_vals else {},
                message=f"Revise {x.name},{y.name}"
            )
        )

        reinserted = []
        if revised:
            # add all neighbors (z, x) except where z == y
            for (z, _x) in csp.get_neighbors(x):
                # neighbors() returns (z, x) pairs; skip the neighbor equal to y
                if z == y:
                    continue
                Q.append((z, _x))
                reinserted.append((z.name, _x.name))

            # Snapshot: after propagation (arcs reinserted)
            st = State(
                domains={v.name: set(v.domain) for v in csp.variables.values()},
                queue=[(a, b) for a, b in Q],
                current_arc=None,
                removed={},
                message=f"Propagation after {x.name}"
            )
            st.reinserted = reinserted
            states.append(st)

        # Check for failure
        for d in (v.domain for v in csp.variables.values()):
            if len(d) == 0:
                states.append(
                    State(
                        domains={v.name: set(v.domain) for v in csp.variables.values()},
                        queue=[(a, b) for a, b in Q],
                        current_arc=None,
                        removed={},
                        message="Failure: some domain became empty"
                    )
                )
                return states

    # Final stabilized state
    states.append(
        State(
            domains={v.name: set(v.domain) for v in csp.variables.values()},
            queue=[],
            current_arc=None,
            removed={},
            message="Final state (arc-consistent)"
        )
    )

    return states


def revise(x, y, csp):
    removed = set()

    # find the constraint x -> y
    constraint = None
    reversed_constraint = False
    for c in csp.constraints:
        if c.var1 == x and c.var2 == y:
            constraint = c
            reversed_constraint = False
            break
        elif c.var1 == y and c.var2 == x:
            constraint = c
            reversed_constraint = True
            break

    # if no constraint exists between x and y, nothing to do
    if constraint is None:
        return False, set()

    # For each value in x.domain, check existence of supporting value in y.domain
    for val_x in list(x.domain):
        ok = False
        for val_y in list(y.domain):
            if not constraint:
                continue
            if not reversed_constraint and constraint.is_satisfied(val_x, val_y):
                ok = True
                break
            if reversed_constraint and constraint.is_satisfied(val_y, val_x):
                ok = True
                break
        if not ok:
            x.domain.remove(val_x)
            removed.add(val_x)

    return len(removed) > 0, removed