import osmnx as ox
import matplotlib.pyplot as plt

# 1. Load the graph from your file
# Replace 'your_file.graphml' with the actual path
G = ox.load_graphml("roves_undirected.graphml")

# 2. Visualize the graph
# node_size=0 hides the intersection points for a cleaner look
fig, ax = ox.plot_graph(G, node_color="r", node_size=15, edge_linewidth=2, edge_color="#666666")

plt.show()