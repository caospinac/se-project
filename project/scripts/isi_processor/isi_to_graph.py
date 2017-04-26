from pprint import pprint
import json
import re

from .isi_utils import *
import igraph as ig


class TreeOfScience():

    def __init__(self, txt):
        self.graph = ig.Graph()
        self.txt = txt
        self.configure()

    def __build_graph(self):
        entries = get_entries(self.txt.split('\nER\n\n'))
        labels = get_label_list(entries)

        duplicates = detect_duplicate_labels(labels)
        unique_labels = list(set(patch_list(labels, duplicates)))
        edge_relations = extract_edge_relations(entries)
        unique_edge_relations = list(set(
            patch_tuple_list(edge_relations, duplicates)
        ))

        identifiers = dict(zip(unique_labels, range(len(unique_labels))))
        self.graph = ig.Graph(
            patch_tuple_list(unique_edge_relations, identifiers),
            directed=True
        )

        pattern = re.compile(
            r"".join(
                [
                    "^(?P<AU>[^,]+)?, ",
                    "(?P<PY>\d{4})?, ",
                    "(?P<SO>[^,]+)?",
                    "(, V(?P<VL>\d+))?",
                    "(, P(?P<PG>\d+))?",
                    "(, DOI (?P<DI>.+))?",
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

        article_keys = {
                'AU': 'Author',
                'DI': 'Doi',
                'PG': 'Page',
                'PY': 'Published year',
                'SO': 'Journal',
                'VL': 'Volume'
        }

        self.graph.vs["title"] = [
            "<br>".join(
                [
                    "{}: {}".format(
                        article_keys[x], vs[x] if vs[x] is not None else "N/A"
                    )
                    for x in article_keys.keys()
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

        def get_color_by_group(group):
            if group == "leave":
                return "#4CAC33"
            elif group == "trunk":
                return "#F5A200"
            elif group == "root":
                return "#824D1E"

        tree_indices = [z for x in tree.values() for z in x]
        self.graph.vs["group"] = ["None"] * self.graph.vcount()
        self.graph.vs["color"] = ["None"] * self.graph.vcount()
        for key in tree:
            for v_index in tree[key]:
                self.graph.vs[v_index]["group"] = key
                self.graph.vs[v_index]["color"] = get_color_by_group(key)
                self.graph.vs[v_index]["label"] = self.graph.vs[v_index]["PY"]

        tree_graph = self.graph.subgraph(tree_indices)
        tree_graph = tree_graph.clusters(ig.WEAK).giant()
        tree_graph.vs["id"] = tree_graph.vs.indices
        tree_graph.vs["value"] = [
            get_indicator_by_group(vs)
            for vs in tree_graph.vs
        ]

        return tree_graph

    def get_graph(self):
        tree_graph = self.get_tree_graph()
        nodes = [
            vs.attributes()
            for vs in tree_graph.vs
        ]

        edges = [
            {
                "from": es.tuple[0],
                "to": es.tuple[1],
                "arrows":'to'
            }
            for es in tree_graph.es
        ]
        return json.dumps(nodes), json.dumps(edges)


if __name__ == '__main__':
    tree = TreeOfScience(
        open(
            'Entrepreneurial Marketing 120ART 22-OCT-16.txt',
            'r'
        ).read()
    )

    tree.get_html_graph()

    with open("resulting_graph.html", "w+") as fh:
        fh.write(tree.get_html_graph())
    print('Leave:')
    pprint([tree.graph.vs['title'][x] for x in tree.leave()])
    print('Trunk:')
    pprint([tree.graph.vs['title'][x] for x in tree.trunk()])
    print('Root:')
    pprint([tree.graph.vs['title'][x] for x in tree.root()])
