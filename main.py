import numpy as np
import random
from time import sleep
import networkx as nx

G = nx.Graph()
for i in range(10):
    G.add_node(
        i,
        x=random.gauss(5, 3),
        y=random.gauss(5, 3),
        z=random.gauss(0, 0.5),
        stability=1,
    )


def get_pos(node):
    n = G.nodes[node]
    return np.array([n["x"], n["y"], n["z"]])


def update_edges():
    for u, v in G.edges:
        G.edges[u, v]["distance"] = np.linalg.norm(get_pos(u) - get_pos(v))


for node in G.nodes:
    for other_node in G.nodes:
        if node != other_node and random.random() < 0.3:
            G.add_edge(node, other_node, distance=0)
    update_edges()


def tick():
    for node in G.nodes:
        G.nodes[node]["stability"] -= random.uniform(0.01, 0.1)
        if G.nodes[node]["stability"] <= random.gauss(0.5, 0.5):
            G.nodes[node]["x"] += random.uniform(-0.1, 0.1)
            G.nodes[node]["y"] += random.uniform(-0.1, 0.1)
            G.nodes[node]["z"] += random.uniform(-0.1, 0.1)
            G.nodes[node]["stability"] = 1
    update_edges()


while True:
    tick()
    sleep(1)
