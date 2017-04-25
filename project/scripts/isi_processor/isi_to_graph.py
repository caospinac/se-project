import igraph as ig
from pprint import pprint
import isi_utils as ut
import re


class TreeOfScience():

    def __init__(self, path):
        self.graph = ig.Graph()
        self.path = path
        self.configure()

    def __build_graph(self):
        entries = ut.get_entries(open(self.path, 'r').read().split('\nER\n\n'))
        labels = ut.get_label_list(entries)

        duplicates = ut.detect_duplicate_labels(labels)
        unique_labels = list(set(ut.patch_list(labels, duplicates)))
        edge_relations = ut.extract_edge_relations(entries)
        unique_edge_relations = list(set(
            ut.patch_tuple_list(edge_relations, duplicates)
        ))

        identifiers = dict(zip(unique_labels, range(len(unique_labels))))
        self.graph = ig.Graph(
            ut.patch_tuple_list(unique_edge_relations, identifiers),
            directed=True
        )

        pattern = re.compile(
            r"".join(
                [
                    "^(?P<AU>[^,]+)?, ",
                    "(?P<PY>\d{4})?, ",
                    "(?P<SO>[^,]+)?",
                    "(, (?P<VL>V\d+))?",
                    "(, (?P<PG>P\d+))?",
                    "(, (?P<DI>DOI .+))?",
                ]
            )
        )

        classified_labels = [
            pattern.match(line).groupdict()
            if pattern.match(line) else {
                'AU': None,
                'DI': None,
                'PG': None,
                'PY': None,
                'SO': None,
                'VL': None,
            }
            for line in unique_labels
        ]

        for key in ['AU', 'DI', 'PG', 'PY', 'SO', 'VL']:
            self.graph.vs[key] = [
                article[key] for article in classified_labels
            ]

        self.graph.vs["title"] = [
            ", ".join(
                [
                    x for x in vs.attributes().values() if x != None
                ]
            )
            for vs in self.graph.vs
        ]

        self.graph.vs["id"] = self.graph.vs.indices

    def __preprocess_graph(self):
        valid_vs = self.graph.vs.select(
            lambda v: v.indegree() != 1 or v.outdegree() != 0).indices
        self.graph = self.graph.subgraph(valid_vs)

        self.graph = self.graph.clusters(ig.WEAK).giant()

    def configure(self):
        self.__build_graph()
        self.__preprocess_graph()

    def root(self, offset=0, count=10):
        from operator import itemgetter

        valid_vs = self.graph.vs.select(_outdegree_eq=0).indices
        items = zip(
            self.graph.vs[valid_vs].indices,
            self.graph.vs[valid_vs].indegree(),
            self.graph.vs[valid_vs].outdegree(),
        )

        sorted_items = sorted(items, key=itemgetter(1), reverse=True)
        indices = list(zip(*sorted_items))[0][offset:offset + count]

        return indices

    def trunk(self, offset=0, count=10):
        from operator import itemgetter

        items = zip(
            self.graph.vs.indices,
            self.graph.betweenness(),
        )

        sorted_items = sorted(items, key=itemgetter(1), reverse=True)
        indices = list(zip(*sorted_items))[0][offset:offset + count]
        return indices

    def branch(self, offset=0, count=10):
        raise NotImplementedError('This feature is not implemented yet')

    def leave(self, offset=0, count=10):
        from operator import itemgetter

        valid_vs = self.graph.vs.select(_indegree_eq=0).indices
        items = zip(
            self.graph.vs[valid_vs].indices,
            self.graph.vs[valid_vs].indegree(),
            self.graph.vs[valid_vs].outdegree(),
        )

        sorted_items = sorted(items, key=itemgetter(2), reverse=True)
        indices = list(zip(*sorted_items))[0][offset:offset + count]

        return indices

    def get_tree_graph(self):
        tree = {
            "leave": self.leave(),
            "trunk": self.trunk(),
            "root": self.root()
        }
        def get_indicator_by_group(vs):
            if vs["group"] == "leave":
                return vs.outdegree()
            elif vs["group"] == "trunk":
                return vs.betweenness()
            elif vs["group"] == "root":
                return vs.indegree()

        tree_indices = [z for x in tree.values() for z in x]
        self.graph.vs["group"] = ["None"]*self.graph.vcount()
        for key in tree:
            for vs_index in tree[key]:
                self.graph.vs[vs_index]["group"] = key
        tree_graph = self.graph.subgraph(tree_indices)
        tree_graph.vs["id"] = tree_graph.vs.indices
        tree_graph.vs["label"] = tree_graph.vs["group"]
        tree_graph.vs["value"] = [
            get_indicator_by_group(vs)
            for vs in tree_graph.vs
        ]
        ig.plot(
            tree_graph,
            layout="fr",
            vertex_colors="black",
        )
        return tree_graph


if __name__ == '__main__':
    tree = TreeOfScience('Entrepreneurial Marketing 120ART 22-OCT-16.txt')
    graph_tree = tree.get_tree_graph()
    print('Leave:')
    pprint([tree.graph.vs['title'][x] for x in tree.leave()])
    print('Trunk:')
    pprint([tree.graph.vs['title'][x] for x in tree.trunk()])
    print('Root:')
    pprint([tree.graph.vs['title'][x] for x in tree.root()])

    from jinja2 import Environment, FileSystemLoader
    import json

    nodes = [
        vs.attributes()
        for vs in graph_tree.vs
    ]

    edges = [
        {
            "from": es.tuple[0],
            "to": es.tuple[1],
            "arrows":'to'
        }
        for es in graph_tree.es
    ]

    env = Environment(
        loader=FileSystemLoader(""),
    )

    html_content = env.get_template("graph_plot.html").render(
        nodes=json.dumps(nodes),
        edges=json.dumps(edges)
    )

    with open("my_new_file.html", "w+") as fh:
        fh.write(html_content)
