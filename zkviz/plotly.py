import networkx as nx
import plotly.graph_objs as go


class NetworkPlotly:

    def __init__(self, name='Zettelkasten'):
        """
        Build network to visualize with Plotly

        Parameters
        ----------
        name : str
            The network name.
        """
        self.graph = nx.Graph()

    def add_node(self, node_id, title):
        """
        Add a node to the network.

        Parameters
        ----------
        node_id : str, or int
            A  unique identifier for the node, typically the zettel ID.
        title : str
            The text label for each node, typically the zettel title.

        """
        self.graph.add_node(node_id, title=title)

    def add_edge(self, source, target):
        """
        Add a node (a zettel) to the network.

        Parameters
        ----------
        source : str or int
            The ID of the source zettel.
        target : str or int
            The ID of the target (cited) zettel.

        """
        self.graph.add_edge(source, target)

    def build_plotly_figure(self, pos=None):
        """
        Creates a Plot.ly Figure that can be view online or offline.

        Parameters
        ----------
        graph : nx.Graph
            The network of zettels to visualize
        pos : dict
            Dictionay of zettel_id : (x, y) coordinates where to draw nodes. If
            None, the Kamada Kawai layout will be used.

        Returns
        -------
        fig : plotly Figure

        """

        if pos is None:
            # The kamada kawai layout produces a really nice graph but it's
            # a O(N^2) algorithm. It seems only reasonable to draw the graph
            # with fewer than ~1000 nodes.
            if len(self.graph) < 1000:
                pos = nx.layout.kamada_kawai_layout(self.graph)
            else:
                pos = nx.layout.random_layout(self.graph)

        # Create scatter plot of the position of all notes
        node_trace = go.Scatter(
            x=[],
            y=[],
            text=[],
            mode='markers',
            hoverinfo='text',
            marker=dict(
                showscale=True,
                # colorscale options
                #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
                #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
                #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
                colorscale='YlGnBu',
                reversescale=True,
                color=[],
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Centrality',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2)))

        for node in self.graph.nodes():
            x, y = pos[node]
            text = '<br>'.join([node, self.graph.node[node].get('title', '')])
            node_trace['x'] += tuple([x])
            node_trace['y'] += tuple([y])
            node_trace['text'] += tuple([text])

        # Color nodes based on the centrality
        for node, centrality in nx.degree_centrality(self.graph).items():
            node_trace['marker']['color']+=tuple([centrality])

        # Draw the edges as annotations because it's only sane way to draw arrows.
        edges = []
        for from_node, to_node in self.graph.edges():
            edges.append(
                dict(
                    # Tail coordinates
                    ax=pos[from_node][0], ay=pos[from_node][1], axref='x', ayref='y',
                    # Head coordinates
                    x=pos[to_node][0], y=pos[to_node][1], xref='x', yref='y',
                    # Aesthetics
                    arrowwidth=2, arrowcolor='#666', arrowhead=2,
                    # Have the head stop short 5 px for the center point,
                    # i.e., depends on the node marker size.
                    standoff=5,
                    )
                )

        fig = go.Figure(
            data=[node_trace],
            layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=edges,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            )
        )
        return fig

    def render(self, output, view=True):
        """
        Render the network to disk.

        Parameters
        ----------
        output : str
            Name of the output file.
        view : bool
            Open the rendered network using the default browser. Default is
            True.

        """
        fig = self.build_plotly_figure()
        if not output.endswith('.html'):
            output += '.html'
        fig.write_html(output, auto_open=view)
