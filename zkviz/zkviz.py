"""

Visualize the notes network of a Zettelkasten.

Each arrow represents a link from one zettel to another. The script assumes
that zettels have filenames of the form "YYYYMMDDHHMM This is a title" and that
links have the form [[YYYYMMDDHHMM]]

"""
import glob
import os.path
import re
from textwrap import fill




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


def create_graph(zettels, graph):
    """
    Create of graph of the zettels linking to each other.

    Parameters
    ----------
    zettels : list of dictionaries

    Returns
    -------
    graph : nx.Graph

    """

    for doc in zettels:
        graph.add_node(doc['id'], title=doc['title'])
        for link in doc['links']:
            graph.add_edge(doc['id'], link)
    return graph


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


def parse_args(args=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--notes-dir', default='.',
                        help='path to folder containin notes. [.]')
    parser.add_argument('--output', default='zettel-network',
                        help='name of output file. [zettel-network]')
    parser.add_argument('--pattern', action='append',
            help=('pattern to match notes. You can repeat this argument to'
            ' match multiple file types. [*.md]'))
    parser.add_argument('--use-graphviz', action='store_true', default=False,
            help='Use Graphviz instead of plotly to render the network.')
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
    args = parse_args(args)

    zettels = parse_zettels(args.zettel_paths)

    # Fail in case we didn't find a zettel
    if not zettels:
        raise FileNotFoundError("I'm sorry, I couldn't find any files.")

    if args.use_graphviz:
        from zkviz.graphviz import NetworkGraphviz
        import graphviz
        try:
            graphviz.version()
        except graphviz.ExecutableNotFound:
            raise FileNotFoundError(fill(
                "The Graphviz application must be installed for the"
                " --use-graphviz option to work. Please see"
                " https://graphviz.org/download/ for installation"
                " instructions."
           ))
        graph = NetworkGraphviz()
    else:
        from zkviz.plotly import NetworkPlotly
        graph = NetworkPlotly()

    graph = create_graph(zettels, graph)
    graph.render(args.output)


if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except FileNotFoundError as e:
        # Failed either because it didn't find any files or because Graphviz
        # wasn't installed
        sys.exit(e)
