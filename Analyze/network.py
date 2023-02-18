import pandas as pd
import networkx as nx
import networkx.algorithms.community as nx_comm
import matplotlib.pyplot as plt
import numpy as np
from cdlib import algorithms
from datetime import datetime

class NetworkAnalyzer:

    @classmethod
    def community_layout(cls, graph, partition):
        """
        given a graph and a partition, determine where the nodes should be drawn on a canvas
        :param graph: nx.network
        :param partition: a set of sets
        :return: node positions
        """
        pos_communities = NetworkAnalyzer._position_communities(graph, partition, scale=3)
        pos_nodes = NetworkAnalyzer._position_nodes(graph, partition, scale=0.1)
        # combine positions
        pos = dict()
        for node in graph.nodes():
            pos[node] = pos_communities[node] + pos_nodes[node]
        return pos

    @classmethod
    def give_transaction_variety(cls, filepath):
        """
        return how much people participated in a time series of transactions.
        !!! Note: this part of code is incomplete, do not use.
        :param filepath: filepath
        :return: a list of ints
        """
        df = pd.read_csv(filepath)
        result = []
        for i in range(10):
            df_from = df['from'][i * 1000:i * 1000 + 1000]
            df_to = df['to'][i * 1000:i * 1000 + 1000]
            s = set(df_from)
            s.update(df_to)
            result.append(len(s))
        return result

    @classmethod
    def give_transaction_variety_single(cls, filepath):
        """
        return how much people participated in a file of transactions.
        :param filepath: filepath
        :return: int of num people
        """
        df = pd.read_csv(filepath)
        df_from = df['from']
        df_to = df['to']
        s = set(df_from)
        s.update(df_to)
        return len(s)

    @classmethod
    def give_clustering(cls, filepath):
        """
        from a file path give a average clustering
        :param filepath: filepath
        :return: a float indicating average clustering
        """
        df = pd.read_csv(filepath)
        df["weight"] = [a for a in df["value"]]
        G = nx.from_pandas_edgelist(df, source="from", target="to", edge_attr="weight")
        return nx.average_clustering(G)

    @classmethod
    def apply_all_and_output(cls, filepaths, method):
        """
        apply a method to a pd dataframe and put the output in the ./result folder
        :param filepaths: the paths of the graph in csv
        :param method: a function that only have a single argument pd.dataframe
        :return: pd.dataframe object
        """
        result = []
        for path in filepaths:
            tmp_list = method(path)
            result.append(pd.DataFrame(tmp_list, columns=[filepaths]))
        return pd.concat(result, axis=1)

    @classmethod
    def visualize_comm(cls, graph, communities, threshold=0):
        """
        visualize the community structure
        :param graph: networkx graph
        :param communities: a set of sets containing all communities
        :param threshold: the lowest number of degrees a node has to have in order to be drawn
        :return: None
        """
        partition = dict()
        for com_num in range(len(communities)):
            for node in communities[com_num]:
                partition[node] = com_num
        out_deg = graph.degree()
        to_keep = [n[0] for n in out_deg if n[1] >= 10]
        small_g = graph.subgraph(to_keep)
        to_keep_set = set([n[0] for n in out_deg if n[1] >= 10])
        pos = NetworkAnalyzer.community_layout(small_g, partition)
        for com_num in range(len(communities)):
            nl = [a for a in communities[com_num] if a in to_keep_set]
            rand = (np.random.rand(), np.random.rand(), np.random.rand())
            nc = [rand for _ in range(len(nl))]
            nx.draw(small_g,
                    pos=pos,
                    nodelist=nl,
                    node_color=nc,
                    )
        plt.show()

    @classmethod
    def comm_num_series(cls):
        y = []
        x = []
        for i in range(1, 1066):
            try:
                df = pd.read_csv("./transaction_data/1000/{}.csv".format(i))
                df["weight"] = [a for a in df["value"]]
                G = nx.from_pandas_edgelist(df, source="from", target="to", edge_attr="weight")
                if len(df) == 1000:
                    comm_num = len(algorithms.walktrap(G).communities)
                    y.append(comm_num)
                    x.append(i)
            except KeyError:
                pass
            except nx.exception.AmbiguousSolution:
                pass
            except ValueError:
                pass
            except TypeError:  # I really don't know why this happens all the time, so I have to give up some data
                pass
        return y, x

    @classmethod
    def comm_num_time_scatter(cls):
        y = []
        x = []
        for i in range(1, 1066):
            try:
                df = pd.read_csv("./transaction_data/1000/{}.csv".format(i))
                df["weight"] = [a for a in df["value"]]
                G = nx.from_pandas_edgelist(df, source="from", target="to", edge_attr="weight")
                if len(df) == 1000:
                    comm_num = len(algorithms.walktrap(G).communities)
                    y.append(comm_num)
                    time = datetime.strptime(df['metadata'][999], r"{'blockTimestamp': '%Y-%m-%dT%H:%M:%S.%fZ'}")
                    #  fit in time data
                    #  {'blockTimestamp': '2023-02-09T05:53:47.000Z'}
                    x.append(time)
            except KeyError:
                pass
            except nx.exception.AmbiguousSolution:
                pass
            except ValueError:
                pass
            except TypeError:  # I really don't know why this happens all the time, so I have to give up some data
                pass
        return y, x

    @classmethod
    def _position_communities(cls, g, partition, **kwargs):
        # create a weighted graph, in which each node corresponds to a community,
        # and each edge weight to the number of edges between communities
        between_community_edges = NetworkAnalyzer._find_between_community_edges(g, partition)

        communities = set(partition.values())
        hypergraph = nx.DiGraph()
        hypergraph.add_nodes_from(communities)
        for (ci, cj), edges in between_community_edges.items():
            hypergraph.add_edge(ci, cj, weight=len(edges))

        # find layout for communities
        pos_communities = nx.spring_layout(hypergraph, scale=10)

        # set node positions to position of community
        pos = dict()
        for node, community in partition.items():
            pos[node] = pos_communities[community]
        return pos

    @classmethod
    def _find_between_community_edges(cls, g, partition):

        edges = dict()

        for (ni, nj) in g.edges():
            ci = partition[ni]
            cj = partition[nj]

            if ci != cj:
                try:
                    edges[(ci, cj)] += [(ni, nj)]
                except KeyError:
                    edges[(ci, cj)] = [(ni, nj)]

        return edges

    @classmethod
    def _position_nodes(cls, g, partition, **kwargs):
        """
        Positions nodes within communities.
        """
        communities = dict()
        for node, community in partition.items():
            try:
                communities[community] += [node]
            except KeyError:
                communities[community] = [node]

        pos = dict()
        for ci, nodes in communities.items():
            subgraph = g.subgraph(nodes)
            pos_subgraph = nx.spring_layout(subgraph, **kwargs)
            pos.update(pos_subgraph)

        return pos

