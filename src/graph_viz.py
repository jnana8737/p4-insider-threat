import pandas as pd
import networkx as nx
from pyvis.network import Network
import os

def build_privilege_graph():
    df = pd.read_csv('outputs/scored_events.csv')

    # only high/critical events for clarity
    high_risk = df[df['severity'].isin(['HIGH','CRITICAL'])]

    G = nx.DiGraph()

    for _, row in high_risk.iterrows():
        user = str(row.get('user_id', ''))
        resource = str(row.get('resource', ''))
        action = str(row.get('action', ''))
        severity = str(row.get('severity', 'LOW'))

        color_map = {'CRITICAL': 'red', 'HIGH': 'orange', 'MEDIUM': 'gold', 'LOW': 'green'}
        color = color_map.get(severity, 'gray')

        G.add_node(user, color='skyblue', size=20, title=f"User: {user}")
        G.add_node(resource, color='lightgreen', size=15, title=f"Resource: {resource}")
        G.add_edge(user, resource, title=action, color=color)

    net = Network(height='600px', width='100%', bgcolor='#222222', font_color='white', directed=True)
    net.from_nx(G)
    net.save_graph('outputs/privilege_graph.html')
    print(f"Graph saved — {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

if __name__ == "__main__":
    build_privilege_graph()