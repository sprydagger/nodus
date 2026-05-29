from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.spatial import KDTree
import numpy as np
import random
import networkx as nx
# from time import sleep


universe = nx.Graph()
for i in range(50):
    universe.add_node(
        i,
        pos=np.array([random.gauss(0, 5), random.gauss(0, 5), random.gauss(0, 1)]),
        home=None,
        vel=np.array([0, 0, 0]),
        stability=1,
        owner=None,
    )
    universe.nodes[i]["home"] = universe.nodes[i]["pos"].copy()


def update_edge_distances():
    for u, v in universe.edges:
        universe.edges[u, v]["distance"] = np.linalg.norm(
            universe.nodes[u]["pos"] - universe.nodes[v]["pos"]
        )


def draw_graph(ax):
    ax.clear()
    xs = [universe.nodes[n]["pos"][0] for n in universe.nodes]
    ys = [universe.nodes[n]["pos"][1] for n in universe.nodes]
    zs = [universe.nodes[n]["pos"][2] for n in universe.nodes]

    ax.scatter(xs, ys, zs, c="blue", s=50)
    for u, v in universe.edges:
        x_line = [universe.nodes[u]["pos"][0], universe.nodes[v]["pos"][0]]
        y_line = [universe.nodes[u]["pos"][1], universe.nodes[v]["pos"][1]]
        z_line = [universe.nodes[u]["pos"][2], universe.nodes[v]["pos"][2]]
        ax.plot(x_line, y_line, z_line, c="gray", alpha=0.5)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Universe Nodes and Connections")
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_zlim(-15, 15)


def generate_starting_edges():
    positions = [universe.nodes[n]["pos"] for n in universe.nodes]
    nodes = list(universe.nodes)
    tree = KDTree(positions)
    for node in nodes:
        k = min(4, len(nodes))
        distances, indices = tree.query(universe.nodes[node]["pos"], k=k)
        indices = np.atleast_1d(indices)
        for i in range(1, len(indices)):
            neighbor = nodes[int(indices[i])]
            if not universe.has_edge(node, neighbor):
                universe.add_edge(node, neighbor)


generate_starting_edges()
update_edge_distances()

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")


def animate(frame):
    tick()
    draw_graph(ax)
    return (ax,)


def tick():
    for node in universe.nodes:
        pos = universe.nodes[node]["pos"]
        r = pos - universe.nodes[node]["home"]
        weight = 1 - np.exp(-(np.linalg.norm(r) ** 2) / 80.0)
        curl = np.array([-r[1], r[0], 0]) * 0.05 * weight
        home_pull = (universe.nodes[node]["home"] - pos) * 0.02
        universe.nodes[node]["pos"] += home_pull
        universe.nodes[node]["pos"] += curl
        universe.nodes[node]["stability"] -= random.uniform(0.01, 0.1)
        if universe.nodes[node]["stability"] <= 0.3:
            universe.nodes[node]["pos"] += np.random.uniform(-0.1, 0.1, 3)
            universe.nodes[node]["stability"] = 1
    update_edge_distances()
    to_remove = [
        (u, v) for u, v in universe.edges if universe.edges[u, v]["distance"] > 5
    ]
    for u, v in to_remove:
        universe.remove_edge(u, v)


def print_sovereignty():
    owners = Counter(universe.nodes[n]["owner"] for n in universe.nodes)
    for owner, count in owners.items():
        print(f"{owner}: {count} nodes")


print_sovereignty()

scat = ax.scatter([], [], c="blue", s=5)

anim = animation.FuncAnimation(fig, animate, interval=33, cache_frame_data=False)
plt.show()

# while True:
#     tick()
#     draw_graph(ax)
#     plt.savefig('universe.png')
#     sleep(1)
