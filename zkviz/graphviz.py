from textwrap import fill

from graphviz import Digraph


class NetworkGraphviz:

    def __init__(self, name='Zettelkasten', engine='sfdp', shape='record'):
        """
        Build network to visualize with Graphviz.

        Parameters
        ----------
        name : str (optional)
            Name of the network. Default is "Zettelkasten".
        engine : str
            Layout engine used by Graphviz. The default is 'sfdp', which is a
            good default. See the graphviz documentation for alternatives.
        shape : str {record, plaintext}
            The shape, or style, of each node. The default is "record".
        """
        self.name = name
        self.engine = engine
        self.graph = Digraph(comment=self.name, engine=self.engine)
        self.shape = shape

    def wrap_title(self, text, width=30):
        """
        Wrap the title to be a certain width.

        Parameters
        ----------
        text : str
            The text to wrap.
        width : int
            The text width, in characters.

        """
        return fill(text, width)

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
        if self.shape == 'plaintext':
            label = self.wrap_title("{} {}".format(node_id, title)).strip()
        elif self.shape == 'record':
            # Wrap in {} so the elements are stacked vertically
            label = "{" + '|'.join([node_id, self.wrap_title(title)]) + "}"

        self.graph.node(node_id, label, shape=self.shape)

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
        self.graph.edge(source, target)

    def render(self, output, view=True):
        """
        Render the network to disk.

        Parameters
        ----------
        output : str
            Name of the output file.
        view : bool
            Show the network using the default PDF viewer. Default is True.

        """
        self.graph.render(output, view=view)
