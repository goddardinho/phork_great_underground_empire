import json
import networkx as nx
import matplotlib.pyplot as plt

# Load the map data
with open('map.json', 'r') as f:
    data = json.load(f)

G = nx.DiGraph()

# Add nodes
for node in data['nodes']:
    G.add_node(node)

# Add edges
for edge in data['edges']:
    G.add_edge(edge['from'], edge['to'], direction=edge.get('direction', ''))

plt.figure(figsize=(18, 12))
pos = nx.spring_layout(G, k=0.5, iterations=50)
nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', font_size=8, arrows=True)

# Draw edge labels (directions)
edge_labels = {(e['from'], e['to']): e.get('direction', '') for e in data['edges']}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

plt.title('Zork Map Visualization')
plt.tight_layout()
plt.show()
