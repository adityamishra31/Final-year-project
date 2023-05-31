import networkx as nx
import plotly.graph_objects as go

def         visualize_local_constraints(local_constraints):
    # Create an empty directed graph
    G = nx.DiGraph()

    # Add nodes for each activity
    activities = set()
    for constraint in local_constraints:
        activities.add(constraint[0])
        activities.add(constraint[1])
    for activity in activities:
        G.add_node(activity)

    # Add edges for each local constraint
    for constraint in local_constraints:
        G.add_edge(constraint[0], constraint[1], weight=constraint[2])

    # Set the positions of the nodes in the graph
    pos = nx.spring_layout(G)

    # Create an empty figure
    fig = go.Figure()

    # Add scatter trace for nodes
    nodes = list(G.nodes)
    node_positions = list(pos.values())
    node_x, node_y = zip(*node_positions)
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        marker=dict(size=5),
        text=nodes,
        hoverinfo='text'
    ))

    # Add trace for edges
    edge_x = []
    edge_y = []
    edge_weights = []
    for edge in G.edges:
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_weights.append(G.edges[edge]['weight'])

    fig.add_trace(go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=1),
        hoverinfo=None
    ))

    # Add text annotations for edge labels
    fig.update_layout(
        annotations=[
            go.layout.Annotation(
                x=(pos[edge[0]][0] + pos[edge[1]][0]) / 2,
                y=(pos[edge[0]][1] + pos[edge[1]][1]) / 2,
                text=str(G.edges[edge]['weight']),
                showarrow=False,
                font=dict(color='green')
            ) for edge in G.edges
        ]
    )

    # Set the layout
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    # Show the figure
    return fig
