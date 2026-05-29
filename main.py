from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.spatial import KDTree
import numpy as np
import random
import networkx as nx
from tqdm import trange


universe = nx.Graph()
for i in range(100):
    universe.add_node(
        i,
        pos=np.array([random.gauss(0, 5), random.gauss(0, 5), random.gauss(0, 1)]),
        home=None,
        vel=np.zeros(3, dtype=float),
        stability=1,
        owner=None,
    )

universe.nodes[0]["owner"] = "019e7403-3c72-7ce4-81ac-e452b0e60d6b"
universe.nodes[10]["owner"] = "019e7403-9ecb-758d-8a34-efad0f72acbf"
universe.nodes[20]["owner"] = "019e7403-b8b5-7c36-84e9-cdaa9266dcf4"


def update_edge_distances():
    edges = list(universe.edges)
    if not edges:
        return
    u_idx = [node_index[u] for u, v in edges]
    v_idx = [node_index[v] for u, v in edges]
    dists = np.linalg.norm(positions[u_idx] - positions[v_idx], axis=1)
    for i, (u, v) in enumerate(edges):
        universe.edges[u, v]["distance"] = dists[i]


def draw_graph(ax):
    ax.clear()
    xs = [universe.nodes[n]["pos"][0] for n in universe.nodes]
    ys = [universe.nodes[n]["pos"][1] for n in universe.nodes]
    zs = [universe.nodes[n]["pos"][2] for n in universe.nodes]

    colors = []
    for n in universe.nodes:
        owner = universe.nodes[n]["owner"]
        if owner is None:
            colors.append("gray")
        elif owner == "019e7403-3c72-7ce4-81ac-e452b0e60d6b":
            colors.append("red")
        elif owner == "019e7403-9ecb-758d-8a34-efad0f72acbf":
            colors.append("blue")
        elif owner == "019e7403-b8b5-7c36-84e9-cdaa9266dcf4":
            colors.append("green")
        else:
            colors.append("white")

    ax.scatter(xs, ys, zs, c=colors, s=50)
    for u, v in universe.edges:
        x_line = [universe.nodes[u]["pos"][0], universe.nodes[v]["pos"][0]]
        y_line = [universe.nodes[u]["pos"][1], universe.nodes[v]["pos"][1]]
        z_line = [universe.nodes[u]["pos"][2], universe.nodes[v]["pos"][2]]
        ax.plot(x_line, y_line, z_line, c="gray", alpha=0.5)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Universe")
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_zlim(-15, 15)


def generate_starting_edges():
    positions = [universe.nodes[n]["pos"] for n in universe.nodes]
    nodes = list(universe.nodes)
    tree = KDTree(positions)
    for node in nodes:
        k = min(6, len(nodes))
        distances, indices = tree.query(universe.nodes[node]["pos"], k=k)
        indices = np.atleast_1d(indices)
        for i in range(1, len(indices)):
            neighbor = nodes[int(indices[i])]
            if not universe.has_edge(node, neighbor):
                universe.add_edge(node, neighbor)


fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")


def animate(frame):
    tick()
    draw_graph(ax)
    if frame % 1000 == 0:
        print_sovereignty()
    return (ax,)


def tick():
    global positions, velocities, homes, stability
    center = np.zeros(3, dtype=float)

    # vectorized physics
    r = positions - center
    norms = np.linalg.norm(r, axis=1, keepdims=True)
    weight = 1 - np.exp(-(norms**2) / 80.0)
    curl = np.column_stack([-r[:, 1], r[:, 0], np.zeros(N)]) * 0.005 * weight

    home_pull = (homes - positions) * 0.015
    velocities += curl + home_pull
    velocities *= 0.85
    positions += velocities

    # home drift
    drift = np.random.uniform(-0.1, 0.1, (N, 3))
    homes += drift
    homes[:, 0] *= 0.9999
    homes[:, 1] *= 0.9999
    homes[:, 2] *= 0.9975

    # stability
    stability -= np.random.uniform(0.01, 0.1, N)
    low = (stability < 0.6) & (np.random.rand(N) < 0.1)
    positions[low] += np.random.uniform(-0.1, 0.1, (low.sum(), 3))
    stability[low] = 1.0

    # sync back to graph
    for i, node in enumerate(universe.nodes):
        universe.nodes[node]["pos"] = positions[i]
        universe.nodes[node]["vel"] = velocities[i]
        universe.nodes[node]["home"] = homes[i]
        universe.nodes[node]["stability"] = stability[i]

    update_edge_distances()

    for u, v in universe.edges:
        u_pos = universe.nodes[u]["pos"]
        v_pos = universe.nodes[v]["pos"]
        diff = v_pos - u_pos
        unit = diff / np.linalg.norm(diff)
        universe.nodes[u]["vel"] += unit * 0.001
        universe.nodes[v]["vel"] -= unit * 0.001
    update_edge_distances()

    to_remove = [
        (u, v)
        for u, v in universe.edges
        if universe.edges[u, v]["distance"] > prune_threshold
    ]
    for u, v in to_remove:
        universe.remove_edge(u, v)

    # ownership logic
    for node in universe.nodes:
        if universe.nodes[node]["owner"] is not None:
            if random.random() < 0.05:
                for neighbor in universe.neighbors(node):
                    if universe.nodes[neighbor]["owner"] is None:
                        universe.nodes[neighbor]["owner"] = universe.nodes[node][
                            "owner"
                        ]
                        break


def print_sovereignty():
    owners = Counter(universe.nodes[n]["owner"] for n in universe.nodes)
    for owner, count in owners.items():
        print(f"{owner}: {count} nodes")


# presim
for i in range(200):
    for node in universe.nodes:
        pos = universe.nodes[node]["pos"]
        r = pos - np.array([0.0, 0.0, 0.0])
        weight = 1 - np.exp(-(np.linalg.norm(r) ** 2) / 80.0)
        curl = np.array([-r[1], r[0], 0]) * 0.005 * weight
        universe.nodes[node]["pos"] += curl
        universe.nodes[node]["pos"] += np.random.uniform(-0.1, 0.1, 3)

for node in universe.nodes:
    universe.nodes[node]["home"] = universe.nodes[node]["pos"].copy()

N = len(universe.nodes)
nodes_list = list(universe.nodes)
node_index = {n: i for i, n in enumerate(nodes_list)}
positions = np.array([universe.nodes[n]["pos"] for n in nodes_list])
velocities = np.array([universe.nodes[n]["vel"] for n in nodes_list])
homes = np.array([universe.nodes[n]["home"] for n in nodes_list])
stability = np.array([universe.nodes[n]["stability"] for n in nodes_list], dtype=float)

generate_starting_edges()
update_edge_distances()

avg_distance = np.mean([universe.edges[u, v]["distance"] for u, v in universe.edges])
prune_threshold = avg_distance * 2

scat = ax.scatter([], [], c="blue", s=5)


for i in trange(100000, desc="Equilibrating universe"):
    tick()
    # if i % 1000 == 0:
    #     print_sovereignty()


anim = animation.FuncAnimation(fig, animate, interval=33, cache_frame_data=False)
plt.show()

# while True:
#     tick()
#     draw_graph(ax)
#     plt.savefig('universe.png')
#     sleep(1)
