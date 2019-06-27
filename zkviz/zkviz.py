"""

Visualize the notes network of a Zettelkasten.

Each arrow represents a link from one zettel to another. The script assumes
that zettels have filenames of the form "YYYYMMDDHHMM This is a title" and that
links have the form [[YYYYMMDDHHMM]]

"""
import glob
import os.path
import re

import networkx as nx
import plotly
import plotly.graph_objs as go


PAT_ZK_ID = re.compile(r'^(?P<id>\d+)\s(.*)')
PAT_LINK = re.compile(r'\[\[(\d+)\]\]')


def parse_zettels(filepaths):
    """ Parse the ID and title from the filename.

    Assumes that the filename has the format "YYYYMMDDHHMMSS This is title"

    """
    documents = []
    for filepath in filepaths:
        basename = os.path.basename(filepath)
        filename, ext = os.path.splitext(basename)
        r = PAT_ZK_ID.match(filename)
        if not r:
            continue

        with open(filepath, encoding='utf-8') as f:
            links = PAT_LINK.findall(f.read())

        document = dict(id=r.group(1), title=r.group(2), links=links)
        documents.append(document)
    return documents


def create_graph(zettels):
    """
    Create of graph of the zettels linking to each other.

    Parameters
    ----------
    zettels : list of dictionaries

    Returns
    -------
    graph : nx.Graph

    """

    g = nx.Graph()

    for doc in zettels:
        g.add_node(doc['id'], title=doc['title'])
        for link in doc['links']:
            g.add_edge(doc['id'], link)
    return g


def list_zettels(notes_dir, pattern='*.md'):
    """
    List zettels in a directory.

    Parameters
    ----------
    notes_dir : str
        Path to the directory containing the zettels.
    pattern : str (optional)
        Pattern matching zettels. The default is '*.md'. If there are multiple
        patterns, separate them with a |, such as in '*.md|*.txt'

    """

    filepaths = []

    for patt in pattern.split('|'):
        filepaths.extend(glob.glob(os.path.join(notes_dir, patt)))
    return sorted(filepaths)


def create_plotly_plot(graph, pos=None):
    """
    Creates a Plot.ly Figure that can be view online of offline.

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
        pos = nx.layout.kamada_kawai_layout(graph)

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

    for node in graph.nodes():
        x, y = pos[node]
        text = '<br>'.join([node, graph.node[node].get('title', '')])
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([text])

    # Color nodes based on the centrality
    for node, centrality in nx.degree_centrality(graph).items():
        node_trace['marker']['color']+=tuple([centrality])

    # Draw the edges as annotations because it's only sane way to draw arrows.
    edges = []
    for from_node, to_node in graph.edges():
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


def parse_args(args=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--notes-dir', default='.',
                        help='path to folder containin notes. [.]')
    parser.add_argument('--output', default='zettel-network.html',
                        help='name of output file. [zettel-network.html]')
    parser.add_argument('--pattern', action='append',
            help=('pattern to match notes. You can repeat this argument to'
            ' match multiple file types. [*.md]'))
    parser.add_argument('zettel_paths', nargs='*', help='zettel file paths.')
    args = parser.parse_args(args=args)

    # Use the list of files the user specify, otherwise, fall back to
    # listing a directory.
    if not args.zettel_paths:
        if args.pattern is None:
            args.pattern = ['*.md']
        patterns = '|'.join(args.pattern)

        args.zettel_paths = list_zettels(args.notes_dir, pattern=patterns)
    return args


def main(args=None):
    import sys
    args = parse_args(args)

    zettels = parse_zettels(args.zettel_paths)

    # Fail in case we didn't find a zettel
    if not zettels:
        sys.exit("I'm sorry, I couldn't find any files.")

    graph = create_graph(zettels)
    fig = create_plotly_plot(graph)

    plotly.offline.plot(fig, filename=args.output)


if __name__ == "__main__":
    import sys
    sys.exit(main())
