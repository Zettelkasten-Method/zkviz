"""

Visualize the notes network of a Zettelkasten.

Each arrow represents a link from one zettel to another. The script assumes
that zettels have filenames of the form "YYYYMMDDHHMM This is a title" and that
links have the form [[YYYYMMDDHHMM]]

"""
import glob
import os.path
import re
from textwrap import wrap

from graphviz import Digraph


PAT_ZK_ID = re.compile(r'^(?P<id>\d+)\s(.*)\.md')
PAT_LINK = re.compile(r'\[\[(\d+)\]\]')


def parse_zettels(filepaths):
    """ Parse the ID and title from the filename.

    Assumes that the filename has the format "YYYYMMDDHHMMSS This is title"

    """
    documents = []
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        r = PAT_ZK_ID.match(filename)
        if not r:
            continue

        with open(filepath, encoding='utf-8') as f:
            links = PAT_LINK.findall(f.read())

        document = dict(id=r.group(1), title=r.group(2), links=links)
        documents.append(document)
    return documents


def wrap_title(text, width=30):
    """ Wrap the title to be a certain width. """
    return '\\n'.join(wrap(text, 29))


def add_node(graph, node_id, title, shape='plaintext'):
    """ Add a node to the graph according to its shape.

    Parameters
    ----------
    shape : str {'plaintext', 'record'}
        The shape to use for each note.

    """
    if shape == 'plaintext':
        label = wrap_title("{} {}".format(node_id, title)).strip()
    elif shape == 'record':
        # Wrap in {} so the elements are stacked vertically
        label = "{" + '|'.join([node_id, wrap_title(title)]) + "}"

    graph.node(node_id, label, shape=shape)


def create_graph(filepaths, output, node_style='record', layout='sfdp'):
    """

    Parameters
    ----------
    notes_dir : str
    output : str
        Name of the output file.
    node_style : str {record, plaintext}
        The style of each node
    pattern : str
        Globbing pattern used to find zettels.
    layout : str
        Layout engine used by Graphviz.
    """
    documents = parse_zettels(filepaths)

    dot = Digraph(comment='Zettelkasten', engine=layout)

    for doc in documents:
        add_node(dot, doc['id'], doc['title'], shape=node_style)
        for link in doc['links']:
            dot.edge(doc['id'], link)
    dot.render(output+'.gv', view=True)


def list_zettels(notes_dir, pattern='*.md'):
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


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--notes-dir', default='.',
                        help='path to folder containin notes. [.]')
    parser.add_argument('--output', default='zettel-network',
                        help='name of output file. [zettel-network]')
    parser.add_argument('--style', default='record',
                        choices=['record', 'plaintext'],
                        help='style of each node.')
    parser.add_argument('--pattern', default='*.md',
                        help='pattern to match notes. [*.md]')
    parser.add_argument('--layout',
                        default='sfdp',
                        choices=['circo', 'dot', 'fdp', 'neato',
                                 'osage', 'patchwork', 'sfdp', 'twopi'],
                        help='layout engine used by graphviz. [sfdp]'
                        )
    parser.add_argument('zettel_paths', nargs='*', help='zettel file paths.')
    args = parser.parse_args()

    if args.zettel_paths:
        zettel_paths = args.zettel_paths
    else:
        zettel_paths = list_zettels(args.notes_dir, pattern=args.pattern)

    create_graph(zettel_paths, args.output, node_style=args.style,
                 layout=args.layout)
