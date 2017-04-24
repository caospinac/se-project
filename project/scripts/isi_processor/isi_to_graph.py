import igraph as ig
import re
from pprint import pprint
import isi_utils as ut


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

        self.graph.vs['label'] = unique_labels
        self.graph.vs['betweenness'] = self.graph.betweenness()

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
            self.graph.vs['betweenness'],
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


if __name__ == '__main__':
    # <AQUI EL ARCHIVO!!!!!!!!!!!!
    tree = TreeOfScience('Entrepreneurial Marketing 120ART 22-OCT-16.txt')
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    print('Leave:')
    pprint([tree.graph.vs['label'][x] for x in tree.leave()])
    print('Trunk:')
    pprint([tree.graph.vs['label'][x] for x in tree.trunk()])
    print('Root:')
    pprint([tree.graph.vs['label'][x] for x in tree.root()])
