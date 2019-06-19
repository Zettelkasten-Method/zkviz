"""

Visualize the notes network of a Zettelkasten.

Each arrow represents a link from one zettel to another. The script assumes
that zettels have filenames of the form "YYYYMMDDHHMM This is a title" and that
links have the form [[YYYYMMDDHHMM]]

"""
import glob
import os.path
import re
import argparse

import networkx as nx
import plotly
import plotly.graph_objs as go


PAT_ZK_ID = re.compile(r'^(?P<id>\d+)\s(.*)\.md')
PAT_LINK = re.compile(r'\[\[(\d+)\]\]')

def log(msg, is_verbose=False):
    if not is_verbose:
        return
    print(msg)
    
def printProgressBar(iteration, total, prefix = "", decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    Adapted from <https://stackoverflow.com/a/34325723/1460929>
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    suffix = "Complete"
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s [%d/%d]' % (prefix, bar, percent, suffix, iteration, total), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def parse_zettels(filepaths, is_verbose=False):
    """ Parse the ID and title from the filename.

    Assumes that the filename has the format "YYYYMMDDHHMMSS This is title"

    """
    documents = []
    log("Parsing zettels ...", is_verbose)
    count = len(filepaths)
    for index, filepath in enumerate(filepaths):
        if is_verbose:
            printProgressBar(index+1, count, length=50, prefix="  ")

        filename = os.path.basename(filepath)
        r = PAT_ZK_ID.match(filename)
        if not r:
            continue

        with open(filepath, encoding='utf-8') as f:
            links = PAT_LINK.findall(f.read())

        document = dict(id=r.group(1), title=r.group(2), links=links)
        documents.append(document)
    return documents


def create_graph(zettels, is_verbose=False):
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

    log("Creating graph of zettels linking to each other ...", is_verbose)
    count = len(zettels)
    for index, doc in enumerate(zettels):
        if is_verbose:
            printProgressBar(index+1, count, length=50, prefix="  ")

        g.add_node(doc['id'], title=doc['title'])
        for link in doc['links']:
            g.add_edge(doc['id'], link)
    return g


def list_zettels(notes_dir, pattern='*.md', is_verbose=False):
    """
    List zettels in a directory.

    Parameters
    ----------
    notes_dir : str
        Path to the directory containing the zettels.
    pattern : str (optional)
        Pattern matching zettels. The default is '*.md'.

    """

    filepaths = glob.glob(os.path.join(notes_dir, pattern))
    return filepaths
        
def create_plotly_plot(graph, pos=None, is_verbose=False):
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

    log("Creating plot ...", is_verbose)

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

    log("  Adding nodes ...", is_verbose)
    count_nodes = len(graph.nodes())
    for index, node in enumerate(graph.nodes()):
        if is_verbose:
            printProgressBar(index+1, count_nodes, length=50, prefix="    ")
            
        x, y = pos[node]
        text = '<br>'.join([node, graph.node[node].get('title', '')])
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['text'] += tuple([text])

    # Color nodes based on the centrality
    log("  Coloring nodes ...", is_verbose)
    for node, centrality in nx.degree_centrality(graph).items():
        node_trace['marker']['color']+=tuple([centrality])

    # Draw the edges as annotations because it's only sane way to draw arrows.
    log("  Drawing edges ...", is_verbose)
    edges = []
    count_edges = len(graph.edges())
    for index, from_node, to_node in enumerate(graph.edges()):
        if is_verbose:
            printProgressBar(index+1, count_edges, length=50, prefix="    ")
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

    log("  Drawing figure ...", is_verbose)
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


def main(args=None):
    from argparse import ArgumentParser
    import sys

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose',
                        help='prints progress to STDOUT',
                        action="store_true")
    parser.add_argument('--notes-dir', default='.',
                        help='path to folder containin notes. [.]')
    parser.add_argument('--output', default='zettel-network.html',
                        help='name of output file. [zettel-network.html]')
    parser.add_argument('--pattern', default='*.md',
                        help='pattern to match notes. [*.md]')
    parser.add_argument('zettel_paths', nargs='*', help='zettel file paths.')
    args = parser.parse_args(args=args)

    # Use the list of files the user specify, otherwise, fall back to
    # listing a directory.
    if args.zettel_paths:
        zettel_paths = args.zettel_paths
    else:
        zettel_paths = list_zettels(args.notes_dir, pattern=args.pattern, is_verbose=args.verbose)

    zettels = parse_zettels(zettel_paths, is_verbose=args.verbose)

    # Fail in case we didn't find a zettel
    if not zettels:
        sys.exit("I'm sorry, I couldn't find any files.")

    graph = create_graph(zettels, is_verbose=args.verbose)
    fig = create_plotly_plot(graph, is_verbose=args.verbose)

    plotly.offline.plot(fig, filename=args.output)


if __name__ == "__main__":
    import sys
    sys.exit(main())
