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
        vel=np.array([0,0,0]),
        stability=1,
        owner=None,
    )


def update_edge_distances():
    for u, v in universe.edges:
        universe.edges[u, v]['distance'] = np.linalg.norm(
            universe.nodes[u]['pos'] - universe.nodes[v]['pos']
        )


def draw_graph(ax):
    ax.clear()
    xs = [universe.nodes[n]['pos'][0] for n in universe.nodes]
    ys = [universe.nodes[n]['pos'][1] for n in universe.nodes]
    zs = [universe.nodes[n]['pos'][2] for n in universe.nodes]

    ax.scatter(xs, ys, zs, c='blue', s=50)
    for u, v in universe.edges:
        x_line = [universe.nodes[u]['pos'][0], universe.nodes[v]['pos'][0]]
        y_line = [universe.nodes[u]['pos'][1], universe.nodes[v]['pos'][1]]
        z_line = [universe.nodes[u]['pos'][2], universe.nodes[v]['pos'][2]]
        ax.plot(x_line, y_line, z_line, c='gray', alpha=0.5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Universe Nodes and Connections')
    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.set_zlim(-15, 15)


def generate_starting_edges():
    positions = [universe.nodes[n]["pos"] for n in universe.nodes]
    tree = KDTree(positions)
    for node in universe.nodes:
        distances, indices = tree.query(universe.nodes[node]['pos'], k=4)  # Includes the node itself
        for i in range(1, 4):  # Skip the node itself
            neighbor = list(universe.nodes)[indices[i]]
            if not universe.has_edge(node, neighbor):
                universe.add_edge(node, neighbor)


generate_starting_edges()
update_edge_distances()

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

def animate(frame):
    # update model
    tick()
    # update scatter
    xs = [universe.nodes[n]['pos'][0] for n in universe.nodes]
    ys = [universe.nodes[n]['pos'][1] for n in universe.nodes]
    zs = [universe.nodes[n]['pos'][2] for n in universe.nodes]
    scat._offsets3d = (xs, ys, zs)

    # update Line3DCollection segments
    segments = [
        [
            [universe.nodes[u]['pos'][0], universe.nodes[u]['pos'][1], universe.nodes[u]['pos'][2]],
            [universe.nodes[v]['pos'][0], universe.nodes[v]['pos'][1], universe.nodes[v]['pos'][2]],
        ]
        for u, v in edges_list
    ]
    coll.set_segments(segments)

    return (scat, coll)


def tick():
    center = np.array([0.0, 0.0, 0.0])
    for node in universe.nodes:
        pos = universe.nodes[node]['pos']
        r = pos - center
        weight = np.exp(-np.linalg.norm(r)**2 / 50.0)
        curl = np.array([-r[1], r[0], 0]) * 0.05 * weight
        universe.nodes[node]['pos'] += curl
        universe.nodes[node]['stability'] -= random.uniform(0.01, 0.1)
        if universe.nodes[node]['stability'] <= 0.3:
            universe.nodes[node]['pos'] += np.random.uniform(-0.1, 0.1, 3)
            universe.nodes[node]['stability'] = 1
    update_edge_distances()


# prepare persistent artists for blitting (use a single Line3DCollection for all edges)
from mpl_toolkits.mplot3d.art3d import Line3DCollection

edges_list = list(universe.edges)
xs = [universe.nodes[n]['pos'][0] for n in universe.nodes]
ys = [universe.nodes[n]['pos'][1] for n in universe.nodes]
zs = [universe.nodes[n]['pos'][2] for n in universe.nodes]

scat = ax.scatter(xs, ys, zs, c='blue', s=10)

# build segments for the collection: each segment is [[x1,y1,z1], [x2,y2,z2]]
segments = [
    [
        [universe.nodes[u]['pos'][0], universe.nodes[u]['pos'][1], universe.nodes[u]['pos'][2]],
        [universe.nodes[v]['pos'][0], universe.nodes[v]['pos'][1], universe.nodes[v]['pos'][2]],
    ]
    for u, v in edges_list
]

coll = Line3DCollection(segments, colors='gray', alpha=0.5)
ax.add_collection3d(coll)


def init():
    return (scat, coll)


anim = animation.FuncAnimation(fig, animate, init_func=init, frames=300, interval=1, blit=True)

# Save with ffmpeg for faster encoding; if ffmpeg not available, fallback to pillow GIF
try:
    anim.save('universe.mp4', writer='ffmpeg', dpi=80, fps=10)
except Exception:
    anim.save('universe.gif', writer='pillow')

# while True:
#     tick()
#     draw_graph(ax)
#     plt.savefig('universe.png')
#     sleep(1)
