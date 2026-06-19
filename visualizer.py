import os
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import gridspec

from csp import build_graph
from matplotlib.widgets import Button
from csp import CSP
import state

def build_graph(csp: CSP):

    G = nx.Graph()

    for variable in csp.variables.values():
        G.add_node(variable.name)

    for constraint in csp.constraints:
        G.add_edge(
            constraint.var1.name,
            constraint.var2.name
        )

    return G

class CSPVisualizer:

    def __init__(self, csp):
        self.csp = csp

    def draw_state(self, queue, current_arc=None):

        G = build_graph(self.csp)

        state = self.states[self.index]

        labels = {}

        for v in self.csp.variables.values():

            domain = sorted(v.domain)

            removed = state.removed.get(v.name, set())

            display = []

            for val in domain:
                if val in removed:
                    display.append(f"({val})")
                else:
                    display.append(str(val))

            labels[v.name] = f"{v.name}\n{{{','.join(display)}}}"

        fig, (ax_graph, ax_queue) = plt.subplots(
            1,
            2,
            figsize=(12, 6),
            gridspec_kw={"width_ratios": [3, 1]}
        )

        pos = nx.spring_layout(G, seed=42)

        edge_colors = []

        for edge in G.edges():

            if current_arc is not None:

                x, y = current_arc

                if edge == (x.name, y.name) or \
                   edge == (y.name, x.name):

                    edge_colors.append("red")

                else:
                    edge_colors.append("black")

            else:
                edge_colors.append("black")

        nx.draw(
            G,
            pos,
            labels=labels,
            node_size=5000,
            node_color="lightblue",
            edge_color=edge_colors,
            width=3,
            font_size=10,
            ax=ax_graph
        )

        ax_graph.set_title("Graphe de contraintes")

        queue_text = ""

        if current_arc is not None:

            queue_text += (
                f"Arc courant : "
                f"{current_arc[0].name}"
                f" → "
                f"{current_arc[1].name}\n\n"
                f"" # afficher la contrainte correspondante si possible
            )

            queue_text += (
                f"Revise("
                f"{current_arc[0].name},"
                f"{current_arc[1].name}"
                f")\n\n"
            )

        queue_text += "Queue :\n\n"

        for arc in queue:
            queue_text += (
                f"{arc[0].name}"
                f" → "
                f"{arc[1].name}\n"
            )

        ax_queue.axis("off")

        ax_queue.text(
            0,
            1,
            queue_text,
            fontsize=12,
            va="top"
        )

        plt.tight_layout()
        plt.show()

class StateNavigator:

    def __init__(self, states, csp):
        self.states = states
        self.csp = csp
        self.index = 0

        self.fig = plt.figure(figsize=(12, 6))

        self.ax_graph = self.fig.add_subplot(1, 2, 1)
        self.ax_info = self.fig.add_subplot(1, 2, 2)

        self.create_buttons()
        self.render()

    def create_buttons(self):
        ax_prev = plt.axes([0.7, 0.02, 0.1, 0.05])
        ax_next = plt.axes([0.81, 0.02, 0.1, 0.05])

        self.btn_prev = Button(ax_prev, "Previous")
        self.btn_next = Button(ax_next, "Next")

        self.btn_prev.on_clicked(self.previous)
        self.btn_next.on_clicked(self.next)
    
    def next(self, event):
        print("Next button clicked")
        if self.index < len(self.states) - 1:
            print(f"Moving to state {self.index + 2}")
            self.index += 1
            self.render()
        else:
            print("Already at the last state")
    
    def previous(self, event):
        print("Previous button clicked")
        if self.index > 0:
            print(f"Moving to state {self.index}")
            self.index -= 1
            self.render()
        else:
            print("Already at the first state")

    def render(self):
        print(f"Rendering state {self.index + 1}/{len(self.states)}")
        self.ax_graph.clear()
        self.ax_info.clear()
        state = self.states[self.index]

        self.ax_info.axis("off")

        text = f"State {self.index + 1}/{len(self.states)}\n\n"

        if state.current_arc:
            x, y = state.current_arc
            text += f"Arc: {x.name} → {y.name}\n"
            text += f"Revise({x.name},{y.name})\n\n"

        text += "Queue:\n"
        for a, b in state.queue:
            text += f"{a.name} → {b.name}\n"

        self.ax_info.text(0, 1, text, va="top")

        G = build_graph(self.csp)
        pos = nx.spring_layout(G, seed=42)

        edge_colors = []

        reinserted_pairs = set(state.reinserted) if hasattr(state, 'reinserted') else set()

        for u, v in G.edges():
            # highlight current arc in red
            if state.current_arc and (
                (u == state.current_arc[0].name and v == state.current_arc[1].name)
                or
                (u == state.current_arc[1].name and v == state.current_arc[0].name)
            ):
                edge_colors.append("red")
            # highlight newly reinserted arcs in green
            elif (u, v) in reinserted_pairs or (v, u) in reinserted_pairs:
                edge_colors.append("green")
            else:
                edge_colors.append("black")


        # Build labels using the snapshot domains in the state and mark removed values
        labels = {}
        for var_name in self.csp.variables:
            dom = sorted(list(state.domains.get(var_name, [])))
            removed = state.removed.get(var_name, set())
            display = []
            for val in dom:
                if val in removed:
                    display.append(f"({val})")
                else:
                    display.append(str(val))
            labels[var_name] = f"{var_name}\n{{{','.join(display)}}}"

        nx.draw(
            G,
            pos,
            labels=labels,
            ax=self.ax_graph,
            node_color="lightblue",
            edge_color=edge_colors,
            node_size=3000
        )

        plt.tight_layout()
        self.fig.canvas.draw()


def save_states_as_images(states, csp, out_dir="snapshots"):
    """Export each state to a separate PNG file in `out_dir`.

    Each image shows the constraint graph on the left and the queue/info on the right.
    """
    os.makedirs(out_dir, exist_ok=True)

    # stable layout across images
    G = build_graph(csp)
    pos = nx.spring_layout(G, seed=42)

    for i, state in enumerate(states, start=1):
        fig, (ax_graph, ax_queue) = plt.subplots(
            1,
            2,
            figsize=(12, 6),
            gridspec_kw={"width_ratios": [3, 1]}
        )

        # build edge colors: highlight current arc (red) and reinserted arcs (green)
        reinserted_pairs = set(state.reinserted) if hasattr(state, 'reinserted') else set()
        edge_colors = []
        for u, v in G.edges():
            if state.current_arc and (
                (u == state.current_arc[0].name and v == state.current_arc[1].name)
                or
                (u == state.current_arc[1].name and v == state.current_arc[0].name)
            ):
                edge_colors.append("red")
            elif (u, v) in reinserted_pairs or (v, u) in reinserted_pairs:
                edge_colors.append("green")
            else:
                edge_colors.append("black")

        # Build labels using snapshot domains in the state and mark removed values
        labels = {}
        for var_name in csp.variables:
            dom = sorted(list(state.domains.get(var_name, [])))
            removed = state.removed.get(var_name, set())
            display = []
            for val in dom:
                if val in removed:
                    display.append(f"({val})")
                else:
                    display.append(str(val))
            labels[var_name] = f"{var_name}\n{{{','.join(display)}}}"

        nx.draw(
            G,
            pos,
            labels=labels,
            ax=ax_graph,
            node_color="lightblue",
            edge_color=edge_colors,
            node_size=3000
        )

        ax_graph.set_title(f"State {i}: {state.message}")

        # queue/info text on the right
        ax_queue.axis("off")
        info_text = f"State {i}/{len(states)}\n\n"
        if state.current_arc:
            arc_constraint = None
            for c in csp.constraints:
                if (c.var1.name == state.current_arc[0].name and c.var2.name == state.current_arc[1].name) or (c.var1.name == state.current_arc[1].name and c.var2.name == state.current_arc[0].name):
                    arc_constraint = c
                    break 
            if arc_constraint:
                info_text += f"Arc: {state.current_arc[0].name} → {state.current_arc[1].name}\n"
                info_text += f"Constraint: {arc_constraint.condition.__name__ if hasattr(arc_constraint.condition, '__name__') else str(arc_constraint.condition)}\n"
            x, y = state.current_arc
            info_text += f"Arc: {x.name} → {y.name}\n"
            info_text += f"Revise({x.name},{y.name})\n\n"

        info_text += "Queue:\n"
        for a, b in state.queue:
            info_text += f"{a.name} → {b.name}\n"

        if state.reinserted:
            info_text += "\nReinserted:\n"
            for (u, v) in state.reinserted:
                info_text += f"{u} → {v}\n"

        ax_queue.text(0, 1, info_text, fontsize=12, va="top")

        plt.tight_layout()

        safe_name = state.message.replace(' ', '_').replace(':', '')
        filename = f"{i:02d}_{safe_name}.png"
        path = os.path.join(out_dir, filename)
        fig.savefig(path)
        plt.close(fig)

    print(f"Saved {len(states)} snapshot images to {out_dir}")


def _group_states_by_arc(states):
    """Group the states list into one summary per arc processed.

    For each arc (x,y) processed we produce a dict with:
      - arc: (x, y)
      - domains: domains after revise
      - removed: removed values from x
      - reinserted: list of reinserted arcs
      - queue: queue snapshot at that moment
      - message: descriptive message
    """
    arc_summaries = []
    i = 0
    n = len(states)
    while i < n:
        s = states[i]
        if s.current_arc:
            x, y = s.current_arc
            summary = {
                'arc': (x, y),
                'domains': dict(s.domains),
                'removed': dict(s.removed) if s.removed else {},
                'reinserted': list(s.reinserted) if hasattr(s, 'reinserted') else [],
                'queue': list(s.queue),
                'message': s.message,
            }

            # check next states for revise (removed) and propagation (reinserted)
            j = i + 1
            while j < n and states[j].current_arc == s.current_arc:
                sj = states[j]
                if sj.removed:
                    summary['domains'] = dict(sj.domains)
                    summary['removed'] = dict(sj.removed)
                j += 1

            # look for a propagation snapshot after the revise
            if j < n and getattr(states[j], 'reinserted', None):
                summary['reinserted'] = list(states[j].reinserted)
                summary['queue'] = list(states[j].queue)
                summary['domains'] = dict(states[j].domains)
                summary['message'] = states[j].message
                j += 1

            arc_summaries.append(summary)
            i = j
        else:
            i += 1

    return arc_summaries


def save_states_table(states, csp, out_dir="snapshots_table", per_page=6):
    """Create paged PNGs showing a table-like layout.

    Left column: initial graph and queue (spanning rows).
    Right column: up to `per_page` panels (one per processed arc) stacked vertically.
    """
    os.makedirs(out_dir, exist_ok=True)

    # build arc summaries
    arc_summaries = _group_states_by_arc(states)
    if not arc_summaries:
        print("No arc processing steps found to build table.")
        return

    # stable base graph layout
    G = build_graph(csp)
    pos = nx.spring_layout(G, seed=42)

    total = len(arc_summaries)
    page = 0
    for start in range(0, total, per_page):
        page += 1
        chunk = arc_summaries[start:start+per_page]
        rows = len(chunk)

        fig = plt.figure(figsize=(12, 3 * max(1, rows)))
        gs = gridspec.GridSpec(rows, 2, width_ratios=[2, 3], hspace=0.6)

        # left column spanning all rows: initial graph + queue (we'll use the first left subplot spanning)
        ax_left = fig.add_subplot(gs[:, 0])
        ax_left.axis('off')

        # draw initial graph using initial domains from states[0]
        init_state = states[0]
        labels = {}
        for var_name in csp.variables:
            dom = sorted(list(init_state.domains.get(var_name, [])))
            labels[var_name] = f"{var_name}\n{{{','.join(str(d) for d in dom)}}}"

        nx.draw(G, pos, labels=labels, ax=ax_left, node_color='lightblue', node_size=2500)
        ax_left.set_title('État initial')

        # draw queue text under the initial graph
        qtext = "Queue initiale:\n\n"
        for a, b in init_state.queue:
            qtext += f"{a.name} → {b.name}\n"
        ax_left.text(0, -0.12, qtext, transform=ax_left.transAxes, va='top')

        # right column: one axis per arc summary
        for r, summary in enumerate(chunk):
            ax = fig.add_subplot(gs[r, 1])
            ax.axis('off')

            # edge colors
            reinserted_pairs = set(summary.get('reinserted', []))
            edge_colors = []
            ux, vy = summary['arc']
            for u, v in G.edges():
                if (u == ux.name and v == vy.name) or (u == vy.name and v == ux.name):
                    edge_colors.append('red')
                elif (u, v) in reinserted_pairs or (v, u) in reinserted_pairs:
                    edge_colors.append('green')
                else:
                    edge_colors.append('black')

            # labels with removed marking
            labels = {}
            for var_name in csp.variables:
                dom = sorted(list(summary['domains'].get(var_name, [])))
                removed = summary.get('removed', {}).get(var_name, set())
                display = []
                for val in dom:
                    if val in removed:
                        display.append(f"({val})")
                    else:
                        display.append(str(val))
                labels[var_name] = f"{var_name}\n{{{','.join(display)}}}"

            nx.draw(G, pos, labels=labels, ax=ax, node_color='wheat', edge_color=edge_colors, node_size=1200)

            title = f"{summary['arc'][0].name} → {summary['arc'][1].name} : {summary.get('message','') }"
            ax.set_title(title)

            # add small text with queue and reinserted
            info = ""
            if summary.get('removed'):
                info += "Suppression: \n"
                for var, vals in summary['removed'].items():
                    info += f"{var}: {sorted(list(vals))}\n"
            if summary.get('reinserted'):
                info += "\nPropagation (réinserés):\n"
                for u, v in summary['reinserted']:
                    info += f"{u} → {v}\n"

            ax.text(0, -0.15, info, transform=ax.transAxes, va='top', fontsize=9)

        filename = f"table_page_{page:02d}.png"
        path = os.path.join(out_dir, filename)
        plt.tight_layout()
        fig.savefig(path)
        plt.close(fig)

    print(f"Saved table pages to {out_dir}")