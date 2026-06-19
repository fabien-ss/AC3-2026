from csp import CSP
from csp import Variable
from csp import Constraint

from visualizer import CSPVisualizer
from state import State
from visualizer import StateNavigator, save_states_as_images

from matplotlib import pyplot as plt

from ac3 import ac3

csp = CSP()

# Test demandé: Variables X,Y,Z avec domaines {1,2} et contraintes X < Y, Y = Z
# X = Variable("X", [1, 2])
# Y = Variable("Y", [1, 2])
# Z = Variable("Z", [1, 2])

# csp.add_variable(X)
# csp.add_variable(Y)
# csp.add_variable(Z)

# csp.add_constraint(Constraint(X, Y, lambda x, y: x < y))
# csp.add_constraint(Constraint(Y, X, lambda x, y: x > y))
# csp.add_constraint(Constraint(Y, Z, lambda y, z: y == z))

# X = Variable("X", [1, 2])
# Y = Variable("Y", [1, 2])

# csp.add_variable(X)
# csp.add_variable(Y)

# csp.add_constraint(Constraint(X, Y, lambda x, y: x < y))
# csp.add_constraint(Constraint(Y, X, lambda y, x: y > x))

A = Variable("A", [1,2,3])
B = Variable("B", [1,2,3])
C = Variable("C", [1,2,3])
D = Variable("D", [1,2,3])

for v in [A,B,C,D]:
    csp.add_variable(v)

constraints = [
    (A,B),
    (B,C),
    (C,D)
]

# for X,Y in constraints:
#     csp.add_constraint(
#         Constraint(X,Y,lambda x,y: x < y)
#     )
#     csp.add_constraint(
#         Constraint(Y,X,lambda y,x: y > x)
#     )

# ecrire les conrraintes manuelleent
csp.add_constraint(Constraint(A,B,lambda a,b: a < b))
csp.add_constraint(Constraint(B,A,lambda b,a: b > a))
csp.add_constraint(Constraint(B,C,lambda b,c: b < c))
csp.add_constraint(Constraint(C,B,lambda c,b: c > b))
csp.add_constraint(Constraint(C,D,lambda c,d: c < d))
csp.add_constraint(Constraint(D,C,lambda d,c: d > c))


states = ac3(csp)

# Export snapshots as images (one PNG per state) for "photo" visualization
save_states_as_images(states, csp, out_dir="snapshots")

# Also create table-style pages grouping arc processing steps
from visualizer import save_states_table
save_states_table(states, csp, out_dir="snapshots_table", per_page=6)

# Launch interactive navigator if desired
navigator = StateNavigator(states, csp)

plt.show()